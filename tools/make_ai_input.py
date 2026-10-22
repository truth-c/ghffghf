"""AI 이미지 생성용 입력 이미지를 만든다: [Elyn 레퍼런스 | 원본 프레임] 을 가로로 붙인 한 장.

이미지를 여러 장 넣을 수 없는 도구에서 쓰기 위한 것. 여러 장이 되면 레퍼런스와
frames/<이름>/original/NNN.png 를 따로 넣는 편이 낫다.

사용법: python3 tools/make_ai_input.py [bow dance sit ...]   (인자 없으면 전부)
결과:   frames/<이름>/ai_input/NNN.png  (1024x512, 고유 프레임 번호 = redraw 번호)
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "reference" / "elyn_3.webp"  # GIF와 같은 SD(치비) 체형
CELL = 512


def on_white(img):
    img = img.convert("RGBA")
    img.thumbnail((CELL, CELL), Image.LANCZOS)
    cell = Image.new("RGBA", (CELL, CELL), "white")
    cell.alpha_composite(img, ((CELL - img.width) // 2, (CELL - img.height) // 2))
    return cell


def make(name):
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    out = src / "ai_input"
    out.mkdir(exist_ok=True)
    ref = on_white(Image.open(REFERENCE))
    for k in range(manifest["unique_frames"]):
        frame = Image.open(src / "original" / f"{next(f['index'] for f in manifest['frames'] if f['redraw'] == k):03d}.png")
        frame = frame.convert("RGBA").resize((CELL, CELL), Image.NEAREST)
        pair = Image.new("RGB", (CELL * 2, CELL), "white")
        pair.paste(ref.convert("RGB"), (0, 0))
        pair.paste(frame.convert("RGB"), (CELL, 0))
        pair.save(out / f"{k:03d}.png")
    print(f"{name}: {manifest['unique_frames']}장 -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(p.name for p in (ROOT / "frames").iterdir() if (p / "manifest.json").exists())
    for n in names:
        make(n)
