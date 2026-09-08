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

## D3 — the strain's gas-exchange data is a separate file, not a `strain.yaml` block

**Where:** PART C.

The prompt asks for the E. coli specifics "into `strains/eciML1515/`, referenced from
`strain.yaml`". Adding a `gas_exchange:` block to `strain.yaml` works and is what I did first —
and it changes `resolved_config.yaml` for **every** eciML1515 run, because `dump_resolved`
records the whole merged config. Measured: the numeric outputs stayed byte-identical and
`resolved_config.yaml` gained 21 lines. That breaks the prompt's own requirement that every
existing strain's committed outputs stay byte-identical.

**Decided:** the data lives in `strains/eciML1515/gas_exchange.yaml`, is loaded by
`config.apply_gasflux` **only when a run enables the layer**, and `strain.yaml` references it
in a comment (comments do not reach the resolved config). Gas-flux runs then record the block
in their own `resolved_config.yaml`, where it belongs. Verified afterwards: eciML1515,
mmaripaludis and syn6803 TPCs byte-identical, Candida gate 79/79.

## D4 — configuration D folds in as a spec builder, not a third calibrator

**Where:** PART B.

`calibration_multi.py` already carries three organism entry points (`run`, `run_syn6803`,
`run_methanogen`) over one `PSpec`/`to_pert`/`log_prior`/`init_walkers` core, and his
`calibration_configD.py` imports exactly those. So what configuration D actually adds is a
*parameter set*, not an algorithm: the same twelve levers, optionally widened envelope priors,
plus one dimension (`C_max_mult`) that turns the carbon cap from a swept boundary condition
into a fitted one.

**Decided:** add `build_overflow_specs()` and `WIDE_ENVELOPE_SPECS` beside
`build_vdl_specs()`, and `build_pm_medium()` as the medium-general form of `_build_pm_rich`.
Neither `calibration_configD.py` nor `calibration_configD_full.py` is carried across.

**What is NOT folded, and why that is not a fudge:** the likelihood. Its two terms are (1) a
growth TPC against the R2A measurements and (2) the overflow threshold against Basan's. Term
(2) is ported in full and generically, as `gasflux.overflow_threshold` (bisect the substrate
ceiling, return the growth rate where excretion switches on). Term (1) needs
`derived_N0_R_results_with_carbon.csv`, which is not in the snapshot (D2). Writing a
likelihood against data we do not have would be inventing a fixture, so the sampler entry
point is deliberately not written: what is in place is the spec set, the operating point and
the threshold term, so that adding one data file and one likelihood function completes it
**inside** `calibration_multi` and not beside it.

## D5 — his configuration-B NLDM numbers are not reproducible from his committed script, and I established why rather than tolerating it

**Where:** PART E, and it changed PART C.

Configuration B reproduces to ~1e-4 on glucose-minimal, LB and BHI, but NLDM was 1.2 % off in
r_max with T_opt 2 °C low, and his glucose uptake was 0 where the port's was up to 4.4. Three
tests, in order:

1. **Not the medium as coded.** Built the model both ways and diffed all 331 exchange upper
   bounds: **0 differ**. His `set_medium_nldm` and the port's `set_medium_recipe` agree exactly.
2. **Not the O2-sink closure ordering.** Rebuilt configuration B with the sinks closed AFTER
   `build_provider`, as he did (this does move `translation_coeff` 0.07867 -> 0.0775, so the
   two states really are different). Every number: **identical to the port**. Under the growth
   law the biosynthesis cap does not bind, so `translation_coeff` has no effect here.
3. **Not a commit on `main`.** Transcribed his own `build_pm` / `set_medium_nldm` /
   `block_free_o2_sinks` / `flux_tpc` into a self-contained replica and ran it in a worktree at
   **his fork point** (`8c2c30f`). Result: **identical to the port**, and equally 1.2 % away
   from his committed CSV. So no change in this repository explains it.

**What does:** the committed `gasflux_C60.csv` is dated **1 Sep 18:04** and the script that
supplies its `build_pm` is dated **4 Sep 09:52** — the file was edited after the run. His
`set_medium_nldm` carries a `recipe=False` path described as "the legacy blanket bound", and
running the port with that blanket medium reproduces his NLDM curve to **1.47e-4 absolute**,
r_max and T_opt exact. His CSV predates his own switch to recipe-proportional ceilings.

**Decided:** keep the recipe medium as the default (it is his later and better model) and add
`NLDM_blanket` to the strain's media as an explicitly-labelled legacy medium, so his numbers
can be reproduced exactly and the difference is a documented change of his rather than an
unexplained movement. `set_medium_recipe` gained `clearance: null` for the blanket mode.

## D6 — the proton-stoichiometry correction needed a model-level fallback, and without it it silently did half the job

**Where:** PART B, found by testing configuration F.

His `set_bdII_nonelectrogenic` takes the cytoplasmic proton from a *reference* reaction and
applies it to both bd-II reactions. My first generic version looked for the internal proton in
each reaction itself — and `CYTBDppNo1` does not have one: in the GECKO arm/isozyme split the
internal proton sits on the arm reaction while the translocated proton sits on the isozyme. So
one of the two bd-II reactions was silently left electrogenic.

**Decided:** `_proton` prefers a proton the reaction carries and otherwise falls back to the
model's proton in that compartment. Verified: both `CYTBDppNo1` and `CYTBD2ppNo1` now go
2 -> 0, and configuration F reproduces the qualitative prediction it exists to make — at 42 °C
growth collapses to 0.006 /h while O2 uptake stays at 34 mmol gDW^-1 h^-1, respiration
decoupled from growth.
