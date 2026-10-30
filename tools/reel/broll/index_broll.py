"""Index a folder of B-roll clips: shots (PySceneDetect AdaptiveDetector), one keyframe per shot, one contact sheet per clip.

usage: .venv/Scripts/python.exe broll/index_broll.py FOLDER [-o FOLDER/_index]
-> _index/index.json {clips: [{file, duration, shots: [{n, s, e, thumb}]}]}, _index/<clip>-sheet.jpg (labelled shots)
The director (Claude) looks at the sheets ("read, don't watch") and adds tags/notes to index.json, then picks
overlays for edl.json from it: {"src": <file>, "from": shot.s, "dur": <= shot length, "at": reel time}.
"""
import argparse, json, os, subprocess
from scenedetect import detect, AdaptiveDetector

VIDEO = (".mp4", ".mov", ".m4v", ".webm", ".mkv")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder"); ap.add_argument("-o", "--out")
    a = ap.parse_args()
    out = a.out or os.path.join(a.folder, "_index")
    os.makedirs(out, exist_ok=True)
    clips = []
    for f in sorted(os.listdir(a.folder)):
        if not f.lower().endswith(VIDEO):
            continue
        path = os.path.join(a.folder, f); dur = probe(path)
        scenes = detect(path, AdaptiveDetector()) or []
        spans = [(s.get_seconds(), e.get_seconds()) for s, e in scenes] or [(0.0, dur)]
        stem = os.path.splitext(f)[0]; shots = []
        for n, (s, e) in enumerate(spans, 1):
            thumb = os.path.join(out, f"{stem}-{n:02d}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{(s + e) / 2:.2f}", "-i", path, "-frames:v", "1",
                            "-vf", f"scale=240:-2,drawtext=text='{n} {s:.1f}-{e:.1f}s':x=6:y=6:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.6",
                            "-q:v", "4", thumb], check=True)
            shots.append(dict(n=n, s=round(s, 2), e=round(e, 2), thumb=os.path.relpath(thumb, a.folder), tags=[]))
        cols = min(6, len(shots)); rows = -(-len(shots) // cols)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(out, f"{stem}-%02d.jpg"), "-vf",
                        f"tile={cols}x{rows}:padding=4:color=black", "-frames:v", "1", "-q:v", "4", os.path.join(out, f"{stem}-sheet.jpg")], check=True)
        clips.append(dict(file=f, duration=round(dur, 2), shots=shots))
        print(f"{f}: {dur:.1f} s, {len(shots)} shots")
    json.dump(dict(folder=os.path.abspath(a.folder), clips=clips), open(os.path.join(out, "index.json"), "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main()
