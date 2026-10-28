#!/usr/bin/env python3
"""Render the share cards on the Called It! brand (lib/brand.py), 1200x630 each, so a shared link and the
article show the same picture. Deterministic given the same data.json files; standard library only.

    python3 tools/build_cards.py [runs/every runs/doll ...]

Per run (one composition, written to two identical files):
  article/cards/<run>.png             the card at the top of the run's article section
  site/assets/social/<run>.png        the og:image / twitter:image of the run's page
Gallery (the canonical share card for the whole thing):
  site/assets/social/index.png  and  article/cards/index.png
Also refreshed, for the site's "scorecard as rendered" figure:
  article/figures/scorecard-<run>.png the header of runs/<run>/report.html at 1x, 1200x640

Everything is 1200x630 CSS px rendered at device scale 1 through the same headless Chrome
tools/render_png.py uses, so each file is exactly 1200x630. Nothing on a card is under 22 CSS px.
"""
from __future__ import annotations

import html
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))
import render_png  # noqa: E402
from lib import brand, config  # noqa: E402

W, H = 1200, 630
TMP = ROOT / "tmp" / "cards"
FONT_PREFIX = (ROOT / "site" / "assets" / "fonts").as_uri() + "/"
SITE_HOST = "rickmanelius.github.io/called-it"  # placeholder until GitHub Pages exists


def esc(s):
    return html.escape(str(s if s is not None else ""))


def pct(x):
    return "n/a" if x is None else f"{round(x * 100)}%"


CARD_CSS = """
body { width: 1200px; height: 630px; overflow: hidden; }
.card { width: 1200px; height: 630px; padding: 52px 64px 48px; display: flex; flex-direction: column; justify-content: space-between; background: var(--page); }
.chip { font-family: var(--font-mono); font-size: 22px; font-weight: 500; letter-spacing: .04em; text-transform: uppercase; color: var(--muted); }
h1 { margin: 10px 0 0; font-size: 58px; font-weight: 700; line-height: 1.05; letter-spacing: -.02em; color: var(--ink); }
.tiles { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 18px; margin: 26px 0 0; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 16px; padding: 20px 24px 18px; display: flex; flex-direction: column; gap: 4px; }
.tile .k { font-size: 22px; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); }
.tile .v { font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 78px; font-weight: 600; line-height: 1; color: var(--ink); margin: 6px 0 4px; white-space: nowrap; }
.tile .v small { font-size: 30px; font-weight: 600; letter-spacing: 0; }
.tile .s { font-size: 22px; color: var(--muted); line-height: 1.25; }
.tile.gap { background: var(--accent); border-color: var(--accent); }
.tile.gap .k, .tile.gap .s { color: var(--on-accent-small); } .tile.gap .v { color: var(--on-accent); }
.bars { margin: 22px 0 0; display: flex; flex-direction: column; gap: 10px; }
.bar { display: grid; grid-template-columns: 130px minmax(0, 1fr); align-items: center; gap: 14px; }
.bar .l { font-size: 22px; font-weight: 700; color: var(--ink); }
.bar .t { height: 24px; background: var(--surface-2); border-radius: 6px; display: flex; align-items: center; }
.bar .f { height: 24px; border-radius: 6px; }
.bar .n { margin-left: 12px; font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 22px; color: var(--muted); white-space: nowrap; }
.foot { display: flex; justify-content: space-between; align-items: baseline; font-size: 22px; color: var(--muted); }
.foot .url { font-family: var(--font-mono); color: var(--ink-2); }
.wordmark { font-size: 150px; font-weight: 700; line-height: .95; letter-spacing: -.035em; color: var(--ink); margin: 0; }
.wordmark span { color: var(--accent); }
.tag { font-size: 40px; font-weight: 500; color: var(--ink); margin: 14px 0 0; letter-spacing: -.01em; }
.sub { font-size: 30px; color: var(--muted); margin: 8px 0 0; }
.row { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); margin: 26px 0 0; border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); }
.row div { padding: 14px 18px; border-right: 1px solid var(--border); display: flex; flex-direction: column; gap: 2px; }
.row div:last-child { border-right: 0; }
.row .n { font-size: 24px; color: var(--muted); }
.row .g { font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 56px; font-weight: 600; line-height: 1; color: var(--ink); }
.rowlabel { font-size: 22px; color: var(--muted); margin: 8px 0 0; }
"""


def page(body: str, title: str) -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f'<style>{brand.base_css(FONT_PREFIX)}\n{CARD_CSS}</style></head><body>{body}</body></html>')


def run_card(data: dict) -> str:
    r, a = data["run"], data["aggregate"]
    pb = a["per_bar"]
    gap = a["generosity_gap"]
    grader = ", ".join(sorted(data.get("grader_models", {}))) or "no grader"
    tiles = "".join(
        f'<div class="tile"><div class="k">{b.title()}</div><div class="v">{pct(pb[b]["hit_rate_all"])}</div>'
        f'<div class="s">{pb[b]["met"]} met · {pb[b]["not_met"]} not met · {pb[b]["unresolved"]} unresolved</div></div>'
        for b in config.BARS)
    tiles += (f'<div class="tile gap"><div class="k">Generosity gap</div><div class="v">{"n/a" if gap is None else f"{round(gap * 100)}<small> pts</small>"}</div>'
              f'<div class="s">lenient minus strict</div></div>')
    bars = "".join(
        f'<div class="bar"><div class="l">{b.title()}</div><div class="t">'
        f'<div class="f" style="width: {max(1.5, (pb[b]["hit_rate_all"] or 0) * 100):.1f}%; background: var(--bar-{b})"></div>'
        f'<div class="n">{pct(pb[b]["hit_rate_all"])} ({pb[b]["met"]} of {a["n_claims"]})</div></div></div>'
        for b in config.BARS)
    body = (f'<div class="card"><div><div class="chip">{esc(config.NAME)} v{config.VERSION} · {esc(r["subject"]["name"])} · {r["target_year"]} · graded {r["evidence_window"]["end"]} · {esc(grader)}</div>'
            f'<h1>{esc(r["subject"]["name"])}: {r["target_year"]} predictions, graded</h1>'
            f'<div class="tiles">{tiles}</div><div class="bars">{bars}</div></div>'
            f'<div class="foot"><span>Graded at three bars, receipts attached</span><span class="url">{SITE_HOST}</span></div></div>')
    return page(body, f"{r['subject']['name']} share card")


def index_card(datas: list[dict]) -> str:
    rows = sorted(datas, key=lambda d: d["aggregate"]["generosity_gap"] or 0)
    cells = "".join(f'<div><span class="n">{esc(d["run"]["subject"]["name"])}</span><span class="g">{"n/a" if d["aggregate"]["generosity_gap"] is None else round(d["aggregate"]["generosity_gap"] * 100)}</span></div>' for d in rows)
    body = (f'<div class="card"><div><h1 class="wordmark">Called It<span>!</span></h1>'
            f'<p class="tag">Did they actually call it?</p>'
            f'<p class="sub">Using AI Classifiers to Score a Person\'s Annual Predictions</p>'
            f'<div class="row">{cells}</div><div class="rowlabel">generosity gap, lenient minus strict, in points</div></div>'
            f'<div class="foot"><span class="url">{SITE_HOST}</span><span>open source · runs in Claude Code and Codex</span></div></div>')
    return page(body, "Called It! share card")


def render(src: pathlib.Path, out: pathlib.Path, width: int, height: int, scale: int = 1) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [render_png.chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
           f"--force-device-scale-factor={scale}", f"--window-size={width},{height}", f"--screenshot={out}", src.as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not out.exists():
        sys.exit(f"render failed (rc {r.returncode}): {r.stderr[-500:]}")
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size} bytes) at {width * scale}x{height * scale}")


def main(argv):
    runs = [pathlib.Path(p).resolve() for p in argv[1:]] or sorted(p for p in (ROOT / "runs").iterdir() if (p / "data.json").exists())
    cards, social, figures = ROOT / "article" / "cards", ROOT / "site" / "assets" / "social", ROOT / "article" / "figures"
    for d in (cards, social, figures, TMP):
        d.mkdir(parents=True, exist_ok=True)
    datas = []
    for d in runs:
        if not (d / "data.json").exists() or not (d / "grades.jsonl").exists():
            continue
        data = json.loads((d / "data.json").read_text())
        if not data.get("grades"):
            continue
        datas.append(data)
        src = TMP / f"{d.name}.html"
        src.write_text(run_card(data))
        render(src, social / f"{d.name}.png", W, H)
        shutil.copy(social / f"{d.name}.png", cards / f"{d.name}.png")
        if (d / "report.html").exists():
            render(d / "report.html", figures / f"scorecard-{d.name}.png", 1200, 640)
    if datas:
        src = TMP / "index.html"
        src.write_text(index_card(datas))
        render(src, social / "index.png", W, H)
        shutil.copy(social / "index.png", cards / "index.png")


if __name__ == "__main__":
    main(sys.argv)
