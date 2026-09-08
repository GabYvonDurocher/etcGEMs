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
