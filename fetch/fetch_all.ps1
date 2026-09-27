# Ponovno preuzimanje podataka (Windows PowerShell). Pokrenuti iz korijena repozitorija: powershell -File fetch/fetch_all.ps1
# NAPOMENA: OpenAlex i Eurostat se mijenjaju; novo preuzimanje nece dati identicne brojke. Za reprodukciju rada koristite podatke u data/.
. (Join-Path $PSScriptRoot 'queries.ps1')
$ErrorActionPreference = 'Continue'
$root = Split-Path $PSScriptRoot -Parent
$D = Join-Path $root 'data\openalex'; New-Item -ItemType Directory -Force $D | Out-Null
function Get-Url($u, $file) { for ($t=0; $t -lt 6; $t++) { & curl.exe -s -L --max-time 180 -o $file $u; $x = Get-Content $file -Raw -ErrorAction SilentlyContinue; if ($x -and -not ($x -match '^\{"error"')) { return $x }; Start-Sleep (3+3*$t) }; return $x }
# 1. godisnji brojevi
$Q = [ordered]@{ core = $CORE; core_dt = "$CORE AND $DT"; core_res = "$CORE AND $RES"; core_dt_res = "$CORE AND $DT AND $RES"; sme_all = "$SME NOT $NOISE"; sme_dt = "$SME AND $DT NOT $NOISE"; ai_all = $AI }
$tab = @{}
foreach ($n in $Q.Keys) {
  $u = "https://api.openalex.org/works?mailto=$MAIL$KEY&group_by=publication_year&per-page=200&filter=title_and_abstract.search:" + [uri]::EscapeDataString($Q[$n]) + ",publication_year:2000-2025$FILT"
  $x = Get-Url $u (Join-Path $env:TEMP "annual_$n.json")
  foreach ($m in [regex]::Matches($x, '"key":\s*"(\d{4})",\s*"key_display_name":\s*"\d{4}",\s*"count":\s*(\d+)')) { $y=[int]$m.Groups[1].Value; if (-not $tab[$y]) { $tab[$y]=@{} }; $tab[$y][$n]=[int]$m.Groups[2].Value }
  Start-Sleep -Milliseconds 500
}
$csv = @('year,' + (@($Q.Keys) -join ','))
foreach ($y in 2000..2025) { $r=@($y); foreach ($n in $Q.Keys) { $v=0; if ($tab[$y] -and $tab[$y][$n]) { $v=$tab[$y][$n] }; $r+=$v }; $csv += ($r -join ',') }
$csv | Set-Content -Encoding ASCII (Join-Path $D 'openalex_annual.csv')
$Q.GetEnumerator() | % { "$($_.Key)`t$($_.Value)" } | Set-Content -Encoding UTF8 (Join-Path $D 'queries.tsv')
# 2. korpus (cursor paging)
$raw = Join-Path $D 'corpus'; New-Item -ItemType Directory -Force $raw | Out-Null
$sel = 'id,doi,title,publication_year,type,language,primary_location,authorships,keywords,topics,concepts,cited_by_count,abstract_inverted_index'
$flt = "title_and_abstract.search:" + [uri]::EscapeDataString($CORE) + ",publication_year:2010-2025$FILT"
$cursor = '*'; $i = 0
while ($cursor) {
  $i++; $file = Join-Path $raw ("page_{0:D3}.json" -f $i)
  $u = "https://api.openalex.org/works?mailto=$MAIL$KEY&filter=$flt&per-page=200&cursor=" + [uri]::EscapeDataString($cursor) + "&select=$sel"
  $x = Get-Url $u $file
  if ($x -match '"results":\s*\[\s*\]') { Remove-Item $file; break }
  if ($x -match '"next_cursor":\s*"([^"]+)"') { $cursor = $matches[1] } else { $cursor = $null }
  Start-Sleep -Milliseconds 300
}
# 3. Eurostat
$E = Join-Path $root 'data\eurostat'; New-Item -ItemType Directory -Force $E | Out-Null
foreach ($c in 'isoc_eb_ai','isoc_e_dii') { & curl.exe -s -L --max-time 300 -o (Join-Path $E "$c.csv") "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/$c/?format=SDMX-CSV&compressed=false" }
& curl.exe -s -L --max-time 120 -o (Join-Path $E 'indic_is_labels.tsv') "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/codelist/ESTAT/INDIC_IS?format=TSV&lang=en"
Get-Date -Format 'yyyy-MM-dd HH:mm' | Set-Content (Join-Path $D 'retrieved.txt')
"ALL DONE"
