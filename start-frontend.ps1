Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$frontendDir = Join-Path $PSScriptRoot "web-admin\frontend"

if (-not (Test-Path -LiteralPath $frontendDir)) {
    throw "Frontend directory not found: $frontendDir"
}

if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    throw "npm is not installed or not in PATH."
}

Set-Location -LiteralPath $frontendDir

if (-not (Test-Path -LiteralPath "node_modules")) {
    Write-Host "node_modules not found, installing dependencies..."
    npm install
}

Write-Host "Starting frontend dev server..."
npm run dev
