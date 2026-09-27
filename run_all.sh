#!/usr/bin/env bash
# Pokretanje cijelog postupka iz korijena repozitorija (Python 3.10+)
set -e
export PYTHONHASHSEED=0
mkdir -p work results figures
for s in 01_load_corpus 02_screen 03_validation 04_bibliometrics 05_eurostat 06_eurostat_robustness 07_fig_concept; do
  echo "== $s"; python3 python/$s.py > work/$s.log
done
echo "Done. Results in results/, figures in figures/."
