# P16 — decisions, from the first judgement call

## D0 — what this run moves, and the near-degeneracy rule, written before the spectrum is computed

### R1–R4

**R1** is the target: a posterior two runs agree on. **R2 is clarified rather than moved** — this run
will *fix* a parameter, which converts one unidentified direction from a sampling pathology into a
**stated limitation**; that is honesty about R2, not progress on it. **R3** untouched: Y3 settled
that `dTm`'s value is a parameterisation artefact and that the surviving statement is a per-enzyme
**tail** requirement. **R4** untouched.

**Said before the run:** a posterior with a parameter **fixed** is *not* a posterior over the full
model. Whatever comes out carries that caveat in every summary.

### A disclosure that has to come first

The near-degeneracy rule is supposed to be written before its numbers are read. **It cannot be
fully blind, and pretending otherwise would be worse than saying so.** P15 already published, from
this same checkpoint:

- the **smallest three** eigenvalues — 1.947e-04, 6.305e-04, 7.880e-04;
- the **largest** — 2.835e-01;
- the condition number — 1,457;
- and `corr(dTm, tm_scale) = +0.831`.

So eigenvalues 1–3 and 16 are known to me; **4–15 are not**, and the *count* of qualifying
directions is not.

**The threshold is therefore taken from the prompt rather than chosen by me.** The prompt names
**1e-3 of the largest eigenvalue** as its example, and that number was written by the PI without
sight of the full spectrum. Adopting it is not tuning. To make any residual tuning visible, **the
count is reported at 1e-2, 1e-3 and 1e-4**, and the headline is 1e-3.

### The rule

> A direction is **NEAR-DEGENERATE** if its live-point covariance eigenvalue is **below 1e-3 of the
> largest**. Reported also at 1e-2 and 1e-4 for sensitivity; **1e-3 is the headline**.
>
> - **Exactly ONE qualifies** → fixing one parameter suffices; proceed to TASK 2.
> - **TWO OR MORE qualify** → name each pair, report what the full reduction would be, and **STOP**.
>   TASK 4 does not start. Spending ten hours to crash on the second pair is precisely the failure
>   this task exists to prevent.

### Standardisation, stated in advance

The covariance is taken **in the unit cube**, i.e. of `live_u`, not of the natural parameters.
Reason: that is the space `rslice` actually samples in, so it is the space whose conditioning caused
the crash; and it needs no external scale, since the prior transform maps each parameter's prior
onto [0, 1] by construction, making the directions comparable without importing a prior sd or a
live-point sd. Loadings are reported in that basis and named by parameter.

### The caveat that limits what any of this licenses

Live points late in a nested run have **concentrated into the high-likelihood region**. This
covariance therefore describes **the bulk of the posterior at iteration 11,547**, not the prior and
not the full posterior. It licenses statements about **why the sampler failed where it failed**, and
about which parameters are degenerate *there*. It does **not** license a claim about the posterior's
global shape, nor a correlation estimate that would survive to convergence — the run never got
there.

## D1 — the spectrum: the rule says ONE, and the spectrum has no gap. Both are reported.

All sixteen eigenvalues of the live-point covariance (unit cube, 800 points, iteration 11,547) are
in `task1_spectrum.csv`. **Under D0's rule at its headline threshold, exactly ONE direction
qualifies**, so by that rule fixing one parameter suffices and TASK 4 may start.

**But the count is extremely threshold-sensitive, and that has to be said as loudly as the verdict:**

| threshold (ratio to largest) | near-degenerate directions |
|---|---|
| 1e-2 | **6** |
| **1e-3 (headline)** | **1** |
| 1e-4 | **0** |

**There is no gap in this spectrum.** The eigenvalues climb smoothly — ratios to the largest of
6.87e-04, 2.22e-03, 2.78e-03, 4.12e-03, 6.96e-03, 8.84e-03, 1.54e-02, … — with consecutive
factors of 3.24, 1.25, 1.48, 1.69, 1.27. This is **not** the bimodal structure P12 found in its
barrier matrix (13.868 against 1.785, a factor-7.8 window in which the answer was invariant). Here
the answer is whatever the threshold says it is.

**What is real rather than threshold-dependent:** direction #1 is separated from #2 by a factor of
**3.24**, the largest relative gap anywhere in the bottom half of the spectrum, and it is dominated
by **dTm +0.903** with **tm_scale −0.217** and `corr = +0.831`. So there *is* a leading degenerate
direction and it *is* Y3's pair — but it leads a continuum rather than standing alone.

**And the model is pervasively correlated, not singly so.** Several pairs are more strongly
correlated than dTm~tm_scale: `sigma~kcat_scale` **−0.857** (direction #3), `dCp_scale~dTopt`
**−0.853** (#16), `kappa_scale~tm_scale` **+0.804** (#7), `kcat_scale~disc_resp` **−0.803** (#9),
`f_maint~topt_scale` **−0.742**. Fixing one parameter addresses the *worst-conditioned* direction,
not the model's general redundancy.

**Consequence, stated before the run:** a reduced run that crashes again should be read as the
continuum asserting itself, not as a surprise. TASK 3's synthetic check is the guard, and its
result is in D2.

**The live-point caveat holds throughout:** these 800 points had concentrated into the
high-likelihood region by iteration 11,547. This describes the posterior's **bulk there**, not the
prior and not a converged posterior.

## D2 — fix dTm = 0. The geometry and the physics agree, and the cost comparison is a trap.

### The code, read before choosing

`src/etcgem/enzyme_cost.py:421`:

```python
# dTm shifts every Tm uniformly; tm_scale stretches/compresses the Tm spread
# about its mean (narrow -> synchronised sharp collapse; broad -> gradual shoulder).
Tm_shift = pert.dTm + (pert.tm_scale - 1.0) * (self._Tm - np.mean(self._Tm))
fN = U.native_fraction(T - Tm_shift, self._uHTH, self._uSTS, self._uCpu)
```

**`tm_scale` scales about the distribution mean**, so the prompt's physical argument holds rather
than being void: with `dTm = 0` the mean of the meltome is untouched and only its spread moves.

- **(a) fix `tm_scale` = 1, dTm free** asserts *"the measured meltome is uniformly ~4 K too hot."*
- **(b) fix dTm = 0, `tm_scale` free** asserts *"the meltome's centre is right; its spread is not."*

### The measurements

| | synthetic 15-D condition | uncompensated cost at p38 |
|---|---|---|
| **fix dTm = 0** | **458.0** — PASSES the ≤500 rule | 50.32 |
| fix `tm_scale` = 1 | **708.2** — FAILS | 0.084 |

**The geometry is decisive and one-sided: only fixing dTm brings the conditioning under the stop
threshold.** Fixing `tm_scale` leaves 708 and would send TASK 4 into the same failure.

**The cost column looks like it says the opposite, and it is a trap.** The 50.32 is *uncompensated*
— it holds every other parameter at p38 while moving dTm from −4.0214 to 0. **Y3 measured the
compensated cost of dTm = 0 at 0.077 units**, and compensation is exactly what a sampler does. The
0.084 for `tm_scale` is equally uninformative in the other direction: p38 simply happens to sit at
`tm_scale` = 0.9892, already nominal, so fixing it there costs nothing *at that point* while saying
nothing about whether the posterior needs it.

### Y3's invariant is reachable under the choice — checked, not assumed

The enzyme meltome has mean **328.17 K**, sd **6.13**, with the low tail **9.70–12.47 K** below the
mean at the 5th–1st percentile. With `dTm = 0`, delivering Y3's requirement that the least-stable
few per cent sit **4–6 K below measurement** needs

`tm_scale = 1.32–1.62`,

which is **inside the prior bound [0.4, 2.2]** (though 2–3 prior sd out, since the lognormal sd is
0.15). **So the reduced model can still express the invariant that survives reparameterisation.**
Had it not been able to, this choice would have been wrong regardless of conditioning.

### Chosen: **dTm fixed at 0.0** (its `emergent` nominal, `space="add"`, so the sampled value is 0.0 too). Fifteen free parameters.

### Considered and NOT taken: rotating into the eigenbasis

Sampling in the rotated basis — fixing nothing, but sampling along the eigenvectors — would remove
the conditioning problem *and* keep the information, which fixing a parameter does not. It was not
taken for two reasons. The degenerate direction would remain **prior-dominated**: the data do not
constrain it, so its marginal would be its prior transported through a rotation, which is the same
R2 statement in a less legible form. And the rotated coordinates are **linear combinations of a
stability shift, a stability spread, a saturation and a turnover scale** — they have no physical
meaning, so every posterior summary would have to be rotated back to be read, reintroducing the
degeneracy at the point of interpretation. One paragraph, no work, as instructed.

### The uncertainty now hidden — to be carried in every summary

**Fixing dTm = 0 removes the model's ability to say that the whole meltome is displaced.** Any
uniform error in the measured melting temperatures — a systematic offset in the source dataset, a
calibration difference between in-vitro and in-vivo — can no longer be absorbed, and will instead
be pushed into `tm_scale` (as a spread change) and into the catalytic parameters. **The posterior
that follows is a posterior over a model that assumes the meltome's mean is exactly right.** That
is a stated limitation, not a silent reduction, and it appears in TASK 5's table, in the report's
reconciliation, and in OPEN_ITEMS 1.24.

## D3 — the reduced run: settings, the agreement rule, and the predictions carried forward

Written before the sampler was launched.

### Settings — P15's D1 exactly, except the dimension

| | |
|---|---|
| free parameters | **15** (`dTm` pinned at 0.0) |
| nlive | 800 |
| sample / bound | `rslice`, slices 3 / `multi` |
| stopping | dlogz < 0.1 |
| `first_update` | `{'min_eff': 30}` |
| checkpoint | every 30 min; wall-clock cap **16 h** |
| processes | 16 |

**The sampler is NOT changed**, in particular not in response to P15's crash. If this run crashes,
it is reported with the same covariance diagnosis P15 used, and the sampler still is not changed.

The reduction was verified before launch: `log L` at p38 with `dTm` pinned reproduces TASK 3's
**−60.3092** exactly, and the 15→16 expansion round-trips on every other coordinate.

### The agreement rule

> **AGREED** if a second seed's log Z agrees within combined reported error **AND** no posterior
> median differs by more than two Monte-Carlo errors. **The second seed runs ONLY if the first
> converges.**

### The two predictions, carried forward unchanged from P15 D1

> **(i)** The posterior moves **away** from parameter values placing any temperature within **1 % of
> `_MASK_G`**, reported as the fraction of posterior samples doing so, with **P11's posterior** as
> comparator.
>
> **(ii)** Posterior-predictive growth at **15 °C rises**, against the measured **0.0937 /h**.

Unchanged in wording, and still diagnostics rather than criteria.

### One thing that must not be read as success

If this run converges, **it converges over a model with `dTm` fixed**. Comparing its log Z to
P11's or P15's would be comparing evidences for **different models**, which is a legitimate thing
to do only as a Bayes factor and is **not** what the agreement rule is testing. The agreement rule
compares **two seeds of the same reduced model** and nothing else.

## D4 — addendum 1, pre-registered while the reduced run is still sampling and no posterior exists

Written at 10:2x on 2026-09-11, with `red1` at an early iteration and **no samples, weights or
summary written**. Every item below is therefore a prediction or a reporting commitment, not an
interpretation.

### 1. The eigendecomposition is reported ALONGSIDE the marginals, not instead of them

TASK 5 will report, for the posterior covariance of the 15 free parameters **in the unit cube**:
each direction's **eigenvalue**, its **loadings on all fifteen parameters**, and its
**posterior/prior width ratio**.

That ratio is exactly defined here because the prior is **uniform on the unit cube**: along any unit
direction the prior sd is **1/√12 = 0.2887**, so the ratio is **√(12 λ_k)**. A classification,
stated now rather than after:

> **CONSTRAINED** if the ratio is **< 0.5** (the data halve the prior width or better);
> **PRIOR-DOMINATED** if **> 0.8**; **INTERMEDIATE** in between.
> The count in each class is reported.

**Why this matters and is not decoration.** With correlations of 0.80–0.86 the **marginals will be
wide while the combinations are tight**, and fifteen marginals alone would *understate* what the
data determine. That is the mirror image of P4's error, whose unconverged intervals were
misleadingly *narrow*. Both are failures to report the geometry; they simply point in opposite
directions.

### 2. A prediction that can be checked rather than explained afterwards

**Predicted:** the three pairs stronger than the one fixed — **`sigma~kcat_scale` −0.857**,
**`dCp_scale~dTopt` −0.853**, **`kappa_scale~tm_scale` +0.804** — will appear in the posterior as
**prior-dominated directions with tight orthogonal complements**: a wide direction along the
correlation and a narrow one across it.

**If they do not** — if the data constrain those parameters individually — that is reported as a
failed prediction, and it means **the live-point covariance from a crashed run was not
representative of the posterior**. That would be worth knowing in its own right, because P15's
entire diagnosis, P16's spectrum and the choice of which parameter to fix all rest on that
covariance.

### 3. `tm_scale` railing is a finding, not a nuisance

TASK 2 established that with `dTm` pinned at 0, Y3's 4–6 K tail requirement needs **`tm_scale`
1.32–1.62**, against a prior bound of **[0.4, 2.2]**.

> `tm_scale`'s posterior is reported **with its bound printed beside it**, together with the
> **fraction of posterior mass within 5 % of 2.2**.
>
> **If it piles against 2.2, the reduction relocated the degeneracy rather than removing it, and
> that is reported as prominently as the convergence verdict** — in the report's opening, in
> OPEN_ITEMS, and in an evidence row.

### 4. The hidden uncertainty travels with every summary

In the words fixed in D2: **this posterior assumes the meltome's mean is exactly right, and any
uniform error in the measured melting temperatures is now absorbed by `tm_scale` and the catalytic
parameters.** That sentence appears in the parameter table's caption, in the report's
reconciliation, and in every evidence row that quotes a number from this posterior.

### 5. If it crashes again: diagnose, name the direction, STOP

> Diagnose the live-point covariance exactly as P15 did, name the degenerate direction, and **stop**.
> **Do not fix a second parameter in response.** That would be the fifth threshold moved after
> seeing its data.

And it would be **the expected outcome, not a surprise**: D1 documented that this spectrum is a
**continuum with no gap**, so removing its leading direction leaves the next one only 3.24× larger.
A second crash would therefore make the case for **a different approach entirely** — reparameterise,
re-specify the thermal model, or bring data that breaks the redundancies — rather than for another
reduction.

## D5 — D4's prediction FAILED, and the consequence is the one D4 named in advance

D4 predicted that `sigma~kcat_scale`, `dCp_scale~dTopt` and `kappa_scale~tm_scale` would appear in
the reduced posterior as **prior-dominated directions with tight orthogonal complements**. They do
not.

| pair | P15 live points | **P16 posterior** | most-loaded direction |
|---|---|---|---|
| `sigma~kcat_scale` | **−0.857** | **+0.334** (sign flipped) | #7, ratio 0.605, INTERMEDIATE |
| `dCp_scale~dTopt` | **−0.853** | **−0.308** | #2, ratio 0.306, **CONSTRAINED** |
| `kappa_scale~tm_scale` | **+0.804** | **+0.106** | #3, ratio 0.425, **CONSTRAINED** |
| *(`dTm~tm_scale`, fixed)* | +0.831 | — | absent by construction |

**The prediction is falsified, and D4 said what that would mean: the live-point covariance from a
crashed run was not representative of the posterior.** One correlation even reverses sign.

**Why, mechanically.** Late in a nested run the live points occupy a thin **iso-likelihood shell**,
not the posterior bulk. On a shell, any two parameters that trade off *along* a likelihood contour
appear strongly anti-correlated by construction — the shell is a level set, so movement is confined
to it. The posterior integrates over **all** shells from the prior down, and those contour-following
correlations largely cancel. **D0's caveat was therefore too generous:** it said the live-point
covariance describes "the posterior's **bulk** at iteration 11,547"; it describes the **shell** at
that likelihood level, which is a different and much narrower object.

**What this does and does not undercut.**

- **Undercut:** any inference from P15's live-point correlations to *posterior* correlations. P15's
  report, P16 D1's "the model is pervasively correlated", and the framing of Y3's pair as a
  *posterior* ridge all over-reached. They are statements about a shell.
- **NOT undercut:** P15's explanation of *why the sampler crashed*. The live points at that
  iteration really were degenerate along `dTm`/`tm_scale` — that is what `rslice` samples in, and
  it is what collapsed the slice bracket. The diagnosis of the failure stands; the extrapolation to
  the posterior does not.
- **NOT undercut:** the choice to fix `dTm`. It was made on the **synthetic conditioning check**
  (458 versus 708) and on the **code's definition** of `tm_scale`, and it is vindicated by outcome —
  the run converged in 9.59 h where the 16-D run crashed, with `tm_scale` **not** railing.

A correction, not a rescue: the remedy was right for a reason narrower than the one given.

## D6 — the run converged and the posterior is HALF DEAD. The componentwise median is unusable.

| | log L | peak predicted growth |
|---|---|---|
| MAP sample | **−10.704** | **1.7255 /h** (83 % of the measured 2.0761) |
| **componentwise median** | **−30.558** | **0.0043 /h** |
| 95th percentile of weighted log L | −13.420 | — |

**Posterior-predictive peak growth over 300 importance-weighted draws: median 0.0016 /h, 5/95
[0.0000, 1.7106], against a measured peak of 2.0761. 50.7 % of the posterior mass has a peak growth
below half the measurement.**

**So roughly half of this converged posterior is on models that do not grow.**

**This is not a sampling failure.** The run met its own dlogz criterion, n_eff is 5,988, and the MAP
is a good fit. It is what the posterior of *this model under this likelihood* actually is: P12
measured the live-dead gap at ~11.7 log-likelihood units, and **e^−11.7 ≈ 8×10⁻⁶ is easily
outweighed if the dead region carries more than ~10⁵ times the prior volume of the live one** —
which, in 15 dimensions, it plainly can. **Likelihood ratio loses to volume ratio.**

**Consequences, taken now rather than at writing-up time:**

1. **"R² at the posterior median" is meaningless here and will not be quoted as such.** The median
   is a dead model, so its R² (growth −2.01, respiration −3.17) measures the median's
   unrepresentativeness, not the model's fit. This is **P12 D1's finding recurring**: a
   componentwise median of a correlated, multi-region posterior is a point in none of its regions.
   TASK 5 reports R² **at the MAP sample** and **as a posterior-predictive distribution**, with the
   median's value shown only as evidence that it is unusable.
2. **The same applies to every marginal median in the parameter table.** They are reported, because
   the prompt asks for them and they are what a reader expects, but each is labelled with the fact
   that the vector of medians is not a posterior sample and scores 20 units worse than the MAP.
3. **This is the sharpest form yet of the R2/R3 problem**, and it is a *result*: the data as
   currently used do not exclude non-growing parameterisations. Whether that is the support
   handling (1.21 chose `clamp` precisely to charge dead models more), the prior volumes, or a
   missing constraint is a modelling question, and it is now stated with a number rather than
   suspected.

## D7 — completed-seed audit, 12 September: the agreement rule FAILS

Both runs met dlogz<0.1 without crashing. Log evidences agree: difference 0.022486 against
combined reported error 0.147777. But 14/15 marginal medians fail the existing two-MC-error
check; only dTopt passes. The same 14 fail a supplementary dynesty strand bootstrap.
**D3's verdict is DISAGREED. No further parameter is fixed and no new sampler is launched.**

The full audit is `audit_report.md`. Separate audit_* tables preserve every original result.
Both covariances are importance-weighted in the prior unit cube; eigen-width counts are
4 constrained / 6 intermediate / 5 prior-dominated in red1, versus 6 / 6 / 3 in red2.
These are diagnostics of disagreeing runs, not established biological identification.
Neither run has tm_scale mass near 2.2; medians/5–95 are 1.069/[0.793,1.515] and
0.956/[0.783,1.228]. Every statement conditions on dTm=0 and the measured meltome mean
being exact; uniform mean error is excluded and must be absorbed elsewhere.

**Corrections to D5:** its correlations were unweighted. The weighted three pairs are
+0.370/-0.639/+0.298 in red1 and +0.307/-0.393/-0.040 in red2. None shows the specified
broad-pair/tight-orthogonal pattern at the registered width thresholds. This does NOT prove
individual identification; broad marginals and seed disagreement prevent that conclusion.
Live points occupy a likelihood-constrained region, not the posterior or literally one
iso-likelihood shell. The dimensional reduction also changes the posterior being compared.

**Qualification to D6:** its seed-1 predictive numbers remain a recorded diagnostic, but
"this is not a sampling failure" is not established by a single stopping criterion and
ESS. Seed 2 has not yet been tested for the same predictive fraction. The inactive f_metab
parameter should reproduce its prior; its unit-cube mean is instead 0.319/0.394 versus
0.5, a useful null test identifying a computational inference problem to investigate.
Original arrays, weights and restored unit-cube coordinates cross-check, so this is not
an obvious audit alignment error. The exact sampling failure mechanism remains unproven.

P16's original MASK_G and 15 C predictions, line-scan classifications and D6 predictive
R2 reporting remain unassessed. The posterior-dependent programme is not unblocked.
