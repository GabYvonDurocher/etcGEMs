#!/usr/bin/env python3
"""measure_figures.py -- is every figure legible at the size it is rendered?

    python3 reports/ecoli_deck/measure_figures.py

The threshold is fixed in DECISIONS.md D17 BEFORE any figure was measured: a text element must
render at >= 9 pt, the governing element is the tick label, and matplotlib's default tick size is
10 pt -- so the criterion is a rendered scale factor

    f = rendered width in points / native width in points     with     f >= 0.9

Native width comes from the PNG's own pixel width and dpi (`px / dpi * 72`); the rendered width
from the size directive in `deck.qmd` against the slide's measured text block -- linewidth
398.3386 pt, textheight 252.0748 pt, both read from a one-frame Beamer probe (`\\the\\linewidth`)
rather than assumed. A figure inside a `{.column width="N%"}` gets N % of the linewidth.

Prints the table and exits 1 if any figure is below threshold, so the shortfall cannot be lost.
"""
import io
import os
import re
import sys

from PIL import Image

LW, TH = 398.3386, 252.0748
THRESHOLD = 0.9
DEFAULT_TICK_PT = 10.0


def rows():
    src = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "deck.qmd"),
                  encoding="utf-8").read()
    here = os.path.dirname(os.path.abspath(__file__))
    out = []
    for blk in re.split(r"(?=^## )", src, flags=re.M):
        title = blk.split("\n", 1)[0].strip().lstrip("# ").strip()
        col = re.search(r'\{\.column width="(\d+)%"\}', blk)
        for m in re.finditer(r"!\[.*?\]\((\S+?\.png)\)\{(width|height)=(\d+)%\}", blk, re.S):
            path, kind, val = m.group(1), m.group(2), int(m.group(3))
            im = Image.open(os.path.join(here, path))
            dpi = (im.info.get("dpi") or (100, 100))[0] or 100
            nat = im.width / dpi * 72
            avail = LW * (int(col.group(1)) / 100 if col else 1.0)
            rend = avail * val / 100 if kind == "width" else TH * val / 100 * im.width / im.height
            out.append((title, os.path.basename(path), im.width, im.height, int(dpi), nat,
                        f"{kind}={val}%", bool(col), rend, rend / nat))
    return out


def main():
    data = rows()
    print(f"threshold f >= {THRESHOLD} (tick label >= {THRESHOLD*DEFAULT_TICK_PT:.0f} pt from "
          f"matplotlib's {DEFAULT_TICK_PT:.0f} pt default); slide text block "
          f"{LW:.1f} x {TH:.1f} pt\n")
    print(f"{'figure':30s} {'px':>10s} {'dpi':>4s} {'native':>7s} {'spec':>11s} {'rend':>6s} "
          f"{'f':>5s} {'tick':>5s}  verdict")
    bad = 0
    for t, name, w, h, dpi, nat, spec, col, rend, f in sorted(data, key=lambda r: r[-1]):
        ok = f >= THRESHOLD
        bad += 0 if ok else 1
        print(f"{name:30s} {f'{w}x{h}':>10s} {dpi:>4d} {nat:7.1f} {spec:>11s} {rend:6.1f} "
              f"{f:5.2f} {f*DEFAULT_TICK_PT:5.1f}  {'ok' if ok else 'BELOW'}"
              f"{' (in column)' if col else ''}")
    print(f"\n[figures] {len(data)} figures, {bad} below the threshold")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
