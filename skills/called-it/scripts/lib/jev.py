"""TypeSafe System One (Jev) client. Standard library only.

Every request is cached on disk under the run, keyed by the hash of (model, state, questions),
and the cache stores the model that actually answered. A run can therefore be replayed with no
key and no network, and a published scorecard states exactly which model graded it.

When there is no TYPESAFE_API_KEY, `ask` raises NoGrader. The CLI then writes the unanswered
questions to `cache/pending/` for the host model to answer in the same shape (see SKILL.md).
"""
from __future__ import annotations

import hashlib
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from . import config


class NoGrader(RuntimeError):
    pass


class JevError(RuntimeError):
    pass


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def request_hash(model: str, state, questions: dict) -> str:
    return hashlib.sha256(canonical({"model": model, "state": state, "questions": questions}).encode()).hexdigest()


class Cache:
    def __init__(self, root: Path):
        self.root = root
        self.answers = root / "answers"
        self.pending = root / "pending"
        self.answers.mkdir(parents=True, exist_ok=True)
        self.pending.mkdir(parents=True, exist_ok=True)

    def get(self, h: str) -> dict | None:
        p = self.answers / f"{h}.json"
        if p.exists():
            return json.loads(p.read_text())
        return None

    def put(self, h: str, record: dict) -> None:
        (self.answers / f"{h}.json").write_text(json.dumps(record, indent=1, ensure_ascii=False))
        pend = self.pending / f"{h}.json"
        if pend.exists():
            pend.unlink()

    def mark_pending(self, h: str, model: str, state, questions: dict) -> None:
        p = self.pending / f"{h}.json"
        if not p.exists():
            p.write_text(json.dumps({"hash": h, "model": model, "state": state, "questions": questions}, indent=1, ensure_ascii=False))

    def pending_count(self) -> int:
        return len(list(self.pending.glob("*.json")))


def _post(model: str, state, questions: dict, key: str) -> dict:
    body = json.dumps({"model": model, "state": state, "questions": questions}).encode()
    delay = 1.0
    last = None
    for attempt in range(6):
        req = urllib.request.Request(
            config.JEV_ENDPOINT, data=body, method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=config.JEV_TIMEOUT_S) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            text = e.read().decode(errors="replace")[:500]
            last = f"HTTP {e.code}: {text}"
            if e.code in (408, 429, 500, 502, 503, 504, 529):
                time.sleep(delay)
                delay = min(delay * 2, 20)
                continue
            raise JevError(last)
        except (urllib.error.URLError, TimeoutError) as e:
            last = str(e)
            time.sleep(delay)
            delay = min(delay * 2, 20)
    raise JevError(f"gave up after retries: {last}")


class Jev:
    """ask() returns the `answers` object from the API, from cache when present."""

    def __init__(self, cache: Cache, model: str = config.JEV_MODEL, offline: bool = False):
        self.cache = cache
        self.model = model
        self.offline = offline
        self.key = config.env("TYPESAFE_API_KEY")
        self.calls = 0
        self.input_tokens = 0

    def ask(self, state, questions: dict) -> dict:
        h = request_hash(self.model, state, questions)
        hit = self.cache.get(h)
        if hit:
            return hit["answers"]
        if self.offline or not self.key:
            self.cache.mark_pending(h, self.model, state, questions)
            raise NoGrader(h)
        resp = _post(self.model, state, questions, self.key)
        self.calls += 1
        self.input_tokens += int(resp.get("usage", {}).get("input_tokens", 0))
        record = {
            "hash": h,
            "requested_model": self.model,
            "answered_model": resp.get("model"),
            "grader": "jev",
            "state": state,
            "questions": questions,
            "answers": resp["answers"],
            "usage": resp.get("usage"),
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.cache.put(h, record)
        return record["answers"]

    def ask_fresh(self, state, questions: dict) -> dict:
        """Ask live, bypassing and not updating the cache. For measuring drift against a cached answer."""
        if not self.key:
            raise NoGrader("fresh ask needs TYPESAFE_API_KEY")
        resp = _post(self.model, state, questions, self.key)
        self.calls += 1
        self.input_tokens += int(resp.get("usage", {}).get("input_tokens", 0))
        return resp["answers"]

    def ask_many(self, items: list[tuple], workers: int = config.JEV_MAX_CONCURRENCY) -> list[dict | None]:
        """items: list of (state, questions). Returns answers in order; None where no grader was available."""
        def one(item):
            try:
                return self.ask(*item)
            except NoGrader:
                return None
        with ThreadPoolExecutor(max_workers=workers) as ex:
            return list(ex.map(one, items))


def answered_models(cache: Cache) -> dict[str, int]:
    counts: dict[str, int] = {}
    for p in cache.answers.glob("*.json"):
        rec = json.loads(p.read_text())
        m = rec.get("answered_model") or rec.get("grader") or "unknown"
        counts[m] = counts.get(m, 0) + 1
    return counts


# Question builders. IDs are for code; the model never sees them, so the meaning lives in the text.

def noul(instructions: str, true: str | None = None, false: str | None = None) -> dict:
    q = {"type": "noul", "instructions": instructions}
    if true or false:
        q["criteria"] = {"true": true or "", "false": false or ""}
    return q


def score(instructions: str, levels: list[str]) -> dict:
    return {"type": "score", "instructions": instructions, "criteria": levels}


def choice(instructions: str, options: dict[str, str]) -> dict:
    return {"type": "choice", "instructions": instructions, "criteria": options}
