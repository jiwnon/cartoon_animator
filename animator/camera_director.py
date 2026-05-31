from pathlib import Path
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


class CameraDirector:
    def __init__(self, config: dict):
        self.config = config
        self.resolution = config.get("resolution", "1920x1080")
        self.fps = config.get("fps", 30)
        self.duration_map = config.get("panel_duration", DURATION_MAP)
        self.ken_burns = KenBurns(self.resolution, self.fps)
        self.parallax = Parallax(self.resolution, self.fps)
        self.renderer = ClipRenderer(self.resolution, self.fps)

    def render(self, panel: Panel, output_dir: Path) -> str:
        scene_type = panel.scene_type or "other"
        duration = self.duration_map.get(scene_type, 3.0)
        focus = panel.scene_meta.get("focus_point", [0.5, 0.5])
        pace = panel.scene_meta.get("pace", "normal")

        if scene_type == "action":
            effect = self.ken_burns.zoom_in_shake(panel.image_path, duration, pace, focus)
        elif scene_type == "emotion":
            effect = self.ken_burns.slow_zoom_in(panel.image_path, duration, focus)
        elif scene_type == "background":
            effect = self.ken_burns.panorama_pan(panel.image_path, duration)
        elif scene_type == "dialogue":
            effect = self.ken_burns.subtle_zoom(panel.image_path, duration, focus)
        else:
            effect = self.ken_burns.static(panel.image_path, duration)

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
