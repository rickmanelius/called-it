#!/usr/bin/env python3
"""Drop the raw `html` field from cached page records under runs/*/cache/pages, keeping the extracted text.

Idempotent. Run once after upgrading from a version that stored HTML, or any time before publishing.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
n, saved = 0, 0
for p in sorted(ROOT.glob("runs/*/cache/pages/*.json")):
    rec = json.loads(p.read_text())
    if "html" in rec:
        html = rec.pop("html")
        rec.setdefault("html_bytes", len(html.encode("utf-8", errors="replace")))
        before = p.stat().st_size
        p.write_text(json.dumps(rec, ensure_ascii=False))
        saved += before - p.stat().st_size
        n += 1
print(f"stripped html from {n} cached pages, {saved / 1e6:.1f} MB smaller")
sys.exit(0)
