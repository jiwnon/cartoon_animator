"""
크롤링만 단독 테스트하는 스크립트.

사용법:
  python test_crawl.py --url "https://comic.naver.com/webtoon/detail?titleId=XXXXX&no=1"
"""

import argparse
import yaml
from pathlib import Path
from crawler.naver_crawler import NaverWebtoonCrawler, parse_naver_url


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="네이버 웹툰 에피소드 URL")
    parser.add_argument("--output", default="./data", help="저장 경로")
    parser.add_argument("--show", action="store_true", help="브라우저 화면 표시 (headless=False)")
    args = parser.parse_args()

    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if args.show:
        config["crawler"]["headless"] = False

    crawler = NaverWebtoonCrawler(config["crawler"])

    print("=" * 50)
    print(f"URL: {args.url}")
    print("=" * 50)

    panels = crawler.crawl(args.url)

    if not panels:
        print("[오류] 패널을 찾지 못했습니다.")
        print("  → --show 옵션으로 브라우저를 띄워 직접 확인해보세요.")
        return

    meta = parse_naver_url(args.url)
    save_dir = Path(args.output) / meta["title_id"] / f"ep{meta['episode']}"

    panels = crawler.download(panels, save_dir)

    saved = [p for p in panels if p.image_path]
    print("=" * 50)
    print(f"완료: {len(saved)}/{len(panels)}개 저장 → {save_dir}/panels/")
    print("=" * 50)


if __name__ == "__main__":
    main()
