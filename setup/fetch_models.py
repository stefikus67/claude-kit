"""Download the two Slovene speech models from CLARIN.SI (Apache-2.0) into tools/sl-stt/models/.

  <sl-stt venv python> -X utf8 setup/fetch_models.py

RSDO-DS2-ASR-E2E 2.0 (handle 11356/1737) and RSDO-DS2-P&C 3.6 (11356/1735), about 860 MB together.
Each .tar.zst holds one .nemo; it is streamed straight to models/<name>.nemo. Skips models already in place.
"""
import os, sys, tarfile, time, urllib.request
import zstandard

MODELS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "sl-stt", "models")
BASE = "https://www.clarin.si/repository/xmlui/bitstream/handle/"
JOBS = [
    ("rsdo-asr-2.0.nemo", BASE + "11356/1737/sl-SI_GEN_nemo-2.0.tar.zst", 486707200),
    ("rsdo-pc-3.6.nemo", BASE + "11356/1735/sl-SI_GEN_nemo-3.6.tar.zst", 444200960),
]


class Progress:
    def __init__(self, f, total, label):
        self.f, self.total, self.label, self.n, self.t = f, total, label, 0, 0

    def read(self, k=-1):
        b = self.f.read(k)
        self.n += len(b)
        if time.time() - self.t > 5:
            self.t = time.time()
            print(f"  {self.label}: {self.n / 1e6:.0f} / {self.total / 1e6:.0f} MB", flush=True)
        return b


def fetch(name, url, size):
    dst = os.path.join(MODELS, name)
    if os.path.exists(dst) and os.path.getsize(dst) == size:
        print(f"{name} already in place")
        return
    print(f"downloading {name} from CLARIN.SI")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "claude-kit"}), timeout=60) as r:
                stream = zstandard.ZstdDecompressor().stream_reader(Progress(r, int(r.headers.get("Content-Length", 0)), name))
                with tarfile.open(fileobj=stream, mode="r|") as tar:
                    for m in tar:
                        if m.isfile() and m.name.endswith(".nemo"):
                            tmp = dst + ".part"
                            with tar.extractfile(m) as src, open(tmp, "wb") as out:
                                while chunk := src.read(1 << 20):
                                    out.write(chunk)
                            os.replace(tmp, dst)
                            break
            if os.path.exists(dst) and os.path.getsize(dst) == size:
                print(f"{name} OK ({size / 1e6:.0f} MB)")
                return
            raise RuntimeError(f"{name}: wrong size after download")
        except Exception as e:
            print(f"  attempt {attempt + 1} failed: {e}", flush=True)
            time.sleep(5)
    sys.exit(f"FAILED: could not download {name} from {url}")


if __name__ == "__main__":
    os.makedirs(MODELS, exist_ok=True)
    for job in JOBS:
        fetch(*job)
