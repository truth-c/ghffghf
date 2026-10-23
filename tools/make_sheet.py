"""프레임을 격자 한 장(스프라이트 시트)으로 모은다. AI가 전체 동작 맥락을 보고 한 번에 다시 그리게 하기 위한 것.

사용법: python3 tools/make_sheet.py sit [bow dance ...]          (기본 4x3=12칸)
        python3 tools/make_sheet.py --cols 6 --rows 5 sit        (칸 수 지정)
        python3 tools/make_sheet.py --ranges 1-17,18-33 bow      (동작 구간별 시트 -> sheets/bow_seqN)
결과:   sheets/<이름>_N.png   격자 시트 (칸당 200x200 + 아래 번호 띠, 회색 격자선)
        sheets/<이름>_N.json  어느 칸이 몇 번 프레임인지 (tools/slice_sheet.py 가 사용)
칸 아래 번호(1, 2, 3 ...)는 AI가 순서를 놓치지 않게 하기 위한 것. 자를 때는 번호 띠를 버린다.
"""
import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LINE = 3
LABEL = 36


def font(size):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make(name, max_cols, max_rows):
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    w, h = manifest["size"]
    ch = h + LABEL
    total = manifest["unique_frames"]
    sheets = math.ceil(total / (max_cols * max_rows))
    per = math.ceil(total / sheets)
    out = ROOT / "sheets"
    out.mkdir(exist_ok=True)
    for old in out.glob(f"{name}_*"):
        if old.stem.split("_")[-1].isdigit():  # 이전 번호 시트만 지움 (_all 등은 유지)
            old.unlink()

    for s in range(sheets):
        ids = list(range(s * per, min(total, (s + 1) * per)))
        rows = math.ceil(len(ids) / min(max_cols, len(ids)))
        cols = math.ceil(len(ids) / rows)  # 빈 칸이 적게 (예: 9장은 4x3 대신 3x3)
        sheet = Image.new("RGB", (cols * w, rows * ch), "white")
        draw = ImageDraw.Draw(sheet)
        for i, k in enumerate(ids):
            x, y = (i % cols) * w, (i // cols) * ch
            sheet.paste(Image.open(src / "redraw" / f"{k:03d}.png").convert("RGB"), (x, y))
            draw.text((x + w // 2, y + h + LABEL // 2), str(i + 1), fill="black", font=font(26), anchor="mm")
        for c in range(1, cols):
            draw.line([(c * w, 0), (c * w, rows * ch)], fill="#bbbbbb", width=LINE)
        for r in range(1, rows):
            draw.line([(0, r * ch), (cols * w, r * ch)], fill="#bbbbbb", width=LINE)
        stem = f"{name}_{s + 1}"
        sheet.save(out / f"{stem}.png")
        (out / f"{stem}.json").write_text(json.dumps({"name": name, "cols": cols, "rows": rows, "frames": ids, "label": LABEL}))
        print(f"{stem}.png: {cols}x{rows} 격자, 프레임 {ids[0]}~{ids[-1]}")


def make_ranges(name, ranges, max_cols):
    """지정한 구간(1부터 세는 번호, 예: 1-17)마다 시트 한 장. 칸 번호는 전체 프레임 번호로 표시."""
    src = ROOT / "frames" / name
    manifest = json.loads((src / "manifest.json").read_text())
    w, h = manifest["size"]
    ch = h + LABEL
    out = ROOT / "sheets"
    out.mkdir(exist_ok=True)
    for n, part in enumerate(ranges.split(","), 1):
        a, b = map(int, part.split("-"))
        ids = list(range(a - 1, b))
        # 빈 칸이 적고 너무 길쭉하지 않은 배치
        cols = min(range(3, max_cols + 2), key=lambda c: c * math.ceil(len(ids) / c) - len(ids) + abs(c / math.ceil(len(ids) / c) - 1.4))
        rows = math.ceil(len(ids) / cols)
        sheet = Image.new("RGB", (cols * w, rows * ch), "white")
        draw = ImageDraw.Draw(sheet)
        for i, k in enumerate(ids):
            x, y = (i % cols) * w, (i // cols) * ch
            sheet.paste(Image.open(src / "redraw" / f"{k:03d}.png").convert("RGB"), (x, y))
            draw.text((x + w // 2, y + h + LABEL // 2), str(k + 1), fill="black", font=font(26), anchor="mm")
        for c in range(1, cols):
            draw.line([(c * w, 0), (c * w, rows * ch)], fill="#bbbbbb", width=LINE)
        for r in range(1, rows):
            draw.line([(0, r * ch), (cols * w, r * ch)], fill="#bbbbbb", width=LINE)
        stem = f"{name}_seq{n}"
        sheet.save(out / f"{stem}.png")
        (out / f"{stem}.json").write_text(json.dumps({"name": name, "cols": cols, "rows": rows, "frames": ids, "label": LABEL}))
        print(f"{stem}.png: {cols}x{rows} 격자, 프레임 {a}~{b} ({len(ids)}장)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*")
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--ranges", help="구간별 시트, 예: 1-17,18-33 (칸 번호는 전체 프레임 번호)")
    args = ap.parse_args()
    if args.ranges:
        make_ranges(args.names[0], args.ranges, max(args.cols, 6))
        raise SystemExit
    names = args.names or sorted(p.name for p in (ROOT / "frames").iterdir() if (p / "manifest.json").exists())
    for n in names:
        make(n, args.cols, args.rows)
