# Start the API (http://localhost:5000) and the Vite dev server (http://localhost:5173, /api proxied to Flask).
# Run from anywhere:  powershell -File scripts/dev.ps1
$root = Split-Path -Parent $PSScriptRoot
$py = Join-Path (Split-Path -Parent $root) ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }
Start-Process $py -ArgumentList "-m", "pmo" -WorkingDirectory $root
Set-Location (Join-Path $root "frontend")
npm run dev
