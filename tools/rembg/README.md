# rembg (background removal, local)

Installed 2026-10-27 (Ultra Claude Phase 2). rembg 2.0.86, onnxruntime 1.31.1 (CPU), Python 3.11 venv in `.venv`. Photos never leave the laptop.

**Models: BiRefNet only.** Never the default `u2net` (the pick says its licence is a problem for commercial use).
- `birefnet-general-lite` (224 MB, downloaded to `~/.rembg/models/`): the default here. About 50 s per photo on this CPU, clean edges on product shots.
- `birefnet-general` (bigger, slower): only when the lite edges are not good enough. Downloads on first use.
- `birefnet-portrait`: people and hair.

```bash
# one photo
~/claude-kit/tools/rembg/.venv/Scripts/rembg.exe   # Mac/Linux: .venv/bin/rembg i -m birefnet-general-lite in.jpg out.png
# a whole folder (loads the model once, faster per photo)
~/claude-kit/tools/rembg/.venv/Scripts/rembg.exe   # Mac/Linux: .venv/bin/rembg p -m birefnet-general-lite in_folder/ out_folder/
```

Output is a PNG with transparency. To check a cut, composite it on a loud colour (composite on magenta).
