"""AI가 다시 그린 시트를 칸별로 잘라 frames/<이름>/redraw/ 에 넣는다.

사용법: python3 tools/slice_sheet.py sheets/sit_1.json 결과이미지.png
결과 이미지 크기·비율이 원본 시트와 달라도 칸 수 기준으로 나눠 200x200으로 맞춘다.
"""
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INSET = 0.02  # 격자선이 섞이지 않게 칸 가장자리를 살짝 잘라냄


def slice_sheet(layout_path, result_path):
    layout = json.loads(Path(layout_path).read_text())
    manifest = json.loads((ROOT / "frames" / layout["name"] / "manifest.json").read_text())
    size = tuple(manifest["size"])
    img = Image.open(result_path).convert("RGB")
    cw, ch = img.width / layout["cols"], img.height / layout["rows"]
    for i, k in enumerate(layout["frames"]):
        x, y = (i % layout["cols"]) * cw, (i // layout["cols"]) * ch
        box = (round(x + cw * INSET), round(y + ch * INSET), round(x + cw * (1 - INSET)), round(y + ch * (1 - INSET)))
        cell = Image.new("RGB", size, "white")
        part = img.crop(box).resize((round(size[0] * (1 - 2 * INSET)), round(size[1] * (1 - 2 * INSET))), Image.LANCZOS)
        cell.paste(part, (round(size[0] * INSET), round(size[1] * INSET)))
        cell.save(ROOT / "frames" / layout["name"] / "redraw" / f"{k:03d}.png")
    print(f"{len(layout['frames'])}칸 -> frames/{layout['name']}/redraw/")


if __name__ == "__main__":
    slice_sheet(*sys.argv[1:3])
