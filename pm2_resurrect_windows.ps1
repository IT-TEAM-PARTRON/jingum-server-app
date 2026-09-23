$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot

$Pm2Path = Join-Path $env:APPDATA "npm\pm2.cmd"
if (-not (Test-Path -LiteralPath $Pm2Path)) {
    $Pm2Command = Get-Command pm2.cmd -ErrorAction SilentlyContinue
    if (-not $Pm2Command) {
        throw "pm2.cmd was not found for Windows user $env:USERNAME."
    }
    $Pm2Path = $Pm2Command.Source
}

& $Pm2Path resurrect
if ($LASTEXITCODE -ne 0) {
    throw "pm2 resurrect failed with exit code $LASTEXITCODE."
}
