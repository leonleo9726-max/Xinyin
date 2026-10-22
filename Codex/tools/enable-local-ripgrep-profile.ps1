$ErrorActionPreference = "Stop"

$profilePath = $PROFILE
$profileDir = Split-Path -Parent $profilePath
$localLoader = Join-Path $PSScriptRoot "use-local-ripgrep.ps1"

New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

if (-not (Test-Path -LiteralPath $profilePath)) {
  New-Item -ItemType File -Force -Path $profilePath | Out-Null
}

$begin = "# BEGIN Codex local ripgrep"
$end = "# END Codex local ripgrep"
$block = @"
$begin
. "$localLoader"
$end
"@

$content = Get-Content -LiteralPath $profilePath -Raw
$pattern = "(?s)" + [regex]::Escape($begin) + ".*?" + [regex]::Escape($end)

if ($content -match $pattern) {
  $content = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block })
} else {
  if ($content.Length -gt 0 -and -not $content.EndsWith("`n")) {
    $content += "`r`n"
  }
  $content += $block + "`r`n"
}

Set-Content -LiteralPath $profilePath -Value $content -Encoding utf8

. $localLoader

Write-Output "PROFILE=$profilePath"
Get-Alias rg
& (Join-Path $PSScriptRoot "rg.exe") --version
