# INSTALL (for Claude Code: follow this to the end)

You are installing claude-kit on the user's computer. The user is Gaber (video editor). Work through the steps yourself. Ask him only for what only he can do (Homebrew password, a click in the browser, a restart). Keep him posted in one line per step, in his language.

Total: about 30-45 min, mostly downloads (~3 GB). No paid tools, no accounts needed. CPU is fine.

## 1. The repo
- It must sit at `~/claude-kit` (Windows: `%USERPROFILE%\claude-kit`). If it is missing: `git clone https://github.com/stefikus67/claude-kit ~/claude-kit`. If git is missing, download `https://github.com/stefikus67/claude-kit/archive/refs/heads/main.zip` and unpack it so that `~/claude-kit/INSTALL.md` exists.
- If it already exists: `git -C ~/claude-kit pull`.

## 2. Setup script (long: run it in the background and check on it)
- **Windows:** `powershell -ExecutionPolicy Bypass -File "$HOME\claude-kit\setup\setup.ps1"`
- **macOS / Linux:** `bash ~/claude-kit/setup/setup.sh`

It installs Git, ffmpeg, Node.js, uv (which brings Python 3.11), gitleaks and RTK; builds three Python 3.11 venvs (`tools/sl-stt/.venv`, `tools/reel/.venv`, `tools/rembg/.venv`); downloads the Slovene speech models from CLARIN.SI; installs HyperFrames locally; copies the skills to `~/.claude/skills/`; merges a block into `~/.claude/CLAUDE.md` (the rest of that file is kept); sets `"enableWorkflows": true` in `~/.claude/settings.json` (backup written); and runs two smoke tests.

If it stops: read the error, fix the cause on this machine, run it again (every step skips what is done). Typical fixes:
- "not on PATH" right after winget: open a fresh shell (or refresh PATH) and re-run.
- macOS: a pinned package has no wheel for this Mac (arm64). Relax only that pin in the generated `tools/sl-stt/.venv/requirements-mac.txt` (or `tools/reel/requirements-lock.txt`), re-run, and tell Gaber which pin you changed.
- Model download interrupted: re-run, it resumes per model.
Never skip the smoke tests, and never mark a failed step as done.

## 3. Plugins, RTK hook, safety guard (in this order)
**a. Plugins from the official Anthropic marketplace** (`claude-plugins-official`):
```
claude plugin install superpowers@claude-plugins-official
claude plugin install frontend-design@claude-plugins-official
claude plugin install context7@claude-plugins-official
claude plugin install playwright@claude-plugins-official
claude plugin install claude-security@claude-plugins-official
```
- superpowers: brainstorming, plans, debugging, TDD, verification.
- frontend-design: any UI.
- context7: current library docs.
- playwright: browser automation.
- claude-security: security reviews.

If the CLI refuses or the marketplace is unknown, run `claude plugin marketplace add anthropics/claude-plugins-official` first. If it still fails, give Gaber the same lines as `/plugin install ...` to type into Claude Code himself.

**b. RTK hook** (shortens command output so Claude spends fewer tokens; telemetry already off): `rtk init -g --hook-only --auto-patch`. Skip it if `rtk` is not installed (it is optional on Mac and Linux).

**c. Safety guard, last** (it blocks dangerous commands, reading secrets, and Claude editing its own config): `guard-pack` from karanb192/claude-code-hooks (MIT).
```
claude plugin marketplace add karanb192/claude-code-hooks
claude plugin install guard-pack@claude-code-hooks
```
Install it last: afterwards Claude can no longer change its own settings, so later config changes are Gaber's to paste. Tell him that in one line.

## 4. Done test (all must hold; show Gaber the result)
- [ ] `~/.claude/skills/` contains: council, decoding-briefs, director, fact-checking-claims, forging-new-ideas, obsidian-bases, obsidian-markdown, prompt-forge, running-research-ops, winning-hackathons.
- [ ] The setup printed "rembg OK" (background removal: `tools/rembg/README.md`).
- [ ] `~/.claude/CLAUDE.md` contains the `claude-kit:start` block.
- [ ] Smoke test 1 printed a Slovene transcript of `tools/sl-stt/test/clip.wav` (readable Slovene sentences).
- [ ] Smoke test 2 printed a HyperFrames version.
- [ ] The five plugins and guard-pack installed (or Gaber has the lines to type); RTK hook on, or skipped with the reason.
- [ ] `git --version`, `ffmpeg -version`, `node --version` and `uv --version` work in a new shell.

## 5. Footage
Raw clips come from Stepan through a Google Drive folder (the link is in Gaber's prompt or email). Claude cannot sign in to Google for him:
1. Open the folder link in his browser (Windows `start "" "<link>"`, macOS `open "<link>"`).
2. Ask him to select all files and click Download (Drive zips them), or to drag them out with Google Drive for desktop.
3. Make the project folder `~/claude-kit/reels/<yyyy-mm-dd>-<short-name>/intake/` and move or unzip the clips there (find the zip in Downloads yourself).
4. List each clip with `ffprobe` (duration, resolution, fps, audio yes/no).
Never ask for his Google password.

## 6. Finish
- Tell Gaber to restart Claude Code (the new skills and CLAUDE.md load at start) and to open `~/claude-kit` as the folder.
- Report in his language: what is installed, which done-test items passed, anything that failed or that you changed, and the next step: "say which reel to make from the footage, and the director skill takes it from there".
- First real edit: `director` skill → `references/pipeline.md` (ingest → review → render). Speech recognition was tested on clean read speech only, so the first real clip is the real test. Check names and numbers in REVIEW.md before rendering.
