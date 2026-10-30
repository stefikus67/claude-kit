# claude-kit

A Claude Code setup for making Slovene short-form video, plus a set of thinking skills. Built by Stepan with Claude.

## What's inside
- **Video pipeline** (`tools/`):
  - `sl-stt`: Slovene speech to text with word timings, using the RSDO models from CLARIN.SI (Apache-2.0).
  - `reel`: cut proposals for Slovene speech, frame-accurate cuts, burned-in captions in 4 styles (HyperFrames), punch-ins, B-roll overlays, cover frame, English version.
  - `rembg`: local background removal (BiRefNet), for covers and product shots.
- **Prerequisites the setup installs:** Git, ffmpeg, Node.js, uv + Python 3.11, gitleaks, RTK.
- **Plugins** (installed by Claude from INSTALL.md): superpowers, frontend-design, context7, playwright, claude-security, and the guard-pack safety hooks.
- **Skills** (`skills/`, copied to `~/.claude/skills/`):
  - `director`: plans, scripts, edits and posts reels, based on a fact-checked virality playbook (`docs/`).
  - `prompt-forge`: briefs, prompts for any AI or tool, a writing check, Slovene proofreading.
  - `decoding-briefs`, `running-research-ops`, `forging-new-ideas`, `fact-checking-claims`, `winning-hackathons`, `council`.
  - `obsidian-markdown`, `obsidian-bases` (vendored from kepano/obsidian-skills, MIT).
- **Working rules** (`claude/CLAUDE.md`): merged into `~/.claude/CLAUDE.md`.

## Install
Paste this into Claude Code:
```
Install claude-kit: clone https://github.com/stefikus67/claude-kit to ~/claude-kit, then read ~/claude-kit/INSTALL.md and follow it to the end.
```
Or by hand: clone, then run `setup/setup.ps1` (Windows) or `setup/setup.sh` (macOS/Linux).

## Licences
Own code and skills: free to use. Vendored and adapted parts keep their licences: `skills/prompt-forge/NOTICES.md` (MIT, nidhinjs/prompt-master). Models: RSDO-DS2-ASR-E2E 2.0 and RSDO-DS2-P&C 3.6 (Apache-2.0, CLARIN.SI), downloaded at setup. HyperFrames (Apache-2.0) is installed from npm.
