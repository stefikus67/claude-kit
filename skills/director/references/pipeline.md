# Edit pipeline (raw clips to reel)

Tools live in `~/claude-kit/tools/` (built 2026-10-28):
- `sl-stt/` for Slovene words with forced-aligned timings
- `reel/` for cuts, captions and render

They were tested on FLEURS clean read speech only. Treat Stepan's first real clip as the test.

```bash
R=$HOME/claude-kit/tools/reel
# "python" below = the reel venv: $R/.venv/Scripts/python.exe (Windows) or $R/.venv/bin/python (Mac/Linux)
python -X utf8 $R/reel.py ingest <project-dir> <clip1.mp4> [clip2.mp4 ...]   # about 1.5 min per minute of footage
#  -> <project>/REVIEW.md, <project>/edl.json, work/<clip>/{words.json, cuts.json, captions.srt}
python -X utf8 $R/reel.py render <project-dir> [--draft]                     # about 8 min per 60 s reel (HyperFrames on CPU)
#  -> <project>/out/reel.mp4 (1080x1920, 30 fps, captions burned in, punch-ins), reel.srt, reel-frames.png, reel-cover.jpg
python -X utf8 $R/reel.py translate <project-dir>     # -> work/en_chunks.json: fill every "en" (the director translates)
python -X utf8 $R/reel.py render <project-dir> --lang en   # -> out/reel-en.mp4, same cut, English captions
```

## Review (the director's job between ingest and render)
1. Read `REVIEW.md`, which holds the transcript with times, ⚠ low-confidence words, and the cut table.
2. Decide **every `propose` cut**: `edl.json` → `clips[].decisions: {"retake-07": "keep"}`.
   - Auto cuts apply unless set to `"keep"`.
   - `retake` with 2 matching words is often a natural repetition, so keep it.
   - `cue` cuts back to the start of the interrupted sentence; check the restart is complete.
3. Fix the text: `clips[].fixes: {"Utopi": "Uthappa", "nambarvan": "Number One"}`.
   - Matching is per word and ignores case and trailing punctuation.
   - Names, brands, numbers and the glossary (Tivoli, Biennale, Kaval, Ljubljana place names) go here.
   - At render, the fixed text is re-aligned to the audio, so timings stay exact.
4. Clip order = the order of `clips[]`. Remove a clip by deleting it from the list.
5. Captions: `captions.style`:
   - `klasika`: white with an outline, phrase by phrase
   - `pill`: a light pill; words darken as they're spoken
   - `highlight`: uppercase; the active word gets a red box
   - `pop`: 1-3 big words; the active word in yellow
   - `none`: no captions
   - Optional settings: `accent` (hex) and `top` (y of the caption band, default 1180, which keeps captions clear of the Instagram UI).
   - Samples: `~/claude-kit/tools/reel/samples/look-*.mp4`.
6. Render, then **look at `reel-frames.png`** and spot-check the mp4 before calling it done.

## Known limits
- **Punch-ins:** a 115% zoom on every second sentence (`export.punch_in`, `export.punch_scale`; set `punch_in: false` for vlog or promo footage).
- **B-roll:** `edl.json` → `overlays: [{"src": "intake/broll/x.mp4", "at": 10.9, "dur": 2.4, "from": 3.0}]`:
  - `at` is in reel time (read it from `work/reel_words.json`). `from` is the start inside the clip (video only).
  - Photos get a slow push-in. The main audio keeps playing, and captions stay on top.
  - Place B-roll on the noun it shows, 1-2.5 s each.
- **Finding B-roll:** `$R/.venv/Scripts/python.exe $R/broll/index_broll.py <folder>` splits each clip into shots (PySceneDetect) and writes `_index/<clip>-sheet.jpg` (labelled keyframes) and `index.json`. Look at the sheets, add tags, and take `from`/`dur` from a shot. Tested on 2 clips: 14 s.
- No music or beat sync yet. librosa is installed in `$R/.venv` but not wired.
- Raw CTC word timestamps are early after pauses, which is why `sl-stt` force-aligns everything. Don't feed raw ASR times to the cutter.
- The HyperFrames render pulls Google Fonts and GSAP from a CDN, so it needs internet. libass + ffmpeg is the offline fallback (spike `make_captions.py`).
- Audio longer than 100 s uses local attention in the ASR (untested on real long audio).
- **English version:** timings are per caption chunk; words inside a chunk are spread by length, so English captions don't follow word-exact timing. Translate meaning per chunk, keeping the length similar.
- **Cover:** `reel-cover.jpg` is the frame 0.5 s into the first word. Check it in the 4:5 grid crop, and pick another frame if the face is mid-blink.
