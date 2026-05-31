from dataclasses import dataclass, field


@dataclass
class EffectParams:
    image_path: str
    duration: float
    ffmpeg_filter: str
    resolution: str = "720x1080"
    extra_filters: list[str] = field(default_factory=list)


class KenBurns:
    def __init__(self, fps: int = 30):
        self.fps = fps

    def _base_zoompan(self, image_path: str, duration: float, resolution: str,
                      zoom_expr: str, x_expr: str, y_expr: str) -> EffectParams:
        d_frames = int(duration * self.fps)
        ffmpeg_filter = (
            f"zoompan=z='{zoom_expr}':"
            f"x='{x_expr}':y='{y_expr}':"
            f"d={d_frames}:s={resolution}:fps={self.fps}"
        )
        return EffectParams(image_path=image_path, duration=duration,
                            ffmpeg_filter=ffmpeg_filter, resolution=resolution)

    def zoom_in_shake(self, image_path: str, duration: float, resolution: str,
                      pace: str = "normal", focus: list = None) -> EffectParams:
        params = self._base_zoompan(
            image_path, duration, resolution,
            zoom_expr="if(lte(zoom,1.0),1.0,zoom+0.008)",
            x_expr="iw/2-(iw/zoom/2)",
            y_expr="ih/2-(ih/zoom/2)",
        )
        params.extra_filters = ["hue=s=1.2"]
        return params

    def slow_zoom_in(self, image_path: str, duration: float, resolution: str,
                     focus: list = None) -> EffectParams:
        fx = focus[0] if focus else 0.5
        fy = focus[1] if focus else 0.5
        return self._base_zoompan(
            image_path, duration, resolution,
            zoom_expr="if(lte(zoom,1.0),1.0,zoom+0.002)",
            x_expr=f"iw*{fx}-(iw/zoom/2)",
            y_expr=f"ih*{fy}-(ih/zoom/2)",
        )

    def panorama_pan(self, image_path: str, duration: float,
                     resolution: str) -> EffectParams:
        d_frames = int(duration * self.fps)
        ffmpeg_filter = (
            f"zoompan=z='1.05':"
            f"x='iw*on/{d_frames}':y='ih/2-(ih/zoom/2)':"
            f"d={d_frames}:s={resolution}:fps={self.fps}"
        )
        return EffectParams(image_path=image_path, duration=duration,
                            ffmpeg_filter=ffmpeg_filter, resolution=resolution)

    def subtle_zoom(self, image_path: str, duration: float, resolution: str,
                    focus: list = None) -> EffectParams:
        return self._base_zoompan(
            image_path, duration, resolution,
            zoom_expr="if(lte(zoom,1.0),1.0,zoom+0.001)",
            x_expr="iw/2-(iw/zoom/2)",
            y_expr="ih/2-(ih/zoom/2)",
        )

    def static(self, image_path: str, duration: float,
               resolution: str) -> EffectParams:
        d_frames = int(duration * self.fps)
        ffmpeg_filter = (
            f"zoompan=z='1.0':x='0':y='0':"
            f"d={d_frames}:s={resolution}:fps={self.fps}"
        )
        return EffectParams(image_path=image_path, duration=duration,
                            ffmpeg_filter=ffmpeg_filter, resolution=resolution)
