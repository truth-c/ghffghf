"""다시 그린 프레임(frames/<이름>/redraw/*.png)을 원본 순서와 타이밍대로 GIF로 합친다.

사용법: python3 tools/build.py bow [dance sit ...]   (인자 없으면 전부)
        python3 tools/build.py --step 2 bow            (2장마다 1장만 사용, 프레임 시간은 2배)
결과:   output/<이름>_elyn.gif

--step N 을 쓰면 redraw 폴더에서 0, N, 2N ... 번 프레임만 그리면 된다.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent


def build(name, step=1):
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    size = tuple(manifest["size"])

    redrawn = {}
    used = sorted({f["redraw"] for f in manifest["frames"][::step]})
    for k in used:
        img = Image.open(src / "redraw" / f"{k:03d}.png").convert("RGBA")
        if img.size != size:
            img = img.resize(size, Image.LANCZOS)
        # 원본처럼 흰 배경에 합성
        bg = Image.new("RGBA", size, "white")
        bg.alpha_composite(img)
        redrawn[k] = bg.convert("RGB")

    picked = manifest["frames"][::step]
    frames = [redrawn[f["redraw"]] for f in picked]
    durations = [sum(f["duration"] for f in manifest["frames"][i:i + step])
                 for i in range(0, len(manifest["frames"]), step)]

    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    path = out / f"{name}_elyn.gif"
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   loop=manifest["loop"], disposal=2, optimize=False)
    print(f"{name}: {len(frames)}프레임 -> {path.relative_to(ROOT)}")


if __name__ == "__main__":
    args = sys.argv[1:]
    step = 1
    if args[:1] == ["--step"]:
        step = int(args[1])
        args = args[2:]
    names = args or sorted(p.name for p in (ROOT / "frames").iterdir() if (p / "manifest.json").exists())
    for n in names:
        build(n, step)
