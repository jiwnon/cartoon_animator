import argparse
import yaml
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def load_config(config_path: str = "config.yaml") -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_crawl(url: str, output_dir: str, config: dict):
    from crawler.playwright_crawler import WebtoonCrawler
    crawler = WebtoonCrawler(config["crawler"])
    panels = crawler.crawl(url)

    from crawler.ocr_extractor import OCRExtractor
    ocr = OCRExtractor()
    panels = ocr.extract_all(panels)

    from classifier.metadata_parser import MetadataParser
    meta = MetadataParser().parse(url)
    save_dir = Path(output_dir) / meta["title"] / meta["episode"]
    save_dir.mkdir(parents=True, exist_ok=True)

    from crawler.image_downloader import ImageDownloader
    ImageDownloader().save(panels, save_dir)
    print(f"[crawl] {len(panels)} panels saved → {save_dir}")
    return save_dir, meta


def run_classify(input_dir: str, config: dict):
    from classifier.panel_sorter import PanelSorter
    from classifier.scene_classifier import SceneClassifier

    panels = PanelSorter().load(input_dir)
    classifier = SceneClassifier(config["classifier"])
    results = classifier.classify_all(panels)
    print(f"[classify] {len(results)} panels classified")
    return results


def run_animate(input_dir: str, config: dict):
    from animator.camera_director import CameraDirector

    director = CameraDirector(config["animator"])
    clips = director.render_all(input_dir)
    print(f"[animate] {len(clips)} clips rendered")
    return clips


def run_audio(input_dir: str, config: dict):
    from audio.tts_engine import TTSEngine
    from audio.bgm_mapper import BGMMapper
    from audio.sfx_mapper import SFXMapper
    from audio.audio_mixer import AudioMixer

    tts = TTSEngine(config["audio"])
    bgm = BGMMapper()
    sfx = SFXMapper()
    mixer = AudioMixer(config["audio"])

    audio_tracks = mixer.mix(input_dir, tts, bgm, sfx)
    print(f"[audio] {len(audio_tracks)} audio tracks generated")
    return audio_tracks


def run_render(input_dir: str, output_path: str, config: dict):
    from renderer.final_render import FinalRenderer

    renderer = FinalRenderer(config["renderer"])
    renderer.render(input_dir, output_path)
    print(f"[render] output → {output_path}")


def run_all(url: str, output_dir: str, config: dict):
    save_dir, meta = run_crawl(url, output_dir, config)
    input_dir = str(save_dir)
    run_classify(input_dir, config)
    run_animate(input_dir, config)
    run_audio(input_dir, config)
    out_file = save_dir / "output" / f"{meta['title']}_{meta['episode']}.mp4"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    run_render(input_dir, str(out_file), config)


def main():
    parser = argparse.ArgumentParser(description="WebtoonAnimate pipeline")
    parser.add_argument("--step", choices=["crawl", "classify", "animate", "audio", "render", "all"], default="all")
    parser.add_argument("--url", type=str, help="Webtoon episode URL (required for crawl/all)")
    parser.add_argument("--input", type=str, help="Input directory (for classify/animate/audio/render)")
    parser.add_argument("--output", type=str, default="./data", help="Output root directory")
    parser.add_argument("--config", type=str, default="config.yaml")
    args = parser.parse_args()

    config = load_config(args.config)

    if args.step == "all":
        if not args.url:
            parser.error("--url is required for --step all")
        run_all(args.url, args.output, config)

    elif args.step == "crawl":
        if not args.url:
            parser.error("--url is required for --step crawl")
        run_crawl(args.url, args.output, config)

    elif args.step == "classify":
        run_classify(args.input, config)

    elif args.step == "animate":
        run_animate(args.input, config)

    elif args.step == "audio":
        run_audio(args.input, config)

    elif args.step == "render":
        out_file = Path(args.input) / "output" / "final.mp4"
        run_render(args.input, str(out_file), config)


if __name__ == "__main__":
    main()
