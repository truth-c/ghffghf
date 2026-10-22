"""칸 크기·배치가 제각각인 AI 결과 이미지 여러 장을 순서대로 잘라 프레임으로 만든다.

시트마다 칸 수만 알려주면 칸을 등분해서 자르고, 캐릭터 부분만 오려서
  - 시트마다 캐릭터 크기가 다르게 그려진 것을 맞추고 (시트별 중간 키를 같게)
  - 앞뒤 프레임보다 유독 크거나 작은 칸을 이웃 크기에 맞추고
  - 바닥 높이와 아랫부분 가로 중심을 원본 프레임 위치에 맞춘다 (떨림 보정)

사용법: python3 tools/assemble.py sit a.png:3x2 b.png:3x2 c.png:3x1 ...
        (가로칸x세로칸, 왼쪽 위부터 오른쪽으로 읽는 순서, 전체 칸 수 = 프레임 수)
결과:   frames/<이름>/redraw/ 를 덮어씀 -> python3 tools/build.py <이름>
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
INSET = 8  # 격자선이 섞이지 않게 칸 가장자리에서 버릴 픽셀
MARGIN = 3


def content_box(img):
    mask = np.asarray(img.convert("RGB")).astype(int).sum(2) < 700
    rows = np.nonzero(mask.sum(1) >= 3)[0]
    cols = np.nonzero(mask.sum(0) >= 3)[0]
    return cols[0], rows[0], cols[-1] + 1, rows[-1] + 1


def lower_center(img):
    """아래 25% 부분의 가로 중심 (이미지 안 좌표)."""
    mask = np.asarray(img.convert("RGB")).astype(int).sum(2) < 700
    h = mask.shape[0]
    return np.nonzero(mask[h - h // 4:])[1].mean()


def cut(spec):
    path, grid = spec.rsplit(":", 1)
    cols, rows = map(int, grid.lower().split("x"))
    img = Image.open(path).convert("RGB")
    cw, ch = img.width / cols, img.height / rows
    sprites = []
    for r in range(rows):
        for c in range(cols):
            cell = img.crop((round(c * cw) + INSET, round(r * ch) + INSET, round((c + 1) * cw) - INSET, round((r + 1) * ch) - INSET))
            sprites.append(cell.crop(content_box(cell)))
    return sprites


def main(name, specs):
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    w, h = manifest["size"]
    first = {f["redraw"]: f["index"] for f in reversed(manifest["frames"])}

    sheets = [cut(s) for s in specs]
    total = sum(len(s) for s in sheets)
    if total != manifest["unique_frames"]:
        sys.exit(f"칸 수 합계 {total} != 프레임 수 {manifest['unique_frames']}")

    # 시트마다 캐릭터 크기 맞추기: 시트별 중간 키 -> 전체 중간 키
    target = np.median([s.height for sheet in sheets for s in sheet])
    sprites = []
    for sheet in sheets:
        k = target / np.median([s.height for s in sheet])
        sprites += [s.resize((round(s.width * k), round(s.height * k)), Image.LANCZOS) for s in sheet]

    # 앞뒤 프레임보다 크기가 튀는 칸(AI가 유독 크거나 작게 그린 칸)을 이웃 크기에 맞춤
    size = [np.sqrt(s.width * s.height) for s in sprites]
    for i, s in enumerate(sprites):
        near = np.median([size[(i + d) % total] for d in range(-2, 3)])
        if abs(size[i] / near - 1) > 0.12:
            k = near / size[i]
            sprites[i] = s.resize((round(s.width * k), round(s.height * k)), Image.LANCZOS)
            print(f"  {i}번 프레임 크기 보정 x{k:.2f}")

    # 원본 프레임의 바닥·아래 중심
    anchors = []
    for i in range(total):
        o = Image.open(src / "original" / f"{first[i]:03d}.png").convert("RGB")
        _, _, _, bottom = content_box(o)
        anchors.append((bottom, lower_center(o.crop((0, 0, w, bottom)))))

    # 전체 공통 배율: 모든 프레임이 200x200 안에 들어가게
    scale = 10.0
    for s, (bottom, cx) in zip(sprites, anchors):
        lc = lower_center(s)
        scale = min(scale, (bottom - MARGIN) / s.height, (w - 2 * MARGIN) / s.width)
    print(f"{name}: {total}프레임, 공통 배율 {scale:.3f}")

    for i, (s, (bottom, cx)) in enumerate(zip(sprites, anchors)):
        lc = lower_center(s)
        s = s.resize((round(s.width * scale), round(s.height * scale)), Image.LANCZOS)
        out = Image.new("RGB", (w, h), "white")
        x = min(max(MARGIN, round(cx - lc * scale)), w - MARGIN - s.width)  # 화면 밖으로 나가면 안쪽으로 밀어 넣음
        out.paste(s, (x, bottom - s.height))
        out.save(src / "redraw" / f"{i:03d}.png")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
