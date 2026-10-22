# Elyn 캐릭터 시트 & 리드로우 가이드

레퍼런스: `reference/elyn_1~5.webp` (SD 체형은 `elyn_3.webp`가 GIF와 가장 가까움)

## 핵심 특징

| 부위 | 원본 GIF | Elyn |
|---|---|---|
| 머리 장식 | 갈색 토끼 귀 | **보라색 챙 넓은 마녀 모자**, 금색 띠, 끝이 살짝 꺾인 고깔 |
| 머리카락 | 갈색, 짧은 포니테일 | **연보라~라벤더 롱 웨이브**, 일자 앞머리, 끝으로 갈수록 밝아짐 |
| 눈 | 하늘색 | **보라/핑크빛 보라** |
| 겉옷 | 검정 재킷 + 하늘색 안감 | **짙은 보라 망토(로브)**, 금색 테두리, 목에 금색 장식 |
| 안옷 | 남색 상의 + 파란 치마 | **연보라 원피스** |
| 다리 | 검정 타이츠 | 흰 다리 / 흰 양말 + 짙은 신발 |
| 표정 | `:3` 입 | 그대로 유지 (Elyn도 `:3` 표정 레퍼런스 있음) |

## 색상 (레퍼런스에서 추출)

| 용도 | 색 |
|---|---|
| 모자 짙은 부분 / 망토 | `#382950` `#463c7c` `#60457a` |
| 모자 챙 밝은 부분 | `#8d35df` `#a151c2` |
| 머리카락 | `#a887cd` `#ae88e9` `#c29cd7` `#e1bdd9` |
| 원피스 | `#b8a3f1` `#c29cd7` |
| 금색 장식 | `#d4a63c` 부근 |
| 피부 | `#f7e8f3` `#fdecec` |

## AI 생성 프롬프트

입력: `frames/<이름>/ai_input/NNN.png` (왼쪽 Elyn, 오른쪽 원본 프레임)
— 이미지 여러 장을 넣을 수 있으면 `reference/elyn_3.webp` + `frames/<이름>/original/NNN.png` 를 따로 넣는 게 더 좋음.

```
Redraw the character on the RIGHT as the witch girl on the LEFT (Elyn).
Keep EXACTLY the same pose, body position, size, framing, and simple flat chibi
art style of the right image. Only change the character design:
- bunny ears -> large purple wide-brimmed witch hat with a gold band
- brown hair -> long wavy lavender hair with blunt bangs
- blue eyes -> purple eyes, keep the ":3" mouth
- black jacket -> dark purple cloak with gold trim and gold clasp
- blue skirt / navy top -> light lavender dress
White background. Output ONLY the redrawn character, square image.
```

한국어 도구용:

```
오른쪽 캐릭터를 왼쪽 마녀 소녀(엘린)로 다시 그려줘.
오른쪽 그림의 포즈, 위치, 크기, 구도, 단순한 SD 그림체는 정확히 그대로 유지하고
캐릭터 디자인만 바꿔줘:
- 토끼 귀 -> 금색 띠가 있는 큰 보라색 마녀 모자
- 갈색 머리 -> 일자 앞머리의 긴 웨이브 라벤더 머리
- 하늘색 눈 -> 보라색 눈, ":3" 입은 유지
- 검정 재킷 -> 금색 테두리와 금색 장식이 있는 짙은 보라 망토
- 파란 치마/남색 상의 -> 연보라 원피스
흰 배경, 정사각형, 다시 그린 캐릭터만 출력.
```

## 프레임 일관성 팁

- **키 프레임 먼저**: `sheet.png` 에서 포즈가 크게 바뀌는 프레임 몇 장을 먼저 만들고, 마음에 드는 결과를
  다음 프레임 생성 때 레퍼런스로 같이 넣으면 모자 모양·색이 덜 흔들림.
- 결과물은 **오른쪽 캐릭터만** 정사각형으로 저장 (1024x512 두 장짜리를 그대로 넣으면 찌그러짐).
- 저장 위치: `frames/<이름>/redraw/NNN.png` (같은 번호로 덮어쓰기) → `python3 tools/build.py`
