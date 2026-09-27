# Pokretanje cijelog postupka iz korijena repozitorija (Windows PowerShell, Python 3.10+)
$ErrorActionPreference = 'Stop'
$env:PYTHONHASHSEED = '0'
New-Item -ItemType Directory -Force work, results, figures | Out-Null
foreach ($s in '01_load_corpus','02_screen','03_validation','04_bibliometrics','05_eurostat','06_eurostat_robustness','07_fig_concept') {
  Write-Output "== $s"; python "python/$s.py" > "work/$s.log"; if ($LASTEXITCODE -ne 0) { throw "$s failed" }
}
Write-Output 'Done. Results in results/, figures in figures/.'
