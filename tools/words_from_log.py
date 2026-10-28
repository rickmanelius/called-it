#!/usr/bin/env python3
"""Collect the word-level chunks `hyperframes transcribe --json` streams on stderr into one words.json, and print
each narration line's words with times (using timing.json to assign words to lines). Standard library only.

    python3 tools/words_from_log.py <transcribe.log> <project dir>
"""
import json
import pathlib
import sys

log = pathlib.Path(sys.argv[1])
proj = pathlib.Path(sys.argv[2])
words = []
for line in log.read_text().splitlines():
    line = line.strip()
    if not line.startswith("{"):
        continue
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        continue
    if obj.get("type") == "words":
        words.extend(obj.get("words", []))
words.sort(key=lambda w: w["start"])
(proj / "words.json").write_text(json.dumps(words, indent=0))
timing = json.loads((proj / "timing.json").read_text())
print(f"{len(words)} words")
for ln in timing["lines"]:
    ws = [w for w in words if ln["start"] - 0.3 <= w["start"] <= ln["end"] + 0.3]
    print(f"\n{ln['id']} ({ln['start']:.2f}-{ln['end']:.2f}):")
    print("  " + "  ".join(f"{w['text']}@{w['start']:.2f}" for w in ws))
