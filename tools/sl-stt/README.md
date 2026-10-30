# sl-stt: Slovene speech to text with word timestamps (offline, CPU)

Built 2026-10-28 (Ultra Claude Phase 3). Evidence: Stepan's STT spike (not in the kit).

- **ASR:** RSDO-DS2-ASR-E2E 2.0 (CLARIN.SI 11356/1737, Apache-2.0). NeMo conformer-CTC, 630 h of ARTUR.
- **Punctuation and casing:** RSDO-DS2-P&C 3.6 (CLARIN.SI 11356/1735, Apache-2.0). SloBERTa, loaded through transformers because NeMo 3.0 dropped `nemo.collections.nlp`.
- **Venv:** Python 3.11 in `.venv`, with torch CPU, nemo_toolkit[asr] 3.0.0, transformers 5.2, num2words and pysubs2.
- **Models:** in `models/`, 930 MB. The SloBERTa config and tokenizer download once to `models/hf/`.

## Use
```bash
T=$HOME/claude-kit/tools/sl-stt
$T/.venv/Scripts/python.exe -X utf8 $T/sl_stt.py transcribe clip.mp4 -o out/
#  -> out/audio.wav (16 kHz mono), out/words.json, out/transcript.txt, out/captions.srt
# after fixing the transcript (names, numbers, glossary) in a copy of transcript.txt:
$T/.venv/Scripts/python.exe -X utf8 $T/sl_stt.py align out/audio.wav out/fixed.txt -o out/words_fixed.json --srt out/captions_fixed.srt
```
- `words.json`: `{"words": [{"w": "Robin", "s": 0.88, "e": 1.36}, ...], "duration": 51.92}`. Display words carry punctuation and casing. `transcribe` also writes `raw` (the ASR word); `align` writes `conf`.
- `align` re-times any corrected text against the audio by CTC forced alignment with the same model. Digits are spelled out with num2words (sl) for alignment and kept as digits for display. Words below 0.3 confidence are printed: those are the ones to look at.
- `--clean` runs ffmpeg highpass + afftdn + loudnorm first. **It raised WER from 15.1% to 17.9% on clean read speech**, so it is off by default. Try it only on noisy phone audio and compare.
- Audio longer than 100 s switches the conformer to local attention (128/128) so RAM stays flat. That path is **not yet tested** on real long audio.

## Measured (2026-10-28, i5-1334U, idle CPU, FLEURS clip A, 51.9 s clean read speech)
- WER 15.1%, the same transcript as the spike.
- Timings:
  - The first NeMo import plus model load is about 53 s.
  - Transcription is 10.6 s (RTF 0.21).
  - P&C is about 7 s including its load.
  - `align` takes about 60 s, mostly the model load.
- Aligned start times vs the ASR timestamps: median difference 0.12 s, p90 0.24 s.
- **Not tested:** spontaneous speech, noise, phone mic, long files, dialect. Stepan's own clip is the real test.

## Licences
Models: Apache-2.0 (RSDO, CLARIN.SI). SloBERTa tokenizer and config: EMBEDDIA/sloberta (CC-BY-SA-4.0 on HF; only the config and tokenizer are used, and the weights come from the RSDO .nemo). NeMo: Apache-2.0.
