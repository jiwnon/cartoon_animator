import json
import re
from pathlib import Path
from crawler.playwright_crawler import Panel

SCENE_TYPES = ["action", "dialogue", "emotion", "background", "other"]

CLASSIFY_PROMPT = """이 웹툰 패널 이미지를 분석해서 JSON만 출력해줘. 설명 없이 JSON만.

씬 타입:
- action: 싸움, 충돌, 빠른 움직임, 효과선
- dialogue: 캐릭터 간 대화, 말풍선 위주
- emotion: 감정 표현, 클로즈업 얼굴
- background: 배경 묘사, 인물 없거나 매우 작음
- other: 위에 해당 없음

텍스트 분류:
- narration: 네모 박스 안 텍스트, 배경/상황 설명, 내레이션, 독백 (말풍선 아닌 것)
- dialogues: 말풍선 안 대사 목록

출력 형식:
{"type":"dialogue","confidence":0.9,"tags":["conversation"],"zoom_direction":"in","pace":"normal","focus_point":[0.5,0.5],"narration":"내레이션 텍스트 (없으면 빈 문자열)","dialogues":["대사1","대사2"]}"""


def _parse_json_from_response(text: str) -> dict:
    """중괄호 depth 추적으로 첫 번째 완전한 JSON 객체만 추출."""
    text = text.strip()
    start = text.find('{')
    if start == -1:
        raise ValueError(f"JSON을 찾을 수 없음: {text[:200]}")

    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start):
        if escape:
            escape = False
            continue
        if ch == '\\' and in_string:
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                return json.loads(text[start:i + 1])

    raise ValueError(f"완전한 JSON 객체를 찾을 수 없음: {text[:200]}")


class SceneClassifier:
    def __init__(self, config: dict):
        self.model = config.get("model", "llava")
        self.host = config.get("ollama_host", "http://localhost:11434")
        self.threshold = config.get("confidence_threshold", 0.5)

    def classify(self, panel: Panel) -> dict:
        import ollama

        client = ollama.Client(host=self.host)
        response = client.chat(
            model=self.model,
            messages=[{
                "role": "user",
                "content": CLASSIFY_PROMPT,
                "images": [panel.image_path],
            }],
        )

        raw = response["message"]["content"]
        result = _parse_json_from_response(raw)

        if result.get("confidence", 0) < self.threshold:
            result["type"] = "other"

        # 기본값 보정
        result.setdefault("narration", "")
        result.setdefault("dialogues", [])

        return result

    def classify_all(self, panels: list[Panel]) -> list[Panel]:
        for panel in panels:
            try:
                result = self.classify(panel)
            except Exception as e:
                print(f"  panel {panel.order:03d} 분류 실패: {e} → other로 처리")
                result = {
                    "type": "other",
                    "confidence": 0.0,
                    "tags": [],
                    "zoom_direction": "none",
                    "pace": "normal",
                    "focus_point": [0.5, 0.5],
                    "narration": "",
                    "dialogues": [],
                }

            panel.scene_type = result["type"]
            panel.scene_meta = result
            panel.narration_text = result.get("narration", "")
            panel.dialogue_text = " / ".join(result.get("dialogues", []))

            narr_preview = f' 내레이션="{panel.narration_text[:20]}..."' if panel.narration_text else ""
            print(f"  panel {panel.order:03d} → {panel.scene_type} ({result.get('confidence', 0):.2f}){narr_preview}")

        return panels
