"""AI가 다시 그린 시트를 칸별로 잘라 frames/<이름>/redraw/ 에 넣는다.

사용법: python3 tools/slice_sheet.py sheets/sit_1.json 결과이미지.png
결과 이미지의 실제 회색 격자선을 찾아서 자른다 (AI가 그린 격자는 등간격이 아닐 때가 많음).
못 찾은 선은 칸 간격으로 추정한다. 모든 칸에 같은 배율을 써서 200x200 칸에 가운데 맞춘다.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MARGIN = 6  # 격자선이 섞이지 않게 선 바깥으로 잘라낼 픽셀


def find_lines(profile, count, length):
    """격자선(거의 끝까지 이어지는 회색 줄) 위치를 찾는다. 바깥 테두리 포함 count+1개."""
    hits = np.nonzero(profile > 0.8)[0]
    centers = []
    for i in hits:
        if centers and i - centers[-1][-1] <= 2:
            centers[-1].append(i)
        else:
            centers.append([i])
    centers = [round(sum(c) / len(c)) for c in centers]
    gaps = np.diff(centers)
    step = float(np.median(gaps[gaps > length / count * 0.6])) if len(centers) > 1 else length / count
    first = centers[0] - step * round(centers[0] / step) if centers else 0  # 격자 시작 위치
    lines = []
    for i in range(count + 1):
        expect = first + i * step
        near = [c for c in centers if abs(c - expect) < step * 0.3]
        lines.append(min(near, key=lambda c: abs(c - expect)) if near else round(expect))
    lines[0], lines[-1] = 0, length  # 바깥 테두리는 선이 없을 때가 많아 이미지 끝까지 씀
    return lines, step


def slice_sheet(layout_path, result_path):
    layout = json.loads(Path(layout_path).read_text())
    manifest = json.loads((ROOT / "frames" / layout["name"] / "manifest.json").read_text())
    size = tuple(manifest["size"])
    img = Image.open(result_path).convert("RGB")
    gray = np.asarray(img.convert("L")).astype(int)
    is_line = (gray > 150) & (gray < 225)
    xs, xstep = find_lines(is_line.mean(0), layout["cols"], img.width)
    ys, ystep = find_lines(is_line.mean(1), layout["rows"], img.height)
    scale = size[0] / ((xstep + ystep) / 2)  # 모든 칸에 같은 배율 (비율 유지)
    print("세로선", xs, "가로선", ys)

    for i, k in enumerate(layout["frames"]):
        c, r = i % layout["cols"], i // layout["cols"]
        box = (xs[c] + (MARGIN if c else 0), ys[r] + (MARGIN if r else 0),
               xs[c + 1] - (MARGIN if c + 1 < layout["cols"] else 0), ys[r + 1] - (MARGIN if r + 1 < layout["rows"] else 0))
        part = img.crop(box)
        part = part.resize((round(part.width * scale), round(part.height * scale)), Image.LANCZOS)
        cell = Image.new("RGB", size, "white")
        cell.paste(part, ((size[0] - part.width) // 2, (size[1] - part.height) // 2))
        cell.save(ROOT / "frames" / layout["name"] / "redraw" / f"{k:03d}.png")
    print(f"{len(layout['frames'])}칸 -> frames/{layout['name']}/redraw/")


if __name__ == "__main__":
    slice_sheet(*sys.argv[1:3])
