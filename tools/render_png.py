#!/usr/bin/env python3
"""Render an HTML file to a PNG with headless Chrome. Deterministic given the same HTML and size.

    python3 tools/render_png.py <input.html> <output.png> [width] [height]

Used for the process infographic (1600x900) and for eyeballing report.html. Chrome is looked up in the
usual macOS and Linux locations or taken from $CHROME.
"""
import os
import pathlib
import shutil
import subprocess
import sys

CANDIDATES = [
    os.environ.get("CHROME", ""),
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
    shutil.which("chromium-browser") or "",
]


def chrome() -> str:
    for c in CANDIDATES:
        if c and pathlib.Path(c).exists():
            return c
    sys.exit("no Chrome found; set $CHROME to the binary")


def main(argv):
    if len(argv) < 3:
        sys.exit(__doc__)
    raw, _, frag = argv[1].partition("#")  # a #fragment (e.g. #light) is passed to the page, not the filesystem
    raw, _, query = raw.partition("?")      # likewise a ?query (e.g. ?only=3 for one slide of a deck)
    src = pathlib.Path(raw).resolve()
    out = pathlib.Path(argv[2]).resolve()
    w = argv[3] if len(argv) > 3 else "1600"
    h = argv[4] if len(argv) > 4 else "900"
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", f"--window-size={w},{h}",
           f"--screenshot={out}", src.as_uri() + (f"?{query}" if query else "") + (f"#{frag}" if frag else "")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if not out.exists():
        sys.exit(f"render failed (rc {r.returncode}): {r.stderr[-500:]}")
    print(f"wrote {out} ({out.stat().st_size} bytes) at {w}x{h}")


if __name__ == "__main__":
    main(sys.argv)
