"""Cached page fetching and text extraction. Standard library only.

Pages are cached under runs/<run>/cache/pages/<sha256(url)>.json with the raw body and the extracted
text, so a replay never touches the network and the exact text that was graded is in the repo.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

UA = "Mozilla/5.0 (compatible; called-it/1.0; +https://github.com/rickmanelius/called-it)"
SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "footer", "header", "form", "iframe"}
BLOCK_TAGS = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "blockquote", "pre", "section", "article"}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip = 0
        self.title = ""
        self._in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in SKIP_TAGS:
            self.skip += 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS and self.skip:
            self.skip -= 1
        if tag in BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if not self.skip:
            self.parts.append(data)


def html_to_text(body: str) -> tuple[str, str]:
    p = _Text()
    try:
        p.feed(body)
    except Exception:
        pass
    text = "".join(p.parts)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip(), html.unescape(p.title).strip()


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:24]


class Pages:
    def __init__(self, cache_dir: Path):
        self.dir = cache_dir
        self.dir.mkdir(parents=True, exist_ok=True)

    def path(self, url: str) -> Path:
        return self.dir / f"{url_hash(url)}.json"

    def get(self, url: str, refresh: bool = False, timeout: int = 30) -> dict:
        p = self.path(url)
        if p.exists() and not refresh:
            return json.loads(p.read_text())
        rec = {"url": url, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
                                                   "Accept-Encoding": "identity"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                enc = (resp.headers.get("Content-Encoding") or "").lower()
                if enc in ("gzip", "x-gzip", "deflate") or raw[:2] == b"\x1f\x8b":
                    import zlib
                    try:
                        raw = zlib.decompress(raw, zlib.MAX_WBITS | 32)
                    except zlib.error:
                        pass
                ctype = resp.headers.get("Content-Type", "")
                rec.update(status=resp.status, content_type=ctype, final_url=resp.geturl())
                if "pdf" in ctype or url.lower().endswith(".pdf"):
                    rec["text"] = pdf_to_text(raw)
                    rec["title"] = url.rsplit("/", 1)[-1]
                else:
                    body = raw.decode(resp.headers.get_content_charset() or "utf-8", errors="replace")
                    if "web.archive.org/web/" in url:
                        body = WAYBACK_TOOLBAR.sub("", body)
                    # Only the extracted text is kept: it is what gets graded, its hash is what sources.jsonl
                    # records, and raw HTML drags third-party scripts and keys into a repo meant to be public.
                    rec["text"], rec["title"] = html_to_text(body)
                    rec["html_bytes"] = len(raw)
        except urllib.error.HTTPError as e:
            rec.update(status=e.code, error=str(e), text="")
        except Exception as e:  # network, timeout, decode
            rec.update(status=0, error=repr(e), text="")
        rec["sha256"] = hashlib.sha256((rec.get("text") or "").encode()).hexdigest()
        p.write_text(json.dumps(rec, ensure_ascii=False))
        return rec

    def put_text(self, url: str, text: str, title: str = "", note: str = "") -> dict:
        """Store text obtained another way (a pasted article, a transcript, a browser copy)."""
        rec = {
            "url": url, "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "status": 200,
            "content_type": "text/plain; manual", "text": text, "title": title, "note": note,
            "sha256": hashlib.sha256(text.encode()).hexdigest(),
        }
        self.path(url).write_text(json.dumps(rec, ensure_ascii=False))
        return rec


def wayback_closest(url: str, timestamp: str) -> dict | None:
    """The Wayback Machine snapshot closest to timestamp (YYYYMMDD). Returns {url, timestamp} using the `id_`
    form, which serves the archived page without the Wayback toolbar so the extracted text is the page's own."""
    # The availability API wants the bare URL (scheme optional); percent-encoding the slashes makes it return nothing.
    bare = url.split("://", 1)[-1]
    api = f"https://archive.org/wayback/available?url={bare}&timestamp={timestamp}"
    data = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": UA}), timeout=30) as resp:
                data = json.loads(resp.read())
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:  # archive.org rate-limits bursts of lookups
                time.sleep(20 * (attempt + 1))
                continue
            import sys
            print(f"wayback lookup failed: {e!r}", file=sys.stderr)
            return None
        except Exception as e:  # say why, so a network failure is not mistaken for "never archived"
            import sys
            print(f"wayback lookup failed: {e!r}", file=sys.stderr)
            return None
    if data is None:
        return None
    snap = (data.get("archived_snapshots") or {}).get("closest")
    if not snap or not snap.get("available"):
        return None
    ts = snap["timestamp"]
    # The `id_` form serves the original bytes, which are often brotli-compressed and undecodable without a
    # dependency; the plain form serves decoded HTML plus a toolbar that html_to_text strips (see WAYBACK_TOOLBAR).
    return {"url": f"https://web.archive.org/web/{ts}/{url}", "timestamp": ts}


WAYBACK_TOOLBAR = re.compile(r"<!--\s*BEGIN WAYBACK TOOLBAR INSERT\s*-->.*?<!--\s*END WAYBACK TOOLBAR INSERT\s*-->", re.S)


def pdf_to_text(raw: bytes) -> str:
    """Best effort without a dependency: use pdftotext if present, else return an empty string and let the
    model read the PDF with its own tools. Never guess at PDF content."""
    exe = shutil.which("pdftotext")
    if not exe:
        return ""
    try:
        out = subprocess.run([exe, "-layout", "-", "-"], input=raw, capture_output=True, timeout=60)
        return out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return ""


def youtube_captions(video_id: str, out_dir: Path, lang: str = "en") -> Path | None:
    """Download English captions (manual or auto) with yt-dlp if installed. Returns the .vtt path."""
    exe = shutil.which("yt-dlp")
    if not exe:
        return None
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [exe, "-q", "--skip-download", "--write-auto-sub", "--write-sub", "--sub-lang", lang,
           "--sub-format", "vtt", "-o", str(out_dir / "%(id)s.%(ext)s"), f"https://www.youtube.com/watch?v={video_id}"]
    try:
        subprocess.run(cmd, capture_output=True, timeout=180)
    except Exception:
        return None
    hits = sorted(out_dir.glob(f"{video_id}*.vtt"))
    return hits[0] if hits else None


def vtt_to_text(vtt: str) -> str:
    """Collapse a WebVTT file into plain text, dropping timestamps, cue settings and the rolling duplicates
    that YouTube auto-captions produce."""
    lines = []
    last = ""
    for line in vtt.splitlines():
        s = line.strip()
        if not s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in s or s.isdigit():
            continue
        s = re.sub(r"<[^>]+>", "", s)
        s = html.unescape(s)
        if s and s != last:
            lines.append(s)
            last = s
    return re.sub(r"\s+", " ", " ".join(lines)).strip()
