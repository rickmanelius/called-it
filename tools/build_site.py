#!/usr/bin/env python3
"""Build the static site: a gallery index and one page per graded subject. Deterministic; standard library only.

    python3 tools/build_site.py [--out site] [--base-url https://rickmanelius.github.io/called-it/]

site/index.html            gallery: one card per subject with the headline numbers, the cross-subject figures
site/<run>/index.html      subject page: tiles, share section, links to the full scorecard, the bars, downloads, the post draft
site/<run>/report.html     copy of the run's scorecard (font paths rewritten to the site's assets)
site/<run>/<run>.xlsx, data.json, post.md, rubrics.md, share.json, share.md, claims.csv, grades.csv, evidence.csv
site/assets/               figures, the infographic, the fonts, the 1200x630 social cards

Every page carries Open Graph and Twitter card tags pointing at its social card, built from --base-url.
The default base URL is a placeholder until GitHub Pages exists for the public repo.
Look and type come from lib/brand.py (sample B, dark only).
"""
from __future__ import annotations

import html
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "called-it" / "scripts"))
from lib import brand, config  # noqa: E402

BASE_URL = "https://rickmanelius.github.io/called-it/"  # placeholder until the public repo has Pages turned on
REPO_URL = "https://github.com/rickmanelius/called-it"
TITLE = "Called It!"
SUBTITLE = "Using AI Classifiers to Score a Person's Annual Predictions"
INDEX_DESCRIPTION = ("Using AI classifiers to score a person's annual predictions. Four 2026 lists graded at three bars (strict, standard, lenient) "
                     "with every receipt attached. The gap between the bars is the finding.")
ARTICLE_URL = "https://www.rickmanelius.com/p/called-it"  # placeholder until the post is live

SITE_CSS = """
body { font-size: 16px; line-height: 1.5; }
main { max-width: 1040px; margin: 0 auto; padding: 32px 16px 64px; }
.badge { color: var(--muted); font-size: 13px; letter-spacing: .04em; text-transform: uppercase; }
h1 { font-size: 44px; font-weight: 700; margin: 10px 0 4px; letter-spacing: -.025em; line-height: 1.05; }
h1 .bang { color: var(--accent); }
h2 { font-size: 22px; font-weight: 700; margin: 36px 0 12px; letter-spacing: -.01em; }
.subtitle { font-size: 20px; color: var(--muted); margin: 0 0 16px; }
.lede { color: var(--ink-2); }
ul.lede { padding-left: 22px; margin: 10px 0 18px; } ul.lede li { margin: 5px 0; }
.btn { display: inline-flex; align-items: center; gap: 10px; min-height: 48px; padding: 0 20px; border-radius: 10px; border: 1.5px solid var(--border); background: var(--surface); color: var(--ink); font-weight: 700; font-size: 15px; text-decoration: none; cursor: pointer; font-family: var(--font-text); }
.btn:hover { border-color: var(--accent); color: var(--ink); }
.btn.primary { background: var(--accent); border-color: var(--accent); color: var(--on-accent); }
.btn.primary:hover { background: var(--accent-hover); border-color: var(--accent-hover); color: var(--on-accent); }
.banner { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin: 14px 0 10px; padding: 14px 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 14px; }
.banner .note { color: var(--muted); font-size: 13px; }
.game { color: var(--muted); font-size: 14px; margin: 0 0 24px; }
.cards { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 16px; margin: 20px 0 8px; }
.card { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 18px 20px; display: block; text-decoration: none; min-width: 0; }
.card:hover { border-color: var(--accent); color: var(--ink); }
.card h3 { margin: 0 0 2px; font-size: 20px; font-weight: 700; } .card .k { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .06em; }
.rates { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 6px; margin: 12px 0 6px; }
.rates > div { background: var(--page); border: 1px solid var(--border); border-radius: 8px; padding: 8px 6px; text-align: center; min-width: 0; }
.rates .v { font-family: var(--font-mono); font-size: 20px; font-weight: 600; font-variant-numeric: tabular-nums; } .rates .l { color: var(--muted); font-size: 10px; text-transform: uppercase; letter-spacing: .04em; white-space: nowrap; }
.rates > div.gap { background: var(--accent); border-color: var(--accent); } .rates > div.gap .v { color: var(--on-accent); } .rates > div.gap .l { color: var(--on-accent-small); }
.tiles { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; margin: 20px 0; }
.tile { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; } .tile .k { color: var(--muted); font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: .08em; }
.tile .v { font-family: var(--font-mono); font-variant-numeric: tabular-nums; font-size: 32px; font-weight: 600; line-height: 1.1; margin-top: 2px; } .tile .s { color: var(--muted); font-size: 12px; margin-top: 4px; }
.tile.gap { background: var(--accent); border-color: var(--accent); color: var(--on-accent); } .tile.gap .k, .tile.gap .s { color: var(--on-accent-small); }
.share { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; margin: 12px 0 8px; }
.share .row { display: flex; flex-wrap: wrap; gap: 12px; margin: 0 0 12px; }
.share textarea { width: 100%; min-height: 96px; resize: vertical; background: var(--page); color: var(--ink); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; font: 14px/1.5 var(--font-text); }
.share .copyrow { display: flex; gap: 12px; align-items: center; margin-top: 8px; } .share .copied { color: var(--good); font-size: 13px; }
.links { display: flex; flex-wrap: wrap; gap: 10px; margin: 12px 0; } .links a { background: var(--surface); border: 1px solid var(--border); border-radius: 10px; padding: 8px 12px; font-size: 14px; text-decoration: none; }
.links a:hover { border-color: var(--accent); color: var(--ink); }
.links a.primary { background: var(--accent); color: var(--on-accent); border-color: var(--accent); }
h2.dl { margin-top: 30px } .links.roomy { gap: 14px; margin: 14px 0 26px } .links.roomy a { display: flex; flex-direction: column; gap: 3px; padding: 12px 16px; min-width: 170px }
.links.roomy a b { font-weight: 700 } .links.roomy a small { color: var(--muted); font-size: 12px } .links.roomy a.primary small { color: var(--on-accent-small) }
figure { margin: 18px 0 } figure img { width: 100%; height: auto; border: 1px solid var(--border); border-radius: 12px; background: var(--page); display: block; }
figcaption { color: var(--muted); font-size: 13px; margin-top: 6px }
pre { background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; overflow-x: auto; font-family: var(--font-mono); font-size: 14px; line-height: 1.6; color: var(--ink); }
pre code { font-family: inherit; } pre .c { color: var(--muted); }
footer { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--border); color: var(--muted); font-size: 13px }
@media (max-width: 640px) { h1 { font-size: 34px; } .tile .v { font-size: 26px; } .cards { grid-template-columns: 1fr; } }
"""


def pct(x):
    return "n/a" if x is None else f"{round(x * 100)}%"


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def meta_tags(*, url: str, title: str, description: str, image: str, image_alt: str, og_type: str) -> str:
    return "\n".join([
        f'<meta name="description" content="{esc(description)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:site_name" content="{esc(TITLE)}">',
        f'<meta property="og:url" content="{esc(url)}">',
        f'<meta property="og:title" content="{esc(title)}">',
        f'<meta property="og:description" content="{esc(description)}">',
        f'<meta property="og:image" content="{esc(image)}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{esc(image_alt)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:site" content="@rickmanelius">',
        '<meta name="twitter:creator" content="@rickmanelius">',
        f'<meta name="twitter:title" content="{esc(title)}">',
        f'<meta name="twitter:description" content="{esc(description)}">',
        f'<meta name="twitter:image" content="{esc(image)}">',
        f'<meta name="twitter:image:alt" content="{esc(image_alt)}">',
    ])


def page(title: str, body: str, *, depth: int, meta: str) -> str:
    font_prefix = "assets/fonts/" if depth == 0 else "../assets/fonts/"
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)}</title>\n{meta}\n<style>{brand.base_css(font_prefix)}\n{SITE_CSS}</style></head><body><main>{body}'
            f'<footer>{config.NAME} v{config.VERSION}. Every number on this site traces to a bar and an evidence row in a committed run folder; <code>called-it replay</code> reproduces it offline.</footer></main></body></html>')


COPY_JS = """
<script>
(function(){var b=document.getElementById('copy-share');if(!b)return;b.addEventListener('click',function(){var t=document.getElementById('share-text');t.select();var ok=false;
try{if(navigator.clipboard){navigator.clipboard.writeText(t.value);ok=true;}else{ok=document.execCommand('copy');}}catch(e){}
var s=document.getElementById('copied');if(s){s.textContent=ok?'Copied.':'Select the text and copy it.';}});})();
</script>
"""


def share_section(run_name: str, share: dict | None) -> str:
    if not share:
        return ""
    quote = ""
    if share.get("quote_url"):
        quote = f'<a class="btn" href="{esc(share["quote_url"])}" target="_blank" rel="noopener">Quote the original post</a>'
    return f"""
<h2>Share this scorecard</h2>
<p class="lede">The game: find the predictor, quote their original post with the card and a one-line overview. The text below is a draft; edit it.</p>
<div class="share">
  <div class="row">
    <a class="btn primary" href="{esc(share.get('intent_url', '#'))}" target="_blank" rel="noopener">Post on X</a>
    {quote}
    <a class="btn" download href="../assets/social/{esc(run_name)}.png">Download the card (1200x630)</a>
  </div>
  <label for="share-text" class="badge">Suggested text</label>
  <textarea id="share-text" readonly>{esc(share.get('text_short', ''))}</textarea>
  <div class="copyrow"><button class="btn" id="copy-share" type="button">Copy</button><span class="copied" id="copied"></span></div>
</div>
{COPY_JS}
"""


def subject_description(a: dict) -> str:
    pb = a["per_bar"]
    gap = a["generosity_gap"]
    return (f"{pct(pb['strict']['hit_rate_all'])} strict · {pct(pb['standard']['hit_rate_all'])} standard · {pct(pb['lenient']['hit_rate_all'])} lenient · "
            f"generosity gap {'n/a' if gap is None else round(gap * 100)} points. {a['n_claims']} claims graded at three bars against the year's evidence, receipts attached.")


def subject_page(data: dict, run_name: str, base_url: str, share: dict | None) -> str:
    r = data["run"]
    a = data["aggregate"]
    pb = a["per_bar"]
    name = r["subject"]["name"]
    gap = a["generosity_gap"]
    tiles = "".join(f'<div class="tile"><div class="k">{b.title()}</div><div class="v">{pct(pb[b]["hit_rate_all"])}</div><div class="s">{pb[b]["met"]} met · {pb[b]["not_met"]} not met · {pb[b]["unresolved"]} unresolved</div></div>' for b in config.BARS)
    tiles += f'<div class="tile gap"><div class="k">Generosity gap</div><div class="v">{"n/a" if gap is None else f"{round(gap * 100)} pts"}</div><div class="s">lenient minus strict</div></div>'
    title = f"{name}: {r['target_year']} predictions, graded"
    body = f"""
<div class="badge"><a href="../index.html">called-it</a> · {esc(name)} · {r['target_year']} · graded {r['evidence_window']['end']} · {esc(', '.join(sorted(data.get('grader_models', {}))))}</div>
<h1>{esc(name)}: {r['target_year']} predictions, graded</h1>
<ul class="lede">
  <li>{a['n_claims']} claims graded at three bars against evidence from {r['evidence_window']['start']} to {r['evidence_window']['end']}.</li>
  <li>Strict is what a hostile critic would require. Lenient is the weakest reading a critic would still concede.</li>
  <li>The gap between them is how much the grade depends on who is grading.</li>
  <li>Everything here is provisional until the year ends.</li>
</ul>
<div class="tiles">{tiles}</div>
{share_section(run_name, share)}
<h2 class="dl">You can view the data in a variety of ways</h2>
<div class="links roomy">
  <a class="primary" href="report.html"><b>Full scorecard</b><small>every claim, bar and evidence row</small></a>
  <a href="rubrics.md"><b>The bars</b><small>as written before any evidence (review sheet)</small></a>
  <a href="{run_name}.xlsx"><b>Workbook (.xlsx)</b><small>claims, bars, grades and evidence on sheets</small></a>
  <a href="data.json"><b>data.json</b><small>everything the scorecard was built from</small></a>
  <a href="claims.csv"><b>claims.csv</b><small>one row per claim</small></a>
  <a href="grades.csv"><b>grades.csv</b><small>one row per claim and bar</small></a>
  <a href="evidence.csv"><b>evidence.csv</b><small>one row per dated, tiered quote</small></a>
  <a href="post.md"><b>Self-review draft</b><small>the thread they could post, one line per claim</small></a>
</div>
<figure><img src="scorecard.png" alt="Scorecard for {esc(name)}"><figcaption>The scorecard as rendered on {r['evidence_window']['end']}.</figcaption></figure>
"""
    meta = meta_tags(url=f"{base_url}{run_name}/", title=title, description=subject_description(a),
                     image=f"{base_url}assets/social/{run_name}.png", og_type="article",
                     image_alt=f"{name}: {r['target_year']} predictions graded at three bars. {subject_description(a)}")
    return page(title, body, depth=1, meta=meta)


def index_page(datas: list[tuple[str, dict]], base_url: str) -> str:
    cards = []
    for run_name, data in datas:
        r, a = data["run"], data["aggregate"]
        pb = a["per_bar"]
        gap = a["generosity_gap"]
        cards.append(f"""<a class="card" href="{run_name}/index.html"><div class="k">{esc(r['subject']['kind'])} · {r['target_year']}</div><h3>{esc(r['subject']['name'])}</h3>
<div class="rates"><div><div class="v">{pct(pb['strict']['hit_rate_all'])}</div><div class="l">strict</div></div><div><div class="v">{pct(pb['standard']['hit_rate_all'])}</div><div class="l">standard</div></div><div><div class="v">{pct(pb['lenient']['hit_rate_all'])}</div><div class="l">lenient</div></div><div class="gap"><div class="v">{"n/a" if gap is None else round(gap * 100)}</div><div class="l">gap, pts</div></div></div>
<div class="k">{a['n_claims']} claims · {pb['strict']['unresolved']} open at strict · as of {r['evidence_window']['end']}</div></a>""")
    body = f"""
<h1>Called It<span class="bang">!</span></h1>
<p class="subtitle">{esc(SUBTITLE)}</p>
<p class="lede">Every holiday season, people make predictions about what will happen in the next year. The problem? Few people go back and evaluate how they did with objectivity. The "Called It!" skill uses best-in-class AI evaluation models to make this trivial.</p>
<!-- Placeholder link until the post is live. -->
<p><a class="btn primary" href="{ARTICLE_URL}">Read the article on rickmanelius.com</a></p>
<h2>How it works</h2>
<figure><img src="assets/process.png" alt="How Called It! works: seven stages from discovering the predictions to a replayable scorecard"><figcaption>Seven stages. The three bars are written and reviewed before any evidence is fetched.</figcaption></figure>
<h2>Already Evaluated Annual Predictions</h2>
<div class="cards">{''.join(cards)}</div>
<figure><img src="assets/hit-rates.png" alt="Hit rate at each bar, by subject"><figcaption>Hit rate at each bar. Unresolved claims count against the rate.</figcaption></figure>
<figure><img src="assets/generosity-gap.png" alt="The generosity gap by subject"><figcaption>The generosity gap: lenient minus strict, in points.</figcaption></figure>
<div class="links"><a href="data/called-it-2026.xlsx">All subjects, one workbook (.xlsx)</a><a href="{REPO_URL}">The skill and every run folder on GitHub</a></div>
<h2>Grade someone</h2>
<p class="lede">Install the skill, point it at a prediction post, and a run folder comes out. Open a pull request with the folder and it joins this gallery.</p>
<pre><code><span class="c"># Claude Code</span>
/plugin marketplace add rickmanelius/called-it
/plugin install called-it@called-it
/called-it "Name" 2026 https://link-to-their-predictions

<span class="c"># Codex and other Agent Skills hosts</span>
npx skills add rickmanelius/called-it -g -y
/called-it "Name" 2026 https://link-to-their-predictions</code></pre>
"""
    meta = meta_tags(url=base_url, title=TITLE, description=INDEX_DESCRIPTION, image=f"{base_url}assets/social/index.png", og_type="website",
                     image_alt="Called It! Using AI Classifiers to Score Annual Predictions. Generosity gap by subject: "
                               + ", ".join(f"{d['run']['subject']['name']} {round((d['aggregate']['generosity_gap'] or 0) * 100)}" for _, d in sorted(datas, key=lambda x: x[1]['aggregate']['generosity_gap'] or 0)))
    return page(f"{TITLE} {SUBTITLE}", body, depth=0, meta=meta)


def main(argv):
    out = ROOT / "site"
    base_url = BASE_URL
    if "--out" in argv:
        out = pathlib.Path(argv[argv.index("--out") + 1])
    if "--base-url" in argv:
        base_url = argv[argv.index("--base-url") + 1]
    if not base_url.endswith("/"):
        base_url += "/"
    out.mkdir(parents=True, exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    (out / "data").mkdir(exist_ok=True)
    for f in ("hit-rates.png", "generosity-gap.png"):
        src = ROOT / "article" / "figures" / f
        if src.exists():
            shutil.copy(src, out / "assets" / f)
    if (ROOT / "article" / "infographic" / "process.png").exists():
        shutil.copy(ROOT / "article" / "infographic" / "process.png", out / "assets" / "process.png")
    if (ROOT / "article" / "data" / "called-it-2026.xlsx").exists():
        shutil.copy(ROOT / "article" / "data" / "called-it-2026.xlsx", out / "data" / "called-it-2026.xlsx")
    if not (ROOT / "site" / "assets" / "fonts").exists() and out != ROOT / "site":
        print("warning: site/assets/fonts is missing; run tools/fetch_fonts.py")
    if out != ROOT / "site":
        for sub in ("fonts", "social"):
            src = ROOT / "site" / "assets" / sub
            if src.exists():
                shutil.copytree(src, out / "assets" / sub, dirs_exist_ok=True)
    datas = []
    for d in sorted(p for p in (ROOT / "runs").iterdir() if (p / "data.json").exists() and (p / "grades.jsonl").exists()):
        data = json.loads((d / "data.json").read_text())
        if not data.get("grades"):
            continue
        run_name = d.name
        sub = out / run_name
        sub.mkdir(exist_ok=True)
        share = None
        if (d / "share.json").exists():
            share = json.loads((d / "share.json").read_text())
        else:
            print(f"warning: {d / 'share.json'} is missing; the share section is skipped for {run_name}")
        (sub / "index.html").write_text(subject_page(data, run_name, base_url, share))
        if (d / "report.html").exists():
            text = (d / "report.html").read_text().replace(brand.DEFAULT_FONT_PREFIX, "../assets/fonts/")
            (sub / "report.html").write_text(text)
        for f in ("data.json", "post.md", "rubrics.md", "share.json", "share.md"):
            if (d / f).exists():
                shutil.copy(d / f, sub / f)
        for f in ("claims.csv", "grades.csv", "evidence.csv", f"{run_name}.xlsx"):
            if (d / "export" / f).exists():
                shutil.copy(d / "export" / f, sub / f)
        shot = ROOT / "article" / "figures" / f"scorecard-{run_name}.png"
        if shot.exists():
            shutil.copy(shot, sub / "scorecard.png")
        datas.append((run_name, data))
    datas.sort(key=lambda x: -(x[1]["aggregate"]["generosity_gap"] or 0))
    (out / "index.html").write_text(index_page(datas, base_url))
    missing = [f"assets/social/{n}.png" for n, _ in datas if not (ROOT / "site" / "assets" / "social" / f"{n}.png").exists()]
    if not (ROOT / "site" / "assets" / "social" / "index.png").exists():
        missing.append("assets/social/index.png")
    if missing:
        print("warning: social images missing (run tools/build_cards.py): " + ", ".join(missing))
    print(f"wrote {out}/index.html and {len(datas)} subject pages (base URL {base_url})")


if __name__ == "__main__":
    main(sys.argv)
