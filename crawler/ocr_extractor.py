from pathlib import Path
from .playwright_crawler import Panel


class OCRExtractor:
    def __init__(self, lang: list[str] = None):
        self.lang = lang or ["ko", "en"]
        self._reader = None

    def _get_reader(self):
        if self._reader is None:
            import easyocr
            self._reader = easyocr.Reader(self.lang)
        return self._reader

    def extract(self, panel: Panel) -> str:
        # TODO: panel.image_path 이미지에서 말풍선 텍스트 추출
        # easyocr로 전체 텍스트 추출 후 말풍선 영역만 필터링
        raise NotImplementedError

    def extract_all(self, panels: list[Panel]) -> list[Panel]:
        for panel in panels:
            panel.dialogue_text = self.extract(panel)
        return panels
