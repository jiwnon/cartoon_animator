"""
영상 변환 단독 테스트.
사용법: python test_animate.py --input data/800770/ep1 --count 5
"""
import argparse
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from classifier.panel_sorter import PanelSorter
from animator.camera_director import CameraDirector


# 테스트용 씬 타입 강제 지정 (분류기 없이도 돌리기 위해)
DEMO_TYPES = ["background", "dialogue", "action", "emotion", "dialogue"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/800770/ep1")
    parser.add_argument("--count", type=int, default=5)
    parser.add_argument("--classify", action="store_true", help="Ollama로 실제 분류 후 변환")
    args = parser.parse_args()

    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    panels = PanelSorter().load(args.input)[: args.count]

    if args.classify:
        from classifier.scene_classifier import SceneClassifier
        print("Ollama 씬 분류 중...")
        panels = SceneClassifier(config["classifier"]).classify_all(panels)
    else:
        for i, panel in enumerate(panels):
            panel.scene_type = DEMO_TYPES[i % len(DEMO_TYPES)]
            panel.scene_meta = {"pace": "normal", "focus_point": [0.5, 0.5], "duration": 3.0}
        print(f"데모 씬 타입 적용: {[p.scene_type for p in panels]}")

    clips_dir = Path(args.input) / "clips"
    clips_dir.mkdir(exist_ok=True)

    director = CameraDirector(config["animator"])
    clips = []
    print("=" * 50)
    for panel in panels:
        print(f"  [{panel.order:03d}] {panel.scene_type} 렌더링 중...")
        clip_path = director.render(panel, clips_dir)
        clips.append(clip_path)
        print(f"  [{panel.order:03d}] 완료 → {clip_path}")

    print("=" * 50)
    print(f"클립 {len(clips)}개 생성 완료 → {clips_dir}")

    # 간단히 이어붙이기
    if len(clips) > 1:
        from renderer.video_concat import VideoConcat
        out = Path(args.input) / "output" / "test_preview.mp4"
        out.parent.mkdir(exist_ok=True)
        VideoConcat().concat(clips, str(out))
        print(f"미리보기 영상 → {out}")


if __name__ == "__main__":
    main()
