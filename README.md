# Elyn GIF 리드로우

원본 GIF 3개(`source/`)를 Elyn 마스코트 캐릭터 버전으로 다시 그리기 위한 작업 폴더.

| 파일 | 동작 | 프레임 | 프레임 시간 |
|---|---|---|---|
| `source/bow.gif` | 숙이며 흔들기 | 70 | 100ms |
| `source/dance.gif` | 팔 휘두르며 춤 | 98 | 100ms |
| `source/sit.gif` | 앉아서 흔들기 | 27 | 100ms |

모두 200×200, 흰 배경, 무한 반복.

## 작업 순서

1. `frames/<이름>/redraw/NNN.png` 를 Elyn으로 다시 그린 그림으로 **같은 파일 이름으로 덮어쓰기**
   - 원본 위치/포즈 참고: `frames/<이름>/original/`, 전체 보기: `frames/<이름>/sheet.png`
   - 크기가 200×200이 아니면 자동으로 맞춰짐. 투명 배경 PNG도 됨(흰 배경에 합성).
2. (AI 시트에서 잘라낸 경우) `python3 tools/slice_sheet.py sheets/<이름>_N.json 결과.png` → `python3 tools/stabilize.py <이름>` 로 떨림 보정
3. GIF로 합치기
   ```
   python3 tools/build.py            # 전부
   python3 tools/build.py dance      # 하나만
   python3 tools/build.py --step 2   # 2장마다 1장만 그렸을 때 (0, 2, 4 ... 번만 그리면 됨)
   ```
4. 결과: `output/<이름>_elyn.gif` (원본과 같은 순서·타이밍·반복)

캐릭터 시트와 AI 생성 프롬프트는 [ELYN.md](ELYN.md). AI 입력 이미지(레퍼런스+원본 프레임)는 `python3 tools/make_ai_input.py` 로 생성.

프레임을 다시 뽑으려면 `python3 tools/extract.py` (필요: `pip install pillow`).
