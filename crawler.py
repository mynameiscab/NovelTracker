# Version: v2.1
# 功能：网页爬虫 + SQLite增量数据管理

import json
import time
import requests
import urllib3
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime, timezone, timedelta

from database import init_database, save_page, get_page_by_url, calculate_hash, add_log

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
                if (now - old).days > DATA_EXPIRE_DAYS:
                    shutil.rmtree(date_dir)
            except ValueError:
                pass


def crawl_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = requests.get(url, headers=headers, timeout=10, verify=False)
            r.encoding = r.apparent_encoding
            if r.status_code == 200:
                html = r.text
                soup = BeautifulSoup(html, "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                return {
                    "url": url,
                    "title": soup.title.text.strip() if soup.title else "无标题",
                    "content_preview": text[:3000],
                    "html": html,
                    "hash": calculate_hash(text),
                    "time": beijing_time().isoformat(),
                    "retry_count": attempt
                }
        except Exception:
            pass
        if attempt < MAX_RETRIES:
            time.sleep(RETRY_INTERVAL)
    return {"url": url, "error": "failed"}


if __name__ == "__main__":
    init_database()
    clean_expired_data()

    old = get_page_by_url(TARGET_URL)
    result = crawl_page(TARGET_URL)

    if "html" in result:
        output_dir = Path("results") / beijing_time().strftime("%Y%m%d") / beijing_time().strftime("%H%M")
        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = str(output_dir / "page.html")
        Path(html_path).write_text(result["html"], encoding="utf-8")

        status = "updated"
        if old and old[4] == result["hash"]:
            status = "unchanged"

        save_page(result["url"], result["title"], status, result["hash"], html_path)
        add_log(TARGET_URL, status, "crawl success")

        result.pop("html")
        (output_dir / "results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        add_log(TARGET_URL, "failed", "crawl failed")

    print("Crawler finished")
