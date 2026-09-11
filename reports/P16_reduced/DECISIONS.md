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
