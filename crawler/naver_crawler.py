"""
네이버 웹툰 전용 크롤러

URL 형식: https://comic.naver.com/webtoon/detail?titleId=XXXXX&no=1

패널 이미지는 image-comic.pstatic.net 에서 서빙됨.
Referer: https://comic.naver.com 헤더 없으면 403.
"""

import time
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

PANEL_IMAGE_DOMAINS = [
    "image-comic.pstatic.net",
    "imgcomic.naver.net",
]

# 이미지 magic bytes (파일 헤더)
IMAGE_MAGIC = {
    b"\xff\xd8\xff": ".jpg",
    b"\x89PNG": ".png",
    b"RIFF": ".webp",  # WebP: RIFF????WEBP
    b"GIF8": ".gif",
}

# 네이버 페이지 UI 이미지 URL 패턴 (패널 아님)
EXCLUDE_URL_KEYWORDS = [
    "thumb", "profile", "icon", "banner", "logo",
    "static.nid", "naver.net/static", "pay.naver",
]

# 실제 웹툰 패널은 보통 이 이상
MIN_PANEL_SIZE_KB = 20


def is_panel_domain(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(domain in host for domain in PANEL_IMAGE_DOMAINS)


def detect_image_ext(data: bytes) -> str | None:
    """magic bytes로 이미지 확장자 판별. 이미지가 아니면 None."""
    for magic, ext in IMAGE_MAGIC.items():
        if data[:len(magic)] == magic:
            # WebP 추가 검증
            if magic == b"RIFF" and data[8:12] != b"WEBP":
                continue
            return ext
    return None


class NaverWebtoonCrawler:
    def __init__(self, config: dict):
        self.delay = config.get("delay", 2.0)
        self.max_panels = config.get("max_panels", 200)
        self.headless = config.get("headless", True)

    def crawl(self, url: str) -> list[Panel]:
        print(f"[naver] 크롤링 시작: {url}")
        captured_urls: list[str] = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent=NAVER_HEADERS["User-Agent"],
                viewport={"width": 1280, "height": 900},
            )
            page = context.new_page()

            def on_request(request: Request):
                if is_panel_domain(request.url) and request.url not in captured_urls:
                    captured_urls.append(request.url)

            page.on("request", on_request)
            page.goto(url, wait_until="networkidle", timeout=30000)
            time.sleep(1)

            self._scroll_to_bottom(page)

            # img 태그 보완 수집
            for u in self._extract_img_tags(page):
                if u not in captured_urls:
                    captured_urls.append(u)

            browser.close()

        panel_urls = [u for u in captured_urls if self._looks_like_panel(u)]
        panel_urls = panel_urls[: self.max_panels]

        print(f"[naver] 후보 URL {len(panel_urls)}개 발견")
        return [Panel(order=i, image_url=u) for i, u in enumerate(panel_urls)]

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
        urls = page.evaluate("""
            () => Array.from(document.querySelectorAll('img'))
                       .map(img => img.src || img.dataset.src || '')
                       .filter(s => s.startsWith('http'))
        """)
        return [u for u in urls if is_panel_domain(u)]

    def _looks_like_panel(self, url: str) -> bool:
        lower = url.lower()
        return not any(kw in lower for kw in EXCLUDE_URL_KEYWORDS)

    def download(self, panels: list[Panel], save_dir: Path) -> list[Panel]:
        """다운로드 + magic bytes 검증 + 리넘버링."""
        panels_dir = save_dir / "panels"
        panels_dir.mkdir(parents=True, exist_ok=True)

        session = requests.Session()
        session.headers.update(NAVER_HEADERS)

        valid_panels = []
        for panel in panels:
            try:
                resp = session.get(panel.image_url, timeout=15)
                resp.raise_for_status()

                # Content-Type 확인
                ct = resp.headers.get("Content-Type", "")
                if "image" not in ct:
                    print(f"  [{panel.order:03d}] 건너뜀 (Content-Type: {ct})")
                    continue

                # 파일 크기 확인
                size_kb = len(resp.content) / 1024
                if size_kb < MIN_PANEL_SIZE_KB:
                    print(f"  [{panel.order:03d}] 건너뜀 ({size_kb:.1f}KB, 너무 작음)")
                    continue

                # magic bytes로 실제 이미지 검증
                ext = detect_image_ext(resp.content)
                if ext is None:
                    print(f"  [{panel.order:03d}] 건너뜀 (이미지 아님)")
                    continue

                dest = panels_dir / f"{len(valid_panels):03d}{ext}"
                dest.write_bytes(resp.content)

                panel.image_path = str(dest)
                panel.order = len(valid_panels)
                valid_panels.append(panel)
                print(f"  [{panel.order:03d}] 저장 완료 ({size_kb:.0f}KB)")

            except Exception as e:
                print(f"  [{panel.order:03d}] 다운로드 실패: {e}")

            time.sleep(0.2)

        print(f"[naver] 유효 패널 {len(valid_panels)}개 / 전체 {len(panels)}개")
        return valid_panels


def parse_naver_url(url: str) -> dict:
    qs = parse_qs(urlparse(url).query)
    return {
        "title_id": qs.get("titleId", ["unknown"])[0],
        "episode": qs.get("no", ["1"])[0],
    }
