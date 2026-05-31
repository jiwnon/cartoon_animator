"""
씬 분류 단독 테스트 스크립트.
사용법: python test_classify.py --input data/800770/ep1 --count 5
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import yaml
from classifier.panel_sorter import PanelSorter
from classifier.scene_classifier import SceneClassifier


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/800770/ep1", help="패널 디렉토리")
    parser.add_argument("--count", type=int, default=5, help="테스트할 패널 수")
    args = parser.parse_args()

    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    panels = PanelSorter().load(args.input)
    panels = panels[: args.count]

    print(f"Ollama 모델: {config['classifier']['model']}")
    print(f"테스트 패널: {len(panels)}개")
    print("=" * 50)

    classifier = SceneClassifier(config["classifier"])
    for panel in panels:
        try:
            result = classifier.classify(panel)
            narration = result.get("narration", "")
            dialogues = result.get("dialogues", [])
            print(f"[{panel.order:03d}] {result['type']:12s} conf={result.get('confidence', 0):.2f}  tags={result.get('tags', [])}")
            if narration:
                print(f"       내레이션: {narration}")
            if dialogues:
                for d in dialogues:
                    print(f"       대사: {d}")
        except Exception as e:
            print(f"[{panel.order:03d}] 오류: {e}")

    print("=" * 50)
    print("완료")


if __name__ == "__main__":
    main()
