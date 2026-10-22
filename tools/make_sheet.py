"""프레임을 격자 한 장(스프라이트 시트)으로 모은다. AI가 전체 동작 맥락을 보고 한 번에 다시 그리게 하기 위한 것.

사용법: python3 tools/make_sheet.py sit [bow dance ...]   (인자 없으면 전부)
결과:   sheets/<이름>_N.png   격자 시트 (칸당 200x200, 회색 격자선)
        sheets/<이름>_N.json  어느 칸이 몇 번 프레임인지 (tools/slice_sheet.py 가 사용)
한 시트에 최대 6x5=30칸. 그보다 많으면 비슷한 크기로 나눠 여러 장.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
COLS, ROWS = 6, 5
LINE = 3


def make(name):
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    w, h = manifest["size"]
    total = manifest["unique_frames"]
    sheets = math.ceil(total / (COLS * ROWS))
    per = math.ceil(total / sheets)
    out = ROOT / "sheets"
    out.mkdir(exist_ok=True)

    for s in range(sheets):
        ids = list(range(s * per, min(total, (s + 1) * per)))
        cols = min(COLS, len(ids))
        rows = math.ceil(len(ids) / cols)
        sheet = Image.new("RGB", (cols * w, rows * h), "white")
        for i, k in enumerate(ids):
            sheet.paste(Image.open(src / "redraw" / f"{k:03d}.png").convert("RGB"), ((i % cols) * w, (i // cols) * h))
        draw = ImageDraw.Draw(sheet)
        for c in range(1, cols):
            draw.line([(c * w, 0), (c * w, rows * h)], fill="#bbbbbb", width=LINE)
        for r in range(1, rows):
            draw.line([(0, r * h), (cols * w, r * h)], fill="#bbbbbb", width=LINE)
        stem = f"{name}_{s + 1}"
        sheet.save(out / f"{stem}.png")
        (out / f"{stem}.json").write_text(json.dumps({"name": name, "cols": cols, "rows": rows, "frames": ids}))
        print(f"{stem}.png: {cols}x{rows} 격자, 프레임 {ids[0]}~{ids[-1]}")


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(p.name for p in (ROOT / "frames").iterdir() if (p / "manifest.json").exists())
    for n in names:
        make(n)
