"""Brand tokens for Called It! (sample B, the dark scoreboard), shared by the report renderer and the
tools under tools/. One place for colours, type and the @font-face rules. Standard library only.

Dark only. Fonts are self-hosted under site/assets/fonts/ (tools/fetch_fonts.py downloads them); every
page states where those files are relative to itself through the prefix argument.
"""
from __future__ import annotations

COLORS = {
    "ground": "#0F1218",
    "surface": "#171C25",
    "surface2": "#1E2430",
    "border": "#2A313D",
    "ink": "#F2F4F7",
    "muted": "#A3ABB8",
    "text2": "#C9D0DA",
    "accent": "#FFB020",
    "accent_hover": "#FFD36B",
    "on_accent": "#0F1218",
    "on_accent_small": "#3D2A00",
    "bar_strict": "#8B93A1",
    "bar_standard": "#D7DCE3",
    "bar_lenient": "#FFB020",
    "met": "#4FD1A1",
    "not_met": "#FF5C5C",  # nudged from #FF7A7A so met/not met clear the colour-vision check (deutan dE 9.9 vs 5.6)
    "unresolved": "#A3ABB8",
}

BAR_COLORS = {"strict": COLORS["bar_strict"], "standard": COLORS["bar_standard"], "lenient": COLORS["bar_lenient"]}
STATUS_COLORS = {"met": COLORS["met"], "not_met": COLORS["not_met"], "unresolved": COLORS["unresolved"]}

FONT_TEXT = "'Space Grotesk', system-ui, -apple-system, 'Segoe UI', sans-serif"
FONT_MONO = "'IBM Plex Mono', ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# (family, css font-weight for the @font-face rule, file name under the fonts folder, weights to request).
# Space Grotesk ships as one variable file covering 300 to 700, so one rule with a range serves all three weights.
FONT_FILES = (
    ("Space Grotesk", "300 700", "space-grotesk.woff2", (400, 500, 700)),
    ("IBM Plex Mono", "500", "ibm-plex-mono-500.woff2", (500,)),
    ("IBM Plex Mono", "600", "ibm-plex-mono-600.woff2", (600,)),
)

# Where report.html inside runs/<run>/ finds the fonts. The site builder rewrites this prefix in its copies.
DEFAULT_FONT_PREFIX = "../../site/assets/fonts/"


def font_face_css(prefix: str = DEFAULT_FONT_PREFIX) -> str:
    rules = []
    for family, weight, fname, _ in FONT_FILES:
        rules.append(f"@font-face {{ font-family: '{family}'; font-style: normal; font-weight: {weight}; font-display: block; "
                     f"src: url('{prefix}{fname}') format('woff2'); }}")
    return "\n".join(rules)


def css_vars() -> str:
    c = COLORS
    return (":root { color-scheme: dark; "
            f"--page:{c['ground']}; --surface:{c['surface']}; --surface-2:{c['surface2']}; --border:{c['border']}; "
            f"--ink:{c['ink']}; --ink-2:{c['text2']}; --muted:{c['muted']}; --grid:{c['border']}; --axis:{c['border']}; --ring:{c['border']}; "
            f"--accent:{c['accent']}; --accent-hover:{c['accent_hover']}; --on-accent:{c['on_accent']}; --on-accent-small:{c['on_accent_small']}; "
            f"--bar-strict:{c['bar_strict']}; --bar-standard:{c['bar_standard']}; --bar-lenient:{c['bar_lenient']}; "
            f"--good:{c['met']}; --critical:{c['not_met']}; --open:{c['unresolved']}; "
            f"--font-text:{FONT_TEXT}; --font-mono:{FONT_MONO}; }}")


def base_css(prefix: str = DEFAULT_FONT_PREFIX) -> str:
    """The shared block: @font-face rules, the custom properties, and the page basics every page starts from."""
    return "\n".join([
        font_face_css(prefix),
        css_vars(),
        "* { box-sizing: border-box; }",
        "html, body { margin: 0; background: var(--page); color: var(--ink); font-family: var(--font-text); }",
        ".mono, code, pre, .num, .badge, .chip { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }",
        "a { color: inherit; text-decoration: underline; text-decoration-color: var(--border); text-underline-offset: 2px; }",
        "a:hover { color: var(--accent-hover); }",
    ])
