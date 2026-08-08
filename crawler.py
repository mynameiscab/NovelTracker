# Version: v2.0
# 功能：网页爬虫 + SQLite历史数据存储
# 更新：集成数据库记录，保留HTML归档
# 目标：https://m.xsw.tw/1725663/

import json
import time
import requests
import urllib3
import shutil
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime, timezone, timedelta

from database import init_database, save_page

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
        if not date_dir.is_dir():
            continue

        try:
            dir_time = datetime.strptime(date_dir.name, "%Y%m%d").replace(tzinfo=BEIJING_TZ)
            if (now - dir_time).days > DATA_EXPIRE_DAYS:
                shutil.rmtree(date_dir)
                print("已清理过期数据:", date_dir)
        except ValueError:
            continue


def crawl_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=10, verify=False)
            response.encoding = response.apparent_encoding

            if response.status_code != 200:
                last_error = f"请求失败: {response.status_code}"
            else:
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
                title = soup.title.text.strip() if soup.title else "无标题"
                text = soup.get_text(separator="\n", strip=True)

                links = []
                for link in soup.find_all("a")[:50]:
                    href = link.get("href")
                    if href:
                        links.append(urljoin(url, href))

                return {
                    "url": url,
                    "title": title,
                    "content_preview": text[:3000],
                    "links": links,
                    "html": html,
                    "time": beijing_time().isoformat(),
                    "retry_count": attempt
                }

        except Exception as e:
            last_error = str(e)

        if attempt < MAX_RETRIES:
            time.sleep(RETRY_INTERVAL)

    return {
        "url": url,
        "error": last_error,
        "retry_count": MAX_RETRIES,
        "time": beijing_time().isoformat()
    }


if __name__ == "__main__":
    init_database()
    clean_expired_data()

    now = beijing_time()
    output_dir = Path("results") / now.strftime("%Y%m%d") / now.strftime("%H%M")
    output_dir.mkdir(parents=True, exist_ok=True)

    result = crawl_page(TARGET_URL)

    html_path = ""
    if "html" in result:
        html_path = str(output_dir / "page.html")
        Path(html_path).write_text(result["html"], encoding="utf-8")

    save_page(
        result.get("url", TARGET_URL),
        result.get("title", ""),
        "success" if "html" in result else "failed",
        html_path
    )

    json_result = result.copy()
    json_result.pop("html", None)

    (output_dir / "results.json").write_text(
        json.dumps(json_result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    txt_content = (
        f"网页标题:\n{result.get('title', '')}\n\n"
        f"正文预览:\n{result.get('content_preview', '')}\n"
    )

    (output_dir / "results.txt").write_text(txt_content, encoding="utf-8")

    print("结果已保存:", output_dir)
