$ErrorActionPreference = "Stop"

$toolsDir = $PSScriptRoot
New-Item -ItemType Directory -Force -Path $toolsDir | Out-Null

$headers = @{
  "User-Agent" = "Codex-ripgrep-installer"
}

$release = Invoke-RestMethod `
  -Uri "https://api.github.com/repos/BurntSushi/ripgrep/releases/latest" `
  -Headers $headers

$asset = $release.assets |
  Where-Object { $_.name -match "x86_64-pc-windows-msvc\.zip$" } |
  Select-Object -First 1

if (-not $asset) {
  throw "Cannot find x86_64-pc-windows-msvc ripgrep asset in latest release."
}

$zipPath = Join-Path $toolsDir $asset.name
$extractDir = Join-Path $toolsDir ("ripgrep-" + $release.tag_name)

Invoke-WebRequest `
  -Uri $asset.browser_download_url `
  -Headers $headers `
  -OutFile $zipPath

Expand-Archive -LiteralPath $zipPath -DestinationPath $extractDir -Force

$rg = Get-ChildItem -LiteralPath $extractDir -Recurse -Filter "rg.exe" |
  Select-Object -First 1

if (-not $rg) {
  throw "Downloaded archive did not contain rg.exe."
}

Copy-Item -LiteralPath $rg.FullName -Destination (Join-Path $toolsDir "rg.exe") -Force

& (Join-Path $toolsDir "rg.exe") --version
