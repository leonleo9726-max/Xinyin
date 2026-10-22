param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("mysql", "production_mysql", "redis", "rabbitmq")]
    [string]$Server
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$envFile = Join-Path $projectRoot ".env"

if (-not (Test-Path -LiteralPath $envFile -PathType Leaf)) {
    throw "Missing MCP environment file: $envFile"
}

$settings = @{}
foreach ($rawLine in Get-Content -LiteralPath $envFile) {
    $line = $rawLine.Trim()
    if ($line.Length -eq 0 -or $line.StartsWith("#")) {
        continue
    }

    $separator = $line.IndexOf("=")
    if ($separator -le 0) {
        continue
    }

    $name = $line.Substring(0, $separator).Trim()
    $settings[$name] = $line.Substring($separator + 1)
}

function Get-RequiredSetting([string]$Name) {
    if (-not $settings.ContainsKey($Name) -or [string]::IsNullOrWhiteSpace($settings[$Name])) {
        throw "Missing required MCP setting: $Name"
    }

    return $settings[$Name]
}

switch ($Server) {
    "mysql" {
        $env:MYSQL_HOST = Get-RequiredSetting "MYSQL_HOST"
        $env:MYSQL_PORT = Get-RequiredSetting "MYSQL_PORT"
        $env:MYSQL_USER = Get-RequiredSetting "MYSQL_USER"
        $env:MYSQL_PASS = Get-RequiredSetting "MYSQL_PASSWORD"
        $env:MYSQL_DB = Get-RequiredSetting "MYSQL_DATABASE"
        & npx -y "@benborla29/mcp-server-mysql"
    }
    "production_mysql" {
        $env:MYSQL_HOST = Get-RequiredSetting "PROD_MYSQL_HOST"
        $env:MYSQL_PORT = Get-RequiredSetting "PROD_MYSQL_PORT"
        $env:MYSQL_USER = Get-RequiredSetting "PROD_MYSQL_USER"
        $env:MYSQL_PASS = Get-RequiredSetting "PROD_MYSQL_PASSWORD"
        $env:MYSQL_DB = Get-RequiredSetting "PROD_MYSQL_DATABASE"
        & npx -y "@benborla29/mcp-server-mysql"
    }
    "redis" {
        $env:REDIS_URL = Get-RequiredSetting "REDIS_URL"
        & npx -y "@easy-mcps/redis-mcp-server@latest"
    }
    "rabbitmq" {
        $managementUri = [Uri](Get-RequiredSetting "RABBITMQ_MANAGEMENT_URL")
        $env:RABBITMQ_HOST = $managementUri.Host
        $env:RABBITMQ_MANAGEMENT_PORT = $managementUri.Port
        $env:RABBITMQ_PROTOCOL = $managementUri.Scheme
        $env:RABBITMQ_USERNAME = Get-RequiredSetting "RABBITMQ_MANAGEMENT_USERNAME"
        $env:RABBITMQ_PASSWORD = Get-RequiredSetting "RABBITMQ_MANAGEMENT_PASSWORD"
        & npx -y "rabbitmq-mcp"
    }
}

exit $LASTEXITCODE
