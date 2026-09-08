# P1 — decisions

Every judgement call, with what it changed and why. Standing rules: `$PARSA_ROOT` and
`$CANDIDAS_ROOT` are READ ONLY; mechanisms belong in `src/etcgem`, E. coli specifics in
`strains/eciML1515/`; everything opt-in and off by default; no strain's committed behaviour
may change; no emcee.

---

## D0 — the fork point is a 25-hour window, and one of the prompt's premises is wrong

**Where:** PART A.

The prompt gives the fork point as `e67b4c0`, 9 July 21:00. That is the *earliest* commit
consistent with his content, not the only one: his `src/etcgem` is byte-identical to `main` at
eleven consecutive commits, `e67b4c0` (2026-07-09 21:00:51) through `8c2c30f` (2026-07-10
21:55:56), diverging at `99eab16` (21:58:06). Reported as a window rather than a point.

More consequential: the prompt says his baseline "predates `a416fd1`". **It does not** —
`a416fd1` is 2 July, a week before, and his `strain.yaml` and every strain input file are
byte-identical to ours. `a416fd1` is therefore removed from the gate's list of admissible
attributions before any number is compared; using it would have let a real movement be
explained away.

**Decided:** report the window and the correction; attribute movements only to `8085036`, to
where in the build his O2 closure happens, or to commits after 10 July.

## D1 — nothing at all is imported from his outputs tree

**Where:** PART G, settled early because it changes what PART C has to do.

PART G allows importing "small text tables needed as INPUT". There are none: every input file
his configurations use is already in this repository and byte-identical (all of
`strains/eciML1515/{dltkcat,media,model,proteomics,thermal}`). The Basan reference is two
constants in a docstring (s_ac 21, λ_ac 0.76), not a table, and the NLDM recipe is a literal
dict in one of his scripts, not a file.

**Decided:** import nothing. The NLDM recipe is transcribed into a new
`strains/eciML1515/media/NLDM_media.csv` **from his source code**, with the citation he gives
(de Raad et al. 2022) recorded in the header — that is transcription of a recipe, not import of
an output.

## D2 — the R2A / respiration data is absent, so D/E/F cannot be gated at all

**Where:** PART A, and it bounds PART E.

`calibration_configD.py` and eight scripts read
`C:\Users\Parsa\Desktop\Presense_Analysis\Ecoli_R2A_LB\tables\derived_N0_R_results_with_carbon.csv`.
No such file exists anywhere in the 1.0 GB snapshot. So the growth and respiration R² values
his report quotes for configurations D, E and F are unreproducible here for want of data,
before the no-emcee rule is even reached.

**Decided:** state it plainly in the gate as a data gap rather than a cost estimate, and ask
for the file rather than inventing a substitute. The mechanisms those configurations use are
still ported and still testable forward — what cannot be checked is the *fit quality*.
