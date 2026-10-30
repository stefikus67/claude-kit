# claude-kit setup for Windows (CPU only). Run in Windows PowerShell 5.1 or PowerShell 7:
#   powershell -ExecutionPolicy Bypass -File "$HOME\claude-kit\setup\setup.ps1"
# Installs ffmpeg, Node.js LTS and uv (winget), builds the two Python 3.11 venvs from the pinned lists, downloads the
# Slovene speech models, installs HyperFrames locally, installs the skills + CLAUDE.md block, then runs smoke tests.
# Safe to run again: every step skips what is already done.
# Test override: $env:CLAUDE_KIT_CLAUDE_DIR = another folder instead of ~/.claude.

$ErrorActionPreference = "Stop"
$Kit  = Split-Path -Parent $PSScriptRoot
$Reel = Join-Path $Kit "tools\reel"
$Stt  = Join-Path $Kit "tools\sl-stt"
$TorchIndex = "https://download.pytorch.org/whl/cpu"
$ClaudeDir = if ($env:CLAUDE_KIT_CLAUDE_DIR) { $env:CLAUDE_KIT_CLAUDE_DIR } else { Join-Path $HOME ".claude" }

function Step($msg) { Write-Host ""; Write-Host "== $msg" -ForegroundColor Cyan }
function Fail($msg) { Write-Host "FAILED: $msg" -ForegroundColor Red; exit 1 }
function Have($cmd) { [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }
function RefreshPath {
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User") + ";" + (Join-Path $HOME ".local\bin") + ";" + $env:Path
}

Step "Checking the kit ($Kit)"
foreach ($p in @("$Reel\reel.py", "$Reel\requirements-lock.txt", "$Reel\package-lock.json",
                 "$Stt\sl_stt.py", "$Stt\requirements-lock.txt", "$Kit\skills\director\SKILL.md")) {
    if (-not (Test-Path $p)) { Fail "missing $p (clone the whole repo to $Kit)" }
}
Write-Host "kit OK"

Step "Installing Git, ffmpeg, Node.js LTS, uv (Python), gitleaks and RTK (winget)"
$pkgs = @(
    @{ cmd = "git";      id = "Git.Git" },
    @{ cmd = "ffmpeg";   id = "Gyan.FFmpeg" },
    @{ cmd = "node";     id = "OpenJS.NodeJS.LTS" },
    @{ cmd = "uv";       id = "astral-sh.uv" },
    @{ cmd = "gitleaks"; id = "Gitleaks.Gitleaks" },
    @{ cmd = "rtk";      id = "rtk-ai.rtk" }
)
foreach ($p in $pkgs) {
    if (Have $p.cmd) { Write-Host "$($p.cmd) already installed"; continue }
    if (-not (Have "winget")) { Fail "winget not found: install 'App Installer' from the Microsoft Store, or install $($p.cmd) by hand" }
    winget install --id $p.id -e --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { Fail "winget install $($p.id)" }
    RefreshPath
}
RefreshPath
foreach ($c in @("git", "ffmpeg", "ffprobe", "node", "npm", "uv", "gitleaks", "rtk")) {
    if (-not (Have $c)) { Fail "$c is not on PATH: open a new PowerShell window and run this script again" }
}
rtk telemetry disable | Out-Null
Write-Host "RTK telemetry off"

Step "Python 3.11 venv for sl-stt (torch CPU + NeMo; ~2 GB download, 5-15 min)"
if (-not (Test-Path "$Stt\.venv\Scripts\python.exe")) {
    uv venv --python 3.11 "$Stt\.venv"
    if ($LASTEXITCODE -ne 0) { Fail "uv venv sl-stt" }
}
uv pip install --python "$Stt\.venv\Scripts\python.exe" -r "$Stt\requirements-lock.txt" --extra-index-url $TorchIndex --index-strategy unsafe-best-match
if ($LASTEXITCODE -ne 0) { Fail "pip install sl-stt" }

Step "Slovene speech models from CLARIN.SI (~860 MB)"
& "$Stt\.venv\Scripts\python.exe" -X utf8 "$PSScriptRoot\fetch_models.py"
if ($LASTEXITCODE -ne 0) { Fail "model download" }

Step "Python 3.11 venv for reel (PySceneDetect, librosa)"
if (-not (Test-Path "$Reel\.venv\Scripts\python.exe")) {
    uv venv --python 3.11 "$Reel\.venv"
    if ($LASTEXITCODE -ne 0) { Fail "uv venv reel" }
}
uv pip install --python "$Reel\.venv\Scripts\python.exe" -r "$Reel\requirements-lock.txt"
if ($LASTEXITCODE -ne 0) { Fail "pip install reel" }

Step "Python 3.11 venv for rembg (background removal; BiRefNet model downloads on first use)"
$Rembg = Join-Path $Kit "tools\rembg"
if (-not (Test-Path "$Rembg\.venv\Scripts\python.exe")) {
    uv venv --python 3.11 "$Rembg\.venv"
    if ($LASTEXITCODE -ne 0) { Fail "uv venv rembg" }
}
uv pip install --python "$Rembg\.venv\Scripts\python.exe" -r "$Rembg\requirements-lock.txt"
if ($LASTEXITCODE -ne 0) { Fail "pip install rembg" }

Step "HyperFrames (caption renderer, local npm install, telemetry off)"
$hf = Join-Path $HOME ".hyperframes"
if (-not (Test-Path "$hf\config.json")) {
    New-Item -ItemType Directory -Force $hf | Out-Null
    '{ "telemetryEnabled": false, "telemetryNoticeShown": true }' | Out-File -Encoding ascii "$hf\config.json"
}
Push-Location $Reel
npm ci --no-fund --no-audit
$rc = $LASTEXITCODE
Pop-Location
if ($rc -ne 0) { Fail "npm ci" }

Step "Claude Code: skills, CLAUDE.md block, settings"
& "$Reel\.venv\Scripts\python.exe" -X utf8 "$PSScriptRoot\configure_claude.py" --claude-dir $ClaudeDir
if ($LASTEXITCODE -ne 0) { Fail "configure_claude" }

Step "Smoke test 1/2: Slovene speech to text (first run loads the model, ~1-6 min)"
$out = Join-Path $env:TEMP "claude-kit-smoke"
& "$Stt\.venv\Scripts\python.exe" -X utf8 "$Stt\sl_stt.py" transcribe "$Stt\test\clip.wav" -o $out
if ($LASTEXITCODE -ne 0) { Fail "sl-stt transcribe" }
Get-Content "$out\transcript.txt" -Encoding UTF8 | Select-Object -First 3

Step "Smoke test 2/2: caption renderer"
Push-Location $Reel
$env:HYPERFRAMES_SKIP_SKILLS = "1"
npx hyperframes --version
$rc = $LASTEXITCODE
Pop-Location
if ($rc -ne 0) { Fail "hyperframes" }
& "$Rembg\.venv\Scripts\rembg.exe" --help | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "rembg" }
Write-Host "rembg OK"

Write-Host ""
Write-Host "DONE. claude-kit ready. Restart Claude Code so it loads the new skills." -ForegroundColor Green
