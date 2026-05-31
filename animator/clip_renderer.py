import ffmpeg
from .ken_burns import EffectParams


class ClipRenderer:
    def __init__(self, resolution: str = "1920x1080", fps: int = 30):
        self.resolution = resolution
        self.fps = fps

    def render(self, effect: EffectParams, output_path: str) -> str:
        vf = effect.ffmpeg_filter
        if effect.extra_filters:
            vf = vf + "," + ",".join(effect.extra_filters)

        (
            ffmpeg
            .input(effect.image_path, loop=1, t=effect.duration, framerate=self.fps)
            .output(
                output_path,
                vf=vf,
                vcodec="libx264",
                pix_fmt="yuv420p",
                r=self.fps,
                t=effect.duration,
            )
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
