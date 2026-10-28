"""Names, versions, defaults. Renaming the tool means editing NAME here and moving the skill folder."""
from __future__ import annotations

import os
from pathlib import Path

NAME = "called-it"
VERSION = "1.0.0"
BADGE_EMOJI = "🎯"

# Grader
JEV_ENDPOINT = "https://api.typesafe.ai/v1/systemone"
JEV_MODELS_ENDPOINT = "https://api.typesafe.ai/v1/models"
# Pinned to the name the alias resolved to on 2026-10-24. Never pin an alias: it moves on release.
JEV_MODEL = "jev-1.14.0"
JEV_MAX_CONCURRENCY = 4
JEV_TIMEOUT_S = 60

# Decision thresholds. Reported in every scorecard, never hidden.
THRESHOLDS = {
    "yes": 0.70,          # a noul at or above this counts as yes
    "no": 0.30,           # at or below this counts as no
    "min_strength": 1.0,  # evidence_strength score (0..2) needed before any bar can be met
}

BARS = ("strict", "standard", "lenient")
VERDICTS = ("met", "not_met", "unresolved")

EVIDENCE_TIERS = {
    1: "primary: official announcement, filing, shipped product, on-chain or price data, government statistics",
    2: "reputable reporting: a major outlet or a domain-leading trade publication",
    3: "market resolution: a Polymarket or Kalshi market on the question that resolved",
    4: "author's own later statement: an admission of a miss is strong, a claim of a hit is weak",
    5: "social chatter: posts or comments from people without standing; never sufficient alone",
}

SPECIFICITY_LEVELS = [
    "A mood, theme or direction with no checkable outcome (for example: 'AI will matter more')",
    "A named outcome with no number, date or threshold (for example: 'agents will reshape company operations')",
    "A named outcome with one checkable element: a number, a date, a named party or a threshold",
    "A named outcome with a number or threshold and a time by which it happens",
]

STRENGTH_LEVELS = [
    "Only anecdotes or social posts from people without standing",
    "A single reputable report, an indirect official statement, or the author's own later admission",
    "Multiple independent reputable reports, a direct primary source, or a resolved prediction market",
]


def env(name: str) -> str | None:
    v = os.environ.get(name)
    return v if v else None


def has_jev() -> bool:
    return env("TYPESAFE_API_KEY") is not None


def has_x() -> bool:
    return env("X_BEARER_TOKEN") is not None


def run_dir(root: Path, run_name: str) -> Path:
    return root / "runs" / run_name


def today() -> str:
    import datetime as _dt
    return _dt.date.today().isoformat()
