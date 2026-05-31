from pathlib import Path

BGM_MAP = {
    "action":     "assets/bgm/action_intense.mp3",
    "dialogue":   "assets/bgm/calm_ambient.mp3",
    "emotion":    "assets/bgm/emotional_piano.mp3",
    "background": "assets/bgm/nature_ambient.mp3",
    "other":      "assets/bgm/calm_ambient.mp3",
}


class BGMMapper:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.map = {k: self.base_dir / v for k, v in BGM_MAP.items()}

    def get(self, scene_type: str) -> Path | None:
        path = self.map.get(scene_type)
        return path if (path and path.exists()) else None

    def build_bgm_timeline(self, panels: list) -> list[dict]:
        # 씬 전환 시 크로스페이드 1초 적용한 BGM 타임라인 반환
        # [{bgm_path, start, end, fade_in, fade_out}, ...]
        timeline = []
        current_time = 0.0

        for panel in panels:
            scene_type = panel.scene_type or "other"
            bgm_path = self.get(scene_type)
            duration = panel.scene_meta.get("duration", 3.0)

            timeline.append({
                "bgm_path": str(bgm_path) if bgm_path else None,
                "scene_type": scene_type,
                "start": current_time,
                "end": current_time + duration,
                "fade_in": 1.0,
                "fade_out": 1.0,
            })
            current_time += duration

        return timeline
