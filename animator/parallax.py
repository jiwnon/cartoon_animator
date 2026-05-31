from .ken_burns import EffectParams


class Parallax:
    """SAM2로 레이어 분리 후 시차 효과. v0.x 이후 구현 예정."""

    def __init__(self, resolution: str = "1920x1080", fps: int = 30):
        self.resolution = resolution
        self.fps = fps

    def split_layers(self, image_path: str) -> list[str]:
        # TODO: SAM2로 foreground/background 분리 → 레이어 이미지 저장
        raise NotImplementedError

    def render(self, image_path: str, duration: float,
               depth_strength: float = 0.05) -> EffectParams:
        # TODO: 레이어별 다른 이동 속도로 시차 효과 생성
        raise NotImplementedError
