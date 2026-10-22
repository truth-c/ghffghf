"""다시 그린 프레임의 떨림을 줄인다.

AI는 칸마다 캐릭터를 조금씩 다른 위치·크기로 그려서 GIF가 떨린다. 프레임마다
  - 바닥(가장 아래 줄)을 원본 프레임의 바닥 높이에 맞추고
  - 아랫부분(하단 25%)의 가로 중심을 원본의 같은 부분 중심에 맞추고
  - 크기는 모든 프레임에 같은 배율을 써서(프레임마다 커졌다 작아지는 것 방지) 200x200 안에 들어가게 한다.

사용법: python3 tools/stabilize.py sit     (frames/sit/redraw/ 를 덮어씀, slice_sheet.py 다음에 실행)
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MARGIN = 3


def measure(img):
    """(위, 아래, 하단 가로중심, 왼쪽, 오른쪽) - 흰 배경이 아닌 부분 기준."""
    a = np.asarray(img.convert("RGB")).astype(int)
    mask = a.sum(2) < 700
    rows = np.nonzero(mask.sum(1) >= 3)[0]
    cols = np.nonzero(mask.sum(0) >= 3)[0]
    top, bottom = rows[0], rows[-1]
    lower = mask[bottom - (bottom - top) // 4: bottom + 1]
    cx = np.nonzero(lower)[1].mean()
    return top, bottom, cx, cols[0], cols[-1]


def stabilize(name):
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    w, h = manifest["size"]
    ids = range(manifest["unique_frames"])
    first = {f["redraw"]: f["index"] for f in reversed(manifest["frames"])}

    drawn = {k: Image.open(src / "redraw" / f"{k:03d}.png").convert("RGB") for k in ids}
    m_new = {k: measure(drawn[k]) for k in ids}
    m_org = {k: measure(Image.open(src / "original" / f"{first[k]:03d}.png")) for k in ids}

    # 모든 프레임이 들어가는 하나의 배율
    scale = 1.0
    for k in ids:
        top, bottom, cx, left, right = m_new[k]
        _, o_bottom, o_cx, _, _ = m_org[k]
        scale = min(scale,
                    (o_bottom - MARGIN) / max(1, bottom - top),
                    (o_cx - MARGIN) / max(1, cx - left),
                    (w - MARGIN - o_cx) / max(1, right - cx))
    print(f"{name}: 배율 {scale:.3f}")

    for k in ids:
        top, bottom, cx, _, _ = m_new[k]
        _, o_bottom, o_cx, _, _ = m_org[k]
        img = drawn[k].resize((round(w * scale), round(h * scale)), Image.LANCZOS)
        dx = round(o_cx - cx * scale)
        dy = round(o_bottom - bottom * scale)
        out = Image.new("RGB", (w, h), "white")
        out.paste(img, (dx, dy))
        out.save(src / "redraw" / f"{k:03d}.png")


if __name__ == "__main__":
    for n in sys.argv[1:]:
        stabilize(n)
