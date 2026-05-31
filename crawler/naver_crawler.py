"""
네이버 웹툰 전용 크롤러

URL 형식: https://comic.naver.com/webtoon/detail?titleId=XXXXX&no=1

패널 이미지는 image-comic.pstatic.net 에서 서빙됨.
Referer: https://comic.naver.com 헤더 없으면 403.
"""

import time
import re
import requests
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from playwright.sync_api import sync_playwright, Page, Request
from .playwright_crawler import Panel


NAVER_HEADERS = {
    "Referer": "https://comic.naver.com",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
}

# 네이버 웹툰 패널 이미지 도메인
PANEL_IMAGE_DOMAINS = [
    "image-comic.pstatic.net",
    "imgcomic.naver.net",
    "comic.naver.com",
]


def is_panel_image(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(domain in host for domain in PANEL_IMAGE_DOMAINS)


class NaverWebtoonCrawler:
    def __init__(self, config: dict):
        self.delay = config.get("delay", 2.0)
        self.max_panels = config.get("max_panels", 100)
        self.headless = config.get("headless", True)

    def crawl(self, url: str) -> list[Panel]:
        """네이버 웹툰 에피소드 1개를 크롤링해서 Panel 리스트 반환."""
        print(f"[naver] 크롤링 시작: {url}")

        captured_urls: list[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=NAVER_HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 900},
            )
            page = context.new_page()

            # 네트워크 인터셉트: 패널 이미지 URL 수집
            def on_request(request: Request):
                if is_panel_image(request.url):
                    if request.url not in captured_urls:
                        captured_urls.append(request.url)

            page.on("request", on_request)

            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(1)

            # 스크롤 내려서 lazy-load 이미지 전부 트리거
            self._scroll_to_bottom(page)

            # 인터셉트로 못 잡은 이미지 img 태그에서 추가 수집
            img_urls = self._extract_img_tags(page)
            for u in img_urls:
                if u not in captured_urls:
                    captured_urls.append(u)

            browser.close()

        panel_urls = [u for u in captured_urls if self._looks_like_panel(u)]
        panel_urls = panel_urls[: self.max_panels]

        print(f"[naver] 패널 이미지 {len(panel_urls)}개 발견")

        panels = [
            Panel(order=i, image_url=url)
            for i, url in enumerate(panel_urls)
        ]
        return panels

    def _scroll_to_bottom(self, page: Page) -> None:
        prev_height = 0
        for _ in range(20):
            page.evaluate("window.scrollBy(0, window.innerHeight * 2)")
            time.sleep(0.5)
            height = page.evaluate("document.body.scrollHeight")
            if height == prev_height:
                break
            prev_height = height

    def _extract_img_tags(self, page: Page) -> list[str]:
        """img 태그에서 패널 이미지 URL 추출 (인터셉트 보완용)."""
        urls = page.evaluate("""
            () => Array.from(document.querySelectorAll('img'))
                       .map(img => img.src || img.dataset.src || '')
                       .filter(s => s.startsWith('http'))
        """)
        return [u for u in urls if is_panel_image(u)]

    def _looks_like_panel(self, url: str) -> bool:
        """썸네일/아이콘이 아닌 실제 패널 이미지인지 필터링."""
        lower = url.lower()
        # 아이콘, 프로필, 광고 제외
        exclude_keywords = ["thumb", "profile", "icon", "banner", "ad", "logo"]
        if any(kw in lower for kw in exclude_keywords):
            return False
        return True

    def download(self, panels: list[Panel], save_dir: Path) -> list[Panel]:
        """패널 이미지를 save_dir/panels/ 에 저장."""
        panels_dir = save_dir / "panels"
        panels_dir.mkdir(parents=True, exist_ok=True)

        session = requests.Session()
        session.headers.update(NAVER_HEADERS)

        for panel in panels:
            ext = self._guess_ext(panel.image_url)
            dest = panels_dir / f"{panel.order:03d}{ext}"

            try:
                resp = session.get(panel.image_url, timeout=15)
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                panel.image_path = str(dest)
                print(f"  [{panel.order:03d}] 저장 완료 ({len(resp.content)//1024}KB)")
            except Exception as e:
                print(f"  [{panel.order:03d}] 다운로드 실패: {e}")

            time.sleep(0.3)

        return panels

    def _guess_ext(self, url: str) -> str:
        path = urlparse(url).path.lower()
        for ext in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
            if path.endswith(ext):
                return ext
        return ".jpg"


def parse_naver_url(url: str) -> dict:
    """URL에서 titleId, 화수(no) 추출."""
    qs = parse_qs(urlparse(url).query)
    return {
        "title_id": qs.get("titleId", ["unknown"])[0],
        "episode": qs.get("no", ["1"])[0],
    }
