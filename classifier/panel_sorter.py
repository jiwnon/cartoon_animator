import json
from pathlib import Path
from crawler.playwright_crawler import Panel


class PanelSorter:
    def load(self, input_dir: str) -> list[Panel]:
        panels_dir = Path(input_dir) / "panels"
        image_files = sorted(panels_dir.glob("*.jpg")) + sorted(panels_dir.glob("*.png"))

        panels = []
        for i, img_path in enumerate(image_files):
            panels.append(Panel(
                order=i,
                image_url="",
                image_path=str(img_path),
            ))

        meta_path = Path(input_dir) / "metadata.json"
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            panels = self._apply_metadata(panels, meta)

        return panels

    def _apply_metadata(self, panels: list[Panel], meta: dict) -> list[Panel]:
        # TODO: metadata.json의 dialogue_text 등을 Panel에 주입
        return panels
