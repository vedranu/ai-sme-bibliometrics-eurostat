# Bibliometric trends and Eurostat evidence on AI in SMEs

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23004118.svg)](https://doi.org/10.5281/zenodo.23004118)

Data and code for the paper:

> Baraća, K., Uroš, V. and Mihanović, D. (2026) *Bibliometric Trends and Eurostat Evidence on Artificial Intelligence in Small and Medium-Sized Enterprises*. Submitted to Global Advances in Management and Entrepreneurship (GAME) Conference Proceedings.

The package reproduces every number, table and figure in the paper from the stored data with one command.

## What the analysis does

1. **Bibliometrics (OpenAlex, 2010-2025).** One query (AI terms AND SME terms in titles and abstracts) is screened in three steps: both concepts present (3,064 records), a strict rule (1,658) and removal of repository deposits and records without a source (analysed core: 1,494 journal articles and reviews). A controlled vocabulary of 43 themes (regular expressions in `python/terms.py`) feeds a co-word network (association strength, Louvain clustering with 50 seeds), a centrality-density map and a thematic evolution across 2010-2020, 2021-2023 and 2024-2025.
2. **Database robustness.** Annual counts of the same query in Scopus and Web of Science Core Collection (counts only, `data/scopus_wos/`) are compared with OpenAlex through CAGR and year-on-year log growth. The OpenAlex source profile (CWTS core, DOAJ, repositories) explains the divergence after 2023.
3. **Eurostat (ICT usage in enterprises, 2021-2025).** AI use by enterprise size (EU-27 and Croatia), cross-country association with the digital intensity index (OLS with 95% CI, Theil-Sen, influence checks, DII 2022 without the AI item), barriers, purposes and technologies.
4. **Validation.** Relevance coding of a random sample of 100 screened records (`validation/precision_sample100_coded.csv`): two authors coded the sample independently (agreement 82%, Cohen's kappa 0.61; all 18 disagreements are records the first coder marked relevant and the second did not). The disagreements were then resolved by discussion; precision and recall of the strict rule are computed against the consensus coding and, for transparency, against each independent coding. A third coding by an AI assistant is included as supplementary information only.

## Repository structure

```
data/openalex/          OpenAlex API pages of the query result (17 JSON pages, 3,332 records),
                        annual counts, queries, retrieval date (27 September 2026)
data/eurostat/          isoc_eb_ai and isoc_e_dii (SDMX-CSV) and indicator labels
data/scopus_wos/        annual counts and exact queries for Scopus and Web of Science
validation/             100-record relevance sample: two independent author codings, consensus coding, AI coding
python/                 analysis pipeline (01-07) and the theme vocabulary (terms.py)
fetch/                  PowerShell scripts that re-download OpenAlex and Eurostat data
results/                tables (CSV) and summary statistics (JSON) produced by the pipeline
figures/                Figures 1-8 of the paper (PNG, 600 dpi)
```

## How to reproduce

Requires Python 3.10 or newer.

```bash
pip install -r requirements.txt
./run_all.sh            # Linux / macOS
```

```powershell
pip install -r requirements.txt
powershell -ExecutionPolicy Bypass -File run_all.ps1   # Windows
```

The pipeline runs in about one minute and writes `results/` and `figures/`. `PYTHONHASHSEED=0` is set by the run scripts, so the Louvain partitions are identical on every run.

| Script | Output |
|---|---|
| `01_load_corpus.py` | record table from the OpenAlex pages |
| `02_screen.py` | screening steps, strict rule, validation sample |
| `03_validation.py` | `validation_summary.json` (inter-coder kappa 0.61; precision against consensus 0.660, 95% CI 0.526-0.773; recall 0.946) |
| `04_bibliometrics.py` | Figures 2-5, Tables 1-3, theme frequencies (Table B1), `bib_summary.json` |
| `05_eurostat.py` | Figures 6-8, Table 4, `eurostat_summary.json` |
| `06_eurostat_robustness.py` | slope CI, Theil-Sen, exclusions, DII 2022 check, reliability flags |
| `07_fig_concept.py` | Figure 1 |

## Re-downloading the data

`fetch/fetch_all.ps1` repeats the OpenAlex and Eurostat downloads. Both sources are updated continuously, so a new download will not give identical numbers. Use the stored data to reproduce the paper. An OpenAlex API key and contact e-mail can be set with the environment variables `OPENALEX_API_KEY` and `OPENALEX_MAIL`.

Scopus and Web of Science were queried through the institutional interface (NSK EZproxy). Only annual counts are shared, because the licences of these databases do not allow redistribution of records.

## Data sources and licences

- **OpenAlex** metadata are released under CC0 (Priem, Piwowar and Orr, 2022).
- **Eurostat** data: © European Union, reused under the Eurostat copyright and licence policy (CC BY 4.0). Datasets `isoc_eb_ai` and `isoc_e_dii`; DII composition overview 2015-2025 (Eurostat CIRCABC).
- **Scopus, Web of Science**: annual counts only.
- **Code** (`python/`, `fetch/`, run scripts): MIT licence (`LICENSE`).
- **Derived data, tables and figures** (`results/`, `figures/`, `validation/`): CC BY 4.0 (`LICENSE-DATA`).

## Citation

Please cite the paper and this package (see `CITATION.cff`):

Uroš, V., Baraća, K. and Mihanović, D. (2026) *Bibliometric trends and Eurostat evidence on AI in SMEs: data and code* (v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.23004118

## Acknowledgement

An AI assistant (Claude, Anthropic) supported the data processing code and a supplementary relevance coding. The authors checked all data, results and references.
