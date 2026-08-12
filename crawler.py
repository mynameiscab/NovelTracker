# Version: v2.1.3
# 功能：网页爬虫 + SQLite增量数据管理
# 更新：修复HTML重复保存、重试次数与HTTPS验证逻辑

import json
import time
import requests
import shutil
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime, timezone, timedelta

from database import init_database, save_page, get_page_by_url, calculate_hash, add_log

TARGET_URL = "https://m.xsw.tw/1725663/"
MAX_RETRIES = 3
RETRY_INTERVAL = 120
DATA_EXPIRE_DAYS = 7
BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_time():
    return datetime.now(BEIJING_TZ)


def clean_expired_data():
    results_dir = Path("results")
    if not results_dir.exists():
        return
    now = beijing_time()
    for date_dir in results_dir.iterdir():
        if date_dir.is_dir():
            try:
                old = datetime.strptime(date_dir.name, "%Y%m%d").replace(tzinfo=BEIJING_TZ)
                if (now - old).days >= DATA_EXPIRE_DAYS:
                    shutil.rmtree(date_dir)
            except ValueError:
                pass


def crawl_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    # MAX_RETRIES 表示失败后的重试次数，因此总请求次数最多为 1 + MAX_RETRIES。
    for attempt in range(MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=10, verify=True)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            return {
                "url": url,
                "title": soup.title.text.strip() if soup.title else "无标题",
                "content_preview": text[:3000],
                "html": html,
                "hash": calculate_hash(text)
            }
        except Exception:
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_INTERVAL)

    return {"url": url, "error": "failed"}


if __name__ == "__main__":
    init_database()
    clean_expired_data()

    old = get_page_by_url(TARGET_URL)
    result = crawl_page(TARGET_URL)

    if "html" in result:
        status = "new" if old is None else ("unchanged" if old[4] == result["hash"] else "updated")

        # 只有首次采集或内容发生变化时才生成新的 HTML 归档。
        html_path = old[7] if old is not None and status == "unchanged" else None
        output_dir = None
        if status != "unchanged":
            output_dir = Path("results") / beijing_time().strftime("%Y%m%d") / beijing_time().strftime("%H%M")
            output_dir.mkdir(parents=True, exist_ok=True)
            html_path = str(output_dir / "page.html")
            Path(html_path).write_text(result["html"], encoding="utf-8")

        save_page(result["url"], result["title"], status, result["hash"], html_path)
        add_log(TARGET_URL, status, "crawl success")

        result.pop("html")
        if output_dir is not None:
            (output_dir / "results.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
    else:
        add_log(TARGET_URL, "failed", "crawl failed")

    print("Crawler finished")
