# Pool reconciliation (P1c): one proteome budget

**What changed.** The model carried TWO redundant enzyme-mass pools (P2c diagnostic):
the etcgem sMOMENT/sector pool (P_total x f_metab x sigma, medium- & growth-law-aware,
scaled by kcat_scale) and the leftover GECKO base pool `prot_pool_exchange`
(static 0.0909 g/gDW). The GECKO pool bound independently and the magnitude levers
(kcat_scale/sigma/P_total) could not touch it, so they saturated at ~1.55. Fix:
from_gecko now relaxes the GECKO base pool supply reaction so the **etcgem
sMOMENT/sector pool is the SOLE proteome budget** (the two are two computations of the
same ~0.1 g/gDW quantity; kept the medium/growth-law-aware sector one, P_total=0.225).

**Single budget is sensible.** sector metabolic pool = f_metab x P_total x sigma
~ 0.109 g/gDW (glucose) -- same order as the GECKO 0.091.
Glucose-minimal reference is UNCHANGED (rmax 0.55; the biosynthesis/translation
cap binds there, not the enzyme pool), so the sensitivity operating point is preserved.

**Ceiling is now movable.** At rich BHI (growth law ON) kcat_scale now lifts rmax
1.02 -> 1.72 (kcat 1 -> 16), and scaling the enzyme budget / sigma moves it further:
budget x1.0/1.4/1.8 -> rmax 1.39/1.95/2.51. Reaching the observed ~2.4 needs budget
~x1.7 (sigma ~0.45 -> ~0.77), which is ABOVE the 0.4-0.5 literature range.

**Honest residual (for P3).** The double-accounting was a fixable artefact and is now
fixed (levers act on the true pool). But the full rich-medium magnitude to ~2.4 still
needs ~1.7x more enzyme budget than the literature sigma allows -- so part is a
genuinely higher in-vivo capacity on rich medium (and the observed 2.4 is a digitized
high-end value), not merely the redundancy. Reconciled emergent descriptors (BHI,
growth law off): rmax 1.04, Topt 37C, CTmax 51C, Ea 0.81 eV.
