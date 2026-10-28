"""The JSONL contract between the model (which does the reading and judging) and the scripts.

One row per line. Required keys are checked here so a malformed row fails at the stage boundary,
not three stages later inside the renderer.
"""
from __future__ import annotations

import json
from pathlib import Path

from . import config

RUN_KEYS = {"name", "subject", "target_year", "season_window", "evidence_window", "canonical_urls", "top_n", "grader", "thresholds"}
SOURCE_KEYS = {"id", "url", "title", "date", "format", "access"}
CLAIM_KEYS = {"id", "source_id", "quote", "date", "author"}
RUBRIC_KEYS = {"claim_id", "bars"}
EVIDENCE_KEYS = {"id", "claim_id", "url", "date", "source", "tier", "quote", "direction"}
GRADE_KEYS = {"claim_id", "bar", "verdict", "met_p", "contradicted_p", "strength", "grader"}

FORMATS = {"essay", "newsletter", "thread", "podcast", "transcript", "video", "pdf", "deck", "article", "page", "other"}
ACCESS = {"free", "paywalled", "login", "unreadable"}
DIRECTIONS = {"supports", "contradicts", "neutral"}


class SchemaError(ValueError):
    pass


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    rows = []
    for i, line in enumerate(path.read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise SchemaError(f"{path.name} line {i}: {e}") from None
    return rows


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def _need(row: dict, keys: set, what: str, i: int) -> None:
    missing = keys - set(row)
    if missing:
        raise SchemaError(f"{what} row {i} ({row.get('id') or row.get('claim_id') or '?'}) missing {sorted(missing)}")


def validate_run(run: dict) -> None:
    _need(run, RUN_KEYS, "run.json", 0)
    for w in ("season_window", "evidence_window"):
        if set(run[w]) != {"start", "end"}:
            raise SchemaError(f"run.json {w} needs start and end")
    if run["grader"].get("provider") not in {"jev", "model"}:
        raise SchemaError("run.json grader.provider must be 'jev' or 'model'")


def validate_sources(rows: list[dict]) -> None:
    seen = set()
    for i, r in enumerate(rows, 1):
        _need(r, SOURCE_KEYS, "sources", i)
        if r["id"] in seen:
            raise SchemaError(f"sources: duplicate id {r['id']}")
        seen.add(r["id"])
        if r["format"] not in FORMATS:
            raise SchemaError(f"sources {r['id']}: format {r['format']!r} not in {sorted(FORMATS)}")
        if r["access"] not in ACCESS:
            raise SchemaError(f"sources {r['id']}: access {r['access']!r} not in {sorted(ACCESS)}")


def validate_claims(rows: list[dict], sources: list[dict] | None = None) -> None:
    ids = {s["id"] for s in sources} if sources else None
    seen = set()
    for i, r in enumerate(rows, 1):
        _need(r, CLAIM_KEYS, "claims", i)
        if r["id"] in seen:
            raise SchemaError(f"claims: duplicate id {r['id']}")
        seen.add(r["id"])
        if ids is not None and r["source_id"] not in ids:
            raise SchemaError(f"claims {r['id']}: unknown source_id {r['source_id']}")
        if "kind" in r and r["kind"] not in {"binary", "spectrum"}:
            raise SchemaError(f"claims {r['id']}: kind must be binary or spectrum")


def validate_rubrics(rows: list[dict], claims: list[dict] | None = None) -> None:
    ids = {c["id"] for c in claims} if claims else None
    for i, r in enumerate(rows, 1):
        _need(r, RUBRIC_KEYS, "rubrics", i)
        if ids is not None and r["claim_id"] not in ids:
            raise SchemaError(f"rubrics: unknown claim_id {r['claim_id']}")
        bars = r["bars"]
        for b in config.BARS:
            if b not in bars or not isinstance(bars[b], dict) or not bars[b].get("criterion"):
                raise SchemaError(f"rubrics {r['claim_id']}: bar {b} needs a 'criterion' string")


def validate_evidence(rows: list[dict], claims: list[dict] | None = None) -> None:
    ids = {c["id"] for c in claims} if claims else None
    seen = set()
    for i, r in enumerate(rows, 1):
        _need(r, EVIDENCE_KEYS, "evidence", i)
        if r["id"] in seen:
            raise SchemaError(f"evidence: duplicate id {r['id']}")
        seen.add(r["id"])
        if ids is not None and r["claim_id"] not in ids:
            raise SchemaError(f"evidence {r['id']}: unknown claim_id {r['claim_id']}")
        if r["tier"] not in config.EVIDENCE_TIERS:
            raise SchemaError(f"evidence {r['id']}: tier must be 1..5")
        if r["direction"] not in DIRECTIONS:
            raise SchemaError(f"evidence {r['id']}: direction must be one of {sorted(DIRECTIONS)}")
        for b in r.get("bars", []):
            if b not in config.BARS:
                raise SchemaError(f"evidence {r['id']}: bar {b!r} unknown")


def validate_grades(rows: list[dict]) -> None:
    for i, r in enumerate(rows, 1):
        _need(r, GRADE_KEYS, "grades", i)
        if r["bar"] not in config.BARS or r["verdict"] not in config.VERDICTS:
            raise SchemaError(f"grades row {i}: bad bar or verdict")


def in_window(date: str, window: dict) -> bool:
    return bool(date) and window["start"] <= date[:10] <= window["end"]
