from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Panel:
    order: int
    image_url: str
    image_path: Optional[str] = None
    dialogue_text: str = ""       # 말풍선 대사
    narration_text: str = ""      # 내레이션/서술 텍스트 (TTS 읽기용)
    scene_type: Optional[str] = None
    scene_meta: dict = field(default_factory=dict)


class WebtoonCrawler:
    def __init__(self, config: dict):
        self.delay = config.get("delay", 2.0)
        self.max_panels = config.get("max_panels", 100)
        self.headless = config.get("headless", True)

    def crawl(self, url: str) -> list[Panel]:
        # TODO: Playwright로 JS 렌더링 후 패널 이미지 URL 수집
        # 1. playwright 브라우저 실행
        # 2. 웹툰 페이지 접속
        # 3. 패널 img 태그 수집
        # 4. Panel 리스트 반환
        raise NotImplementedError

    def _scroll_to_bottom(self, page) -> None:
        # TODO: 무한스크롤 대응
        raise NotImplementedError

    def _extract_panel_urls(self, page) -> list[str]:
        # TODO: 사이트별 셀렉터로 패널 img src 추출
        raise NotImplementedError
