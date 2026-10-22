$localTools = $PSScriptRoot

if ($env:PATH -notlike "*$localTools*") {
  $env:PATH = "$localTools;$env:PATH"
}

Set-Alias -Name rg -Value (Join-Path $localTools "rg.exe") -Scope Global
