from pathlib import Path


class TTSEngine:
    def __init__(self, config: dict):
        self.enabled = config.get("tts_enabled", True)
        self.model = config.get("tts_model", "kokoro")
        self._pipeline = None

    def _get_pipeline(self):
        if self._pipeline is None:
            # TODO: kokoro TTS 파이프라인 초기화
            raise NotImplementedError("Kokoro TTS 초기화 필요")
        return self._pipeline

    def synthesize(self, text: str, output_path: str,
                   voice: str = "af_heart", lang: str = "ko") -> str:
        # TODO: Kokoro TTS로 텍스트 → 음성 파일 생성
        # output_path에 .wav 저장
        raise NotImplementedError

    def synthesize_all(self, panels: list, output_dir: Path) -> list[dict]:
        tts_dir = output_dir / "tts"
        tts_dir.mkdir(exist_ok=True)

        results = []
        for panel in panels:
            if not panel.dialogue_text:
                results.append({"panel_order": panel.order, "audio_path": None, "duration": 0.0})
                continue

            out_path = str(tts_dir / f"tts_{panel.order:03d}.wav")
            self.synthesize(panel.dialogue_text, out_path)
            results.append({"panel_order": panel.order, "audio_path": out_path, "duration": None})

        return results
