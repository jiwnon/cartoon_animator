# 🎬 WebtoonAnimate

> 웹툰 패널 이미지를 자동으로 분석하고, 씬 타입에 맞는 카메라 연출 + TTS 대사 + BGM/효과음을 붙여 애니메이션 영상으로 변환하는 파이프라인

---

## 개요

WebtoonAnimate는 정적인 웹툰 이미지를 영상 콘텐츠로 자동 변환하는 오픈소스 파이프라인입니다.  
크롤링 → 씬 분류 → 카메라 연출 → 오디오 합성 → MP4 렌더링까지 전 과정을 자동화합니다.

**포트폴리오 프로젝트** — 비상업적 용도. 입력 웹툰은 작가 허가를 받거나 직접 제작한 이미지를 사용하세요.

---

## 기능

- **웹툰 크롤링**: Playwright 기반, JS 렌더링 사이트 대응
- **자동 분류**: VLM(Vision Language Model)으로 패널별 씬 타입 태깅
- **씬별 카메라 연출**: 액션/감정/대화/배경 타입에 따라 다른 연출 적용
- **로컬 TTS**: Kokoro TTS + RVC로 캐릭터 목소리 생성 (API 비용 없음)
- **오디오 레이어**: BGM + 효과음 자동 매핑
- **MP4 렌더링**: FFmpeg 기반 최종 영상 출력

---

## 전체 아키텍처

```
[웹툰 URL 입력]
       │
       ▼
┌─────────────────────────────┐
│  1단계: 크롤링               │
│  Playwright → 패널 이미지    │
│  OCR → 말풍선 텍스트 추출    │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  2단계: 분류                 │
│  메타데이터 파싱             │
│  VLM → 씬 타입 태깅          │
│  [액션/대화/감정/배경/기타]  │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  3단계: 애니메이션화         │
│  씬 타입별 카메라 연출        │
│  Ken Burns / Parallax       │
│  FFmpeg 클립 생성            │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  4단계: 오디오               │
│  Kokoro TTS → 대사 음성      │
│  RVC → 캐릭터 목소리 변환    │
│  BGM / 효과음 자동 매핑      │
└────────────┬────────────────┘
             │
             ▼
┌─────────────────────────────┐
│  5단계: 최종 렌더링          │
│  FFmpeg concat              │
│  자막 burn-in               │
│  MP4 출력                   │
└─────────────────────────────┘
```

---

## 씬 타입별 연출 전략

| 씬 타입 | 카메라 연출 | 속도 | 효과음 | BGM |
|--------|-----------|------|--------|-----|
| ⚡ 액션 | 빠른 줌인 + 화면 흔들림 | 빠름 | 충격음, 효과음 | 긴박한 비트 |
| 💬 대화 | 캐릭터 간 컷 전환 | 보통 | 없음 | 잔잔한 배경음 |
| 😢 감정 | 느린 줌인 → 정지 | 느림 | 없음 | 감성적 피아노 |
| 🌄 배경 | 느린 파노라마 팬 | 느림 | 바람, 자연음 | 배경 앰비언트 |
| 🔍 클로즈업 | 줌인 후 정지 | 보통 | 없음 | 상황에 따라 |

---

## 프로젝트 구조

```
WebtoonAnimate/
├── crawler/
│   ├── playwright_crawler.py     # 웹툰 크롤러
│   ├── image_downloader.py       # 패널 이미지 다운로드
│   └── ocr_extractor.py          # 말풍선 OCR (EasyOCR)
│
├── classifier/
│   ├── scene_classifier.py       # VLM 기반 씬 타입 분류
│   ├── panel_sorter.py           # 패널 순서 정렬
│   └── metadata_parser.py        # 작품/화수 메타데이터 파싱
│
├── animator/
│   ├── camera_director.py        # 씬 타입 → 카메라 연출 매핑
│   ├── ken_burns.py              # Ken Burns 효과 구현
│   ├── parallax.py               # 레이어 분리 + 시차 효과
│   └── clip_renderer.py          # 패널별 클립 생성
│
├── audio/
│   ├── tts_engine.py             # Kokoro TTS 래퍼
│   ├── rvc_converter.py          # RVC 목소리 변환
│   ├── bgm_mapper.py             # 씬 타입 → BGM 매핑
│   ├── sfx_mapper.py             # 씬 타입 → 효과음 매핑
│   └── audio_mixer.py            # 오디오 레이어 믹싱
│
├── renderer/
│   ├── video_concat.py           # 클립 concat
│   ├── subtitle_burner.py        # 자막 burn-in
│   └── final_render.py           # 최종 MP4 출력
│
├── assets/
│   ├── bgm/                      # 배경음악 (CC 라이선스)
│   └── sfx/                      # 효과음 (CC 라이선스)
│
├── data/
│   └── {작품명}/
│       └── {화수}/
│           ├── panels/           # 패널 이미지
│           ├── metadata.json     # 메타데이터
│           └── output/           # 생성된 영상
│
├── config.yaml                   # 전체 설정
├── main.py                       # 진입점
└── README.md
```

---

## 설치

### 요구사항

- Python 3.11
- CUDA 12.x (RTX GPU 권장)
- FFmpeg

### 설치 방법

```bash
git clone https://github.com/jiwnon/WebtoonAnimate
cd WebtoonAnimate

pip install -r requirements.txt
playwright install chromium
```

### requirements.txt

```
playwright
pillow
opencv-python
easyocr
ffmpeg-python
kokoro-tts
torch
torchvision
segment-anything-2
anthropic        # 씬 분류용 VLM
python-dotenv
pyyaml
```

---

## 사용법

### 기본 실행

```bash
# 웹툰 URL로 전체 파이프라인 실행
python main.py --url "https://example.com/webtoon/1화" --output ./output

# 특정 단계만 실행
python main.py --step crawl --url "..."
python main.py --step classify --input ./data/작품명
python main.py --step animate --input ./data/작품명/1화
python main.py --step render --input ./data/작품명/1화
```

### config.yaml 설정

```yaml
# 크롤링 설정
crawler:
  delay: 2.0              # 요청 간격 (초)
  max_panels: 100

# 씬 분류 설정
classifier:
  model: claude-sonnet-4  # VLM 모델
  confidence_threshold: 0.7

# 애니메이션 설정
animator:
  resolution: "1920x1080"
  fps: 30
  panel_duration:
    action: 2.5           # 액션씬 패널당 기본 길이 (초)
    dialogue: 4.0
    emotion: 5.0
    background: 3.5

# 오디오 설정
audio:
  tts_enabled: true
  tts_model: "kokoro"
  rvc_enabled: false      # RVC 목소리 변환 여부
  bgm_volume: 0.3
  sfx_volume: 0.6
  voice_volume: 1.0

# 렌더링 설정
renderer:
  format: "mp4"
  quality: "high"         # low / medium / high
  subtitle: true
```

---

## 각 단계 상세

### 1단계: 크롤링

Playwright로 JS 렌더링이 필요한 웹툰 사이트에 대응합니다.  
EasyOCR로 말풍선 텍스트를 추출해 TTS 입력으로 씁니다.

```python
from crawler.playwright_crawler import WebtoonCrawler

crawler = WebtoonCrawler()
panels = crawler.crawl("https://...")
# panels: [{image_path, order, dialogue_text}, ...]
```

### 2단계: 씬 분류

패널 이미지를 VLM에 전달해 씬 타입을 판별합니다.

```python
from classifier.scene_classifier import SceneClassifier

classifier = SceneClassifier(model="claude-sonnet-4")
result = classifier.classify(panel_image)
# result: {type: "action", confidence: 0.92, tags: ["fight", "impact"]}
```

**프롬프트 전략**: 단순 분류 외에 카메라 연출 힌트(`zoom_direction`, `pace`, `focus_point`)도 함께 추출합니다.

### 3단계: 애니메이션화

씬 타입에 따라 FFmpeg 필터 파라미터를 다르게 적용합니다.

```python
from animator.camera_director import CameraDirector

director = CameraDirector()
clip = director.render(panel_image, scene_type="action")
# → 빠른 줌인 + 흔들림 효과가 적용된 .mp4 클립
```

**Ken Burns 구현 예시 (액션씬)**:
```python
# 빠른 줌인 (1.0 → 1.3배, 2.5초)
ffmpeg_filter = (
    "zoompan=z='if(lte(zoom,1.0),1.0,zoom+0.006)':"
    "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
    "d=75:s=1920x1080,"
    "hue=s=1.2"  # 채도 약간 올려서 긴장감
)
```

### 4단계: 오디오

**TTS 흐름**:
```
말풍선 텍스트
    → Kokoro TTS (로컬 추론, RTX 4070 최적화)
    → RVC 변환 (캐릭터별 목소리, 선택사항)
    → 패널 duration에 맞게 타이밍 조정
```

**BGM/효과음 매핑**:
```python
BGM_MAP = {
    "action":     "assets/bgm/action_intense.mp3",
    "dialogue":   "assets/bgm/calm_ambient.mp3",
    "emotion":    "assets/bgm/emotional_piano.mp3",
    "background": "assets/bgm/nature_ambient.mp3",
}

SFX_MAP = {
    "action":     ["assets/sfx/impact_01.wav", "assets/sfx/whoosh.wav"],
    "background": ["assets/sfx/wind.wav", "assets/sfx/birds.wav"],
}
```

BGM은 씬 전환 시 1초 크로스페이드로 자연스럽게 전환합니다.

### 5단계: 최종 렌더링

```python
from renderer.final_render import FinalRenderer

renderer = FinalRenderer()
renderer.render(
    clips=clip_list,
    audio_tracks=audio_list,
    subtitle_srt="output.srt",
    output_path="webtoon_ep1.mp4"
)
```

---

## 오디오 에셋 가이드

BGM과 효과음은 CC0 또는 CC BY 라이선스 소스를 사용합니다.

| 씬 | 추천 키워드 | 소스 |
|----|-----------|------|
| 액션 | action, intense, battle, epic | [Freesound](https://freesound.org), [Pixabay Music](https://pixabay.com/music/) |
| 감정 | emotional, piano, sad, heartfelt | 동일 |
| 배경 | ambient, nature, calm, atmosphere | 동일 |
| 대화 | background, subtle, neutral | 동일 |

효과음:
- 충격음: `impact`, `hit`, `punch`
- 이동/스피드: `whoosh`, `swipe`
- 자연음: `wind`, `rain`, `forest`

---

## 개발 로드맵

### v0.1 — MVP
- [ ] 이미지 한 장 → Ken Burns 영상 변환
- [ ] FFmpeg 파이프라인 기본 구조

### v0.2 — 분류 연동
- [ ] VLM 씬 분류기 구현
- [ ] 씬 타입별 카메라 연출 분기

### v0.3 — 크롤링
- [ ] Playwright 크롤러
- [ ] OCR 말풍선 추출

### v0.4 — 오디오
- [ ] Kokoro TTS 연동
- [ ] BGM/효과음 자동 매핑 + 믹싱

### v0.5 — 완성
- [ ] 전체 파이프라인 통합
- [ ] config.yaml 기반 설정
- [ ] 데모 영상 제작

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| 크롤링 | Playwright, EasyOCR |
| 씬 분류 | Claude API (Vision) |
| 이미지 처리 | OpenCV, Pillow, SAM2 |
| 영상 처리 | FFmpeg, ffmpeg-python |
| TTS | Kokoro TTS |
| 음성 변환 | RVC (Applio / KLM Trainer) |
| 오디오 처리 | librosa, pydub |
| 런타임 | Python 3.11, CUDA 12.x |

---

## 라이선스

MIT License

입력 웹툰 저작권은 원작자에게 있습니다. 반드시 저작권자의 허락을 받거나 직접 제작한 이미지를 사용하세요.

---

## 기여

Issue, PR 환영합니다.  
특히 씬 분류 프롬프트 개선, 새로운 카메라 연출 프리셋, 효과음 매핑 로직에 대한 기여를 환영합니다.
