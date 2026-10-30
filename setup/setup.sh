#!/usr/bin/env bash
# claude-kit setup for macOS (Homebrew) or Linux (apt). CPU only.
#   bash ~/claude-kit/setup/setup.sh
# Same steps as setup.ps1: ffmpeg + Node + uv, two Python 3.11 venvs from the pinned lists, Slovene models,
# HyperFrames, skills + CLAUDE.md block, smoke tests. Safe to run again.
# NOT yet run on a Mac: if a pinned package has no wheel for this machine, relax that one pin and say so.
# Test override: CLAUDE_KIT_CLAUDE_DIR=<dir> instead of ~/.claude.
set -euo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"
REEL="$KIT/tools/reel"; STT="$KIT/tools/sl-stt"
CLAUDE_DIR="${CLAUDE_KIT_CLAUDE_DIR:-$HOME/.claude}"
step() { printf '\n== %s\n' "$1"; }
fail() { echo "FAILED: $1"; exit 1; }
have() { command -v "$1" >/dev/null 2>&1; }

step "Checking the kit ($KIT)"
for p in "$REEL/reel.py" "$REEL/requirements-lock.txt" "$REEL/package-lock.json" "$STT/sl_stt.py" "$STT/requirements-lock.txt" "$KIT/skills/director/SKILL.md"; do
  [ -e "$p" ] || fail "missing $p (clone the whole repo to $KIT)"
done

step "Installing ffmpeg, Node.js and uv"
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
  have brew || fail "Homebrew missing: install it from https://brew.sh (the user runs the installer), then re-run"
  have git || brew install git
  have ffmpeg || brew install ffmpeg
  have node || brew install node
  have uv || brew install uv
  have gitleaks || brew install gitleaks
  have rtk || brew install rtk || echo "rtk: not in Homebrew here, see https://github.com/rtk-ai/rtk (optional)"
else
  have git || { sudo apt-get update && sudo apt-get install -y git; }
  have ffmpeg || { sudo apt-get update && sudo apt-get install -y ffmpeg; }
  have node || { sudo apt-get install -y nodejs npm; }
  have uv || { curl -LsSf https://astral.sh/uv/install.sh | sh; export PATH="$HOME/.local/bin:$PATH"; }
  have gitleaks || echo "gitleaks: optional, install from https://github.com/gitleaks/gitleaks/releases"
  have rtk || echo "rtk: optional, see https://github.com/rtk-ai/rtk"
fi
for c in git ffmpeg ffprobe node npm uv; do have "$c" || fail "$c not on PATH (open a new terminal and re-run)"; done
have rtk && rtk telemetry disable >/dev/null && echo "RTK telemetry off"

step "Python 3.11 venv for sl-stt (torch CPU + NeMo; ~2 GB, 5-15 min)"
[ -x "$STT/.venv/bin/python" ] || uv venv --python 3.11 "$STT/.venv"
if [ "$OS" = "Darwin" ]; then
  # macOS wheels have no +cpu tag and come from PyPI
  sed 's/+cpu//' "$STT/requirements-lock.txt" > "$STT/.venv/requirements-mac.txt"
  uv pip install --python "$STT/.venv/bin/python" -r "$STT/.venv/requirements-mac.txt"
else
  uv pip install --python "$STT/.venv/bin/python" -r "$STT/requirements-lock.txt" --extra-index-url https://download.pytorch.org/whl/cpu --index-strategy unsafe-best-match
fi

step "Slovene speech models from CLARIN.SI (~860 MB)"
"$STT/.venv/bin/python" -X utf8 "$KIT/setup/fetch_models.py"

step "Python 3.11 venv for reel"
[ -x "$REEL/.venv/bin/python" ] || uv venv --python 3.11 "$REEL/.venv"
uv pip install --python "$REEL/.venv/bin/python" -r "$REEL/requirements-lock.txt"

step "Python 3.11 venv for rembg (background removal; model downloads on first use)"
REMBG="$KIT/tools/rembg"
[ -x "$REMBG/.venv/bin/python" ] || uv venv --python 3.11 "$REMBG/.venv"
uv pip install --python "$REMBG/.venv/bin/python" -r "$REMBG/requirements-lock.txt"

step "HyperFrames (local npm install, telemetry off)"
mkdir -p "$HOME/.hyperframes"
[ -f "$HOME/.hyperframes/config.json" ] || echo '{ "telemetryEnabled": false, "telemetryNoticeShown": true }' > "$HOME/.hyperframes/config.json"
(cd "$REEL" && npm ci --no-fund --no-audit)

step "Claude Code: skills, CLAUDE.md block, settings"
"$REEL/.venv/bin/python" -X utf8 "$KIT/setup/configure_claude.py" --claude-dir "$CLAUDE_DIR"

step "Smoke test 1/2: Slovene speech to text (first run ~1-6 min)"
OUT="${TMPDIR:-/tmp}/claude-kit-smoke"
"$STT/.venv/bin/python" -X utf8 "$STT/sl_stt.py" transcribe "$STT/test/clip.wav" -o "$OUT"
head -3 "$OUT/transcript.txt"

step "Smoke test 2/2: caption renderer"
(cd "$REEL" && HYPERFRAMES_SKIP_SKILLS=1 npx hyperframes --version)
"$REMBG/.venv/bin/rembg" --help >/dev/null && echo "rembg OK"

printf '\nDONE. claude-kit ready. Restart Claude Code so it loads the new skills.\n'
