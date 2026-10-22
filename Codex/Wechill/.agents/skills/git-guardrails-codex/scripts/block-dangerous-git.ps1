$inputJson = [Console]::In.ReadToEnd()

try {
    $payload = $inputJson | ConvertFrom-Json
} catch {
    exit 0
}

$command = $null

if ($payload.PSObject.Properties.Name -contains 'tool_input' -and $payload.tool_input.PSObject.Properties.Name -contains 'command') {
    $command = [string]$payload.tool_input.command
} elseif ($payload.PSObject.Properties.Name -contains 'toolInput' -and $payload.toolInput.PSObject.Properties.Name -contains 'command') {
    $command = [string]$payload.toolInput.command
} elseif ($payload.PSObject.Properties.Name -contains 'input' -and $payload.input.PSObject.Properties.Name -contains 'command') {
    $command = [string]$payload.input.command
} elseif ($payload.PSObject.Properties.Name -contains 'command') {
    $command = [string]$payload.command
}

if ([string]::IsNullOrWhiteSpace($command)) {
    exit 0
}

$dangerousPatterns = @(
    '\bgit\s+push\b',
    '\bgit\s+push\b.*\s--force(?:-with-lease)?\b',
    '\bgit\s+reset\s+--hard\b',
    '\bgit\s+clean\s+-[A-Za-z]*f[A-Za-z]*\b',
    '\bgit\s+branch\s+-D\b',
    '\bgit\s+checkout\s+\.\b',
    '\bgit\s+restore\s+\.\b'
)

foreach ($pattern in $dangerousPatterns) {
    if ($command -match $pattern) {
        [Console]::Error.WriteLine("BLOCKED: '$command' matches dangerous pattern '$pattern'. The user has prevented this command.")
        exit 2
    }
}

exit 0
