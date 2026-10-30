# reel: raw Slovene clips to a 1080x1920 reel with burned-in captions

Built 2026-10-28 (Ultra Claude Phase 3 prep). The director skill (`~/.claude/skills/director`) drives it. Tested on FLEURS clean read speech only.

| Part | What | Tested |
|---|---|---|
| `reel.py ingest / render / translate` | The whole pipeline (see the docstring) | End to end on a 52.6 s test take: cuts, 4 text fixes, captions, punch-ins, cover, English version → `tests/e2e/out/` |
| `cut/cutlist.py` | Slovene-aware cut proposals: pauses, lead-in/out, false starts and restarts, "še enkrat" cues, fillers, repeats | Pauses and false start found; no auto cut in speech (`tests/cut/RESULT.md`) |
| `cut/render_cut.py` | Frame-accurate join of the kept segments, 12 ms audio fades, plus a source↔output time map | Re-transcribed output: no trace of the false start |
| `captions/render_captions.py` + `template.html` | HyperFrames caption renderer in 4 styles (klasika, pill, highlight, pop); finished preview over a video or photo, or a transparent layer (.webm/.mov); `--at` snapshot mode | 4 samples in `samples/`, č/š/ž correct |
| `broll/index_broll.py` | Shots per B-roll clip (PySceneDetect 0.7.2 AdaptiveDetector), labelled keyframe contact sheets, index.json for the director | 2 test clips: 1 and 3 shots found, correct times |
| `.venv` | PySceneDetect + librosa (pipeline); rostrum 0.1.0 + auto-editor (cutting comparison only; Stepan chose to keep them, 28.10) | See `tests/cut/RESULT.md` |
| `node_modules` | hyperframes 0.8.209 (Apache-2.0), local install, telemetry disabled, **no global skills or plugin** | |

## Speed (i5-1334U, CPU only)
- STT: about 50 s model load, plus RTF about 0.2.
- Cut and normalise: seconds.
- HyperFrames caption render: about 2 min per 15 s, so **about 8 min per 60 s reel**. Use `--draft` while iterating.

## Needs internet at render
The template loads Google Fonts (Montserrat, Poppins, Inter) and GSAP from jsDelivr. Offline fallback: the libass ASS route from the STT spike (`Stepan's STT spike (not in the kit)`).

## Not built yet
Music and beat sync (librosa installed, not wired), and automatic B-roll choice (the director picks from the index by hand). Built since the first test: punch-ins on alternate sentences, B-roll `overlays[]` (video or photo with push-in), cover frame, `translate` + `render --lang en`.
