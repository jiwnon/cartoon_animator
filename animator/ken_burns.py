from dataclasses import dataclass
from typing import Optional


@dataclass
class EffectParams:
    image_path: str
    duration: float
    ffmpeg_filter: str
    extra_filters: list[str] = None


class KenBurns:
    def __init__(self, resolution: str = "1920x1080", fps: int = 30):
        self.resolution = resolution
        self.fps = fps
        w, h = resolution.split("x")
        self.w, self.h = int(w), int(h)

    def _base_zoompan(self, image_path: str, duration: float,
                      zoom_expr: str, x_expr: str, y_expr: str) -> EffectParams:
        d_frames = int(duration * self.fps)
        ffmpeg_filter = (
            f"zoompan=z='{zoom_expr}':"
            f"x='{x_expr}':y='{y_expr}':"
            f"d={d_frames}:s={self.resolution}:fps={self.fps}"
        )
        return EffectParams(image_path=image_path, duration=duration, ffmpeg_filter=ffmpeg_filter)

    def zoom_in_shake(self, image_path: str, duration: float,
                       pace: str = "normal", focus: list = None) -> EffectParams:
        # 빠른 줌인 + 흔들림 (액션씬)
        params = self._base_zoompan(
            image_path, duration,
            zoom_expr="if(lte(zoom,1.0),1.0,zoom+0.008)",
            x_expr="iw/2-(iw/zoom/2)",
            y_expr="ih/2-(ih/zoom/2)",
        )
        # TODO: hue 채도 올리기, shake 효과 추가
        params.extra_filters = ["hue=s=1.2"]
        return params

    def slow_zoom_in(self, image_path: str, duration: float,
                      focus: list = None) -> EffectParams:
        # 느린 줌인 후 정지 (감정씬)
        fx = focus[0] if focus else 0.5
        fy = focus[1] if focus else 0.5
        return self._base_zoompan(
            image_path, duration,
            zoom_expr="if(lte(zoom,1.0),1.0,zoom+0.002)",
            x_expr=f"iw*{fx}-(iw/zoom/2)",
            y_expr=f"ih*{fy}-(ih/zoom/2)",
        )

    def panorama_pan(self, image_path: str, duration: float) -> EffectParams:
        # 좌→우 파노라마 팬 (배경씬)
        d_frames = int(duration * self.fps)
        ffmpeg_filter = (
            f"zoompan=z='1.05':"
            f"x='iw*on/{d_frames}':y='ih/2-(ih/zoom/2)':"
            f"d={d_frames}:s={self.resolution}:fps={self.fps}"
        )
        return EffectParams(image_path=image_path, duration=duration, ffmpeg_filter=ffmpeg_filter)

    def subtle_zoom(self, image_path: str, duration: float,
                     focus: list = None) -> EffectParams:
        # 미세 줌인 (대화씬)
        return self._base_zoompan(
            image_path, duration,
            zoom_expr="if(lte(zoom,1.0),1.0,zoom+0.001)",
            x_expr="iw/2-(iw/zoom/2)",
            y_expr="ih/2-(ih/zoom/2)",
        )

    def static(self, image_path: str, duration: float) -> EffectParams:
        # 정지 (기타)
        d_frames = int(duration * self.fps)
        ffmpeg_filter = (
            f"zoompan=z='1.0':x='0':y='0':"
            f"d={d_frames}:s={self.resolution}:fps={self.fps}"
        )
        return EffectParams(image_path=image_path, duration=duration, ffmpeg_filter=ffmpeg_filter)
