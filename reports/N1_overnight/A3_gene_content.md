# A3 — the metabolic gene-content screen

_N1 TASK 1. Presence/absence is the one species difference that needs no new data and no
predictor, and nobody had looked. This looks. It reports numbers and does not adjudicate
mechanism._

Produced by `reports/N1_overnight/a3_gene_content.py`, reading `$CANDIDAS_ROOT` read-only
and this repository's committed strain models. Nothing was fetched; annotation is whatever
the RefSeq proteome headers and the repository's existing tables already say.

## Method, and the three things that constrain it

**Orthology by alignment, with a graded absence criterion.** DIAMOND blastp, `--sensitive`,
one target per query, run in both directions for all twelve ordered species pairs. "Absent"
is reported at three nested thresholds so it is a graded claim rather than a binary one:

| criterion | meaning | strength |
|---|---|---|
| `no_rbh` | no reciprocal best hit | weakest — paralogy and gene duplication break reciprocity without anything being absent |
| `no_hit_e10` | no hit at all at e < 1e-10 | the threshold the Candida pipeline uses elsewhere |
| `no_hit_e3` | no hit at all at e < 1e-3 | strongest evidence of genuine absence |

**Namespaces.** Each species is taken in the namespace *its model uses*: RefSeq `XP_` for the
three *Candidozyma* (`phylo/proteomes/*.faa`), UniProt/CGD ordered-locus `CPAR2_` for
*C. parapsilosis* (`gem/inputs/parap_uniprot.tsv`, which is what iDC1003's GPRs are keyed
on). These are different assemblies of different organisms, so **every cross-species
statement here is made by alignment, never by identifier**.

**The trap at model level, stated before any number.** The *C. haemulonii* and
*C. duobushaemulonii* models are the *C. auris* network with genes reassigned by KO evidence:
2863 reactions in all three, 1310–1314 enzyme-costed, differing by 2–4. **Their model-level
gene content is nearly identical by construction.** Only *C. parapsilosis*, whose iDC1003 is
independently curated (2162 reactions), can differ genuinely at level (b). Nothing below
reports construction as biology.

## (a) Proteome level

Proteome sizes: *C. auris* clade I 5424, *C. haemulonii* 5249, *C. duobushaemulonii* 5173,
*C. parapsilosis* 5777.

| present in | absent from | no RBH | no hit e<1e-10 | **no hit e<1e-3** | % of proteome |
|---|---|---|---|---|---|
| *C. auris* | *C. haemulonii* | 569 | 209 | **172** | 3.17% |
| *C. auris* | *C. duobushaemulonii* | 624 | 244 | **205** | 3.78% |
| *C. auris* | *C. parapsilosis* | 803 | 594 | **462** | 8.52% |
| *C. haemulonii* | *C. auris* | 394 | 240 | **189** | 3.60% |
| *C. haemulonii* | *C. duobushaemulonii* | 531 | 206 | **159** | 3.03% |
| *C. haemulonii* | *C. parapsilosis* | 882 | 631 | **511** | 9.74% |
| *C. duobushaemulonii* | *C. auris* | 373 | 208 | **171** | 3.31% |
| *C. duobushaemulonii* | *C. haemulonii* | 455 | 164 | **122** | 2.36% |
| *C. duobushaemulonii* | *C. parapsilosis* | 846 | 601 | **468** | 9.05% |
| *C. parapsilosis* | *C. auris* | 1156 | 748 | **602** | 10.42% |
| *C. parapsilosis* | *C. haemulonii* | 1410 | 784 | **620** | 10.73% |
| *C. parapsilosis* | *C. duobushaemulonii* | 1450 | 816 | **647** | 11.20% |

Note the spread between criteria: for *C. auris* against *C. haemulonii*, 569 genes lack a
reciprocal best hit and 172 lack any hit at all. **The RBH-based figure over-states absence
by more than threefold**, which matters because RBH is the pairing the rest of the project
uses. Full per-gene lists with best hit, identity and e-value: `A3_absent_genes.csv`.

Within the *Candidozyma* clade the gene content differs by 2.4–3.8% in each direction.
*C. parapsilosis* is 8.5–11.2% apart from all three, consistent with its much greater
sequence divergence (53.7% median ortholog identity, against 77.6–78.7% within the clade).

## (b) Model level

Model gene counts: *C. auris* 709, *C. haemulonii* 696, *C. duobushaemulonii* 674,
*C. parapsilosis* 1003.

Of the genes absent from a relative, how many are carried in a metabolic model at all:

| present in | absent from | absent (e<1e-10) | **of which in a model** | absent (e<1e-3) | of which in a model |
|---|---|---|---|---|---|
| *C. auris* | *C. haemulonii* | 209 | **4** | 172 | 4 |
| *C. auris* | *C. duobushaemulonii* | 244 | **7** | 205 | 7 |
| *C. auris* | *C. parapsilosis* | 594 | **10** | 462 | 9 |
| *C. haemulonii* | *C. auris* | 240 | **1** | 189 | 1 |
| *C. haemulonii* | *C. duobushaemulonii* | 206 | **2** | 159 | 1 |
| *C. haemulonii* | *C. parapsilosis* | 631 | **11** | 511 | 11 |
| *C. duobushaemulonii* | *C. auris* | 208 | **1** | 171 | 1 |
| *C. duobushaemulonii* | *C. haemulonii* | 164 | **0** | 122 | 0 |
| *C. duobushaemulonii* | *C. parapsilosis* | 601 | **10** | 468 | 9 |
| *C. parapsilosis* | *C. auris* | 748 | **13** | 602 | 12 |
| *C. parapsilosis* | *C. haemulonii* | 784 | **12** | 620 | 10 |
| *C. parapsilosis* | *C. duobushaemulonii* | 816 | **15** | 647 | 15 |

**Almost none of the gene-content difference is inside the metabolic models.** Between
*C. auris* and *C. haemulonii*, 209 genes are absent and **four** of them are in a model:
protoheme IX farnesyltransferase (`XP_085451290.1`), Dpm2p (`XP_085453340.1`), an
uncharacterised protein (`XP_085453932.1`) and cytidine deaminase (`XP_085455436.1`). Against
*C. duobushaemulonii* it is seven, adding Mg-dependent acid phosphatase,
CDP-diacylglycerol–inositol 3-phosphatidyltransferase and one more uncharacterised protein.
In the reverse direction it is one, in both cases.

**The 1–15 range across the table is small enough to be read gene by gene, and the lists are
in `A3_absent_genes.csv`.** For the two draft models the numbers also carry the construction
caveat above: their gene sets were assigned from the *C. auris* scaffold, so a gene absent
from *C. haemulonii*'s proteome cannot be in *C. haemulonii*'s model, and the asymmetry
(4 and 7 out, 1 and 1 back) partly reflects that. The *C. parapsilosis* rows are the ones
that can carry a genuine model-level signal, and they are the largest — 10 to 15.

## The Xiao et al. 2025 candidates

Searched by description in all four RefSeq proteomes, then **decided by alignment**, because
description-based absence is not absence. The distinction is load-bearing here: a
description search finds no alternative oxidase in *C. haemulonii*, and alignment finds one
at 86.4% identity. The *C. parapsilosis* model namespace carries no descriptions at all, so a
description search there returns zero for everything.

| candidate | *C. auris* | *C. haemulonii* | *C. duobushaemulonii* | *C. parapsilosis* | in any model? |
|---|---|---|---|---|---|
| **alternative oxidase (AOX)** | present | **present (86.4% id)** | present | present | **no** |
| **glutaredoxin (GRX5 family)** | present | present | present | present | **no** |
| iron uptake: ferric reductase (FRE-like) | present | present | present | present | *C. parapsilosis* only |
| iron uptake: ferroxidase / multicopper oxidase (FET3-like) | present | present | present | present | **all four** |
| iron uptake: high-affinity iron permease (FTR1-like) | — | — | — | — | — |
| iron uptake: siderophore transporter (SIT1-like) | — | — | — | — | — |

**All of the named candidates that can be found at all are present in all four species.**
None of them distinguishes the species by presence/absence. Alternative oxidase and the
glutaredoxins are in **no metabolic model**, so the models cannot express them whatever they
do; the ferric reductases are in one model only.

The two dashes are a limit, not a finding: **no protein in any of the four RefSeq proteomes
carries a description matching "iron permease", "ferric permease" or "siderophore"**, so
there was nothing to align and nothing can be said about FTR1 or SIT1 orthologues here. That
would need an annotation source this task is not permitted to fetch.

Per-copy detail, with identity and e-value for every candidate against every species:
`A3_candidates_by_alignment.csv`; description counts: `A3_candidates_by_description.csv`.

## What presence/absence can and cannot support

**It can support:**

* A count. Gene content within the *Candidozyma* clade differs by 2.4–3.8% in each
  direction, and *C. parapsilosis* is 8.5–11.2% from all three.
* That the overwhelming majority of that difference is **outside** the metabolic models —
  0 to 15 genes per comparison, against 122 to 647 in the proteome. Whatever presence/absence
  contributes, the models as they stand can express almost none of it.
* That the four named Xiao et al. candidates that could be located are present in all four
  species, and that AOX and the glutaredoxins are in none of the models.
* That absence estimates depend heavily on the criterion: RBH-based absence over-states
  no-hit absence by more than threefold.

**It cannot support:**

* Any claim about **mechanism**. A gene being present says nothing about whether it is
  expressed, when, or at what level; a gene being absent says nothing about whether its
  function is covered by something else. This screen is a catalogue.
* Any comparison of model-level gene content **between the two draft models**, which are the
  *C. auris* network with genes reassigned and are therefore near-identical by construction.
* Anything about FTR1 or SIT1, for want of an annotation.
* Anything about copy number, since the alignment step takes one target per query. The
  description counts (e.g. 8 ferric reductases in *C. auris*, 6 in *C. haemulonii*) hint at
  copy-number variation and are not a measurement of it.

## Relation to the existing screen

`$CANDIDAS_ROOT/gem/tables/lineage_specific_{auris,summary}.tsv` is an existing
lineage-specific gene list from the Candidas project, framed as gained/lost with
descriptions. This screen is independent of it: it is pairwise rather than lineage-polarised,
it grades absence by alignment threshold, and it crosses the result with model membership,
which the existing table does not. The two should be read together and neither supersedes
the other.

## Files

| file | what |
|---|---|
| `A3_presence_absence_counts.csv` | table (a), all twelve ordered pairs, three criteria |
| `A3_absent_genes.csv` | every absent gene with description, best hit, identity, e-value, and whether it is in a model |
| `A3_model_level_counts.csv` | table (b) |
| `A3_candidates_by_description.csv` | keyword hits per species |
| `A3_candidates_by_alignment.csv` | every candidate copy against every species |
| `A3_candidates_summary.csv` | the candidate table above |
| `A3_meta.json` | proteome and model gene counts |
