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
