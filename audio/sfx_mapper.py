from pathlib import Path

SFX_MAP = {
    "action":     ["assets/sfx/impact_01.wav", "assets/sfx/whoosh.wav"],
    "background": ["assets/sfx/wind.wav", "assets/sfx/birds.wav"],
    "emotion":    [],
    "dialogue":   [],
    "other":      [],
}


class SFXMapper:
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.map = {
            k: [self.base_dir / p for p in v]
            for k, v in SFX_MAP.items()
        }

    def get(self, scene_type: str) -> list[Path]:
        paths = self.map.get(scene_type, [])
        return [p for p in paths if p.exists()]

    def get_for_panel(self, panel) -> list[str]:
        scene_type = panel.scene_type or "other"
        return [str(p) for p in self.get(scene_type)]
