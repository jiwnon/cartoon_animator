import ffmpeg
from pathlib import Path


class VideoConcat:
    def concat(self, clip_paths: list[str], output_path: str) -> str:
        list_file = Path(output_path).parent / "clip_list.txt"
        with open(list_file, "w", encoding="utf-8") as f:
            for path in clip_paths:
                f.write(f"file '{Path(path).resolve()}'\n")

        (
            ffmpeg
            .input(str(list_file), format="concat", safe=0)
            .output(output_path, c="copy")
            .overwrite_output()
            .run(quiet=True)
        )
        list_file.unlink(missing_ok=True)
        return output_path
