#!/usr/bin/env python3
"""check_frames.py -- did any Beamer frame silently lose content?

    python3 reports/ecoli_deck/check_frames.py

Beamer CLIPS an overfull frame and LaTeX does not emit an Overfull warning for it, so a slide can
quietly drop its last bullets and a clean render log proves nothing. This happened twice while the
deck was being written -- the two lever tables filled their frames and the sentences after them
vanished -- and it is invisible unless each frame's tail is checked against its rendered page.

For every frame, the last substantive source line is reduced to its distinctive WORDS and those
are looked for on the page carrying that frame's title. Word overlap rather than a contiguous
substring, because `pdftotext` breaks lines mid-phrase and a numeric CSL leaves superscript digits
glued to the preceding word ("space\u201d2", "MRes3 :"), which defeats substring matching and
produced seven false positives on the first attempt. A frame passes if at least 90 % of the tail's
words are on its page. Exit 1 if any frame fails.
"""
import io
import re
import subprocess
import sys

PDF = "_output/deck.pdf"


def norm(t):
    """Letters and spaces only.

    A numeric CSL glues the reference number to the preceding word in the extracted text
    ("space\u201d2"), and pdftotext keeps the typographic quotes, so anything short of
    letters-only comparison reports phantom clips."""
    t = re.sub(r"\[?@[A-Za-z0-9]+;?\s*\]?", " ", t)          # citation keys -> nothing
    t = re.sub(r"[^A-Za-z\s]", " ", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def lint_source(src):
    """A heading with no blank line before it is not a heading: pandoc folds it into the
    preceding paragraph and Beamer merges the two frames. It has happened twice."""
    bad = []
    ls = src.split("\n")
    for i, l in enumerate(ls):
        if l.startswith("## ") and i and ls[i - 1].strip():
            bad.append((i + 1, l[:48]))
    for n, t in bad:
        print(f"  NO BLANK LINE before heading at line {n}: {t}")
    return len(bad)


def main():
    src = io.open("deck.qmd", encoding="utf-8").read()
    bad = lint_source(src)
    frames = re.split(r"\n## ", src.split("---\n", 2)[2])[1:]
    n = int(subprocess.run(["pdfinfo", PDF], capture_output=True, text=True)
            .stdout.split("Pages:")[1].split()[0])
    pages = [subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), PDF, "-"],
                            capture_output=True, text=True).stdout for p in range(1, n + 1)]
    for f in frames:
        title = f.split("\n", 1)[0].strip()
        if title.startswith("References"):
            continue
        lines = [l for l in f.split("\n")[1:]
                 if l.strip() and not l.strip().startswith((":::", "|", "---", "#"))]
        if not lines:
            continue
        # a figure line counts: a frame whose image fills it drops its CAPTION silently, which
        # is how the scan slide lost the sentence that told the reader what to look at
        if lines[-1].strip().startswith("!["):
            lines[-1] = re.sub(r"^!\[|\]\(.*$", "", lines[-1].strip())
        words = [w for w in norm(lines[-1]).split() if len(w) > 3][-12:]
        page = next((q for q in pages if norm(title)[:38] in norm(q)), None)
        if page is None:
            print(f"  ?? title on no page: {title[:52]}")
            bad += 1
            continue
        if not words:
            continue
        have = norm(page)
        hit = sum(1 for w in words if w in have)
        if hit < 0.9 * len(words):
            print(f"  CLIPPED {title[:44]:46s} {hit}/{len(words)} tail words on page: "
                  f"{' '.join(words)}")
            bad += 1
    print(f"[frames] {len(frames)} frames, {n} pages, {bad} with content missing from their page")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
