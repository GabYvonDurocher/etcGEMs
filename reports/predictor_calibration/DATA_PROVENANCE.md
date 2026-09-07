# A1 — data provenance

_Fetched 2026-09-07 by `reports/predictor_calibration/a1_fetch.py`. Raw files live in `tools/reconstruction/external/a1_data`, which is gitignored._

**Nothing here is substituted.** Where a source publishes only a summary statistic, that is recorded as such and the analysis that depends on it is marked weaker in the report.

## Meltome Atlas melting points, run 'Saccharomyces cerevisiae lysate'

| | |
|---|---|
| file | `full_dataset.json.zip -> meltome_scerevisiae.csv` |
| retrieved from | https://raw.githubusercontent.com/J-SNACKKB/FLIP/main/splits/meltome/full_dataset.json.zip |
| original source | Jarzab et al. 2020, Nat Methods 17:495-503, doi:10.1038/s41592-020-0801-4; PRIDE PXD011929. Redistributed by the FLIP benchmark (J-SNACKKB/FLIP, splits/meltome), which obtained it from http://meltomeatlas.proteomics.wzw.tum.de:5003 |
| entries | 221203 total, 2166 S. cerevisiae proteins with a melting point |
| identifier namespace | UniProt accession (uniprotAccession field) |
| md5 | `827ac24a2d89defb4b4678654a1f496a` |

## Saccharomyces cerevisiae S288c reference proteome

| | |
|---|---|
| file | `proteome_scerevisiae.tsv` |
| retrieved from | https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP000002311&format=tsv&fields=accession,id,protein_name,gene_names,organism_name,length,sequence |
| original source | UniProt proteome UP000002311 |
| entries | 6067 proteins |
| identifier namespace | UniProt accession |
| md5 | `7c52f148d2f3f922dd68c4f7de641f26` |

## Saccharomyces uvarum (S. bayanus var. uvarum) reference proteome

| | |
|---|---|
| file | `proteome_suvarum.tsv` |
| retrieved from | https://rest.uniprot.org/uniprotkb/stream?query=proteome:UP001162085&format=tsv&fields=accession,id,protein_name,gene_names,organism_name,length,sequence |
| original source | UniProt proteome UP001162085 |
| entries | 5489 proteins |
| identifier namespace | UniProt accession |
| md5 | `6e60b4730fcec0908c657031843095a3` |

## the four C. auris clade proteomes (PART D, the same-species noise floor)

| | |
|---|---|
| file | `auris_cladeI.faa, auris_cladeII.faa, auris_cladeIII.faa, auris_cladeIV.faa` |
| retrieved from | $CANDIDAS_ROOT/phylo/proteomes/ (read-only; not copied) |
| original source | NCBI RefSeq, as assembled by the Candidas project |
| entries | auris_cladeI.faa: 5424 proteins; auris_cladeII.faa: 5327 proteins; auris_cladeIII.faa: 5521 proteins; auris_cladeIV.faa: 5506 proteins |
| identifier namespace | RefSeq XP_ accession |
| md5 | `077dbba5; fe8a5d4e; c533c781; 4ce7374b` |

## measured S. cerevisiae vs S. uvarum proteome-wide mean ortholog dTm

| | |
|---|---|
| file | `(none -- summary statistic only)` |
| retrieved from | NOT OBTAINED AS PER-PROTEIN DATA |
| original source | Walunjkar et al. 2025, Mol Biol Evol 42:msaf137, 'Pervasive Divergence in Protein Thermostability is Mediated by Both Structural Changes and Cellular Environments'. The value used throughout Figure 4 and here is the PARENTAL-CONTEXT mean: 1.6 C over 827 ortholog pairs, 85% of S. cerevisiae proteins more thermostable, alongside an 8 C difference in growth thermal limit (IT50). Provenance taken from $CANDIDAS_ROOT/gem/FIG4_etcgem_caption.md lines 72-75 and 250-257. |
| entries | summary statistic only: mean 1.6 C, n = 827 pairs |
| identifier namespace | n/a |
| md5 | `n/a` |

