"""Propose cuts for a Slovene talking-head take from sl-stt words.json (forced-aligned timings).

usage: cutlist.py words.json -o cuts.json [--pause 0.7] [--keep 0.2] [--window 25]
Detectors:
  pause    silence longer than --pause between words; trimmed to --keep on each side       (auto)
  lead     dead air before the first word / after the last word                           (auto)
  cue      a spoken retake cue ("še enkrat", "ponovno", "stop", "od začetka"): cut back to the
           start of the sentence it interrupts, through the cue                            (auto)
  retake   the speaker restarts: a run of >=2 words reappears within --window seconds, with no
           sentence end in between; cut from the first attempt to the restart              (auto if >=3 words match, else propose)
  repeat   a single word said twice in a row ("in in", "da da")                            (propose)
  filler   eee / ehm / mhm / aaa / mmm                                                      (auto)
Output: {"duration", "cuts": [{id, type, level, start, end, reason}], "keep": [[s, e], ...]} where keep
is the media to keep if every auto cut is applied. Nothing is rendered here; the director (Claude)
reviews proposals, then render.py assembles the keep list.
"""
import argparse, json, re, unicodedata

CUES = [("še", "enkrat"), ("ponovno",), ("stop",), ("od", "začetka"), ("še", "1x")]
FILLER = re.compile(r"^(e+m*|a+|m+|hm+|ehm+|mhm+|eh+|ah+|uh+|um+)$")
SENT_END = re.compile(r"[.!?]$")


def norm(w):
    w = unicodedata.normalize("NFC", w).lower()
    return re.sub(r"[^\w]", "", w)


def detect(words, dur, pause=0.7, keep=0.2, window=25.0):
    n = [norm(w["w"]) for w in words]
    cuts = []

    def add(kind, level, s, e, reason):
        if e - s > 0.05:
            cuts.append(dict(type=kind, level=level, start=round(max(0.0, s), 2), end=round(min(dur, e), 2), reason=reason))

    # lead-in / lead-out
    if words:
        add("lead", "auto", 0.0, words[0]["s"] - keep, "dead air before the first word")
        add("lead", "auto", words[-1]["e"] + keep * 2, dur, "dead air after the last word")
    # fillers
    for i, w in enumerate(words):
        if FILLER.match(n[i]):
            add("filler", "auto", w["s"] - 0.03, w["e"] + 0.03, f'filler "{w["w"]}"')
    # cues: cut from the start of the interrupted sentence through the cue
    for i in range(len(words)):
        for cue in CUES:
            if tuple(n[i:i + len(cue)]) == cue:
                j = i - 1
                while j > 0 and not SENT_END.search(words[j - 1]["w"]) and words[i]["s"] - words[j - 1]["s"] < 15:
                    j -= 1
                start = words[j]["s"] if j >= 0 and j < i else words[i]["s"]
                end = words[i + len(cue) - 1]["e"]
                nxt = words[i + len(cue)]["s"] if i + len(cue) < len(words) else dur
                add("cue", "auto", start - 0.05, min(nxt - 0.05, end + 0.3), f'spoken cue "{" ".join(cue)}"')
    # retakes: words[i:i+k] reappears at j (first attempt abandoned)
    used = set()
    for i in range(len(words)):
        if i in used or not n[i] or FILLER.match(n[i]):
            continue
        best = None
        for j in range(i + 1, len(words)):
            if words[j]["s"] - words[i]["s"] > window:
                break
            if any(SENT_END.search(words[t]["w"]) for t in range(i, j)):  # the first attempt was finished
                break
            k = 0
            while j + k < len(words) and i + k < j and n[i + k] == n[j + k]:
                k += 1
            if k >= 2 or (k == 1 and j == i + 1 and len(n[i]) > 1):
                best = (j, k)  # keep searching: the last restart wins
        if best:
            j, k = best
            if j == i + 1 and k == 1:
                add("repeat", "propose", words[i]["s"] - 0.03, words[j]["s"] - 0.03, f'"{words[i]["w"]}" said twice')
            else:
                level = "auto" if k >= 3 else "propose"
                said = " ".join(w["w"] for w in words[i:j])
                add("retake", level, words[i]["s"] - 0.05, words[j]["s"] - 0.05,
                    f'restart: "{said[:60]}{"…" if len(said) > 60 else ""}" said again ({k} words match)')
            used.update(range(i, j))
    # pauses
    for a, b in zip(words, words[1:]):
        if b["s"] - a["e"] > pause:
            add("pause", "auto", a["e"] + keep, b["s"] - keep, f"{b['s'] - a['e']:.1f} s pause")
    cuts.sort(key=lambda c: c["start"])
    for i, c in enumerate(cuts):
        c["id"] = f'{c["type"]}-{i + 1:02d}'
    return cuts


def keep_segments(cuts, dur, levels=("auto",)):
    spans = sorted((c["start"], c["end"]) for c in cuts if c["level"] in levels)
    merged = []
    for s, e in spans:
        if merged and s <= merged[-1][1] + 0.02:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    keep, t = [], 0.0
    for s, e in merged:
        if s - t > 0.08: keep.append([round(t, 2), round(s, 2)])
        t = max(t, e)
    if dur - t > 0.08: keep.append([round(t, 2), round(dur, 2)])
    return keep


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("words"); ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--pause", type=float, default=0.7); ap.add_argument("--keep", type=float, default=0.2); ap.add_argument("--window", type=float, default=25.0)
    a = ap.parse_args()
    d = json.load(open(a.words, encoding="utf-8"))
    dur = d.get("duration") or d["words"][-1]["e"]
    cuts = detect(d["words"], dur, a.pause, a.keep, a.window)
    keep = keep_segments(cuts, dur)
    json.dump(dict(source=d.get("source"), duration=dur, cuts=cuts, keep=keep), open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    out_len = sum(e - s for s, e in keep)
    for c in cuts:
        print(f'{c["id"]:12} {c["level"]:8} {c["start"]:7.2f}-{c["end"]:7.2f} ({c["end"] - c["start"]:4.1f} s)  {c["reason"]}')
    print(f"{dur:.1f} s -> {out_len:.1f} s if auto cuts are applied ({len(keep)} kept segments)")


if __name__ == "__main__":
    main()
