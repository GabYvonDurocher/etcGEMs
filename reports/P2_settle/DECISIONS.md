# P2 — decisions

Every judgement call, with what it changed and why. Standing rules: `$CANDIDAS_ROOT` and
`$PARSA_ROOT` are READ ONLY; decide and proceed when reversible or precedented; stop and record
when a choice would change a committed number, need a scientific judgement, or write inside
either read-only tree. **TASKS 1 and 2 are PROVISIONAL pending Parsa's confirmation** and are
marked as such wherever they set a value.

---

## D0 — N3 (PR #3) is still open, so P2 branches from a `main` that does not contain it

**Where:** TASK 0, and it constrains TASKS 4 and 5.

P2 follows P1, and P1 branched from `main` before N3 was merged. PR #3 (`n3/output-audit`) is
still **open**, so none of N3's work is on `main`: not `reports/N3_output_audit/`, not the
`README.md` additions, and not the one caveat sentence N3 added to
`reports/ecoli_tpc/report.qmd`.

This matters twice. TASK 4 is told to use N3's audit table rather than recompute it, and TASK 5
asks for a sentence in `reports/ecoli_tpc/` that N3 has already written a close relative of.

**Decided:** branch P2 from `main` after the P1 merge, as instructed, and

* read N3's audit table out of the branch (`git show n3/output-audit:reports/N3_output_audit/...`)
  rather than recomputing it — the table is the artefact, not the file's location;
* write TASK 5's third annotation as the **general rule** (T_opt is quoted with its binding
  constraint named; CT_max may be quoted plainly), which is what N3's sentence does not say, so
  the two compose rather than duplicate;
* flag here, for whoever merges: **PR #3 and this branch both touch
  `reports/ecoli_tpc/report.qmd`, in the same bullet.** N3's sentence is the measurement
  ("at this operating point the cap has slack ... at the nominal point it binds"); P2's is the
  rule that follows from three such findings. Keep both, N3's first.

## D1 — TASK 1: the transporter turnover is 300 s⁻¹, settled by experiment (PROVISIONAL)

**Where:** TASK 1.

His sources disagreed: `gasflux.py` sets `TRANSPORT_KCAT = 30.0`; his configuration-A figure,
its CSV filename `mmrt_transport_kcat300.csv` and his report all say 300. Both were run against
his committed output, on the same criterion the P1 gate uses
(`reports/P2_settle/task1_kcat.py`):

| k_cat | T_opt exact in all four media | worst optimum-quantity relative difference | worst curve \|Δgrowth\|/r_max | verdict |
|---|---|---|---|---|
| **300 s⁻¹** | **yes** | **7.4 × 10⁻⁴** | **6.0 × 10⁻⁴** | **reproduces his figure** |
| 30 s⁻¹ | no — 0.5 °C out in NLDM, LB and BHI | 6.8 × 10¹ (r_max 5.5–5.8 % low) | 1.4 × 10⁻¹ | does not |

So 30 was a stale module default his runs overrode.

**Decided:** set `gas_exchange.transport_carrier.kcat_s: 300.0` in
`strains/eciML1515/gas_exchange.yaml` — **strain data, not core code** — with the discrepancy,
the test and the outcome recorded in the comment, and remove the now-redundant override from
`gasflux_configA.yaml` so there is one source of truth. **Provisional**: this says which value
his committed figure was made with, which is not the same as which value he intends.

**One committed output changed and it carries no numbers:** `gasflux_configA/resolved_config.yaml`
loses the line `kcat_s: 300.0` from the overlay block, because the value now arrives from the
strain instead. `gasflux.csv` and `summary.csv` are **byte-identical**.

## D2 — TASK 2: recipe ceilings are canonical; the residual is reported, not stopped on (PROVISIONAL)

**Where:** TASK 2.

The task says to stop and report if a residual remains after the medium is accounted for. For
configuration B — the run in which the 1.2 % was observed — **there is none**: with his blanket
medium the port reproduces his r_max to 2 × 10⁻¹⁵ and every other optimum quantity to the same
order. The medium explains all of it.

A ≤ 5.9 × 10⁻⁴ residual does remain in configurations A and C. I did **not** stop on it,
because it is not a residual of this task and it is not unexplained: P1 isolated it, demonstrated
that his own code at his own fork point reproduces the port exactly (so nothing in this
repository can be responsible), and showed that it tracks *when he ran things* rather than what
any code says. It is four orders of magnitude below his quoted precision. Stopping would have
discarded the task over a difference already attributed in the preceding one.

**Decided:** recipe ceilings are the baseline; `NLDM_blanket` stays as an explicitly labelled
sensitivity, and the gas-flux README says which to quote. **Provisional** pending Parsa: the
clearance (5.0 L gDW⁻¹ h⁻¹) is his choice and is not re-examined here.

**Reported, not adjudicated:** on the canonical medium configuration C's NLDM RQ is 1.04, not
the ≈ 7–9 his report quotes. The high RQ was the blanket medium's unlimited carbon, not the
absent carbon cap — which is a change to what that configuration demonstrates, and his call.

## D3 — TASK 3: c_max is reported on, not changed

**Where:** TASK 3.

The search of `$PARSA_ROOT` found **no literature citation for any `c_max`**, and found his own
report saying the cap is "a boundary condition (a sweep), not a fitted likelihood" and his own
sweep recommending **100–120** while describing 60 as a "flat plateau". 60 appears only as the
representative run in his later configuration summary. In configuration D the cap is a *fitted*
multiplier of 230, which is a different construction under the same name.

I did not change `c_max`, did not conclude whether it is fitted, and did not touch the
configuration-B overlay, exactly as the task requires — even though the sensitivity shows 60
sits past the steepest part of the slope (NLDM T_opt −6.5 °C and E_a +30 % between c_max 80 and
60) and that at 60 acetate overflow is entirely suppressed. Those are reported in
`TASK3_cmax.md` for Parsa to act on.

One dead end recorded so it is not re-trodden: his `configD_capfit` "best-match cap", re-derived
from his own committed sweep, is **c_max = 30**, where model acetate and Basan's line are both
zero — the minimiser matching 0 to 0 at the bottom of the range. It is not evidence for any
value.

## D4 — TASK 4: statuses are recorded with evidence, not inferred; one report is left UNKNOWN

**Where:** TASK 4.

The stamp could have guessed CURRENT / HISTORICAL from commit dates — inputs older than the
last model-changing commit → HISTORICAL. That would be wrong in both directions: N3 found an
input written *after* every model change that still reproduces (`control_tuned`) and inputs
written before one that are unaffected by it (`proteome_sectors/sector_fractions_vs_T.csv`, a
pure function of the proteomics file).

**Decided:** the generator computes only git facts; the STATUS comes from
`reports/report_status.yaml`, where each entry carries the evidence that established it, and a
report with no entry is stamped **UNKNOWN**. `activation_energy` is stamped UNKNOWN and stays
that way: it has not been audited, its inputs span 2026-07-10 to 2026-09-07, and settling it
means re-running the E_a dissections. Claiming CURRENT for it because it *looks* recent is
exactly the failure the stamp exists to prevent.

Where an audit established a report's real input list, that list is authoritative and lives in
the YAML: the scan reads paths out of a report's own files, which misses everything
`reports/ecoli_tpc/assemble.py` builds by string join (all eleven of its directories) and picks
up directories merely named in prose. N3's list is used rather than recomputed, as the task
asked.

## D5 — TASK 5: placement, and the one sentence deliberately written to compose with N3's

**Where:** TASK 5.

Each annotation went where its *cause* is, not where the finding was made: the two-model-states
note immediately before the dissection's conclusion; the 37–44 °C shoulder in the passage that
presents the measured sector allocation, because the measurement's temperature range is what
produces it; the regime sentence appended to the T_opt clause in "Interpretation and caveats".

The third is written as the **general rule** (three constraints move T_opt; CT_max is
insensitive to all three; quote T_opt with its binding constraint named) precisely because N3's
open PR adds the **measurement** to the same bullet. The two say different things and compose;
the merge conflict is flagged in D0 with the resolution, rather than left to be discovered.
