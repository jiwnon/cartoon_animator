import ffmpeg
from pathlib import Path
from .video_concat import VideoConcat
from .subtitle_burner import SubtitleBurner

QUALITY_MAP = {
    "low":    28,
    "medium": 23,
    "high":   18,
}


class FinalRenderer:
    def __init__(self, config: dict):
        self.fmt = config.get("format", "mp4")
        self.crf = QUALITY_MAP.get(config.get("quality", "high"), 18)
        self.subtitle = config.get("subtitle", True)
        self.concat = VideoConcat()
        self.sub_burner = SubtitleBurner()

    def render(self, input_dir: str, output_path: str) -> str:
        input_dir = Path(input_dir)
        clips_dir = input_dir / "clips"
        audio_dir = input_dir / "audio"
        out_dir = Path(output_path).parent
        out_dir.mkdir(parents=True, exist_ok=True)

        clip_paths = sorted(clips_dir.glob("clip_*.mp4"), key=lambda p: p.name)
        if not clip_paths:
            raise FileNotFoundError(f"clips not found in {clips_dir}")

        concat_path = str(out_dir / "concat.mp4")
        self.concat.concat([str(p) for p in clip_paths], concat_path)

        mixed_audio = audio_dir / "mixed.mp3"
        if mixed_audio.exists():
            muxed_path = str(out_dir / "muxed.mp4")
            self._mux_audio(concat_path, str(mixed_audio), muxed_path)
        else:
            muxed_path = concat_path

        if self.subtitle:
            srt_path = str(input_dir / "subtitles.srt")
            if Path(srt_path).exists():
                final_path = self.sub_burner.burn(muxed_path, srt_path, output_path)
            else:
                final_path = muxed_path
        else:
            final_path = muxed_path

        if final_path != output_path:
            Path(final_path).rename(output_path)

        return output_path

    def _mux_audio(self, video_path: str, audio_path: str, output_path: str) -> str:
        video = ffmpeg.input(video_path)
        audio = ffmpeg.input(audio_path)
        (
            ffmpeg
            .output(video, audio, output_path,
                    vcodec="copy", acodec="aac",
                    crf=self.crf, shortest=None)
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
