#!/usr/bin/env python3
"""Build the board deck from the runs and the article: HTML slides, one PNG per slide, a PPTX (one full-bleed
image per slide, the text in the speaker notes, so no fonts are needed on the recipient's machine) and a PDF.

    python3 tools/build_deck.py            # slides.html + notes.json + png/
    <venv python> tools/build_deck.py --pptx   # also deck.pptx (needs python-pptx in that interpreter)

Slides are 1600x900. slides.html shows every slide stacked; slides.html?only=N shows slide N alone, which is
what the renderer uses (hash navigation does not render reliably in headless Chrome).
"""
from __future__ import annotations

import html
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "article" / "deck"
FIG = ROOT / "article" / "figures"
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))
from lib import brand  # noqa: E402

FONT_PREFIX = "../../site/assets/fonts/"  # from article/deck/ to the self-hosted fonts

DECK_CSS = """
html,body { background:#000; font-size:22px; line-height:1.4 }
.slide { width:1600px; height:900px; background:var(--page); color:var(--ink); padding:72px 88px; position:relative; overflow:hidden; margin:0 auto 24px; display:flex; flex-direction:column }
body.only { background:var(--page) } body.only .slide { margin:0 } body.only .slide.hidden { display:none }
.kicker { color:var(--muted); font-family:var(--font-mono); font-size:18px; text-transform:uppercase; letter-spacing:.08em; margin-bottom:14px }
h1 { font-size:88px; font-weight:700; line-height:1.0; letter-spacing:-.03em; margin:0 0 18px; white-space:nowrap } h1 .bang { color:var(--accent) }
h2 { font-size:48px; font-weight:700; line-height:1.08; letter-spacing:-.02em; margin:0 0 22px; white-space:nowrap }
.sub { font-size:28px; color:var(--ink-2); max-width:1200px }
.body { font-size:26px; color:var(--ink); max-width:1300px } .body li { margin:10px 0 }
.tiles { display:grid; grid-template-columns:repeat(4,1fr); gap:20px; margin:30px 0 }
.tile { background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:22px 26px }
.tile .k { color:var(--muted); font-size:16px; font-weight:700; text-transform:uppercase; letter-spacing:.08em } .tile .v { font-family:var(--font-mono); font-variant-numeric:tabular-nums; font-size:60px; font-weight:600; line-height:1.1 } .tile .s { color:var(--muted); font-size:16px }
.tile.gap { background:var(--accent); border-color:var(--accent); color:var(--on-accent) } .tile.gap .k, .tile.gap .s { color:var(--on-accent-small) }
.cols { display:grid; grid-template-columns:1fr 1fr; gap:40px; align-items:start }
.fig { flex:1; display:flex; align-items:center; justify-content:center; min-height:0 } .fig img { max-width:100%; max-height:100%; border:1px solid var(--border); border-radius:12px; background:var(--page) }
.foot { position:absolute; left:88px; right:88px; bottom:36px; display:flex; justify-content:space-between; color:var(--muted); font-size:16px; font-family:var(--font-mono) }
.bars { display:grid; grid-template-columns:150px 1fr; gap:14px 20px; align-items:center; font-size:24px; margin-top:20px }
.bars .bar { height:34px; border-radius:4px } .bars .lbl { font-weight:700 } .bars .ann { color:var(--ink-2); font-size:20px }
.card { background:var(--surface); border:1px solid var(--border); border-radius:16px; padding:22px 26px; font-size:22px } .card h3 { margin:0 0 6px; font-size:28px; font-weight:700 } .card .k { color:var(--muted); font-size:15px; font-weight:700; text-transform:uppercase; letter-spacing:.08em }
.card strong, .body strong { color:var(--accent) }
.grid3 { display:grid; grid-template-columns:repeat(3,1fr); gap:22px }
code { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:2px 8px; font-size:22px }
@media print { @page { size:1600px 900px; margin:0 } html,body { background:var(--page) } .slide { margin:0; page-break-after:always; break-after:page } }
"""
CSS = brand.base_css(FONT_PREFIX) + "\n" + DECK_CSS

SCRIPT = """
<script>
var only = new URLSearchParams(location.search).get('only');
if (only) { document.body.classList.add('only'); document.querySelectorAll('.slide').forEach(function(s, i){ if (String(i + 1) !== only) s.classList.add('hidden'); }); }
</script>
"""


def esc(s):
    return html.escape(str(s if s is not None else ""))


def pct(x):
    return "n/a" if x is None else f"{round(x * 100)}%"


def load_runs():
    out = []
    for d in sorted(p for p in (ROOT / "runs").iterdir() if (p / "data.json").exists()):
        data = json.loads((d / "data.json").read_text())
        if data.get("grades"):
            out.append((d.name, data))
    return out


def scorecard_slide(name, data, bullets):
    a = data["aggregate"]
    pb = a["per_bar"]
    r = data["run"]
    gap = a["generosity_gap"]
    tiles = "".join(f'<div class="tile"><div class="k">{b.title()}</div><div class="v">{pct(pb[b]["hit_rate_all"])}</div><div class="s">{pb[b]["met"]} met · {pb[b]["not_met"]} not met · {pb[b]["unresolved"]} open</div></div>' for b in ("strict", "standard", "lenient"))
    tiles += f'<div class="tile gap"><div class="k">Generosity gap</div><div class="v">{"n/a" if gap is None else f"{round(gap * 100)} pts"}</div><div class="s">lenient minus strict</div></div>'
    body = "".join(f"<li>{esc(b)}</li>" for b in bullets)
    return (f'<div class="kicker">Scorecard · {esc(r["subject"]["kind"])} · as of {r["evidence_window"]["end"]}</div><h2>{esc(name)}: {a["n_claims"]} claims, three bars</h2>'
            f'<div class="tiles">{tiles}</div><ul class="body">{body}</ul>')


def build_slides(runs):
    by = {n: d for n, d in runs}
    slides = []  # (html, notes)

    slides.append((f'<div class="kicker">called-it · October 24, 2026</div><h1>Called It<span class="bang">!</span></h1>'
                   f'<p class="sub"><strong>Using AI Classifiers to Score Annual Predictions.</strong> We graded {len(runs)} sets of 2026 predictions at three bars each, with every receipt attached, before the 2027 prediction season opens. The tool is open source and runs on anyone.</p>'
                   f'<div class="foot"><span>Every · Mike Ippolito · Bob Doll{" · Scott Galloway" if "galloway" in by else ""}</span><span>github.com/rickmanelius/called-it</span></div>',
                   "Title. Three or four public prediction lists for 2026, graded at three bars by a calibrated classifier over committed evidence. Everything in this deck traces to a run folder anyone can replay."))

    slides.append(('<div class="kicker">The ritual and its missing half</div><h2>Everyone predicts. Almost nobody grades.</h2>'
                   '<div class="cols"><div class="body"><p>Every November to January, people who think for a living write down what next year will bring. Then the year happens and the lists are forgotten.</p>'
                   '<p>The few who grade themselves grade generously, because the bar was never written down.</p></div>'
                   '<div class="card"><div class="k">One list, two honest grades</div><h3>Mike Ippolito, 2025 predictions</h3><p>Graded by himself: <strong>21 of 27 (78%)</strong></p><p>Graded by a trade publication: <strong>48%</strong></p><p class="ann">Neither grader wrote down the bar.</p></div></div>',
                   "The problem is not dishonesty. It is that grading your own work at an unwritten bar produces a generous number every time. Ippolito's 78 versus 48 for the same list is the gap this project measures."))

    slides.append(('<div class="kicker">The idea</div><h2>Three bars, written before any evidence</h2>'
                   f'<div class="bars"><div class="lbl">Strict</div><div><div class="bar" style="width:28%;background:{brand.BAR_COLORS["strict"]}"></div><div class="ann">what a hostile critic would require: the literal claim, numbers and dates intact</div></div>'
                   f'<div class="lbl">Standard</div><div><div class="bar" style="width:46%;background:{brand.BAR_COLORS["standard"]}"></div><div class="ann">what a fair reader would accept as "this happened"</div></div>'
                   f'<div class="lbl">Lenient</div><div><div class="bar" style="width:64%;background:{brand.BAR_COLORS["lenient"]}"></div><div class="ann">the weakest reading a critic would still concede counts</div></div></div>'
                   '<ul class="body" style="margin-top:36px"><li>Lenient is lenient about the claim, never about the evidence. Social chatter meets no bar.</li><li>An author admitting a miss is strong evidence. A victory lap is weak.</li><li>The gap between lenient and strict is the number: how much the grade depends on who is grading.</li></ul>',
                   "Every argument about whether a prediction came true is an argument about the bar. Writing three bars before looking at evidence turns that argument into a measurement. The critic floor keeps lenient from meaning gullible."))

    slides.append(('<div class="kicker">Why now</div><h2>A grader whose numbers reproduce</h2>'
                   '<div class="tiles"><div class="tile"><div class="k">Re-asked live</div><div class="v">120</div><div class="s">answers, two subjects, hours apart</div></div>'
                   '<div class="tile"><div class="k">Within 5 points</div><div class="v">97%</div><div class="s">mean drift 1.1 to 1.4 points</div></div>'
                   '<div class="tile"><div class="k">Offline replay</div><div class="v">byte-identical</div><div class="s">no API key, no network</div></div>'
                   '<div class="tile"><div class="k">Cost per subject</div><div class="v">&lt;$0.10</div><div class="s">classifier; X API $0.14 total</div></div></div>'
                   '<ul class="body"><li>Reasoning models do the reading, the searching and the bar-writing.</li><li>TypeSafe\'s Jev answers the same typed yes/no questions over fixed evidence rows and returns calibrated probabilities, not prose.</li><li>Every run commits its sources, claims, bars, evidence and the grader\'s answers. Anyone can replay it.</li></ul>',
                   "Judgement goes to the reasoning model; the repeated yes/no goes to a decision classifier. Drift concentrates where sources disagree, which is where you would want it. The run folder is the unit of publication."))

    cards = []
    for n, d in runs:
        r = d["run"]
        cards.append(f'<div class="card"><div class="k">{esc(r["subject"]["kind"])}</div><h3>{esc(r["subject"]["name"])}</h3><p>{esc(r.get("notes", ""))[:150]}</p><p class="ann">{d["aggregate"]["n_claims"]} claims graded</p></div>')
    slides.append((f'<div class="kicker">The subjects</div><h2>A spread, not a pile-on</h2><div class="grid3" style="grid-template-columns:repeat({min(len(cards), 4)},1fr)">{"".join(cards)}</div>'
                   '<p class="sub" style="margin-top:30px">Chosen for range: a company predicting the thing it builds, a crypto list full of numbers, a macro list with a 30-year ritual. None of them asked for this; all of them wrote things down in public.</p>',
                   "The subjects were chosen for a spread from vague to numeric and from company to person. They are not targets."))

    bullets = {
        "doll": ["Met at every bar: inflation sticky (core PCE 3.0%, unchanged), spreads wider, forward P/E 22 to 19.",
                 "Not met at every bar: earnings growth 32.8% against 'falls short of 14%'; the 10-year above 5% on 22 days against 'high 3s to mid 4s'; S&P up 11.4% against 'no double digits'.",
                 "His own October scorecard: 5 right direction, 0 wrong, 5 too soon. Ours at standard: 4 met, 5 not met, 5 unresolved."],
        "ippolito": ["Met at every bar: prediction-market volume 2X (June to August alone beat all of 2025); Solana REV bottomed in June and doubled by September.",
                     "Not met at every bar: ETH 'best year since 2021' (down 21%); 'ZEC will have a bad 2026' (up 129%).",
                     "Where the bars split: Base's content coins fell 99.8% (standard met) but Base still leads every L2 category (strict not met)."],
        "every": ["The one strict hit: 'designers are going to be able to code' (half of 900 surveyed designers shipped AI-generated code to production).",
                  "Shipper: Cursor will stumble. Hoffman: none will. SpaceX bought Cursor for $60 billion. Neither bar had room for it.",
                  "16 of 22 open at strict: the list is made of adjectives, and October cannot settle 'agents go mainstream'."],
        "galloway": ["Met at standard: space (SpaceX IPO at $1.75 trillion), prediction markets as the year's vice (June alone matched all of 2025; New York sued Kalshi and Polymarket), AI companions as a policy issue (twelve state laws), college enrollment up.",
                     "Not met: Amazon as the Big Tech pick (+7.4% vs the S&P's +12.3%); a 20% AI correction (11% was the worst); the recession; TikTok US as the best investment (closed at $14B, not the $28B he wrote); Scotland.",
                     "The strict row is empty: almost every heading is a thesis, not a number. 8 of 15 still open."],
    }
    for n, d in runs:
        slides.append((scorecard_slide(d["run"]["subject"]["name"], d, [b for b in bullets.get(n, ["See the run folder."]) if b]),
                       f"{d['run']['subject']['name']}: hit rates at the three bars, the gap, and the claims where the bars disagree most. Every cell links to its evidence in the run folder."))

    for fig, kicker, title, notes in (
        ("generosity-gap.png", "Finding 1", "The gap scales with how narrative the list is", "Lenient minus strict: Doll 14, Ippolito 35, Every 50. Nobody publishes this because nobody grades at more than one bar."),
        ("resolved-vs-all.png", "Finding 2", "The same list supports a 100% and a 17%", "Every at lenient, resolved only: 12 of 12. At strict: 1 of 6. Count open claims against the author and lenient is 55%. A scorecard that does not say its convention is not a number."),
        ("numbers-vs-words.png", "Finding 3", "Numbers protect the reader, not the author", "Claims with a number have a smaller gap (25 vs 40) and lower hit rates at standard and lenient (19 and 38 vs 38 and 50). A number is a bar written in advance; it makes a miss undeniable."),
        ("self-grade.png", "Finding 4", "Self-grades differ on one word: wrong", "Doll's own tally has no 'wrong' column; ours has five at the standard bar. The 'too soon' and 'unresolved' columns nearly agree."),
    ):
        slides.append((f'<div class="kicker">{kicker}</div><h2>{esc(title)}</h2><div class="fig"><img src="../figures/{fig}" alt="{esc(title)}"></div>', notes))

    slides.append(('<div class="kicker">Finding 5</div><h2>Some outcomes have no bar</h2>'
                   '<div class="cols"><div class="card"><div class="k">Dan Shipper, Every (Jan 5)</div><h3>"Cursor is the one most likely to stumble."</h3><p>Strict: not met. Standard: not met. Lenient: met (competitive pressure was real).</p></div>'
                   '<div class="card"><div class="k">Reid Hoffman, guest (Jan 5)</div><h3>"I don\'t think any of the horses in the race will particularly stumble."</h3><p>Strict: not met (no longer independent). Standard and lenient: open.</p></div></div>'
                   '<p class="sub" style="margin-top:36px">June 2026: SpaceX acquires Cursor for $60 billion in stock. Not a stumble; not a horse still in the race. Lesson for bar-writing: add one bar the prediction did not seem to need, for the exit.</p>',
                   "The best single pair in the set. Host and guest predicted opposite things and the outcome fit neither. Writing bars in advance teaches you to write one for the exit."))

    slides.append(('<div class="kicker">Caveats</div><h2>What this is not</h2><ul class="body">'
                   '<li>Run on October 24 with ten weeks left. Everything with a December horizon is provisional; the midterm claims are open.</li>'
                   '<li>Text only: both the reasoning model and the classifier. A few claims hinge on things a screenshot would settle.</li>'
                   '<li>Our bars are ours. The review sheets are public and the runs replay; argue with the bars, and the regrade is one command.</li>'
                   '<li>Guest predictions on a subject\'s podcast are shown apart from the subject\'s own.</li></ul>',
                   "The caveats are structural, not apologetic. Provisional grades are labelled; the bars are the thing to argue with."))

    slides.append(('<div class="kicker">The ask</div><h2>Before you publish your 2027 list</h2>'
                   '<div class="cols"><div class="card"><h3>If you are about to publish</h3><p>Write your three bars now, while you still mean them, and publish them with the list.</p></div>'
                   '<div class="card"><h3>If you published a 2026 list</h3><p>Run it on yourself and post the receipts. The tool drafts the thread.</p></div></div>'
                   '<p class="sub" style="margin-top:36px"><code>/plugin marketplace add rickmanelius/called-it</code> &nbsp;·&nbsp; <code>npx skills add rickmanelius/called-it -g -y</code> &nbsp;·&nbsp; no API keys required</p>'
                   '<div class="foot"><span>Runs by pull request join the gallery</span><span>github.com/rickmanelius/called-it</span></div>',
                   "The season opens in a week. Pre-register your bars, or grade your last list. Runs come in by pull request and join the gallery."))
    return slides


def write_html(slides):
    OUT.mkdir(parents=True, exist_ok=True)
    parts = [f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Called It! deck</title><style>{CSS}</style></head><body>']
    for i, (body, _) in enumerate(slides, 1):
        parts.append(f'<section class="slide" id="s{i}">{body}</section>')
    parts.append(SCRIPT + "</body></html>")
    (OUT / "slides.html").write_text("\n".join(parts))
    (OUT / "notes.json").write_text(json.dumps([{"slide": i, "notes": n} for i, (_, n) in enumerate(slides, 1)], indent=1))


def render_pngs(n):
    (OUT / "png").mkdir(exist_ok=True)
    for i in range(1, n + 1):
        subprocess.run([sys.executable, str(ROOT / "tools" / "render_png.py"), f"{OUT / 'slides.html'}?only={i}", str(OUT / "png" / f"slide-{i:02d}.png"), "1600", "900"], check=True, capture_output=True)
    print(f"rendered {n} slides to {OUT / 'png'}")


def write_pptx(slides):
    from pptx import Presentation
    from pptx.util import Inches
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(16), Inches(9)
    blank = prs.slide_layouts[6]
    for i, (_, notes) in enumerate(slides, 1):
        s = prs.slides.add_slide(blank)
        s.shapes.add_picture(str(OUT / "png" / f"slide-{i:02d}.png"), 0, 0, width=prs.slide_width, height=prs.slide_height)
        s.notes_slide.notes_text_frame.text = notes
    prs.save(OUT / "deck.pptx")
    print(f"wrote {OUT / 'deck.pptx'}")


def write_pdf():
    import shutil
    chrome = next((c for c in ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", shutil.which("google-chrome") or "", shutil.which("chromium") or ""] if c and pathlib.Path(c).exists()), None)
    if not chrome:
        print("no Chrome for the PDF")
        return
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={OUT / 'deck.pdf'}", (OUT / "slides.html").as_uri()], capture_output=True, timeout=120)
    print(f"wrote {OUT / 'deck.pdf'}" if (OUT / "deck.pdf").exists() else "pdf failed")


def main(argv):
    runs = load_runs()
    slides = build_slides(runs)
    write_html(slides)
    print(f"wrote {OUT / 'slides.html'} ({len(slides)} slides) and notes.json")
    if "--no-render" not in argv:
        render_pngs(len(slides))
        write_pdf()
    if "--pptx" in argv:
        write_pptx(slides)


if __name__ == "__main__":
    main(sys.argv)
