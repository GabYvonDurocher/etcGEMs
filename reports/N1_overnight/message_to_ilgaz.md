# Draft message to Ilgaz

_Plain text, pasteable. Findings from porting good work, not a list of faults._

---

Hi Ilgaz,

We've finished porting the four Candida species into the etcGEMs framework — they're now
`strains/` entries running on the shared core, and the port reproduces your numbers exactly:
79 of 79 comparisons pass, the fitted sigma/w/P to every digit in `etcgem_calib.json`, and
all 48 predicted growth rates identical at the 4 decimals you round to. That includes the
required Tm and Topt separations from `19_etcgem_counterfactual.py` (32.44 and 32.64 °C, and
15.76 / 14.94 / 15.62) and the pool-binding pair from `16_pool_binding_test.py` (2.045 and
0.758 /h). The check is a script that exits non-zero if it ever stops holding, and it now
runs off a committed fixture so it doesn't need your repository present.

Porting something carefully turns up things that only show up when you run it a second way.
Four of those are below. The first one is the one I'd act on soonest.

**1. `15_run_seq2tm.py` truncates sequences at 1022 aa, and the committed predictions
aren't truncated.**

The script caps every sequence at 1022 residues, with the comment that this is "the ESM2
positional limit, less BOS/EOS". ESM-2 uses rotary position embeddings, so it has no such
limit — and `tables/thermal_tm.csv` was clearly produced without the cap. The effect is that
the script as it stands does not reproduce the table sitting next to it.

I found this trying to verify I was running your predictor and not a lookalike. Taking the
first 200 rows of `thermal_tm.csv` in file order and re-predicting them at batch 4:

* the 156 sequences in batches with no member over 1022 aa came back **exactly** — max
  difference 1.8e-5 °C, r = 1.000000000;
* every batch that contained a truncated member was wrong, by **up to 2.6 °C**.

With the cap removed, all 200 reproduce (1.8e-5 °C). Same for Seq2Topt against
`thermal_topt.csv` (1.1e-4 °C). So the fix is one line, and the committed tables are fine —
it's the script that's out of step with them, which matters because it's the one anyone would
reach for to reproduce or extend them. About 2% of a typical proteome is over 1022 aa, and
because of the batch-4 padding it affects the neighbours too, not just the long protein.

**2. `ATP_Maintenance__cyto` is reversible in iDC1003, and 18 doesn't correct it.**

You found this yourself — it's in the `setup_pool` comment in `19_etcgem_counterfactual.py`
and it's applied there and in `22_thermal_sensitivity.py`. It just never reached
`18_build_etcgem_tpc.py`, which is where the locked mu table comes from. So the published
per-temperature predictions for *C. parapsilosis* have it paying no maintenance and
collecting 3.9 mmol ATP/gDW/h from ADP + Pi.

We can now quantify what that does, because we can run both:

* uncorrected: peak 0.786 /h at 34 °C, thermal limit 55.18 °C, fit R² **−0.323**, and — as
  your comment says — unreachable by any uniform Tm shift;
* corrected: peak 0.683 /h at 36 °C, limit 53.33 °C, fit R² **+0.042**, reachable at 32.64 °C.

Nothing else moves: with the solver held constant, the other three species are identical to
0.000000 /h, and the fitted globals don't move at all (the fit is on *C. auris*). The
corrected limits are 52.72 / 53.33 / 53.56 / 54.53, i.e. exactly the 52.7–54.5 °C range in
`FIG4_LOCKED.md` — so the locked range is the corrected one, and the locked mu table is the
uncorrected one. We've made the correction the default and kept the uncorrected run as a
labelled sensitivity so both stay reproducible.

**3. The 0.52 °C in circulation is the pre-deduplication number.**

`FIG4_LOCKED.md` and the Fig 4 caption both treat 0.411 °C (n = 432 unique protein pairs) as
the right one, and deduplication is the first of the caption's "three decisions that are easy
to undo by accident". But 0.52 (0.518, n = 1041, reaction-level) is what's quoted in the
discussion notes and in downstream prompts. Worth pinning down which travels, because the
fold-gap headline is computed from it.

For what it's worth, measuring it proteome-wide rather than over model enzymes — same
predictor, same batch protocol, RBH orthologs across the whole proteome — gives 0.151 °C for
*auris* − *haemulonii*. Not a correction to your number; a different quantity, over a
different set.

**4. One thing that isn't your code: Seq2Tm may not resolve within-proteome variation.**

We scored it against the measured *S. cerevisiae* meltome (Meltome Atlas, 1949 proteins with
a melting point). Within that one proteome the correlation with measurement is **r = −0.05**.
Before reading anything into that we ran the same predictor through the same code on a random
1500-protein sample of the whole Atlas, across species: **r = +0.76**. So the pipeline is
fine and the predictor works — it resolves thermophily *between* organisms and not variation
*within* a proteome, and the Candida comparison is entirely the second kind. Where a predicted
congeneric ΔTm can be checked against a measured one (*S. cerevisiae* vs *S. uvarum*, measured
1.6 °C), it understates it 17-fold.

We also ran the same-species control that hadn't been run: between *C. auris* clades that are
99.3–100% identical, the predictor returns ΔTm of up to 0.078 °C, five of six significantly
non-zero, where the truth is zero.

None of that says the conclusion is wrong. Correcting the arithmetic for both this and for
what the model requires under our thermal form (13.8 °C rather than 33), the fold gap goes
from ~79× to about 5×. Still a failure — but a differently sized one, and one that rests on a
measurement rather than on the predictor's self-report.

**Two questions, both faster asked than reconstructed:**

* **`common_network.py`** — you ran the identical-scaffold control, but the result isn't in
  `notes/` anywhere we can find. Did the optima still compress on a common scaffold? It
  matters for whether reconstruction depth (662–997 metabolic genes across the four) was
  confounding the comparison.
* **Lipids / membrane** — did any of the 25 audits touch lipid or membrane pathways?
  `allocation_and_trehalose.py` suggests compatible solutes were looked at. We ask because
  it's the one axis neither model can currently express, and Li's own paper and our *E. coli*
  work both land on a lipid-synthesis enzyme as the top control enzyme, which is suggestive
  and nothing more.

Everything above is written up with the commands to reproduce it:
`reports/candida_thermal_limit/K1_port_verification.md` (the port and the gate),
`K2_core_thermal_form.md` (what moved when we switched to our thermal form, one component at
a time), and `reports/predictor_calibration/report.md` (the predictor scoring). Happy to walk
through any of it.

Best,
Gab
