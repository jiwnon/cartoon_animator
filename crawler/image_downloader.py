from pathlib import Path
from .playwright_crawler import Panel


class ImageDownloader:
    def save(self, panels: list[Panel], save_dir: Path) -> list[Panel]:
        panels_dir = save_dir / "panels"
        panels_dir.mkdir(parents=True, exist_ok=True)

        for panel in panels:
            # TODO: panel.image_url → panels_dir/000.jpg 다운로드
            # panel.image_path 업데이트
            raise NotImplementedError

        return panels

    def _download(self, url: str, dest: Path, headers: dict = None) -> None:
        # TODO: requests로 이미지 다운로드 (Referer 헤더 필요한 사이트 대응)
        raise NotImplementedError
