#!/usr/bin/env python3
"""called-it: grade a pundit's annual predictions at three bars, with receipts.

The model (Claude, Codex, or whichever agent hosts the skill) does the reading and judging and writes
JSONL. This script does everything that should be deterministic and replayable: fetching, caching,
asking Jev, scoring, rendering. Run from the repo root:

    python3 skills/called-it/scripts/called_it.py <command> <run> [options]

Commands, in pipeline order: init, fetch, text, add-text, add-captions, x-thread, x-search, markets,
screen, classify, check-rubrics, grade, report, replay, status.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from lib import config, fetch, jev, markets, schema, score, xapi  # noqa: E402
from lib import render  # noqa: E402

ROOT = Path.cwd()


def rdir(run: str) -> Path:
    d = config.run_dir(ROOT, run)
    if not (d / "run.json").exists():
        sys.exit(f"no run at {d}; create it with: called-it init {run} ...")
    return d


def load_run(d: Path) -> dict:
    run = json.loads((d / "run.json").read_text())
    schema.validate_run(run)
    return run


def grader_for(d: Path, run: dict, offline: bool = False) -> jev.Jev:
    cache = jev.Cache(d / "cache" / "jev")
    model = run["grader"].get("model", config.JEV_MODEL)
    return jev.Jev(cache, model=model, offline=offline)


# ---------------------------------------------------------------- init

def cmd_init(a):
    d = config.run_dir(ROOT, a.run)
    if (d / "run.json").exists() and not a.force:
        sys.exit(f"{d}/run.json exists; pass --force to overwrite")
    year = a.year
    run = {
        "name": a.run,
        "tool": {"name": config.NAME, "version": config.VERSION},
        "subject": {"name": a.subject, "kind": a.kind, "website": a.website,
                    "x_handles": [h.strip().lstrip("@") for h in (a.x_handles or "").split(",") if h.strip()],
                    "domains": [s.strip() for s in (a.domains or "").split(",") if s.strip()]},
        "target_year": year,
        "season_window": {"start": a.season_start or f"{year - 1}-10-01", "end": a.season_end or f"{year}-01-31"},
        "evidence_window": {"start": a.evidence_start or f"{year}-01-01", "end": a.evidence_end or config.today()},
        "canonical_urls": a.canonical or [],
        "top_n": a.top_n,
        "grader": {"provider": "jev" if config.has_jev() else "model", "model": config.JEV_MODEL},
        "thresholds": dict(config.THRESHOLDS),
        "created": config.today(),
        "notes": a.notes or "",
    }
    for sub in ("cache/pages", "cache/jev/answers", "cache/jev/pending", "cache/x", "cache/markets", "cache/media", "attachments"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n")
    for f in ("sources.jsonl", "claims.jsonl", "rubrics.jsonl", "evidence.jsonl"):
        p = d / f
        if not p.exists():
            p.write_text("")
    print(f"created {d}")
    print(f"grader: {run['grader']['provider']} ({'TYPESAFE_API_KEY found' if config.has_jev() else 'no TYPESAFE_API_KEY: the host model answers the questions'})")
    print(f"season {run['season_window']['start']}..{run['season_window']['end']}  evidence {run['evidence_window']['start']}..{run['evidence_window']['end']}")


# ---------------------------------------------------------------- sources

def cmd_fetch(a):
    d = rdir(a.run)
    rows = schema.read_jsonl(d / "sources.jsonl")
    schema.validate_sources(rows)
    pages = fetch.Pages(d / "cache" / "pages")
    unreadable = []
    for r in rows:
        if r["url"].startswith("youtube:"):
            vid = r["url"].split(":", 1)[1]
            rec = pages.path(r["url"])
            if rec.exists() and not a.refresh:
                continue
            vtt = fetch.youtube_captions(vid, d / "cache" / "media")
            if vtt:
                text = fetch.vtt_to_text(vtt.read_text())
                pages.put_text(r["url"], text, title=r.get("title", ""), note=f"captions from {vtt.name}")
                r["chars"] = len(text)
            else:
                unreadable.append((r["id"], r["url"], "no captions (yt-dlp missing or none published)"))
            continue
        rec = pages.get(r["url"], refresh=a.refresh)
        text = rec.get("text") or ""
        r["chars"] = len(text)
        r["text_sha256"] = rec.get("sha256")
        if rec.get("status") != 200 or len(text) < 400:
            r["access"] = "unreadable" if rec.get("status") != 200 else r.get("access", "free")
            unreadable.append((r["id"], r["url"], f"status {rec.get('status')} chars {len(text)}"))
    schema.write_jsonl(d / "sources.jsonl", rows)
    print(f"{len(rows)} sources, {len(rows) - len(unreadable)} readable")
    for sid, url, why in unreadable:
        print(f"  UNREADABLE {sid}: {url}  ({why})")
    if unreadable:
        print("Do not guess at unreadable sources. Ask the user to paste the text or log in, then: called-it add-text <run> <source_id> <file>")


def cmd_text(a):
    d = rdir(a.run)
    rows = {r["id"]: r for r in schema.read_jsonl(d / "sources.jsonl")}
    if a.source_id not in rows:
        sys.exit(f"unknown source {a.source_id}")
    rec = fetch.Pages(d / "cache" / "pages").get(rows[a.source_id]["url"])
    text = rec.get("text") or ""
    if a.max_chars:
        text = text[: a.max_chars]
    print(text)


def cmd_add_text(a):
    d = rdir(a.run)
    rows = {r["id"]: r for r in schema.read_jsonl(d / "sources.jsonl")}
    if a.source_id not in rows:
        sys.exit(f"unknown source {a.source_id}")
    text = Path(a.file).read_text()
    fetch.Pages(d / "cache" / "pages").put_text(rows[a.source_id]["url"], text, title=rows[a.source_id].get("title", ""),
                                                 note=a.note or "text supplied manually")
    print(f"stored {len(text)} chars for {a.source_id}")


def cmd_add_captions(a):
    d = rdir(a.run)
    rows = {r["id"]: r for r in schema.read_jsonl(d / "sources.jsonl")}
    if a.source_id not in rows:
        sys.exit(f"unknown source {a.source_id}")
    text = fetch.vtt_to_text(Path(a.vtt).read_text())
    fetch.Pages(d / "cache" / "pages").put_text(rows[a.source_id]["url"], text, title=rows[a.source_id].get("title", ""),
                                                 note=f"captions from {Path(a.vtt).name}")
    print(f"stored {len(text)} chars of captions for {a.source_id}")


def cmd_x_thread(a):
    d = rdir(a.run)
    posts = xapi.thread(a.root_id, a.username, d / "cache" / "x")
    text = "\n\n".join(f"[{p['created_at'][:10]}] {p['text']}" for p in posts)
    url = xapi.post_url(a.username, a.root_id)
    fetch.Pages(d / "cache" / "pages").put_text(url, text, title=posts[0]["text"][:80] if posts else "", note="X API thread hydration")
    print(f"{len(posts)} posts stored as text for {url}")
    print("Add a sources.jsonl row with that url (format: thread) if it is not there yet.")


def cmd_x_search(a):
    d = rdir(a.run)
    run = load_run(d)
    w = run["season_window"]
    n = xapi.count_window(a.username, w["start"], w["end"], a.terms)
    print(f"{n} posts match; estimated ${n * xapi.PRICE_PER_POST_USD:.2f} to read")
    if a.count_only:
        return
    if n > a.max_posts:
        sys.exit(f"over --max-posts {a.max_posts}; narrow the terms or raise the cap deliberately")
    posts = xapi.search_window(a.username, w["start"], w["end"], a.terms, d / "cache" / "x")
    for p in posts:
        print(f"{p['created_at'][:10]} {p['url']}\n    {p['text'][:200].replace(chr(10), ' ')}")


def cmd_markets(a):
    d = rdir(a.run)
    pm = markets.polymarket(a.query, d / "cache" / "markets")
    ks = markets.kalshi(a.query, d / "cache" / "markets")
    for r in pm.get("results", []) + ks.get("results", []):
        print(json.dumps(r, ensure_ascii=False))
    print(f"# polymarket {len(pm.get('results', []))}, kalshi {len(ks.get('results', []))}", file=sys.stderr)


# ---------------------------------------------------------------- claims

def _passages(text: str, min_chars: int = 60, max_chars: int = 700) -> list[str]:
    out = []
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if len(para) < min_chars:
            continue
        if len(para) <= max_chars:
            out.append(para)
            continue
        sents = re.split(r"(?<=[.!?])\s+", para)
        buf = ""
        for s in sents:
            if len(buf) + len(s) > max_chars and buf:
                out.append(buf.strip())
                buf = ""
            buf += " " + s
        if buf.strip():
            out.append(buf.strip())
    return out


def claim_questions() -> dict:
    return {
        "is_prediction": jev.noul(
            "Does `passage` make a forward-looking claim about what will happen or be true during `target_year` that could later be checked against public evidence?",
            true="It states or clearly implies an outcome, trend, number, event or ranking for the target year.",
            false="It describes the past or present, gives advice, asks a question, or is too vague to ever check.",
        ),
        "specificity": jev.score("How specific and checkable is the prediction in `passage`?", config.SPECIFICITY_LEVELS),
        "kind": jev.choice("Is the predicted outcome in `passage` binary or a matter of degree?", {
            "binary": "It either happens or it does not (a launch, an approval, a ranking, a named event).",
            "spectrum": "It can be partly right depending on magnitude, share, price, count or definition.",
        }),
        "boldness": jev.score("How bold is the prediction in `passage` relative to what most informed observers expected when it was made?", [
            "Consensus or near-certain at the time",
            "Plausible but contested",
            "Contrarian or surprising to most informed observers",
        ]),
    }


def cmd_screen(a):
    """Passage-level recall check: which passages look like predictions but are not covered by any claim."""
    d = rdir(a.run)
    run = load_run(d)
    sources = schema.read_jsonl(d / "sources.jsonl")
    claims = schema.read_jsonl(d / "claims.jsonl")
    pages = fetch.Pages(d / "cache" / "pages")
    g = grader_for(d, run, offline=a.offline)
    items, meta = [], []
    for s in sources:
        if s.get("access") == "unreadable":
            continue
        text = pages.get(s["url"]).get("text") or ""
        for p in _passages(text):
            state = {"subject": run["subject"]["name"], "target_year": run["target_year"], "published": s["date"], "passage": p}
            items.append((state, {"is_prediction": claim_questions()["is_prediction"]}))
            meta.append((s["id"], p))
    answers = g.ask_many(items)
    quotes = [c["quote"].lower()[:60] for c in claims]
    missed = []
    for (sid, p), ans in zip(meta, answers):
        if ans is None:
            continue
        pr = ans["is_prediction"]["noul"]
        covered = any(q and q in p.lower() for q in quotes)
        if pr >= a.min_p and not covered:
            missed.append({"source_id": sid, "is_prediction": pr, "passage": p})
    missed.sort(key=lambda m: -m["is_prediction"])
    schema.write_jsonl(d / "screen.jsonl", missed)
    pend = g.cache.pending_count()
    print(f"{len(items)} passages screened, {len(missed)} look like predictions not yet in claims.jsonl -> screen.jsonl")
    if pend:
        print(f"{pend} questions pending for the host model (cache/jev/pending). Answer them, then rerun.")


def cmd_classify(a):
    """Score every claim the model wrote, rank, and mark the top N as selected."""
    d = rdir(a.run)
    run = load_run(d)
    sources = schema.read_jsonl(d / "sources.jsonl")
    claims = schema.read_jsonl(d / "claims.jsonl")
    schema.validate_claims(claims, sources)
    g = grader_for(d, run, offline=a.offline)
    items = []
    for c in claims:
        state = {"subject": run["subject"]["name"], "target_year": run["target_year"], "published": c["date"],
                 "author": c.get("author"), "passage": c["quote"], "context": c.get("context", "")}
        items.append((state, claim_questions()))
    answers = g.ask_many(items)
    for c, ans in zip(claims, answers):
        if ans is None:
            continue
        c["scores"] = {
            "is_prediction": ans["is_prediction"]["noul"],
            "specificity": ans["specificity"]["score"],
            "specificity_conf": ans["specificity"]["confidence"],
            "boldness": ans["boldness"]["score"],
            "kind_p": ans["kind"]["probabilities"],
        }
        c.setdefault("kind", ans["kind"]["choice"])
        # Rank: must read as a prediction; then prefer specific and bold.
        c["rank_score"] = round(ans["is_prediction"]["noul"] * (1 + ans["specificity"]["score"] / 3) * (1 + ans["boldness"]["score"] / 2), 4)
    scored = [c for c in claims if "rank_score" in c]
    scored.sort(key=lambda c: -c["rank_score"])
    taken = 0
    for i, c in enumerate(scored, 1):
        c["rank"] = i
        guest = c.get("attribution") == "guest" and not a.include_guests
        if "pinned" in c:
            c["selected"] = bool(c["pinned"])
        elif guest:
            c["selected"] = False  # guests are graded only when pinned; the subject's own words fill the top N
        else:
            taken += 1
            c["selected"] = taken <= run["top_n"]
    schema.write_jsonl(d / "claims.jsonl", claims)
    pend = g.cache.pending_count()
    print(f"{len(scored)}/{len(claims)} claims scored; {sum(1 for c in claims if c.get('selected'))} selected (top_n={run['top_n']})")
    low = [c for c in scored if c["scores"]["is_prediction"] < 0.5]
    if low:
        print(f"{len(low)} claims the grader does not read as predictions (is_prediction < 0.5): " + ", ".join(c["id"] for c in low))
    if pend:
        print(f"{pend} questions pending for the host model (cache/jev/pending). Answer them, then rerun.")
    if g.calls:
        print(f"jev calls {g.calls}, input tokens {g.input_tokens}")


# ---------------------------------------------------------------- rubrics

def rubric_questions() -> dict:
    return {
        "critic_accepts": jev.noul(
            "Would a skeptical critic of the author agree that `criterion` is a fair test of `claim` at the stated `bar`?",
            true="The criterion tests what the claim actually asserted; it does not move the goalposts in the author's favour or against them beyond what the bar name implies.",
            false="The criterion tests something the claim did not assert, or is so loose that almost anything would satisfy it, or so tight that no reasonable reading of the claim could.",
        ),
        "checkable": jev.noul(
            "Can `criterion` be settled by public evidence available by the end of `target_year`?",
            true="A specific public fact, number, release, ranking or event would settle it.",
            false="It depends on private information, taste, or a judgement nobody can verify.",
        ),
    }


def cmd_check_rubrics(a):
    d = rdir(a.run)
    run = load_run(d)
    claims = {c["id"]: c for c in schema.read_jsonl(d / "claims.jsonl")}
    rubrics = schema.read_jsonl(d / "rubrics.jsonl")
    schema.validate_rubrics(rubrics, list(claims.values()))
    selected = {cid for cid, c in claims.items() if c.get("selected")}
    missing = selected - {r["claim_id"] for r in rubrics}
    if missing:
        print(f"WARNING {len(missing)} selected claims have no rubric: {sorted(missing)}")
    g = grader_for(d, run, offline=a.offline)
    items, meta = [], []
    for r in rubrics:
        c = claims[r["claim_id"]]
        for bar in config.BARS:
            state = {"claim": c["quote"], "author": c.get("author"), "target_year": run["target_year"], "bar": bar,
                     "bar_meaning": {"strict": "what a hostile critic would require before conceding",
                                     "standard": "what a fair reader would accept as 'this happened'",
                                     "lenient": "the weakest reading a critic would still concede counts"}[bar],
                     "criterion": r["bars"][bar]["criterion"]}
            items.append((state, rubric_questions()))
            meta.append((r, bar))
    answers = g.ask_many(items)
    flags = 0
    for (r, bar), ans in zip(meta, answers):
        if ans is None:
            continue
        chk = r["bars"][bar].setdefault("check", {})
        chk["critic_accepts"] = ans["critic_accepts"]["noul"]
        chk["checkable"] = ans["checkable"]["noul"]
        if chk["critic_accepts"] < 0.5 or chk["checkable"] < 0.5:
            flags += 1
            print(f"FLAG {r['claim_id']} {bar}: critic_accepts={chk['critic_accepts']:.2f} checkable={chk['checkable']:.2f}\n    {r['bars'][bar]['criterion']}")
    schema.write_jsonl(d / "rubrics.jsonl", rubrics)
    print(f"{len(rubrics)} rubrics x 3 bars checked, {flags} flagged for a human look")
    pend = g.cache.pending_count()
    if pend:
        print(f"{pend} questions pending for the host model (cache/jev/pending). Answer them, then rerun.")


def cmd_sheet(a):
    """Render the rubric review sheet: every selected claim with its three bars, measures and check scores."""
    d = rdir(a.run)
    run = load_run(d)
    claims = {c["id"]: c for c in schema.read_jsonl(d / "claims.jsonl")}
    rubrics = {r["claim_id"]: r for r in schema.read_jsonl(d / "rubrics.jsonl")}
    sources = {s["id"]: s for s in schema.read_jsonl(d / "sources.jsonl")}
    selected = sorted([c for c in claims.values() if c.get("selected")], key=lambda c: c.get("rank", 999))
    flagged = 0
    out = [f"# Rubric review sheet: {run['subject']['name']}, {run['target_year']}", "",
           f"{len(selected)} selected claims, three bars each. Written before any evidence was gathered. "
           "Edit `rubrics.jsonl`, then rerun `check-rubrics` and `sheet`. A flag means the critic check put the bar under even odds of being a fair reading, or doubted it is checkable; it is a prompt to look, not a verdict.", ""]
    for c in selected:
        r = rubrics.get(c["id"])
        s = sources.get(c["source_id"], {})
        tag = " (guest)" if c.get("attribution") == "guest" else ""
        out.append(f"## {c['id']}. {c.get('author', '')}{tag}: {render._short(c['quote'], 120)}")
        out.append("")
        out.append(f"> {c['quote']}")
        out.append("")
        out.append(f"{c.get('date', '')}, [{s.get('title', c['source_id'])}]({s.get('url', '')}). Rank {c.get('rank')}, {c.get('kind', '?')}, horizon {c.get('horizon', '')}. {c.get('context', '')}")
        out.append("")
        if not r:
            out.append("**No rubric yet.**")
            out.append("")
            continue
        out.append("| Bar | What counts | How we look | Critic | Checkable |")
        out.append("|---|---|---|---:|---:|")
        for bar in config.BARS:
            b = r["bars"][bar]
            chk = b.get("check", {})
            ca, ck = chk.get("critic_accepts"), chk.get("checkable")
            flag = " ⚑" if (ca is not None and ca < 0.5) or (ck is not None and ck < 0.5) else ""
            flagged += 1 if flag else 0
            out.append(f"| **{bar}**{flag} | {b['criterion']} | {b.get('measure', '')} | {'' if ca is None else f'{ca:.2f}'} | {'' if ck is None else f'{ck:.2f}'} |")
        if r.get("notes"):
            out.append("")
            out.append(f"Notes: {r['notes']}")
        out.append("")
    out.insert(3, f"Flags: {flagged} of {3 * len(selected)} bars.")
    out.insert(4, "")
    (d / "rubrics.md").write_text("\n".join(out))
    print(f"wrote {d / 'rubrics.md'}: {len(selected)} claims, {flagged} flagged bars")


# ---------------------------------------------------------------- grading

def cmd_grade(a):
    d = rdir(a.run)
    run = load_run(d)
    claims = {c["id"]: c for c in schema.read_jsonl(d / "claims.jsonl")}
    rubrics = schema.read_jsonl(d / "rubrics.jsonl")
    evidence = schema.read_jsonl(d / "evidence.jsonl")
    as_of = getattr(a, "as_of", None)
    out_dir = d
    if as_of:
        # A scorecard as of an earlier date: only evidence dated on or before it, written to a snapshot folder.
        evidence = [e for e in evidence if e["date"][:10] <= as_of]
        run = dict(run, evidence_window=dict(run["evidence_window"], end=as_of))
        out_dir = d / "snapshots" / as_of
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n")
    schema.validate_rubrics(rubrics, list(claims.values()))
    schema.validate_evidence(evidence, list(claims.values()))
    g = grader_for(d, run, offline=a.offline)
    items, meta, grades = [], [], []
    for r in rubrics:
        c = claims[r["claim_id"]]
        if not c.get("selected", True):
            continue
        for bar in config.BARS:
            ev = [e for e in evidence if e["claim_id"] == c["id"] and (not e.get("bars") or bar in e["bars"])]
            ev.sort(key=lambda e: (e["tier"], e["date"]))
            if not ev:
                grades.append({"claim_id": c["id"], "bar": bar, "verdict": "unresolved", "reason": "no evidence gathered",
                               "met_p": None, "contradicted_p": None, "strength": None, "evidence_ids": [],
                               "grader": {"provider": "none"}})
                continue
            state = score.grading_state(run, c, bar, r["bars"][bar]["criterion"], ev, r["bars"][bar].get("measure", ""))
            items.append((state, score.grading_questions()))
            meta.append((c, bar, ev, r["bars"][bar]))
    answers = g.ask_many(items)
    pending = 0
    window_end = run["evidence_window"]["end"]
    year_end = f"{run['target_year']}-12-31"
    for row in grades:  # pairs with no evidence, added above
        row["provisional"] = (claims[row["claim_id"]].get("horizon") or year_end) > window_end
    for (c, bar, ev, bar_def), ans in zip(meta, answers):
        crit = bar_def["criterion"]
        if ans is None:
            pending += 1
            grades.append({"claim_id": c["id"], "bar": bar, "verdict": "unresolved", "reason": "grader answer pending",
                           "met_p": None, "contradicted_p": None, "strength": None, "evidence_ids": [e["id"] for e in ev],
                           "grader": {"provider": "pending"}})
            continue
        met_p = ans["met"]["noul"]
        con_p = ans["contradicted"]["noul"]
        strength = ans["strength"]["score"]
        v, why = score.verdict(met_p, con_p, strength, run["thresholds"])
        h = jev.request_hash(g.model, score.grading_state(run, c, bar, crit, ev, bar_def.get("measure", "")), score.grading_questions())
        rec = g.cache.get(h) or {}
        grades.append({"claim_id": c["id"], "bar": bar, "verdict": v, "reason": why, "met_p": met_p, "contradicted_p": con_p,
                       "strength": strength, "strength_probs": ans["strength"]["probabilities"],
                       "strength_conf": ans["strength"]["confidence"], "evidence_ids": [e["id"] for e in ev],
                       "grader": {"provider": rec.get("grader", "jev"), "model": rec.get("answered_model")},
                       "question_hash": h, "provisional": (c.get("horizon") or year_end) > window_end})
    implied = score.monotone(grades)
    schema.write_jsonl(out_dir / "grades.jsonl", grades)
    scope = [c for c in claims.values() if c.get("selected", True) and any(r["claim_id"] == c["id"] for r in rubrics)]
    agg = score.aggregate(grades, scope)
    if as_of:
        models = jev.answered_models(jev.Cache(d / "cache" / "jev"))
        out = render.render(run, schema.read_jsonl(d / "sources.jsonl"), scope, rubrics, evidence, grades, agg, models, {"as_of": as_of})
        (out_dir / "report.md").write_text(out["markdown"])
        (out_dir / "report.html").write_text(out["html"])
        (out_dir / "data.json").write_text(json.dumps(out["data"], indent=1, ensure_ascii=False))
        print(f"snapshot as of {as_of}: {len(evidence)} evidence rows in window -> {out_dir}")
    print(f"{len(grades)} (claim, bar) pairs graded; pending {pending}; {implied} verdicts implied by a neighbouring bar")
    for bar, s in agg["per_bar"].items():
        print(f"  {bar:9s} met {s['met']:3d}  not_met {s['not_met']:3d}  unresolved {s['unresolved']:3d}  hit rate (all) {s['hit_rate_all']}")
    print(f"  generosity gap (lenient - strict): {agg['generosity_gap']}")
    if g.calls:
        print(f"jev calls {g.calls}, input tokens {g.input_tokens}")
    if pending:
        print(f"{pending} questions pending for the host model (cache/jev/pending). Answer them, then rerun grade.")


# ---------------------------------------------------------------- report

def cmd_report(a):
    d = rdir(a.run)
    run = load_run(d)
    sources = schema.read_jsonl(d / "sources.jsonl")
    claims = schema.read_jsonl(d / "claims.jsonl")
    rubrics = schema.read_jsonl(d / "rubrics.jsonl")
    evidence = schema.read_jsonl(d / "evidence.jsonl")
    grades = schema.read_jsonl(d / "grades.jsonl")
    schema.validate_grades(grades)
    graded_ids = {g["claim_id"] for g in grades}
    scope = [c for c in claims if c["id"] in graded_ids]
    agg = score.aggregate(grades, scope)
    models = jev.answered_models(jev.Cache(d / "cache" / "jev"))
    extras = {}
    ledger = d / "cache" / "x" / "xapi-ledger.jsonl"
    if ledger.exists():
        rows = schema.read_jsonl(ledger)
        extras["x_posts"] = sum(r["posts"] for r in rows)
        extras["x_spend"] = sum(r["est_usd"] for r in rows)
    extras["jev_tokens"] = sum(int((json.loads(p.read_text()).get("usage") or {}).get("input_tokens", 0))
                               for p in (d / "cache" / "jev" / "answers").glob("*.json"))
    import hashlib
    extras["input_sha256"] = {f: hashlib.sha256((d / f"{f}.jsonl").read_bytes()).hexdigest()
                              for f in ("sources", "claims", "rubrics", "evidence", "grades") if (d / f"{f}.jsonl").exists()}
    out = render.render(run, sources, scope, rubrics, evidence, grades, agg, models, extras)
    (d / "report.md").write_text(out["markdown"])
    (d / "report.html").write_text(out["html"])
    (d / "data.json").write_text(json.dumps(out["data"], indent=1, ensure_ascii=False))
    _export_csv(d, scope, grades, evidence)
    print(f"wrote {d / 'report.md'}, report.html, data.json, export/*.csv")
    print(render.badge(run, models))


def _export_csv(d: Path, claims, grades, evidence) -> None:
    import csv
    out = d / "export"
    out.mkdir(exist_ok=True)
    with (out / "claims.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "rank", "selected", "author", "attribution", "date", "kind", "domain", "horizon", "quote", "context", "source_id", "split_of"])
        for c in sorted(claims, key=lambda c: c.get("rank", 999)):
            w.writerow([c.get(k, "") for k in ("id", "rank", "selected", "author", "attribution", "date", "kind", "domain", "horizon", "quote", "context", "source_id", "split_of")])
    with (out / "grades.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["claim_id", "bar", "verdict", "provisional", "met_p", "contradicted_p", "strength", "reason", "evidence_ids", "grader_model"])
        for g in grades:
            w.writerow([g["claim_id"], g["bar"], g["verdict"], g.get("provisional", ""), g.get("met_p", ""), g.get("contradicted_p", ""),
                        g.get("strength", ""), g.get("reason", ""), " ".join(g.get("evidence_ids", [])), (g.get("grader") or {}).get("model", "")])
    with (out / "evidence.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "claim_id", "bars", "tier", "direction", "date", "source", "url", "quote", "found_by"])
        for e in evidence:
            w.writerow([e["id"], e["claim_id"], " ".join(e.get("bars", [])), e["tier"], e["direction"], e["date"], e["source"], e["url"], e["quote"], e.get("found_by", "")])


def cmd_archive(a):
    """Fetch the Wayback Machine snapshot closest to the source's publication date and compare it with the live text."""
    import difflib
    d = rdir(a.run)
    rows = schema.read_jsonl(d / "sources.jsonl")
    by_id = {r["id"]: r for r in rows}
    if a.source_id not in by_id:
        sys.exit(f"unknown source {a.source_id}")
    r = by_id[a.source_id]
    pages = fetch.Pages(d / "cache" / "pages")
    snap = fetch.wayback_closest(r["url"], (a.at or r["date"]).replace("-", ""))
    if not snap:
        print("no snapshot found")
        return
    rec = pages.get(snap["url"], refresh=a.refresh)
    live = pages.get(r["url"]).get("text") or ""
    arch = rec.get("text") or ""
    ratio = difflib.SequenceMatcher(None, live, arch).ratio() if live and arch else 0.0
    r["archive"] = {"url": snap["url"], "timestamp": snap["timestamp"], "similarity": round(ratio, 4), "chars": len(arch)}
    schema.write_jsonl(d / "sources.jsonl", rows)
    print(f"snapshot {snap['timestamp']} ({len(arch)} chars) vs live ({len(live)} chars): similarity {ratio:.3f}")
    if a.diff:
        for line in difflib.unified_diff(arch.splitlines(), live.splitlines(), "archived", "live", lineterm="", n=0):
            if line.startswith(("+", "-")) and len(line) > 3 and not line.startswith(("+++", "---")):
                print(line[:220])
    print("To grade the words as published, add a source row whose url is the snapshot url and point claims at it.")


def cmd_drift(a):
    """Re-ask a sample of cached grading questions live and report how far the answers moved."""
    import random
    d = rdir(a.run)
    run = load_run(d)
    g = grader_for(d, run)
    recs = []
    for p in sorted((d / "cache" / "jev" / "answers").glob("*.json")):
        rec = json.loads(p.read_text())
        if rec.get("grader") == "jev" and "met" in rec.get("answers", {}):
            recs.append(rec)
    if not recs:
        sys.exit("no cached grading answers to compare")
    random.Random(a.seed).shuffle(recs)
    sample = recs[: a.n]
    diffs, rows = [], []
    for rec in sample:
        fresh = g.ask_fresh(rec["state"], rec["questions"])
        for q, old in rec["answers"].items():
            new = fresh[q]
            if old["type"] == "noul":
                dlt = abs(new["noul"] - old["noul"])
            elif old["type"] == "score":
                dlt = abs(new["score"] - old["score"]) / max(len(old["legend"]) - 1, 1)
            else:
                dlt = 1.0 - new["probabilities"].get(old["choice"], 0.0)
            diffs.append(dlt)
            rows.append((rec["state"]["claim"]["quote"][:50], rec["state"]["bar"], q, old.get("noul", old.get("score")), new.get("noul", new.get("score")), dlt))
    diffs_pts = [round(x * 100, 1) for x in diffs]
    print(f"{len(sample)} grading requests re-asked live ({g.model}), {len(diffs)} answers compared")
    print(f"mean drift {sum(diffs_pts) / len(diffs_pts):.1f} points, max {max(diffs_pts):.1f}, within 5 points: {sum(1 for x in diffs_pts if x <= 5) / len(diffs_pts):.0%}")
    verdict_flips = 0
    th = run["thresholds"]
    for quote, bar, q, old, new, dlt in rows:
        if q in ("met", "contradicted") and old is not None and new is not None:
            if (old >= th["yes"]) != (new >= th["yes"]):
                verdict_flips += 1
                print(f"  threshold crossed: {quote!r} {bar} {q}: {old:.2f} -> {new:.2f}")
    print(f"answers crossing the {th['yes']} threshold: {verdict_flips}")
    (d / "drift.json").write_text(json.dumps({"model": g.model, "requests": len(sample), "answers": len(diffs), "mean_pts": round(sum(diffs_pts) / len(diffs_pts), 2),
                                             "max_pts": max(diffs_pts), "within_5": round(sum(1 for x in diffs_pts if x <= 5) / len(diffs_pts), 3),
                                             "threshold_crossings": verdict_flips, "rows": [list(r) for r in rows]}, indent=1))


def workbook_sheets(run: dict, sources, claims, rubrics, evidence, grades, agg) -> list[dict]:
    """The sheets of a run workbook; shared with tools/build_workbook.py for the combined file."""
    rub = {r["claim_id"]: r for r in rubrics}
    g = {(x["claim_id"], x["bar"]): x for x in grades}
    name = run["subject"]["name"]
    sheets = []
    sheets.append({"name": "Summary", "headers": ["metric", "value"], "widths": [34, 60], "rows": [
        ["subject", name], ["run", run["name"]], ["target year", run["target_year"]],
        ["season window", f"{run['season_window']['start']} to {run['season_window']['end']}"],
        ["evidence window", f"{run['evidence_window']['start']} to {run['evidence_window']['end']}"],
        ["claims graded", agg["n_claims"]],
        ["strict: met / not met / unresolved", f"{agg['per_bar']['strict']['met']} / {agg['per_bar']['strict']['not_met']} / {agg['per_bar']['strict']['unresolved']}"],
        ["standard: met / not met / unresolved", f"{agg['per_bar']['standard']['met']} / {agg['per_bar']['standard']['not_met']} / {agg['per_bar']['standard']['unresolved']}"],
        ["lenient: met / not met / unresolved", f"{agg['per_bar']['lenient']['met']} / {agg['per_bar']['lenient']['not_met']} / {agg['per_bar']['lenient']['unresolved']}"],
        ["hit rate strict (all claims)", agg["per_bar"]["strict"]["hit_rate_all"]],
        ["hit rate standard (all claims)", agg["per_bar"]["standard"]["hit_rate_all"]],
        ["hit rate lenient (all claims)", agg["per_bar"]["lenient"]["hit_rate_all"]],
        ["generosity gap (lenient minus strict)", agg["generosity_gap"]],
        ["thresholds", json.dumps(run["thresholds"])],
        ["grader model", run["grader"].get("model", "")],
        ["tool", f"{config.NAME} {config.VERSION}"],
    ]})
    sheets.append({"name": "Sources", "headers": ["subject", "id", "role", "format", "access", "date", "author", "title", "url", "chars", "note"],
                   "widths": [16, 6, 11, 11, 10, 12, 28, 48, 60, 8, 60], "wrap": [7, 10],
                   "rows": [[name, s["id"], s.get("role", ""), s["format"], s["access"], s["date"], s.get("author", ""), s["title"], s["url"], s.get("chars", ""), s.get("note", "")] for s in sources]})
    crow = []
    for c in sorted(claims, key=lambda c: c.get("rank", 999)):
        sc = c.get("scores", {})
        ladder = agg["ladder"].get(c["id"], "")
        crow.append([name, c["id"], c.get("rank", ""), bool(c.get("selected")), c.get("attribution", ""), c.get("author", ""), c.get("date", ""), c.get("kind", ""),
                     c.get("domain", ""), c.get("horizon", ""), c["quote"], c.get("context", ""), c.get("source_id", ""), c.get("split_of", ""),
                     sc.get("is_prediction", ""), sc.get("specificity", ""), sc.get("boldness", ""),
                     g.get((c["id"], "strict"), {}).get("verdict", ""), g.get((c["id"], "standard"), {}).get("verdict", ""), g.get((c["id"], "lenient"), {}).get("verdict", ""),
                     ladder, bool(g.get((c["id"], "strict"), {}).get("provisional", False))])
    sheets.append({"name": "Claims", "headers": ["subject", "id", "rank", "selected", "attribution", "author", "date", "kind", "domain", "horizon", "quote", "context", "source_id", "split_of",
                                                 "p_is_prediction", "specificity_0to3", "boldness_0to2", "strict", "standard", "lenient", "ladder", "provisional"],
                   "widths": [16, 6, 6, 9, 11, 18, 12, 9, 14, 12, 70, 60, 9, 9, 12, 12, 12, 11, 11, 11, 14, 11], "wrap": [10, 11], "rows": crow})
    rrow = []
    for c in sorted(claims, key=lambda c: c.get("rank", 999)):
        r = rub.get(c["id"])
        if not r:
            continue
        for bar in config.BARS:
            b = r["bars"][bar]
            chk = b.get("check", {})
            gr = g.get((c["id"], bar), {})
            rrow.append([name, c["id"], bar, b["criterion"], b.get("measure", ""), chk.get("critic_accepts", ""), chk.get("checkable", ""),
                         gr.get("verdict", ""), gr.get("met_p", ""), gr.get("contradicted_p", ""), gr.get("strength", ""), gr.get("reason", ""), gr.get("implied_from", ""), r.get("notes", "")])
    sheets.append({"name": "Rubrics+Grades", "headers": ["subject", "claim_id", "bar", "criterion", "measure", "critic_accepts", "checkable", "verdict", "p_met", "p_contradicted", "strength_0to2", "reason", "implied_from", "notes"],
                   "widths": [16, 8, 9, 70, 60, 10, 10, 11, 8, 10, 10, 36, 11, 50], "wrap": [3, 4, 11, 13], "rows": rrow})
    sheets.append({"name": "Evidence", "headers": ["subject", "id", "claim_id", "bars", "tier", "direction", "date", "source", "url", "quote", "found_by"],
                   "widths": [16, 6, 8, 22, 5, 11, 12, 30, 60, 90, 11], "wrap": [9],
                   "rows": [[name, e["id"], e["claim_id"], " ".join(e.get("bars", [])), e["tier"], e["direction"], e["date"], e["source"], e["url"], e["quote"], e.get("found_by", "")] for e in evidence]})
    return sheets


def cmd_xlsx(a):
    from lib import xlsx
    d = rdir(a.run)
    run = load_run(d)
    sources = schema.read_jsonl(d / "sources.jsonl")
    claims = schema.read_jsonl(d / "claims.jsonl")
    rubrics = schema.read_jsonl(d / "rubrics.jsonl")
    evidence = schema.read_jsonl(d / "evidence.jsonl")
    grades = schema.read_jsonl(d / "grades.jsonl")
    graded_ids = {g["claim_id"] for g in grades}
    scope = [c for c in claims if c["id"] in graded_ids] or claims
    agg = score.aggregate(grades, scope)
    out = d / "export" / f"{run['name']}.xlsx"
    out.parent.mkdir(exist_ok=True)
    xlsx.write_xlsx(out, workbook_sheets(run, sources, claims, rubrics, evidence, grades, agg), title=f"{run['subject']['name']} {run['target_year']} predictions, graded by called-it")
    print(f"wrote {out}")


def cmd_post(a):
    """Draft the self-review the subject could publish: a thread of one line per claim with the receipts linked."""
    d = rdir(a.run)
    run = load_run(d)
    data_path = d / "data.json"
    if not data_path.exists():
        sys.exit("run `report` first")
    data = json.loads(data_path.read_text())
    agg = data["aggregate"]
    pb = agg["per_bar"]
    by_bar = {(g["claim_id"], g["bar"]): g for g in data["grades"]}
    claims = sorted(data["claims"], key=lambda c: c.get("rank", 999))
    bar = a.bar
    name = run["subject"]["name"]
    link = a.link or f"runs/{run['name']}/report.html"
    word = {"met": "called it", "not_met": "missed", "unresolved": "too soon to say"}
    glyph = render.GLYPH
    lines = [f"# Draft self-review for {name} (bar: {bar})", "",
             "A thread the subject could post. One line per claim, graded at the chosen bar, with the receipts linked. Edit freely; the numbers come from the run.", "",
             "---", "",
             f"My {run['target_year']} predictions break into {agg['n_claims']} checkable claims. Here is how they scored as of {run['evidence_window']['end']}, graded at three bars by called-it with every receipt attached: "
             f"{render._pct(pb['strict']['hit_rate_all'])} strict, {render._pct(pb['standard']['hit_rate_all'])} standard, {render._pct(pb['lenient']['hit_rate_all'])} lenient. "
             f"{pb[bar]['unresolved']} still open. Thread:", ""]
    n = 1
    for c in claims:
        g = by_bar.get((c["id"], bar))
        if not g:
            continue
        v = g["verdict"]
        prov = " (provisional)" if g.get("provisional") else ""
        lines.append(f"{n}/ {glyph[v]} {word[v]}{prov}: \"{render._short(c['quote'], 160)}\"")
        n += 1
    lines += ["", f"{n}/ Every grade, bar and evidence row is here: {link}. If you think a bar is unfair, say which one; the run is replayable and I will regrade.", ""]
    (d / "post.md").write_text("\n".join(lines))
    print(f"wrote {d / 'post.md'} ({n} posts)")


def cmd_share(a):
    """Draft the quote-post for sharing a scorecard: the text, the original post to quote, the card and the page link.

    The sharing game: find the author's original prediction post, quote it with the 1200x630 card and
    one line of numbers, link the scorecard page. share.json is what the site's Share button reads;
    share.md is the human copy with both text lengths."""
    import urllib.parse
    d = rdir(a.run)
    run = load_run(d)
    data_path = d / "data.json"
    if not data_path.exists():
        sys.exit("run `report` first")
    data = json.loads(data_path.read_text())
    agg = data["aggregate"]
    pb = agg["per_bar"]
    name = run["subject"]["name"]
    handles = run["subject"].get("x_handles") or []
    handle = handles[0] if handles else None
    quote_url = next((u for u in run.get("canonical_urls", []) if "x.com/" in u or "twitter.com/" in u), None)
    base = a.base_url.rstrip("/") + "/"
    page_url = f"{base}{run['name']}/"
    s, m, l = (render._pct(pb[b]["hit_rate_all"]) for b in ("strict", "standard", "lenient"))
    gap = round(agg["generosity_gap"] * 100)
    n = agg["n_claims"]
    still_open = pb["strict"]["unresolved"]
    who = f"@{handle}" if handle else name
    year = run["target_year"]
    text_short = (f"Scored {who}'s {year} predictions at three bars: {s} strict, {m} standard, {l} lenient. "
                  f"Generosity gap: {gap} points. {n} claims, receipts attached.")
    text_long = (f"{text_short} {still_open} still open at the strict bar as of {run['evidence_window']['end']}. "
                 f"Every bar was written before the evidence was gathered, and the run replays offline. "
                 f"Argue with a bar, not the number.")
    intent_url = "https://x.com/intent/post?" + urllib.parse.urlencode({"text": text_short, "url": page_url})
    share = {
        "subject": name, "handle": handle, "quote_url": quote_url, "page_url": page_url,
        "card": f"cards/{run['name']}.png", "text_short": text_short, "text_long": text_long,
        "intent_url": intent_url,
    }
    (d / "share.json").write_text(json.dumps(share, indent=2) + "\n")
    quote_line = f"Quote this post: {quote_url}" if quote_url else f"No X post among the canonical sources; link the page and name {name} instead."
    md = [f"# Share the {name} scorecard", "",
          "The game: find the author's original prediction post, quote it with the card and one line of numbers, link the page.", "",
          f"1. {quote_line}",
          f"2. Attach the card: `article/cards/{run['name']}.png` (1200x630, the same image the page shows in link previews).",
          f"3. Link the page: {page_url}", "",
          "## Short (fits one post)", "", "```", text_short, "```", "",
          "## Longer", "", "```", text_long, "```", "",
          f"One-click: {intent_url}", ""]
    (d / "share.md").write_text("\n".join(md))
    print(f"wrote {d / 'share.json'} and {d / 'share.md'} ({len(text_short)} chars short)")


def cmd_replay(a):
    a.offline = True
    cmd_grade(a)
    cmd_report(a)


def cmd_status(a):
    d = rdir(a.run)
    run = load_run(d)
    cache = jev.Cache(d / "cache" / "jev")
    print(f"run {run['name']}: {run['subject']['name']} ({run['subject']['kind']}), target {run['target_year']}")
    for f in ("sources", "claims", "rubrics", "evidence", "grades"):
        rows = schema.read_jsonl(d / f"{f}.jsonl")
        extra = ""
        if f == "claims":
            extra = f", {sum(1 for r in rows if r.get('selected'))} selected"
        if f == "sources":
            extra = f", {sum(1 for r in rows if r.get('access') == 'unreadable')} unreadable"
        print(f"  {f:9s} {len(rows):4d}{extra}")
    print(f"  jev answers cached {len(list(cache.answers.glob('*.json')))}, pending {cache.pending_count()}, models {jev.answered_models(cache)}")
    ledger = d / "cache" / "x" / "xapi-ledger.jsonl"
    if ledger.exists():
        rows = schema.read_jsonl(ledger)
        print(f"  x api posts read {sum(r['posts'] for r in rows)} (est ${sum(r['est_usd'] for r in rows):.2f})")


# ---------------------------------------------------------------- main

def main(argv=None):
    p = argparse.ArgumentParser(prog=config.NAME, description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=f"{config.NAME} {config.VERSION}")
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("init", help="create a run folder");  s.set_defaults(fn=cmd_init)
    s.add_argument("run"); s.add_argument("--subject", required=True); s.add_argument("--kind", choices=["person", "company", "publication"], default="person")
    s.add_argument("--website"); s.add_argument("--year", type=int, required=True); s.add_argument("--canonical", nargs="*")
    s.add_argument("--x-handles"); s.add_argument("--domains"); s.add_argument("--top-n", type=int, default=20)
    s.add_argument("--season-start"); s.add_argument("--season-end"); s.add_argument("--evidence-start"); s.add_argument("--evidence-end")
    s.add_argument("--notes"); s.add_argument("--force", action="store_true")

    s = sp.add_parser("fetch", help="fetch every source into the cache");  s.set_defaults(fn=cmd_fetch)
    s.add_argument("run"); s.add_argument("--refresh", action="store_true")

    s = sp.add_parser("text", help="print a source's extracted text");  s.set_defaults(fn=cmd_text)
    s.add_argument("run"); s.add_argument("source_id"); s.add_argument("--max-chars", type=int, default=0)

    s = sp.add_parser("add-text", help="store text obtained manually for a source");  s.set_defaults(fn=cmd_add_text)
    s.add_argument("run"); s.add_argument("source_id"); s.add_argument("file"); s.add_argument("--note")

    s = sp.add_parser("add-captions", help="store a .vtt caption file as a source's text");  s.set_defaults(fn=cmd_add_captions)
    s.add_argument("run"); s.add_argument("source_id"); s.add_argument("vtt")

    s = sp.add_parser("archive", help="fetch the Wayback snapshot nearest the source date and compare with the live page");  s.set_defaults(fn=cmd_archive)
    s.add_argument("run"); s.add_argument("source_id"); s.add_argument("--at", help="YYYY-MM-DD (default: the source date)")
    s.add_argument("--diff", action="store_true"); s.add_argument("--refresh", action="store_true")

    s = sp.add_parser("x-thread", help="hydrate an X thread via the API (needs X_BEARER_TOKEN)");  s.set_defaults(fn=cmd_x_thread)
    s.add_argument("run"); s.add_argument("root_id"); s.add_argument("username")

    s = sp.add_parser("x-search", help="search one account inside the season window");  s.set_defaults(fn=cmd_x_search)
    s.add_argument("run"); s.add_argument("username"); s.add_argument("--terms", default="predict OR predictions OR prediction")
    s.add_argument("--count-only", action="store_true"); s.add_argument("--max-posts", type=int, default=300)

    s = sp.add_parser("markets", help="search Polymarket and Kalshi for a question");  s.set_defaults(fn=cmd_markets)
    s.add_argument("run"); s.add_argument("query")

    s = sp.add_parser("screen", help="find prediction-like passages not yet in claims.jsonl");  s.set_defaults(fn=cmd_screen)
    s.add_argument("run"); s.add_argument("--min-p", type=float, default=0.6); s.add_argument("--offline", action="store_true")

    s = sp.add_parser("classify", help="score and rank claims.jsonl, select the top N");  s.set_defaults(fn=cmd_classify)
    s.add_argument("run"); s.add_argument("--offline", action="store_true")
    s.add_argument("--include-guests", action="store_true", help="let guest claims compete for the top N (default: only pinned guests are graded)")

    s = sp.add_parser("check-rubrics", help="ask the grader whether each bar is fair and checkable");  s.set_defaults(fn=cmd_check_rubrics)
    s.add_argument("run"); s.add_argument("--offline", action="store_true")

    s = sp.add_parser("sheet", help="write rubrics.md, the human review sheet of claims and bars");  s.set_defaults(fn=cmd_sheet)
    s.add_argument("run")

    s = sp.add_parser("grade", help="grade every (claim, bar) on the evidence");  s.set_defaults(fn=cmd_grade)
    s.add_argument("run"); s.add_argument("--offline", action="store_true")
    s.add_argument("--as-of", dest="as_of", help="YYYY-MM-DD: grade on evidence dated up to this day and write a snapshot under snapshots/<date>/")

    s = sp.add_parser("report", help="render report.md, report.html and data.json");  s.set_defaults(fn=cmd_report)
    s.add_argument("run")

    s = sp.add_parser("xlsx", help="write export/<run>.xlsx with sources, claims, rubrics, grades and evidence");  s.set_defaults(fn=cmd_xlsx)
    s.add_argument("run")

    s = sp.add_parser("post", help="draft the self-review thread the subject could publish, from data.json");  s.set_defaults(fn=cmd_post)
    s.add_argument("run"); s.add_argument("--bar", choices=list(config.BARS), default="standard"); s.add_argument("--link")

    s = sp.add_parser("share", help="draft the quote-post for sharing the scorecard: text, the original post to quote, the card and the page link");  s.set_defaults(fn=cmd_share)
    s.add_argument("run"); s.add_argument("--base-url", dest="base_url", default="https://rickmanelius.github.io/called-it/", help="where the gallery is served (placeholder until GitHub Pages exists)")

    s = sp.add_parser("drift", help="re-ask a sample of cached grading questions live and measure the drift");  s.set_defaults(fn=cmd_drift)
    s.add_argument("run"); s.add_argument("--n", type=int, default=20); s.add_argument("--seed", type=int, default=1)

    s = sp.add_parser("replay", help="grade from cache only and re-render (no network, no key)");  s.set_defaults(fn=cmd_replay)
    s.add_argument("run")

    s = sp.add_parser("status", help="what the run holds");  s.set_defaults(fn=cmd_status)
    s.add_argument("run")

    a = p.parse_args(argv)
    try:
        a.fn(a)
    except schema.SchemaError as e:
        sys.exit(f"schema error: {e}")
    except (jev.JevError, xapi.XError) as e:
        sys.exit(f"api error: {e}")


if __name__ == "__main__":
    main()
