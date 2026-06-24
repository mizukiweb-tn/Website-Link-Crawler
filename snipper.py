import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

# --- 設定 ---
REQUEST_TIMEOUT = 10      # タイムアウト（秒）
REQUEST_DELAY = 0.5       # リクエスト間の待機時間（秒）
MAX_WORKERS = 5           # 同時スレッド数
USER_AGENT = "MyPortfolioCrawler/1.0"


def get_robots_parser(base_url: str) -> RobotFileParser:
    """robots.txt を取得してパーサーを返す"""
    rp = RobotFileParser()
    robots_url = urljoin(base_url, "/robots.txt")
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        pass  # robots.txt がなければ許可とみなす
    return rp


def fetch_links(url: str, base_url: str) -> list[str]:
    """指定URLのページから同一ドメイン・同一パスのリンクを取得する"""
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    parsed_base = urlparse(base_url)
    links = []

    for tag in soup.find_all("a", href=True):
        next_url = urljoin(url, tag["href"])
        parsed_next = urlparse(next_url)

        # 同一ドメイン・同一パス配下・フラグメントなし に絞る
        if (
            parsed_next.netloc == parsed_base.netloc
            and parsed_next.path.startswith(parsed_base.path)
            and not parsed_next.fragment
        ):
            # クエリやフラグメントを除いた正規化URL
            clean_url = parsed_next._replace(fragment="").geturl()
            links.append(clean_url)

    return links


def crawl(start_url: str, max_depth: int = 2) -> list[str]:
    """
    BFS（幅優先）でクローリングし、訪問したURLのリストを返す。

    Args:
        start_url: クローリング開始URL
        max_depth: 最大深さ

    Returns:
        訪問したURLのリスト
    """
    base_url = start_url
    visited: set[str] = set()
    visited_lock = threading.Lock()
    results: list[str] = []
    results_lock = threading.Lock()

    robots = get_robots_parser(base_url)

    # (url, depth) のキューをBFSで処理
    queue = [(start_url, 0)]
    queue_lock = threading.Lock()

    def process(url: str, depth: int):
        # robots.txt チェック
        if not robots.can_fetch(USER_AGENT, url):
            print(f"[SKIP] robots.txt により除外: {url}")
            return

        time.sleep(REQUEST_DELAY)  # サーバー負荷対策
        links = fetch_links(url, base_url)

        print(f"[depth={depth}] {url}")
        with results_lock:
            results.append(url)

        if depth >= max_depth:
            return

        new_tasks = []
        with visited_lock:
            for link in links:
                if link not in visited:
                    visited.add(link)
                    new_tasks.append((link, depth + 1))

        # 新しいURLをキューに追加（スレッドプール内でサブミット）
        with queue_lock:
            queue.extend(new_tasks)

    with visited_lock:
        visited.add(start_url)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process, start_url, 0)}

        while futures:
            done = set()
            for future in as_completed(futures):
                done.add(future)
                future.result()  # 例外を再スローさせる

                # キューに新しいURLがあれば追加
                with queue_lock:
                    while queue:
                        url, depth = queue.pop(0)
                        futures.add(executor.submit(process, url, depth))

            futures -= done

    return results


if __name__ == "__main__":
    start_url = "https://example.com/"
    max_depth = 3

    print(f"クローリング開始: {start_url} (最大深さ: {max_depth})")
    found_urls = crawl(start_url, max_depth)
    print(f"\n合計 {len(found_urls)} ページを収集しました。")