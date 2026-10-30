"""Assemble the kept segments of a take into one video (frame-accurate re-encode, 12 ms audio fades at every join).

usage: render_cut.py IN.mp4 cuts.json OUT.mp4 [--levels auto,propose] [--crf 18]
cuts.json from cutlist.py. By default only "auto" cuts are applied; --levels auto,propose applies proposals too.
Also writes OUT.map.json: for every kept segment its source range and output start, so captions/B-roll timed on
the source can be mapped to the cut (and back).
"""
import argparse, json, subprocess, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cutlist import keep_segments


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input"); ap.add_argument("cuts"); ap.add_argument("out")
    ap.add_argument("--levels", default="auto"); ap.add_argument("--crf", default="18")
    a = ap.parse_args()
    d = json.load(open(a.cuts, encoding="utf-8"))
    keep = keep_segments(d["cuts"], d["duration"], tuple(a.levels.split(",")))
    has_video = bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=index", "-of", "csv=p=0", a.input],
                                    capture_output=True, text=True).stdout.strip())
    f, labels, fade = [], [], 0.012
    for i, (s, e) in enumerate(keep):
        if has_video:
            f.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
        f.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,afade=t=in:d={fade},afade=t=out:st={max(0, e - s - fade):.3f}:d={fade}[a{i}]")
        labels.append((f"[v{i}]" if has_video else "") + f"[a{i}]")
    f.append("".join(labels) + f"concat=n={len(keep)}:v={1 if has_video else 0}:a=1" + ("[v][a]" if has_video else "[a]"))
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.input, "-filter_complex", ";".join(f)]
    cmd += (["-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", a.crf, "-pix_fmt", "yuv420p"] if has_video else []) + ["-map", "[a]", "-c:a", "aac", "-b:a", "192k", a.out]
    subprocess.run(cmd, check=True)
    t, segs = 0.0, []
    for s, e in keep:
        segs.append(dict(src_start=s, src_end=e, out_start=round(t, 3))); t += e - s
    json.dump(dict(source=a.input, cuts=a.cuts, levels=a.levels, duration=round(t, 3), segments=segs), open(os.path.splitext(a.out)[0] + ".map.json", "w"), indent=1)
    print(f"{len(keep)} segments, {d['duration']:.1f} s -> {t:.1f} s -> {a.out}")


if __name__ == "__main__":
    main()
