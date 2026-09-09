# Claude Code prompt — K4: carry the ETC membrane-area constraint to the Candida strains — does a physical membrane limit do what enzyme thermostability could not? (autonomous)

Run from the project root (`.../MICROADAPT/etcGEMs`). Runs IN PARALLEL with P4, which is refitting
E. coli. **P4 owns `strains/eciML1515/` and `reports/ecoli_gasflux/`; this prompt owns
`strains/c*/` and `reports/candida_*`.** Do not write outside your half, and expect the repository
to change beneath you in P4's half. Branch from `main` as it stands when you start, and say which
commit that was.

**Why this is possible now and was not before.** Every mechanism the Candida etcGEM could express
took its species-specificity from Seq2Tm/Seq2Topt, and A1 established that Seq2Tm has **no
per-protein validity within a proteome** (r = −0.048 against a measured *S. cerevisiae* meltome;
+0.762 across the tree of life). So every enzyme-thermal route is answered. P1 collapsed Parsa's
Configs E and F into ONE table-driven ETC mechanism in the core — a constraint on membrane real
estate, keyed on a per-strain table of complexes with area footprints, turnovers and
electrogenicity — and P3 gated it against measured E. coli respirometry (Config E respiration
R² 0.72, Config F 0.96). It is therefore a **validated mechanism being carried to a new organism**,
not a speculation.

It is also the first mechanism in either codebase whose species-specificity need not come from a
sequence predictor: membrane composition and ETC complement are measurable phenotypes that can
differ between organisms with near-identical proteomes.

**What this prompt is NOT.** It is not a claim that membranes explain the Candida thermal
divergence. It builds the capability, applies it, and reports what happens. Adjudicating mechanism
is explicitly out of scope — several previous runs in this series found the interesting result was
not the one the prompt anticipated.

REFERENCE, read first: `docs/CANDIDA_DISCUSSION_2026-09-07.md` (§3a, §4, §5, §6a — the membrane
axis and why it is the leading open candidate), `reports/predictor_calibration/report.md` (A1),
`reports/candida_thermal_limit/K2_core_thermal_form.md` (the 13.8 °C required separation, and the
ladder), the core ETC-area module P1 created, and `strains/eciML1515/`'s ETC complex table as the
worked example.

---

```
Work AUTONOMOUSLY; commit per task, prefixed "K4 TASK n: "; maintain reports/K4_membrane/DECISIONS.md.
Print a final summary with each task DONE / PARTIAL / STOPPED. Standing rules carry over. Check exit
codes explicitly. $CANDIDAS_ROOT is READ ONLY. Branch `k4/membrane-candida`; do not push to `main`;
end in a PR that is NOT merged. DO NOT WRITE TO `strains/eciML1515/` OR `reports/ecoli_*` — P4 is
running there.

TASK 1 - can the four Candida models express the mechanism at all?
This gates everything. Answer it before building anything.
- For each of the four Candida models, identify the ETC complexes present: NADH dehydrogenases,
  succinate dehydrogenase, the terminal oxidases, ATP synthase, and (importantly for a fungus) the
  alternative oxidase AOX.
- Report per species: which are in the model, which are in the proteome but not the model, and which
  are absent altogether. Use the reconstruction evidence tables and the proteomes.
- **A3 already found that AOX and the glutaredoxins are in NO Candida model.** Confirm or refute
  that here, because if the fungal ETC is largely unmodelled the mechanism cannot bind and that is
  the finding — report it and STOP rather than forcing a constraint onto reactions that are not
  there.
- State plainly whether a membrane-area constraint is expressible in these models. If it is only
  partly expressible, say which species and which complexes.

TASK 2 - the complex table, honestly sourced
- Build `strains/<name>/etc/complexes.csv` for each species that passed TASK 1, in the same format
  as E. coli's, with columns for reaction ID, area footprint, turnover and electrogenicity.
- SOURCING IS THE HARD PART AND MUST BE EXPLICIT. E. coli's footprints come from Szenk 2017. There
  is almost certainly no equivalent for these Candida species. For every value, record in the file
  header: measured for this species / measured for a related fungus / taken from E. coli / assumed.
  A table that is mostly "taken from E. coli" is a legitimate starting point and an illegitimate
  basis for a species comparison — say which you have built.
- **If the footprints cannot be differentiated between the four species, that is decisive for the
  comparison and must be stated in TASK 4 before any result is interpreted.** A constraint whose
  parameters are identical across species cannot explain a difference between them — the same trap
  that Seq2Tm's flat distributions set.
- Fungal mitochondrial inner membrane is not the E. coli inner membrane: cristae give a much larger
  area per cell volume. If you can find a defensible fungal value for available ETC area, use it and
  cite it; if not, treat A_ETC as the single free knob it is in Parsa's formulation and say so.

TASK 3 - apply it
- Run the four Candida strains with the ETC-area constraint on, under the core's `unfolding` thermal
  form and the corrected maintenance (the K2 configuration), sweeping A_ETC from non-binding to
  strongly binding.
- Report per species and per A_ETC: T_opt, CT_max, E_a, rmax, the predicted growth at 40 °C, and
  whether the constraint binds at each temperature.
- THE QUESTION K2 LEFT: the model requires ~13.8 °C of interspecies separation to push the relatives
  below detection at 40 °C, and sequence gives 0.4–0.5 °C. Ask the equivalent here: **what
  interspecies difference in A_ETC (or in the complex table) would be required?** Express it as a
  ratio and in whatever units are natural, and compare it against any measured variation in
  mitochondrial membrane area between fungi you can find.
- Report `sector_flatness.json` alongside, per N1's guard — a constraint that flattens the curve
  makes T_opt meaningless and that must be visible, not inferred.

TASK 4 - what this does and does not license
Write `reports/K4_membrane/report.md` with, in this order:
  1. Whether the mechanism is expressible in these models at all (TASK 1).
  2. What the complex tables are actually made of (TASK 2) — the sourcing table, prominently.
  3. What happens when it is applied (TASK 3).
  4. The required-difference calculation set beside K2's 13.8 °C enzyme-thermal requirement.
  5. A short, explicit section separating what this licenses from what it does not. If the tables
     are undifferentiated between species, the honest statement is that the mechanism has been made
     available and NOT yet tested as an explanation — say exactly that.
- Do not adjudicate mechanism. Report numbers and state what they support.
- Add one paragraph to `docs/CANDIDA_DISCUSSION_2026-09-07.md` §6(a) recording the outcome, dated,
  pointing at the report. Do not rewrite the section.

TASK 5 - what would make this a real test
The value of a negative or inconclusive result here is knowing what would settle it.
- List the specific measurements that would turn this from an available mechanism into a tested
  hypothesis: which quantity, on which species, by what method, and what result would distinguish
  the hypotheses.
- Be concrete about lipidomics versus membrane area versus ETC complement — they are different
  measurements answering different parts of the question.
- Add them to `docs/OPEN_ITEMS.md` §3 with triggers.

VERIFY (report all)
1. TASK 1: the ETC complement per species, in-model / in-proteome-only / absent; AOX specifically;
   whether the mechanism is expressible.
2. TASK 2: the complex tables, and the sourcing breakdown per value — measured / related / E. coli /
   assumed, with counts.
3. TASK 3: the sweep results per species; the required interspecies difference; the flatness metric.
4. TASK 4: the report, with the licensing section quoted in full.
5. TASK 5: the measurement list.
6. `git diff main --stat` — confirmation that nothing under `strains/eciML1515/` or `reports/ecoli_*`
   was touched, and that the Candida gate still passes 79/79 with $CANDIDAS_ROOT unset.

CONSTRAINTS
- TASK 1 is a gate. If the fungal ETC is not in the models, stop and report — do not force a
  constraint onto absent reactions.
- Sourcing is recorded per value. "Taken from E. coli" is acceptable and must be visible.
- Undifferentiated parameters cannot explain a difference. If that is where this lands, say so
  plainly and early — it is the same failure as Seq2Tm's overlapping distributions and it is better
  found by us than by a referee.
- Do not adjudicate mechanism anywhere.
- Do not write to P4's half of the repository.
- Autonomous; commit per task.
```
