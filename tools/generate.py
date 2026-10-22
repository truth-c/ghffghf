"""Gemini 이미지 API로 프레임을 Elyn으로 자동 리드로우한다.

필요: 환경 변수 GEMINI_API_KEY
사용법: python3 tools/generate.py sit --only 0        (한 장 테스트)
        python3 tools/generate.py sit                  (전부, 이미 만든 프레임은 건너뜀)
        python3 tools/generate.py sit --redo 3 7       (특정 프레임 다시)
결과:   frames/<이름>/generated/NNN.png  (AI 원본 결과)
        frames/<이름>/redraw/NNN.png     (200x200으로 맞춰 덮어씀 -> tools/build.py 로 합치기)

모자·색 일관성을 위해 첫 결과(000)를 이후 프레임의 추가 레퍼런스로 함께 보낸다.
"""
import argparse
import base64
import io
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "reference" / "elyn_3.webp"
MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")
URL = "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent"

PROMPT = """Image 1 is Elyn, a witch girl (reference for character design only).
Image 2 is a frame from a chibi animation.{style}
Redraw image 2 with Elyn as the character. Keep EXACTLY the same pose, limb positions,
head tilt, body size, position in the frame, and the simple flat chibi art style and
line thickness of image 2. Only change the character design:
- bunny ears -> large purple wide-brimmed witch hat with a gold band
- brown hair -> long wavy lavender hair with blunt bangs
- light blue eyes -> purple eyes; keep the same facial expression and mouth
- black jacket with light blue lining -> dark purple cloak with gold trim and gold clasp
- navy top and blue skirt -> light lavender dress
- black leggings -> white legs with dark shoes
Plain white background. Square image, same framing as image 2."""
STYLE_NOTE = "\nImage 3 is an already-approved Elyn frame from the same animation: match its hat, hair, colors and outfit exactly."


def png_part(img):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "PNG")
    return {"inline_data": {"mime_type": "image/png", "data": base64.b64encode(buf.getvalue()).decode()}}


def call(parts, key, retries=4):
    body = json.dumps({"contents": [{"parts": parts}],
                       "generationConfig": {"responseModalities": ["IMAGE"]}}).encode()
    for attempt in range(retries):
        req = urllib.request.Request(URL.format(MODEL), body, {"Content-Type": "application/json", "x-goog-api-key": key})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.load(r)
            for part in data["candidates"][0]["content"]["parts"]:
                inline = part.get("inline_data") or part.get("inlineData")
                if inline:
                    return Image.open(io.BytesIO(base64.b64decode(inline["data"])))
            raise RuntimeError(f"이미지 없음: {json.dumps(data)[:300]}")
        except (urllib.error.URLError, RuntimeError, KeyError) as e:
            detail = e.read().decode()[:300] if isinstance(e, urllib.error.HTTPError) else e
            print(f"  실패 ({attempt + 1}/{retries}): {detail}")
            time.sleep(2 ** (attempt + 2))
    raise SystemExit("계속 실패해서 중단함")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--only", type=int, nargs="+")
    ap.add_argument("--redo", type=int, nargs="+", default=[])
    args = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY") or sys.exit("GEMINI_API_KEY 환경 변수가 없음")

    src = ROOT / "frames" / args.name
    manifest = json.loads((src / "manifest.json").read_text())
    size = tuple(manifest["size"])
    gen = src / "generated"
    gen.mkdir(exist_ok=True)

    ref = Image.open(REFERENCE).convert("RGBA")
    ref_white = Image.new("RGBA", ref.size, "white")
    ref_white.alpha_composite(ref)

    todo = args.only if args.only is not None else range(manifest["unique_frames"])
    for k in todo:
        out = gen / f"{k:03d}.png"
        if out.exists() and k not in args.redo and args.only is None:
            continue
        index = next(f["index"] for f in manifest["frames"] if f["redraw"] == k)
        frame = Image.open(src / "original" / f"{index:03d}.png").resize((800, 800), Image.LANCZOS)
        anchor = gen / "000.png"
        use_anchor = k != 0 and anchor.exists()
        parts = [{"text": PROMPT.format(style=STYLE_NOTE if use_anchor else "")}, png_part(ref_white), png_part(frame)]
        if use_anchor:
            parts.append(png_part(Image.open(anchor)))

        print(f"{args.name} {k:03d} 생성 중...")
        result = call(parts, key)
        result.save(out)
        small = result.convert("RGB").resize(size, Image.LANCZOS)
        small.save(src / "redraw" / f"{k:03d}.png")


if __name__ == "__main__":
    main()
