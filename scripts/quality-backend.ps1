$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$python = Join-Path $backend ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $python)) {
    $python = "python"
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock] $Command,
        [Parameter(Mandatory = $true)]
        [string] $Label
    )

    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw "$Label failed with exit code $LASTEXITCODE"
    }
}

$env:APP_ENV = "test"
$env:SECRET_KEY = "ci-only-secret-key-long-enough-for-database-tests"
$env:DEBUG = "False"
$env:ALLOWED_HOSTS = "localhost,testserver"
$env:CORS_ALLOWED_ORIGINS = "http://localhost:5173"
$env:DEMO_MODE = "False"
$env:CELERY_TASK_ALWAYS_EAGER = "True"

Push-Location $backend
try {
    Invoke-Checked { & $python -m ruff check . --no-cache } "Backend ruff"
    Invoke-Checked { & $python manage.py check } "Backend system check"
    Invoke-Checked { & $python manage.py makemigrations --check --dry-run } "Backend migration check"
    Invoke-Checked { & $python manage.py test } "Backend tests"
}
finally {
    Pop-Location
}
