"""Slovene speech-to-text with word timestamps, offline on CPU.

  transcribe IN [-o DIR]       audio/video -> DIR/{audio.wav, words.json, transcript.txt, captions.srt}
  align AUDIO TEXT -o OUT      re-time a corrected transcript (e.g. after a Claude post-pass) -> words.json

Models (CLARIN.SI, Apache-2.0): RSDO-DS2-ASR-E2E 2.0 (11356/1737) and RSDO-DS2-P&C 3.6 (11356/1735), in models/.
words.json = {"words": [{"w": display word, "s": start s, "e": end s}], "source": ..., "duration": s}
"""
import argparse, json, os, re, subprocess, sys, time, unicodedata
import warnings; warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, "models")
os.environ.setdefault("HF_HOME", os.path.join(MODELS, "hf"))
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
ASR_NEMO = os.path.join(MODELS, "rsdo-asr-2.0.nemo")
PC_NEMO = os.path.join(MODELS, "rsdo-pc-3.6.nemo")
LONG_S = 100  # above this, switch the conformer to local attention so RAM stays flat
CLEAN = "highpass=f=80,afftdn=nf=-25,loudnorm=I=-16:TP=-1.5:LRA=11"


def log(*a): print("[sl-stt]", *a, file=sys.stderr, flush=True)


def to_wav(src, dst, clean=True):
    af = ["-af", CLEAN] if clean else []
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", src, "-vn", *af, "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", dst], check=True)


def duration(wav):
    import soundfile as sf
    return sf.info(wav).duration


def load_asr(dur):
    import torch, logging
    logging.getLogger("nemo_logger").setLevel(logging.ERROR)
    from nemo.collections.asr.models import ASRModel
    torch.set_num_threads(os.cpu_count() or 4)
    m = ASRModel.restore_from(ASR_NEMO, map_location="cpu"); m.eval()
    if dur > LONG_S:
        m.change_attention_model("rel_pos_local_attn", [128, 128])
        log(f"{dur:.0f} s audio: local attention")
    return m


# ---------- punctuation + casing (RSDO-DS2-P&C 3.6 without nemo.collections.nlp, gone in NeMo 3.0) ----------
PUNCT = ["", "!", ",", ".", "?"]


class PC:
    def __init__(self):
        import tarfile, torch
        from transformers import AutoConfig, AutoModel, PreTrainedTokenizerFast
        from huggingface_hub import hf_hub_download
        xdir = os.path.join(MODELS, "rsdo-pc-3.6")
        ck = os.path.join(xdir, "model_weights.ckpt")
        if not os.path.exists(ck):
            os.makedirs(xdir, exist_ok=True)
            with tarfile.open(PC_NEMO) as t:
                t.extract("./model_weights.ckpt", xdir, filter="data")
        cfg = AutoConfig.from_pretrained("EMBEDDIA/sloberta")  # config + tokenizer only; weights come from the .nemo
        # CamembertTokenizer in transformers 5.x crashes on this repo; raw tokenizer.json = same pieces as the .nemo spm model
        self.tok = PreTrainedTokenizerFast(tokenizer_file=hf_hub_download("EMBEDDIA/sloberta", "tokenizer.json"), bos_token="<s>", eos_token="</s>",
                                           unk_token="<unk>", pad_token="<pad>", cls_token="<s>", sep_token="</s>", mask_token="<mask>")
        self.enc = AutoModel.from_config(cfg, add_pooling_layer=False)
        sd = torch.load(ck, map_location="cpu", weights_only=True)
        res = torch.nn.Module.load_state_dict(self.enc, {k[11:]: v for k, v in sd.items() if k.startswith("bert_model.") and "pooler" not in k}, strict=False)
        assert not [k for k in res.missing_keys if "position_ids" not in k], res.missing_keys
        self.punct, self.capit = torch.nn.Linear(768, 5), torch.nn.Linear(768, 2)
        for head, name in ((self.punct, "punct"), (self.capit, "capit")):
            head.load_state_dict({"weight": sd[f"{name}_classifier.mlp.layer0.weight"], "bias": sd[f"{name}_classifier.mlp.layer0.bias"]})
        self.enc.eval()

    def _window(self, words):
        import torch
        with torch.inference_mode():
            b = self.tok(words, is_split_into_words=True, return_tensors="pt", truncation=True, max_length=512)
            h = self.enc(**b).last_hidden_state[0]
            p, c = self.punct(h).argmax(-1).tolist(), self.capit(h).argmax(-1).tolist()
        first = {}
        for i, w in enumerate(b.word_ids()):
            if w is not None and w not in first: first[w] = i
        return [(PUNCT[p[first[j]]], c[first[j]] == 1) if j in first else ("", False) for j in range(len(words))]

    def __call__(self, words, size=120, step=90):
        """label per word; overlapping windows, each word keeps the label from the window where it sits farthest from an edge"""
        best = [None] * len(words)
        starts = list(range(0, max(1, len(words) - size + step), step)) or [0]
        for s0 in starts:
            win = words[s0:s0 + size]
            for k, lab in enumerate(self._window(win)):
                j, margin = s0 + k, min(k, len(win) - 1 - k) if s0 + size < len(words) else k
                if best[j] is None or margin > best[j][0]: best[j] = (margin, lab)
        return [b[1] for b in best]


def apply_pc(words, labels):
    out = []
    for w, (p, cap) in zip(words, labels):
        out.append((w[:1].upper() + w[1:] if cap else w) + p)
    if out and not re.search(r"[.!?]$", out[-1]):  # streaming model never sees the end
        out[-1] = out[-1].rstrip(",") + "."
    return out


# ---------- captions ----------
def chunks_of(words, maxc=32, gap=0.35):
    chunks, cur = [], []
    clen = lambda ws: len(" ".join(w["w"] for w in ws))
    for w in words:
        if cur and (clen(cur + [w]) > maxc or w["s"] - cur[-1]["e"] > gap):
            chunks.append(cur); cur = []
        cur.append(w)
        if re.search(r"[.!?]$", w["w"]) or (re.search(r"[,;:]$", w["w"]) and clen(cur) >= 18):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    return chunks


def write_srt(words, path, maxc=32):
    def ts(x):
        ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
    ch = chunks_of(words, maxc)
    with open(path, "w", encoding="utf-8") as f:
        for n, ws in enumerate(ch, 1):
            en = ws[-1]["e"] if n == len(ch) else min(max(ws[-1]["e"], ws[0]["s"] + 0.4), ch[n][0]["s"])
            f.write(f"{n}\n{ts(ws[0]['s'])} --> {ts(en)}\n{' '.join(w['w'] for w in ws)}\n\n")


def clamp_ends(words):
    """CTC word ends swallow the following pause; cap each word at a plausible spoken length (n = spoken chars, if known)"""
    for w in words:
        w["e"] = round(min(w["e"], w["s"] + 0.25 + 0.07 * w.pop("n", len(w["w"]))), 2)
    return words


# ---------- commands ----------
def transcribe(args):
    import torch
    os.makedirs(args.out, exist_ok=True)
    wav = os.path.join(args.out, "audio.wav")
    t0 = time.time(); to_wav(args.input, wav, clean=args.clean); dur = duration(wav)
    t1 = time.time(); m = load_asr(dur); t2 = time.time()
    with torch.inference_mode():
        h = m.transcribe([wav], batch_size=1, timestamps=True, verbose=False)
    log(f"ffmpeg {t1 - t0:.1f} s, model load {t2 - t1:.1f} s, transcription {time.time() - t2:.1f} s (RTF {(time.time() - t2) / dur:.2f})")
    h = h[0] if not isinstance(h, tuple) else h[0][0]
    import soundfile as sf
    audio, _ = sf.read(wav, dtype="float32")
    raw = force_align(m, audio, dur, [x["word"] for x in h.timestamp["word"] if x["word"].strip()])  # timings from forced alignment, see force_align
    t_asr = time.time() - t0
    if not args.no_pc and raw:
        del m
        labels = PC()([w["w"] for w in raw])
        for w, d in zip(raw, apply_pc([w["w"] for w in raw], labels)): w["raw"], w["w"] = w["w"], d
    words = raw
    json.dump(dict(source=os.path.abspath(args.input), duration=round(dur, 2), model="RSDO-DS2-ASR-E2E 2.0" + ("" if args.no_pc else " + RSDO-DS2-P&C 3.6"),
                   words=words), open(os.path.join(args.out, "words.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(args.out, "transcript.txt"), "w", encoding="utf-8").write(" ".join(w["w"] for w in words) + "\n")
    write_srt(words, os.path.join(args.out, "captions.srt"))
    log(f"{len(words)} words, {dur:.1f} s audio, ASR {t_asr:.1f} s, total {time.time() - t0:.1f} s -> {args.out}")


def spoken(token):
    """display token -> the lowercase words the speaker said (digits spelled out) for alignment"""
    from num2words import num2words
    t = unicodedata.normalize("NFC", token).lower()
    t = re.sub(r"(\d+)[.,](\d+)", lambda mo: num2words(float(f"{mo.group(1)}.{mo.group(2)}"), lang="sl"), t)
    t = re.sub(r"\d+", lambda mo: " " + num2words(int(mo.group()), lang="sl") + " ", t)
    t = re.sub(r"[%]", " odstotkov ", t)
    t = re.sub(r"[^\w\s]|_", " ", t)
    return t.split()


def force_align(m, audio, dur, display):
    """CTC forced alignment of display tokens against the audio with the loaded model -> words with s, e, conf.
    Raw CTC word timestamps put a word that follows a pause too early (the word-boundary token is emitted in the silence);
    forced alignment places it where the speech starts, which matters for cutting."""
    import torch, torchaudio
    ids, owner = [], []
    for i, tok in enumerate(display):
        for sw in spoken(tok):
            t = m.tokenizer.text_to_ids(sw)
            ids += t; owner += [i] * len(t)
    if not ids: return []
    with torch.inference_mode():
        sig = torch.tensor(audio)[None]
        lp, lens, _ = m.forward(input_signal=sig, input_signal_length=torch.tensor([sig.shape[1]]))
    blank = lp.shape[-1] - 1
    T = int(lens[0]); fsec = dur / T
    ali, scores = torchaudio.functional.forced_align(lp[:, :T].float(), torch.tensor([ids], dtype=torch.int32), blank=blank)
    spans = torchaudio.functional.merge_tokens(ali[0], scores[0].exp(), blank=blank)  # default blank=0 is wrong for NeMo (blank = last)
    assert len(spans) == len(ids), f"alignment returned {len(spans)} spans for {len(ids)} tokens"
    words = []
    for i, tok in enumerate(display):
        sp = [s for s, o in zip(spans, owner) if o == i]
        if not sp:  # punctuation-only token: glue to the previous word
            if words: words[-1]["w"] += tok
            continue
        words.append(dict(w=tok, s=round(sp[0].start * fsec, 2), e=round(sp[-1].end * fsec, 2), conf=round(sum(s.score for s in sp) / len(sp), 3), n=len("".join(spoken(tok)))))
    return clamp_ends(words)


def align(args):
    import soundfile as sf
    audio, sr = sf.read(args.audio, dtype="float32")
    assert sr == 16000 and audio.ndim == 1, "align expects the 16 kHz mono audio.wav from transcribe"
    dur = len(audio) / sr
    display = open(args.text, encoding="utf-8").read().split()
    words = force_align(load_asr(dur), audio, dur, display)
    if not words: sys.exit("empty text")
    out = dict(source=os.path.abspath(args.audio), duration=round(dur, 2), model="RSDO-DS2-ASR-E2E 2.0 CTC forced alignment", words=words)
    json.dump(out, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    low = [w["w"] for w in words if w["conf"] < 0.3]
    log(f"aligned {len(words)} words; low confidence: {low[:12]}{' ...' if len(low) > 12 else ''}")
    if args.srt: write_srt(words, args.srt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("transcribe"); t.add_argument("input"); t.add_argument("-o", "--out", default="sl-stt-out")
    t.add_argument("--clean", action="store_true", help="ffmpeg highpass/denoise/loudnorm first (raised WER 15.1 -> 17.9 on clean read speech; try only on noisy audio)"); t.add_argument("--no-pc", action="store_true", help="skip punctuation + casing")
    a = sub.add_parser("align"); a.add_argument("audio"); a.add_argument("text"); a.add_argument("-o", "--out", required=True); a.add_argument("--srt")
    args = ap.parse_args()
    {"transcribe": transcribe, "align": align}[args.cmd](args)


if __name__ == "__main__":
    main()
