import re
from urllib.parse import urlparse


class MetadataParser:
    def parse(self, url: str) -> dict:
        # TODO: URL 패턴에서 작품명/화수 추출
        # 사이트별 URL 구조가 다르므로 규칙 추가 필요
        return {
            "title": self._extract_title(url),
            "episode": self._extract_episode(url),
            "url": url,
        }

    def _extract_title(self, url: str) -> str:
        # TODO: URL 또는 페이지 파싱으로 작품명 추출
        parsed = urlparse(url)
        parts = [p for p in parsed.path.split("/") if p]
        return parts[-2] if len(parts) >= 2 else "unknown_title"

    def _extract_episode(self, url: str) -> str:
        # TODO: URL에서 화수 추출 (ep, no, chapter 등 패턴 대응)
        match = re.search(r"(\d+)", urlparse(url).path)
        return f"ep{match.group(1)}" if match else "ep1"
