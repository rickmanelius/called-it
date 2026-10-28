#!/usr/bin/env python3
"""Download the brand fonts as woff2 from Google Fonts into site/assets/fonts/, so headless Chrome
renders every page, card, figure and slide with the same type. Standard library only.

    python3 tools/fetch_fonts.py

Asks the css2 endpoint with a modern Chrome user agent (that is what makes it answer with woff2
URLs), keeps the latin subset of each weight named in lib/brand.py, saves each file under the name
brand.py expects, and writes fonts.json beside them with the source URLs. Idempotent: files that
already exist are left alone unless --force is given.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))
from lib import brand  # noqa: E402

OUT = ROOT / "site" / "assets" / "fonts"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/130.0.0.0 Safari/537.36")


def css_url() -> str:
    fams = {}
    for family, _, _, weights in brand.FONT_FILES:
        fams.setdefault(family, []).extend(str(w) for w in weights)
    parts = [f"family={family.replace(' ', '+')}:wght@{';'.join(sorted(set(ws)))}" for family, ws in fams.items()]
    return "https://fonts.googleapis.com/css2?" + "&".join(parts) + "&display=swap"


def get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def parse_blocks(css: str):
    """Yield (subset, family, weight, url) for every @font-face block in Google's css2 answer."""
    for m in re.finditer(r"/\*\s*([a-z0-9-]+)\s*\*/\s*@font-face\s*\{(.*?)\}", css, re.S):
        subset, body = m.group(1), m.group(2)
        fam = re.search(r"font-family:\s*'([^']+)'", body)
        wt = re.search(r"font-weight:\s*(\d+)", body)
        url = re.search(r"url\(([^)]+\.woff2)\)", body)
        if fam and wt and url:
            yield subset, fam.group(1), int(wt.group(1)), url.group(1)


def main(argv):
    force = "--force" in argv
    OUT.mkdir(parents=True, exist_ok=True)
    css = get(css_url()).decode("utf-8")
    blocks = list(parse_blocks(css))
    manifest = {}
    for family, css_weight, name, weights in brand.FONT_FILES:
        hit = next((b for b in blocks if b[0] == "latin" and b[1] == family and b[2] in weights), None)
        if not hit:
            continue
        _, _, weight, url = hit
        dest = OUT / name
        if dest.exists() and not force:
            print(f"kept {dest.name} ({dest.stat().st_size} bytes)")
        else:
            dest.write_bytes(get(url))
            print(f"fetched {dest.name} ({dest.stat().st_size} bytes) from {url}")
        manifest[name] = {"family": family, "css_weight": css_weight, "requested_weight": weight, "subset": "latin", "source": url}
    missing = [name for _, _, name, _ in brand.FONT_FILES if name not in manifest]
    (OUT / "fonts.json").write_text(json.dumps({"css": css_url(), "files": manifest}, indent=1) + "\n")
    if missing:
        sys.exit(f"missing: {', '.join(missing)}")
    print(f"wrote {OUT / 'fonts.json'}; {len(manifest)} files")


if __name__ == "__main__":
    main(sys.argv)
