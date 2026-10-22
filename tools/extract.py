"""GIF를 프레임 PNG로 분리하고, 중복 프레임을 묶어 다시 그릴 프레임 목록(manifest.json)을 만든다.

사용법: python3 tools/extract.py source/bow.gif [source/dance.gif ...]
결과:   frames/<이름>/original/NNN.png   모든 프레임 (원본 순서)
        frames/<이름>/redraw/KKK.png     다시 그려야 할 고유 프레임 (원본 복사본, 여기에 덮어쓰기)
        frames/<이름>/manifest.json      원본 프레임 -> 고유 프레임 매핑, 프레임 시간
        frames/<이름>/sheet.png          고유 프레임 한눈에 보기
"""
import hashlib
import json
import sys
from pathlib import Path

from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parent.parent


def extract(gif_path):
    gif_path = Path(gif_path)
    name = gif_path.stem
    out = ROOT / "frames" / name
    (out / "original").mkdir(parents=True, exist_ok=True)
    (out / "redraw").mkdir(parents=True, exist_ok=True)

    im = Image.open(gif_path)
    unique = {}  # 픽셀 해시 -> 고유 프레임 번호
    frames = []
    for i, frame in enumerate(ImageSequence.Iterator(im)):
        rgba = frame.convert("RGBA")
        rgba.save(out / "original" / f"{i:03d}.png")
        digest = hashlib.sha1(rgba.tobytes()).hexdigest()
        if digest not in unique:
            unique[digest] = len(unique)
            rgba.save(out / "redraw" / f"{unique[digest]:03d}.png")
        frames.append({"index": i, "redraw": unique[digest], "duration": frame.info.get("duration", 100)})

    manifest = {
        "name": name,
        "size": list(im.size),
        "loop": im.info.get("loop", 0),
        "unique_frames": len(unique),
        "frames": frames,
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    # 고유 프레임 컨택트 시트 (번호 = redraw 파일 이름)
    cols = 10
    w, h = im.size
    rows = (len(unique) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * w, rows * h), "white")
    for k in range(len(unique)):
        sheet.paste(Image.open(out / "redraw" / f"{k:03d}.png"), ((k % cols) * w, (k // cols) * h))
    sheet.save(out / "sheet.png")

    print(f"{name}: 전체 {len(frames)}프레임, 다시 그릴 고유 프레임 {len(unique)}개 -> {out.relative_to(ROOT)}")


if __name__ == "__main__":
    for path in sys.argv[1:] or sorted((ROOT / "source").glob("*.gif")):
        extract(path)
