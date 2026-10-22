"""AI가 다시 그린 시트를 칸별로 잘라 frames/<이름>/redraw/ 에 넣는다.

사용법: python3 tools/slice_sheet.py sheets/sit_1.json 결과이미지.png
결과 이미지의 실제 회색 격자선을 찾아서 자른다 (AI가 그린 격자는 등간격이 아닐 때가 많음).
못 찾은 선은 등간격 위치로 대신한다. 각 칸은 200x200으로 맞춘다.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MARGIN = 6  # 격자선이 섞이지 않게 선 바깥으로 잘라낼 픽셀


def find_lines(profile, count, length):
    """회색 비율 프로필에서 count-1개의 격자선 위치를 찾는다."""
    step = length / count
    lines = [0]
    for i in range(1, count):
        expect = round(i * step)
        lo, hi = max(0, expect - round(step * 0.25)), min(length, expect + round(step * 0.25))
        window = profile[lo:hi]
        lines.append(lo + int(window.argmax()) if window.max() > 0.5 else expect)
    lines.append(length)
    return lines


def slice_sheet(layout_path, result_path):
    layout = json.loads(Path(layout_path).read_text())
    manifest = json.loads((ROOT / "frames" / layout["name"] / "manifest.json").read_text())
    size = tuple(manifest["size"])
    img = Image.open(result_path).convert("RGB")
    gray = np.asarray(img.convert("L")).astype(int)
    is_line = (gray > 150) & (gray < 225)
    xs = find_lines(is_line.mean(0), layout["cols"], img.width)
    ys = find_lines(is_line.mean(1), layout["rows"], img.height)
    print("세로선", xs[1:-1], "가로선", ys[1:-1])

    for i, k in enumerate(layout["frames"]):
        c, r = i % layout["cols"], i // layout["cols"]
        box = (xs[c] + (MARGIN if c else 0), ys[r] + (MARGIN if r else 0),
               xs[c + 1] - (MARGIN if c + 1 < layout["cols"] else 0), ys[r + 1] - (MARGIN if r + 1 < layout["rows"] else 0))
        img.crop(box).resize(size, Image.LANCZOS).save(ROOT / "frames" / layout["name"] / "redraw" / f"{k:03d}.png")
    print(f"{len(layout['frames'])}칸 -> frames/{layout['name']}/redraw/")


if __name__ == "__main__":
    slice_sheet(*sys.argv[1:3])
