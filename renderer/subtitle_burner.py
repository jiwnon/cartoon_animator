import ffmpeg
from pathlib import Path
from crawler.playwright_crawler import Panel


class SubtitleBurner:
    def generate_srt(self, panels: list[Panel], output_path: str) -> str:
        lines = []
        current_time = 0.0

        for i, panel in enumerate(panels):
            if not panel.dialogue_text:
                current_time += panel.scene_meta.get("duration", 3.0)
                continue

            duration = panel.scene_meta.get("duration", 3.0)
            start = self._to_srt_time(current_time)
            end = self._to_srt_time(current_time + duration)

            lines.append(f"{i + 1}")
            lines.append(f"{start} --> {end}")
            lines.append(panel.dialogue_text)
            lines.append("")
            current_time += duration

        Path(output_path).write_text("\n".join(lines), encoding="utf-8")
        return output_path

    def burn(self, video_path: str, srt_path: str, output_path: str) -> str:
        (
            ffmpeg
            .input(video_path)
            .filter("subtitles", srt_path)
            .output(output_path, vcodec="libx264", acodec="copy")
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path

    def _to_srt_time(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
