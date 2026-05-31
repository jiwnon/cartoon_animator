from pathlib import Path
from .tts_engine import TTSEngine
from .bgm_mapper import BGMMapper
from .sfx_mapper import SFXMapper


class AudioMixer:
    def __init__(self, config: dict):
        self.bgm_vol = config.get("bgm_volume", 0.3)
        self.sfx_vol = config.get("sfx_volume", 0.6)
        self.voice_vol = config.get("voice_volume", 1.0)
        self.rvc_enabled = config.get("rvc_enabled", False)

    def mix(self, input_dir: str,
            tts: TTSEngine, bgm: BGMMapper, sfx: SFXMapper) -> list[dict]:
        from classifier.panel_sorter import PanelSorter
        panels = PanelSorter().load(input_dir)
        out_dir = Path(input_dir)

        tts_results = tts.synthesize_all(panels, out_dir)

        if self.rvc_enabled:
            from .rvc_converter import RVCConverter
            rvc = RVCConverter()
            tts_results = rvc.convert_all(tts_results, out_dir)

        bgm_timeline = bgm.build_bgm_timeline(panels)
        sfx_list = [{"panel_order": p.order, "sfx": sfx.get_for_panel(p)} for p in panels]

        audio_tracks = self._merge_tracks(tts_results, bgm_timeline, sfx_list, out_dir)
        return audio_tracks

    def _merge_tracks(self, tts_results: list, bgm_timeline: list,
                      sfx_list: list, out_dir: Path) -> list[dict]:
        # TODO: pydub로 TTS + BGM + SFX 레이어 믹싱
        # 패널별 최종 오디오 파일 생성
        raise NotImplementedError
