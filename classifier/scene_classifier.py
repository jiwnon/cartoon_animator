import base64
import json
from pathlib import Path
from crawler.playwright_crawler import Panel

SCENE_TYPES = ["action", "dialogue", "emotion", "background", "other"]

CLASSIFY_PROMPT = """이 웹툰 패널 이미지를 분석해서 JSON으로 답해줘.

씬 타입:
- action: 싸움, 충돌, 빠른 움직임
- dialogue: 캐릭터 간 대화, 말풍선 위주
- emotion: 감정 표현, 클로즈업 표정
- background: 배경 묘사, 인물 없거나 작음
- other: 위에 해당 없음

응답 형식 (JSON만):
{
  "type": "action|dialogue|emotion|background|other",
  "confidence": 0.0~1.0,
  "tags": ["tag1", "tag2"],
  "zoom_direction": "in|out|none",
  "pace": "fast|normal|slow",
  "focus_point": [0.5, 0.5]
}"""


class SceneClassifier:
    def __init__(self, config: dict):
        self.model = config.get("model", "claude-sonnet-4-6")
        self.threshold = config.get("confidence_threshold", 0.7)
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic()
        return self._client

    def classify(self, panel: Panel) -> dict:
        image_data = Path(panel.image_path).read_bytes()
        b64 = base64.standard_b64encode(image_data).decode("utf-8")
        ext = Path(panel.image_path).suffix.lstrip(".")
        media_type = f"image/{'jpeg' if ext == 'jpg' else ext}"

        response = self._get_client().messages.create(
            model=self.model,
            max_tokens=256,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
                    {"type": "text", "text": CLASSIFY_PROMPT},
                ],
            }],
        )

        raw = response.content[0].text.strip()
        result = json.loads(raw)

        if result.get("confidence", 0) < self.threshold:
            result["type"] = "other"

        return result

    def classify_all(self, panels: list[Panel]) -> list[Panel]:
        for panel in panels:
            result = self.classify(panel)
            panel.scene_type = result["type"]
            panel.scene_meta = result
            print(f"  panel {panel.order:03d} → {panel.scene_type} ({result.get('confidence', 0):.2f})")
        return panels
