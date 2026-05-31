from pathlib import Path


class RVCConverter:
    """RVC 기반 캐릭터 목소리 변환. rvc_enabled: true 일 때만 사용."""

    def __init__(self, model_path: str = None):
        self.model_path = model_path
        self._model = None

    def convert(self, audio_path: str, output_path: str,
                pitch_shift: int = 0) -> str:
        # TODO: RVC 모델로 목소리 변환
        # Applio / KLM Trainer 연동
        raise NotImplementedError

    def convert_all(self, tts_results: list[dict], output_dir: Path) -> list[dict]:
        rvc_dir = output_dir / "rvc"
        rvc_dir.mkdir(exist_ok=True)

        for item in tts_results:
            if not item.get("audio_path"):
                continue
            out_path = str(rvc_dir / Path(item["audio_path"]).name)
            item["audio_path"] = self.convert(item["audio_path"], out_path)

        return tts_results
