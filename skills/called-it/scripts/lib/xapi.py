"""X API v2 helpers (optional; needs X_BEARER_TOKEN). Standard library only.

Two jobs: hydrate a thread so every claim is the posted text rather than a mirror's paraphrase, and
search one account inside a date window for more prediction posts. Every call appends a line to
cache/xapi-ledger.jsonl with the post count so the spend is visible (pay-per-use bills per post read).
"""
from __future__ import annotations

import html
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from . import config

API = "https://api.x.com/2"
FIELDS = "created_at,text,note_tweet,public_metrics,referenced_tweets,conversation_id,author_id"
PRICE_PER_POST_USD = 0.005  # the pay-per-use rate observed on this account; adjust in run.json if it changes


class XError(RuntimeError):
    pass


def _get(path: str, params: dict, token: str) -> dict:
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    delay = 2.0
    for attempt in range(5):
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")[:400]
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(delay)
                delay = min(delay * 2, 60)
                continue
            raise XError(f"HTTP {e.code}: {body}")
    raise XError("gave up after retries")


def _text(t: dict) -> str:
    # The API HTML-escapes <, > and & in post text; store the characters the author typed.
    return html.unescape((t.get("note_tweet") or {}).get("text") or t.get("text", ""))


def _ledger(cache_dir: Path, what: str, n: int) -> None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    with (cache_dir / "xapi-ledger.jsonl").open("a") as f:
        f.write(json.dumps({"at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "what": what,
                            "posts": n, "est_usd": round(n * PRICE_PER_POST_USD, 4)}) + "\n")


def post_url(username: str, post_id: str) -> str:
    return f"https://x.com/{username}/status/{post_id}"


def thread(root_id: str, username: str, cache_dir: Path, day_pad: int = 2) -> list[dict]:
    """All posts by `username` in the conversation rooted at root_id, oldest first, from cache when present."""
    token = config.env("X_BEARER_TOKEN")
    cache = cache_dir / f"x-thread-{root_id}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    if not token:
        raise XError("X_BEARER_TOKEN not set")
    root = _get(f"/tweets/{root_id}", {"tweet.fields": FIELDS, "expansions": "author_id", "user.fields": "username"}, token)
    posts = [root["data"]]
    created = root["data"]["created_at"][:10]
    import datetime as dt
    start = (dt.date.fromisoformat(created) - dt.timedelta(days=0)).isoformat() + "T00:00:00Z"
    end = (dt.date.fromisoformat(created) + dt.timedelta(days=day_pad)).isoformat() + "T00:00:00Z"
    params = {"query": f"conversation_id:{root_id} from:{username}", "max_results": 100, "tweet.fields": FIELDS,
              "start_time": start, "end_time": end}
    while True:
        page = _get("/tweets/search/all", params, token)
        posts.extend(page.get("data", []))
        nxt = page.get("meta", {}).get("next_token")
        if not nxt:
            break
        params["next_token"] = nxt
        time.sleep(1.1)  # full-archive search is rate limited to about one request per second
    seen, out = set(), []
    for t in sorted(posts, key=lambda t: int(t["id"])):
        if t["id"] in seen:
            continue
        seen.add(t["id"])
        out.append({"id": t["id"], "created_at": t["created_at"], "text": _text(t), "url": post_url(username, t["id"]),
                    "metrics": t.get("public_metrics", {})})
    _ledger(cache_dir, f"thread {root_id}", len(out))
    cache.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    return out


def search_window(username: str, start: str, end: str, terms: str, cache_dir: Path, max_pages: int = 3) -> list[dict]:
    """Posts by `username` between start and end (YYYY-MM-DD) matching `terms` (X query syntax, e.g. 'predict OR 2026')."""
    token = config.env("X_BEARER_TOKEN")
    key = f"x-search-{username}-{start}-{end}-{abs(hash(terms))}.json"
    cache = cache_dir / key
    if cache.exists():
        return json.loads(cache.read_text())
    if not token:
        raise XError("X_BEARER_TOKEN not set")
    params = {"query": f"from:{username} ({terms}) -is:retweet", "max_results": 100, "tweet.fields": FIELDS,
              "start_time": f"{start}T00:00:00Z", "end_time": f"{end}T23:59:59Z"}
    posts = []
    for _ in range(max_pages):
        page = _get("/tweets/search/all", params, token)
        posts.extend(page.get("data", []))
        nxt = page.get("meta", {}).get("next_token")
        if not nxt:
            break
        params["next_token"] = nxt
        time.sleep(1.1)
    out = [{"id": t["id"], "created_at": t["created_at"], "text": _text(t), "url": post_url(username, t["id"]),
            "conversation_id": t.get("conversation_id"), "metrics": t.get("public_metrics", {})}
           for t in sorted(posts, key=lambda t: int(t["id"]))]
    _ledger(cache_dir, f"search {username} {start}..{end}", len(out))
    cache.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    return out


def count_window(username: str, start: str, end: str, terms: str) -> int:
    """How many posts a search_window call would read, before paying for it."""
    token = config.env("X_BEARER_TOKEN")
    if not token:
        raise XError("X_BEARER_TOKEN not set")
    params = {"query": f"from:{username} ({terms}) -is:retweet", "granularity": "day",
              "start_time": f"{start}T00:00:00Z", "end_time": f"{end}T23:59:59Z"}
    page = _get("/tweets/counts/all", params, token)
    return int(page.get("meta", {}).get("total_tweet_count", 0))
