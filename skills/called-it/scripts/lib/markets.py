"""Prediction-market lookups (no keys). A resolved market on the same question is tier 3 evidence.

These return candidates. The model decides whether a market actually asks the claim's question; a
market that is merely about the same topic is not evidence of anything.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

POLYMARKET_SEARCH = "https://gamma-api.polymarket.com/public-search"
POLYMARKET_MARKETS = "https://gamma-api.polymarket.com/markets"
KALSHI_EVENTS = "https://api.elections.kalshi.com/trade-api/v2/events"
UA = "called-it/1.0 (research; +https://github.com/rickmanelius/called-it)"


def _get(url: str, params: dict | None = None) -> dict | list:
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def _cached(cache_dir: Path, key: str, fn):
    cache_dir.mkdir(parents=True, exist_ok=True)
    p = cache_dir / f"market-{key}.json"
    if p.exists():
        return json.loads(p.read_text())
    try:
        data = fn()
    except Exception as e:  # network or API shape change: return nothing rather than fail the stage
        data = {"error": repr(e), "results": []}
    p.write_text(json.dumps(data, ensure_ascii=False))
    return data


def polymarket(query: str, cache_dir: Path) -> dict:
    """Events whose title matches the query, with each market's question, close date and outcome prices."""
    def go():
        raw = _get(POLYMARKET_SEARCH, {"q": query, "limit_per_type": 10})
        results = []
        for ev in raw.get("events", []) if isinstance(raw, dict) else []:
            for m in ev.get("markets", []) or []:
                prices = m.get("outcomePrices")
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices)
                    except json.JSONDecodeError:
                        pass
                results.append({
                    "venue": "polymarket",
                    "event": ev.get("title"),
                    "question": m.get("question"),
                    "slug": m.get("slug"),
                    "url": f"https://polymarket.com/event/{ev.get('slug')}" if ev.get("slug") else None,
                    "closed": m.get("closed"),
                    "end_date": m.get("endDate"),
                    "outcomes": m.get("outcomes"),
                    "outcome_prices": prices,
                    "volume": m.get("volumeNum") or m.get("volume"),
                })
        return {"query": query, "results": results}
    return _cached(cache_dir, "pm-" + urllib.parse.quote_plus(query)[:80], go)


def kalshi(query: str, cache_dir: Path, status: str = "settled", pages: int = 3) -> dict:
    """Settled Kalshi events whose title contains every word of the query (case-insensitive). The public
    API has no text search, so this pages through recent settled events and filters locally."""
    words = [w.lower() for w in query.split() if len(w) > 2]

    def go():
        results, cursor = [], None
        for _ in range(pages):
            params = {"status": status, "limit": 200, "with_nested_markets": "true"}
            if cursor:
                params["cursor"] = cursor
            page = _get(KALSHI_EVENTS, params)
            for ev in page.get("events", []):
                title = (ev.get("title") or "").lower()
                if all(w in title for w in words):
                    for m in ev.get("markets", []) or []:
                        results.append({
                            "venue": "kalshi",
                            "event": ev.get("title"),
                            "question": m.get("title") or m.get("subtitle"),
                            "ticker": m.get("ticker"),
                            "url": f"https://kalshi.com/markets/{ev.get('series_ticker', '').lower()}" if ev.get("series_ticker") else None,
                            "status": m.get("status"),
                            "result": m.get("result"),
                            "close_time": m.get("close_time"),
                            "settlement_time": m.get("settlement_time"),
                        })
            cursor = page.get("cursor")
            if not cursor:
                break
            time.sleep(0.3)
        return {"query": query, "results": results}
    return _cached(cache_dir, "ks-" + urllib.parse.quote_plus(query)[:80], go)
