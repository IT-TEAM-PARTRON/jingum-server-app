[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ProjectDir = $PSScriptRoot
$VenvPython = Join-Path $ProjectDir ".venv\Scripts\python.exe"
$Requirements = Join-Path $ProjectDir "requirements.txt"
$EnvFile = Join-Path $ProjectDir ".env"
$EnvExample = Join-Path $ProjectDir ".env.example"
$Ecosystem = Join-Path $ProjectDir "ecosystem.config.js"

Set-Location -LiteralPath $ProjectDir

if (-not (Get-Command node.exe -ErrorAction SilentlyContinue)) {
    throw "Node.js is not installed or is not available in PATH."
}

if (-not (Test-Path -LiteralPath $VenvPython)) {
    $SystemPython = Get-Command python.exe -ErrorAction SilentlyContinue
    if (-not $SystemPython) {
        throw "Python is not installed or is not available in PATH."
    }
    & $SystemPython.Source -m venv (Join-Path $ProjectDir ".venv")
}

& $VenvPython -m pip install --upgrade pip
& $VenvPython -m pip install -r $Requirements

if (-not (Test-Path -LiteralPath $EnvFile)) {
    Copy-Item -LiteralPath $EnvExample -Destination $EnvFile
    throw "Created .env from .env.example. Edit the MariaDB password/settings, then run this script again."
}
if ((Get-Content -Raw -LiteralPath $EnvFile) -match "change-this-password") {
    throw "The .env file still contains the example database password. Update DB_PASSWORD first."
}

$Pm2Command = Get-Command pm2.cmd -ErrorAction SilentlyContinue
if (-not $Pm2Command) {
    & npm.cmd install --global pm2
    $Pm2Command = Get-Command pm2.cmd -ErrorAction SilentlyContinue
}
if (-not $Pm2Command) {
    $DefaultPm2 = Join-Path $env:APPDATA "npm\pm2.cmd"
    if (Test-Path -LiteralPath $DefaultPm2) {
        $Pm2Path = $DefaultPm2
    } else {
        throw "PM2 was installed but pm2.cmd could not be located."
    }
} else {
    $Pm2Path = $Pm2Command.Source
}

& $Pm2Path describe "Jingum_Web" *> $null
if ($LASTEXITCODE -eq 0) {
    & $Pm2Path restart $Ecosystem --update-env
} else {
    & $Pm2Path start $Ecosystem
}

& $Pm2Path save
& $Pm2Path status

Write-Host ""
Write-Host "Deployment complete. PM2 command: $Pm2Path" -ForegroundColor Green
Write-Host "Test URL: http://127.0.0.1:8000/api/all"
Write-Host "Next: configure Windows Task Scheduler using pm2_resurrect_windows.ps1."
