#!/usr/bin/env python3
"""Branded QR code for an akinsmarket.com address: transparent background, round brand-green
dots, square finder rings with soft cores, Akins carrot in the centre (error correction H covers
the knockout).

usage: make_qr.py <url> <out-stem>     writes <out-stem>.svg and <out-stem>.png (2400 px)
needs: segno, cairosvg (render) ; verify with tools/verify_qr.py

capability: render:branded_qr e6585cb1b83f
"""
import re
import sys
from pathlib import Path

import cairosvg
import segno

GREEN = "#194a3b"          # site --main
QUIET = 4                  # modules of transparent margin (QR spec minimum)
DOT = 0.9                  # data-dot diameter, in modules
CORE_ROUND = 0.3           # corner radius of the finder-eye core, as a fraction of its side
LOGO_MODULES = 9           # side of the centre knockout, in modules (odd keeps it centred)
ROOT = Path(__file__).resolve().parent.parent


def carrot_group(x, y, size):
    """The site's favicon carrot, inlined and scaled into a size x size box at (x, y)."""
    svg = (ROOT / "favicon.svg").read_text()
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
    inner = inner.replace('id="v3gr40ccut"', 'id="qrcut"').replace("url(#v3gr40ccut)", "url(#qrcut)")
    inner = inner.replace('id="v3gr40cclip"', 'id="qrclip"').replace("url(#v3gr40cclip)", "url(#qrclip)")
    return f'<g transform="translate({x} {y}) scale({size / 1024})">{inner}</g>'


def build(url):
    qr = segno.make(url, error="h", micro=False, boost_error=False)
    m = [list(row) for row in qr.matrix]
    n = len(m)
    size = n + 2 * QUIET
    lo = (n - LOGO_MODULES) // 2
    hi = lo + LOGO_MODULES

    def in_finder(r, c):
        return (r < 7 and c < 7) or (r < 7 and c >= n - 7) or (r >= n - 7 and c < 7)

    align = []  # alignment-pattern centres (version >= 2): 5x5 blocks that are not finders
    if qr.version >= 2:
        for r in range(2, n - 2):
            for c in range(2, n - 2):
                if in_finder(r, c):
                    continue
                ring = all(m[r + dr][c + dc] for dr in (-2, 2) for dc in range(-2, 3)) and \
                    all(m[r + dr][c + dc] for dc in (-2, 2) for dr in range(-2, 3))
                gap = not any(m[r + dr][c + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1) if (dr, dc) != (0, 0))
                if ring and gap and m[r][c]:
                    align.append((r, c))

    def in_align(r, c):
        return any(abs(r - ar) <= 2 and abs(c - ac) <= 2 for ar, ac in align)

    parts = []
    for r in range(n):
        for c in range(n):
            if not m[r][c] or in_finder(r, c) or in_align(r, c):
                continue
            if lo <= r < hi and lo <= c < hi:
                continue  # centre knockout for the carrot
            cx, cy = c + QUIET + 0.5, r + QUIET + 0.5
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{DOT / 2}"/>')

    def eye(x, y, outer=7, mid=5, core=3):
        # Ring stays SQUARE-cornered: rounding the ring broke OpenCV-class readers at most sizes
        # (2026-11-09 sweep); only the core is softened, which every reader tolerated.
        o, i = outer, mid
        ring = f'<path fill-rule="evenodd" d="{rrect(x, y, o, 0)} {rrect(x + 1, y + 1, i, 0)}"/>'
        cr = f'<path d="{rrect(x + (o - core) / 2, y + (o - core) / 2, core, core * CORE_ROUND)}"/>'
        return ring + cr

    for (r, c) in ((0, 0), (0, n - 7), (n - 7, 0)):
        parts.append(eye(c + QUIET, r + QUIET))
    for (r, c) in align:
        parts.append(eye(c - 2 + QUIET, r - 2 + QUIET, outer=5, mid=3, core=1))

    pad = -0.6  # carrot art has empty margin in its viewBox; the drawn carrot stays inside the knockout
    logo = carrot_group(lo + QUIET + pad, lo + QUIET + pad, LOGO_MODULES - 2 * pad)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
           f'width="{size * 40}" height="{size * 40}" shape-rendering="geometricPrecision">'
           f'<title>QR code: {url}</title>'
           f'<g fill="{GREEN}">{"".join(parts)}</g>{logo}</svg>')
    return svg, qr.version


def rrect(x, y, s, rad):
    """Rounded-square path data (clockwise); rad 0 = plain square."""
    if rad <= 0:
        return f"M{x},{y} H{x + s} V{y + s} H{x} Z"
    return (f"M{x + rad},{y} H{x + s - rad} A{rad},{rad} 0 0 1 {x + s},{y + rad} "
            f"V{y + s - rad} A{rad},{rad} 0 0 1 {x + s - rad},{y + s} H{x + rad} "
            f"A{rad},{rad} 0 0 1 {x},{y + s - rad} V{y + rad} A{rad},{rad} 0 0 1 {x + rad},{y} Z")


def main():
    url, stem = sys.argv[1], Path(sys.argv[2])
    svg, version = build(url)
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".svg").write_text(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=str(stem.with_suffix(".png")),
                     output_width=2400, output_height=2400)
    print(f"version {version}, wrote {stem}.svg and {stem}.png")


if __name__ == "__main__":
    main()
