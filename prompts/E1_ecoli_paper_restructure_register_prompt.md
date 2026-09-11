# Claude Code prompt — E1: what the E. coli paper claims, what has changed, and what is missing from it (autonomous, ~1 h, no solves)

**Run from `../etcGEMs-work`, NOT from the primary checkout.** P15 is running two nested fits in
`etcGEMs` and owns it until tomorrow evening. `etcGEMs-work` is a detached checkout of `main`; make
a branch there. Use `../etcGEMs-venv`. **This is assembly and reading — no solves, no fits, no
figures regenerated.** It must not compete with P15 for cores.

**Why now.** `reports/ecoli_tpc/report.qmd` is the E. coli paper. It was written before the
gas-flux work and before this week, and it now states things the evidence contradicts. There is a
group meeting tomorrow morning. **The deliverable is a register and a short brief, not a
re-render** — P15's posterior lands Saturday and rendering twice wastes the work.

**Two distinct jobs, and the second is the bigger one.**

1. **Corrections.** Specific sentences and tables are now wrong or unsupported.
2. **A gap the paper itself declares.** Gas flux appears in `report.qmd` only three times: the
   uncosted-O₂-sink curation step, a limitations line saying gas flux and carbon-use efficiency
   "are future work", and an acknowledgement thanking Parsa for finding the four sinks. Meanwhile
   `reports/ecoli_gasflux/` holds fourteen committed figures and a 118-line README with no
   write-up. The limitation has been closed and never folded back in.

**Why the gap matters more than the corrections.** The calibration section admits its own weakness:
*"`kappa_scale`/`ngam_*`/`topt_scale`/`dCp_scale`/`tm_scale` stay near their priors — one curve
weakly constrains them."* Thirteen global levers against one digitised growth curve. The gas-flux
work is three media, a temperature series and two flux types with measured respirometry behind it.
That is the answer to the identifiability problem the paper names and leaves open — and it is
exactly the data Pettersen & Almaas 2023 (`refs/PettersenAlmaas_2023.pdf`) say the field lacks.

NOTE TO USER: launch in an auto-approving mode. Reading and writing only.

REFERENCE, read first: `reports/ecoli_tpc/report.qmd` and `supplementary.qmd` in full;
`reports/ecoli_gasflux/README.md` and its `assets/figures/`; `reports/synthesis/evidence.csv` and
its README correction note; `docs/OPEN_ITEMS.md` §0 and items 1.9, 1.12, 1.17, 1.19–1.23;
`reports/P9_surface/`, `P10_respiration_likelihood/`, `P11_nested/`, `P12_modes/`,
`P13_support/`, `P14_posterior/`, `Y1_yeast_audit/`, `Y2_regime_posterior/`, `Y3_tm_shift/`.

---

```
Work AUTONOMOUSLY; commit in parts, prefixed "E1: "; maintain reports/E1_paper_register/
DECISIONS.md FROM THE FIRST JUDGEMENT CALL. Standing rules carry over. Check exit codes explicitly,
never `cmd && check`. In ../etcGEMs-work: branch `e1/paper-register` from the detached main; do not
push to main; end in a PR that is NOT merged. Write NOTHING under ../etcGEMs and do not disturb
P15. Do NOT edit report.qmd itself - this run produces a register, not a revision.

TASK 0 - premise
- Confirm the worktree, the branch, the interpreter. Confirm P15 is running in the primary tree and
  that you write nothing there.
- Read OPEN_ITEMS 0a-0c. State in D0 which of R1-R4 this touches (expected: none - it is a record
  of state, not a measurement) and that its job is reconciliation.

TASK 1 - the correction register, sentence by sentence
Produce `reports/E1_paper_register/corrections.csv`: one row per affected claim, with columns
  section | quoted text (short) | what is wrong | evidence (report + evidence.csv row) | status
where status is one of SUPERSEDED (a new number exists), UNSUPPORTED (the claim cannot be made at
all), INVERTED (the interpretation is backwards), or PENDING-P15 (needs the posterior).
Cover at minimum, verifying each against the file rather than this list:
- **`tbl-corrections` and every 90 % CI in the calibration section.** They come from the "P2 v3
  posterior". P8, P11 and P12 established that intervals from this family's emcee chains are not
  available. Mark UNSUPPORTED, not SUPERSEDED - PENDING-P15 for the ones P15 will supply.
- **The likelihood has changed underneath the posterior.** That fit predates the pFBA tie-break
  (P10), the 1.42 respiration floor (P11) and the clamp support form (P13). It is not the current
  model's posterior. Say so once, prominently.
- **The sector claim is INVERTED.** The paper reads f_metab = 0.281 and f_maint = 0.341 sitting at
  their measured priors as confirmation that "the proteome is not free-fit". P11 classified both
  FLAT; P12 found them pinned at 0.28000 and ~0.35 from every starting point of twelve independent
  optimisations. They do not move because the likelihood is flat in them. That converts a
  supporting argument into a limitation - and P14 established the correct reading: a flat marginal
  is unidentifiability given this data (R2), not a sampling failure.
- **dTm.** The paper says the data "demanded a melting-temperature shift and essentially nothing
  else... The hot collapse is set by T_m", at -5.6 K [-7.2, -2.8]. Y3 shows dTm is NOT load-bearing:
  with the compensating parameters free the profile is flat and dTm = 0 costs 0.077 units with the
  model still growing at 1.739 /h; the compensation runs through `tm_scale`, a stability parameter,
  not catalysis. What survives reparameterisation is a per-enzyme statement - every solution puts
  the least-stable few per cent of enzymes 4-6 C below the measured meltome. The section needs
  rewriting around the tail requirement, not the global value.
- **sigma.** The paper flags 0.867 against a literature ~0.45 as "a tight-budget frontier". P11 put
  it at 0.845, P12's best endpoints at 0.94-0.96. Report the trend.
- **The knife-edge attractor.** P13 found four of twelve independent optimisations park a
  temperature on the death threshold `_MASK_G` exactly (p38's 15 C growth 1.4e-12 below it) to
  escape a ~2.8-unit respiration penalty, and that the current likelihood is state-dependent there
  (|delta| = 0.0157 at p38). So the paper's posterior was computed on a likelihood that rewards a
  specific pathology. This is a named reason the point estimates could move, not only the
  intervals.
- **The R4 correction, which is the PI's own and should be recorded as such.** OPEN_ITEMS 0a R4
  says "nothing has ever been tested against data it was not fit to". That is wrong: the Validation
  section tests the EMERGENT model against Van Derlinden a priori, tracking shape and
  under-predicting the peak ~2.3-fold. The accurate statement is narrower - the emergent model has
  an out-of-sample test; the CALIBRATED model has none, because it was then fitted to that same
  curve. Fix R4 in OPEN_ITEMS to say exactly that.

TASK 2 - what the gas-flux work adds, and what it can claim today
- Read `reports/ecoli_gasflux/README.md` and inventory its fourteen figures by path and content.
- Produce `reports/E1_paper_register/gasflux_inventory.csv`: one row per result, with what it
  shows, its evidence source, and **whether it depends on a converged posterior**. Separate
  clearly:
    * **Stands today, no posterior needed**: the P3 gate (10 of 10 R2 reproduced, worst 0.009 - a
      port-fidelity check against Parsa's computation); overflow emerging from a total-carbon cap
      rather than being imposed (configuration D); the medium-dependence of c_max (60/120/450) and
      that applying 120 to LB collapses growth R2 from 0.83-0.90 to 0.16-0.20; R2 at fixed
      parameter points.
    * **Needs the posterior**: every interval; any configuration comparison quoted as a
      difference; E and F respiration R2 (P10: the old numbers were one arbitrary point of an LP
      face).
    * **Held or blocked**: E and F fits (LP face, D3a); F LB specifically (no exact tie-break at
      1e-9, P10 D1); the remaining eight fits (1.17, blocked behind 1.19).
- Carry 1.9's caveat wherever per-cell rates appear: N0 and fg-C-per-cell are typed constants ~6x
  from his own config log, so growth R2 and scale-free quantities are immune and absolute per-cell
  rates are not.

TASK 3 - the restructure proposal, as options for the PI, not a decision
The paper's shape changes if gas flux enters. Lay out, do not choose:
- **What the two data types together let the paper claim that neither does alone.** The natural
  experiment: does adding O2 and acetate constrain the levers one growth curve left at their
  priors? P11's line-scan classification (GRADIENT-DETERMINED / WALL-BOUNDED / FLAT) is the
  instrument. State the clean version explicitly - two fits on the SAME medium, growth-only then
  growth+flux, comparing classifications and width ratios - and note that the existing fits do not
  constitute it (the paper's calibration is BHI/Van Derlinden with 13 levers; the gas-flux fits are
  NLDM/LB/M9 with 16). Cost it at P15's measured rate as a queue item.
- **Two framings**, with what each requires and what each risks:
    (a) "A calibrated etcGEM of E. coli", with claims hedged to what the evidence supports.
    (b) "What it takes to calibrate one, and what can and cannot be concluded" - which the week's
        work supports more strongly, and for which Pettersen & Almaas 2023 is directly relevant
        prior art that the paper does not currently cite.
  Give the evidence for and against each and the strongest referee objection to each. **Do not
  recommend one.** Mark the section FOR PI JUDGEMENT.
- List which sections of report.qmd would move, be added, or be cut under each framing. Section
  names and one line each; no drafting.

TASK 4 - the brief, which is what gets talked from tomorrow
`reports/E1_paper_register/brief.md`, **two pages maximum**, plain prose, no tables of numbers
beyond what a reader can hold:
- What the E. coli model is and what it now does.
- What this week established, in the order a listener needs it: the surface was cliffed, not
  under-sampled; the cliffs were the respiration term on LP vertices; the fixes (tie-break, floor,
  clamp) and what each was for; the mode question settled to one live basin; where the posterior
  stands as of tomorrow morning (P15 run 1 due ~08:00, run 2 through the day - state it as
  in-flight, quote nothing from it).
- What is genuinely novel and defensible today, separating the E. coli modelling from the two
  audits of the published yeast model (Y1: the coupling-ion defect is absent there and the GECKO
  split makes it structurally impossible; Y2: the T_opt/CT_max asymmetry reproduces at their
  posterior with an interval, and CT_max is NOT insensitive there as it was in ours).
- The honest tension in one paragraph: the most novel material (gas flux) is the least
  statistically settled, and why that affects intervals rather than mechanism.
- Three things the group could usefully argue about. Questions, not conclusions.

TASK 5 - record
- docs/OPEN_ITEMS.md: fix R4 per TASK 1; add an item for the growth-only vs growth+flux comparison
  with its cost; add an item for citing Pettersen & Almaas in the paper.
- reports/synthesis/evidence.csv: rows for anything TASK 1 or 2 establishes that is not already
  there. No re-render.
- Reconcile against 0c in the register's closing section.
- Stamps.

VERIFY (report all)
1. TASK 0: worktree, branch, interpreter, P15 untouched.
2. TASK 1: corrections.csv row count by status; every row quoted against report.qmd with a line
   number; the R4 correction made in OPEN_ITEMS.
3. TASK 2: gasflux_inventory.csv, split three ways by posterior-dependence, with counts.
4. TASK 3: the two framings with evidence for and against and the referee objection to each;
   confirmation that no recommendation was made; the clean-experiment specification and its cost.
5. TASK 4: brief.md, its length, and confirmation it quotes nothing from P15.
6. `git diff main --stat` in ../etcGEMs-work: reports/E1_paper_register/, OPEN_ITEMS,
   evidence.csv, stamps. **report.qmd NOT edited.** Nothing under ../etcGEMs written.

CONSTRAINTS
- A register and a brief. report.qmd is not edited and nothing is re-rendered.
- No solves, no fits, no figures regenerated. Do not compete with P15 for cores.
- Every correction is quoted against the file with a line number, not paraphrased from memory.
- TASK 3 lays out framings; it does not choose. FOR PI JUDGEMENT.
- Nothing from P15 is quoted; it is in flight.
- Autonomous; commit in parts: "E1: corrections", "E1: gasflux inventory", "E1: restructure
  options", "E1: brief", "E1: record".
```
