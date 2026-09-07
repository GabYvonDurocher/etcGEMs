# TASK 1 — why `strains/eciML1515/outputs/tpc/` did not reproduce

_N2 TASK 1. Diagnosed before regenerating, because regenerating destroys the evidence._

## The finding

**The committed file was already stale when it was committed.** It was last *generated* on
2026-07-02 and was then carried unchanged through two months of commits, including the one
that appears in `git log` as having written it.

The cause is a single two-commit change on 2026-07-02, `27cafef` + **`a416fd1`
("medium-dependent sector allocation (ribosome cap)")**, after which the nominal TPC was
never re-run.

## The evidence

Each row is the repository checked out into a scratch worktree and
`etcgem tpc --strain eciML1515` re-run against that state's own code and config.

| commit | date | what it did | Topt | rmax | CTmax |
|---|---|---|---|---|---|
| `27cafef^` | 2026-07-02 | the state the committed file reflects | **37.0** | **0.3407** | 46.856 |
| *the committed file* | | written at `e52e0ed`, same day | **37.0** | **0.3413** | 46.856 |
| `27cafef` | 2026-07-02 | adds `sector_fractions_by_medium` | *(build fails — intermediate state)* | | |
| **`a416fd1`** | 2026-07-02 | **medium-matched sector allocation** | **30.0** | **0.5497** | 46.882 |
| `922e13d` | 2026-07-02 | coupled growth-law partition | 31.0 | 0.5467 | |
| `8085036^` | | | 31.0 | 0.5511 | |
| **`8085036`** | | **closes four uncosted O2 sinks** | 31.0 | **0.5429** | |
| `c6a20ad` | 2026-09-07 | the commit that *committed* the file | **31.0** | **0.5429** | 46.881 |
| today | | | **31.0** | **0.5429** | 46.881 |

Two things follow. **`c6a20ad` produced 31.0 / 0.5429 while committing a file that says
37.0 / 0.3413** — the staleness is not a later regression, it was already there. And the
whole difference is accounted for: 37.0 → 30.0 and 0.341 → 0.550 at `a416fd1`, then
30.0 → 31.0 at `922e13d`, then 0.5511 → 0.5429 at `8085036`, whose own commit message
predicts about −0.3% growth from the O2-sink closure.

## What `a416fd1` changed, and why it moves the optimum and not the envelope

From the `strain.yaml` diff:

```
-  f_metab: 0.285             # metabolic-enzyme sector (measured 30 C)
-  f_maint: 0.374             # maintenance = chaperone + other (measured 30 C)
+  f_metab: 0.483             # metabolic-enzyme sector (measured Glucose 30 C)
+  f_maint: 0.326             # maintenance = chaperone + other (measured Glucose 30 C)
```

The sector split was re-grounded from the **pooled** measured 30 °C proteome to the
**Glucose-minimal** measured 30 °C proteome (the model's default medium), and the allocation
became medium-matched (LB / Glucose / Glycerol) rather than a single curve. In the build log:

| | before | after |
|---|---|---|
| pool budget = P_total × f_metab × σ | 0.5 × 0.285 × 0.45 = **0.0641** | 0.5 × 0.483 × 0.45 = **0.1087** |
| sectors | f = (metab 0.285, bio 0.34, maint 0.374) | f = (metab 0.483, bio 0.19, maint 0.326) |
| `translation_coeff` | 0.2375 (µ* = 0.323) | 0.0787 (µ* = 0.546) |

The metabolic pool gained 70%, and the ribosome cap — which binds at
`f_bio × P_total / translation_coeff` — moved out of the way. So the achievable rate rose and
the temperature at which the *cap* rather than the *enzyme layer* limits growth moved, which
is what dragged Topt down 6 °C.

**The envelope is untouched**, which is exactly the signature the prompt predicted: CTmax
46.856 → 46.881 (+0.03 °C) and Eₐ 0.934 → 0.956 eV. The thermal layer never changed; the
allocation layer did.

## Regenerated

| | committed (stale) | regenerated |
|---|---|---|
| Topt | 37.0 °C | **31.0 °C** |
| rmax | 0.34131 /h | **0.54290 /h** |
| CTmin | 10.732 °C | 9.200 °C |
| CTmax | 46.856 °C | 46.881 °C |
| niche width | 36.123 °C | 37.681 °C |
| B80 | 15.140 °C | 18.965 °C |
| Eₐ | 0.9339 eV | 0.9559 eV |
| skewness | −0.4138 | −0.4292 |

**No scientific conclusion depends on this file.** It is the nominal glucose-minimal smoke-test
output. `reports/ecoli_tpc/` draws on `outputs/calibration_vanderlinden/`,
`outputs/dissect*`, `outputs/elasticity_tuned/` and the anatomy figures; the seven-strain
ceiling table in K2 uses `outputs/calibration_vanderlinden/` (emergent prior 51.82 °C) and
lists this file's CTmax only as a labelled "nominal" row, whose value moves by 0.03 °C.

## What this says about the failure mode

The staleness was not caused by anyone changing a result. It was caused by a configuration
change whose *outputs were not re-generated*, and by that going unnoticed for two months
because nothing checked. N1 TASK 5 adopted the rule that every strain commits its nominal TPC
partly for this reason: a committed artefact that stops reproducing is a signal. This is the
first time that signal has been read.
