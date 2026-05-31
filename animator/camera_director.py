from pathlib import Path
from PIL import Image
from crawler.playwright_crawler import Panel
from .ken_burns import KenBurns
from .parallax import Parallax
from .clip_renderer import ClipRenderer

DURATION_MAP = {
    "action":     2.5,
    "dialogue":   4.0,
    "emotion":    5.0,
    "background": 3.5,
    "other":      3.0,
}

MAX_WIDTH = 720  # 출력 최대 너비 (비율 유지)


def _panel_resolution(image_path: str) -> str:
    """원본 비율을 유지하면서 MAX_WIDTH 이하로 스케일, libx264용 짝수 보정."""
    with Image.open(image_path) as img:
        w, h = img.size
    scale = min(1.0, MAX_WIDTH / w)
    out_w = int(w * scale)
    out_h = int(h * scale)
    out_w = out_w if out_w % 2 == 0 else out_w - 1
    out_h = out_h if out_h % 2 == 0 else out_h - 1
    return f"{out_w}x{out_h}"


class CameraDirector:
    def __init__(self, config: dict):
        self.config = config
        self.fps = config.get("fps", 30)
        self.duration_map = config.get("panel_duration", DURATION_MAP)
        self.ken_burns = KenBurns(self.fps)
        self.parallax = Parallax("720x1280", self.fps)
        self.renderer = ClipRenderer(self.fps)

    def render(self, panel: Panel, output_dir: Path) -> str:
        scene_type = panel.scene_type or "other"
        duration = self.duration_map.get(scene_type, 3.0)
        focus = panel.scene_meta.get("focus_point", [0.5, 0.5])
        pace = panel.scene_meta.get("pace", "normal")

        resolution = _panel_resolution(panel.image_path)

        if scene_type == "action":
            effect = self.ken_burns.zoom_in_shake(panel.image_path, duration, resolution, pace, focus)
        elif scene_type == "emotion":
            effect = self.ken_burns.slow_zoom_in(panel.image_path, duration, resolution, focus)
        elif scene_type == "background":
            effect = self.ken_burns.panorama_pan(panel.image_path, duration, resolution)
        elif scene_type == "dialogue":
            effect = self.ken_burns.subtle_zoom(panel.image_path, duration, resolution, focus)
        else:
            effect = self.ken_burns.static(panel.image_path, duration, resolution)

        out_path = output_dir / f"clip_{panel.order:03d}.mp4"
        self.renderer.render(effect, str(out_path))
        return str(out_path)

    def render_all(self, input_dir: str) -> list[str]:
        from classifier.panel_sorter import PanelSorter
        panels = PanelSorter().load(input_dir)

        clips_dir = Path(input_dir) / "clips"
        clips_dir.mkdir(exist_ok=True)

        clips = []
        for panel in panels:
            clip_path = self.render(panel, clips_dir)
            clips.append(clip_path)
            print(f"  clip {panel.order:03d} rendered → {clip_path}")
        return clips
