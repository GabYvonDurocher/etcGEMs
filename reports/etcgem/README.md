# etcGEM report (Quarto → PDF/docx)

A Quarto report that **embeds pre-generated pipeline outputs** (figures + CSV/JSON
tables) and renders to PDF and docx for sharing with collaborators. It does **not**
re-run the pipeline or any scientific code — rendering is fast because every figure
is a static PNG and every table just reads a CSV.

## Layout

```
reports/etcgem/
  _quarto.yml            project: formats pdf+docx, output-dir _output
  header.tex             LaTeX preamble (line numbers, caption styling, title block)
  references.bib         method references
  nature-communications.csl
  assemble.py            copies run outputs -> assets/ (stable names) + derived figs
  report.qmd             main report (sections 1–9)
  supplementary.qmd      full sensitivity / control / identifiability tables + config
  assets/figures/        populated by assemble.py (git-tracked)
  assets/tables/         populated by assemble.py (git-tracked)
  _output/               rendered report.pdf / report.docx (git-ignored)
```

## Prerequisites

- **Quarto CLI** (`quarto --version`).
- **LaTeX**: either a system TeX (with `xelatex`/`pdflatex`) or
  `quarto install tinytex`.
- In the project venv: `pip install jupyter ipykernel pandas tabulate`
  (`great_tables` is an optional upgrade for prettier tables).

## Workflow

1. Run the pipeline so the outputs exist (build / sweep / decompose / control /
   dltkcat). The report reads these run dirs (see the top of `assemble.py`):

   | asset group | default source run dir |
   |-------------|------------------------|
   | sweep       | `strains/eciML1515/outputs/default` |
   | dltkcat     | `strains/eciML1515/outputs/dltkcat_ext` |
   | decompose   | `strains/eciML1515/outputs/decompose_decomposition_quick` |
   | control     | `strains/eciML1515/outputs/control_control_quick` |
   | calibrated  | `strains/eciML1515/outputs/sweep_calibrated` |
   | sectors     | `strains/eciML1515/outputs/sweep_sectors` |

   **Run the FULL experiments WITH plots** so the PNGs exist — the `*_quick`
   experiments run with `--no-plots` and emit no figures. For the M1.2 / sector
   sections:

   ```bash
   etcgem sweep --strain eciML1515 --experiment calibrated   # -> sweep_calibrated
   etcgem sweep --strain eciML1515 --experiment sectors      # -> sweep_sectors
   ```

   The `sectors` experiment activates the proteome sectors for that run only (via an
   experiment-level `proteome_sectors` override that merges onto the strain, which
   stays disabled at baseline). If you skip the sectors run, `assemble.py` warns and
   §8 simply renders with a missing figure — remove §8 if you want a clean omission.

2. Assemble the assets (copies figures/tables under stable names and generates the
   two derived figures):

   ```bash
   python reports/etcgem/assemble.py
   ```

3. Render:

   ```bash
   cd reports/etcgem
   quarto render                    # report + supplementary, pdf + docx
   # or just the PDF of the main report:
   quarto render report.qmd --to pdf
   ```

   Output lands in `reports/etcgem/_output/` (`report.pdf`, `report.docx`,
   `supplementary.pdf`, `supplementary.docx`).

## Notes

- **Editing sources**: change the run dirs at the top of `assemble.py` to point at
  whichever runs you produced. Prose in `report.qmd` is intentionally short
  placeholder text for the author to expand; figures and tables are wired to real
  assets so it renders immediately.
- Only `_output/` is git-ignored; the `.qmd`, `header.tex`, `references.bib`, CSL,
  `assemble.py` and the copied `assets/` are tracked.
