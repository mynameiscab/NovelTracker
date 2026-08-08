# Version: v1.8
# 功能：自动爬取网页信息并保存北京时间 txt/json/html 结果
# 目标：https://m.xsw.tw/1725663/
# 输出：results/年月日/时间/results.txt, results.json, page.html

import json
import time
import requests
import urllib3
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime, timezone, timedelta

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TARGET_URL = "https://m.xsw.tw/1725663/"

MAX_RETRIES = 3
RETRY_INTERVAL = 120

BEIJING_TZ = timezone(timedelta(hours=8))


def beijing_time():
    return datetime.now(BEIJING_TZ)


def crawl_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=False
            )
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
    now = beijing_time()
    date_dir = now.strftime("%Y%m%d")
    time_dir = now.strftime("%H%M")

    output_dir = Path("results") / date_dir / time_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    result = crawl_page(TARGET_URL)

    # 保存完整 HTML
    if "html" in result:
        (output_dir / "page.html").write_text(
            result["html"],
            encoding="utf-8"
        )

    # JSON 不保存完整 HTML
    json_result = result.copy()
    json_result.pop("html", None)
    if "html" in result:
        json_result["html_file"] = "page.html"

    (output_dir / "results.json").write_text(
        json.dumps(json_result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    txt_content = (
        f"网页标题:\n{result.get('title', '')}\n\n"
        f"正文预览:\n{result.get('content_preview', '')}\n\n"
        f"链接:\n" + "\n".join(result.get("links", []))
    )

    (output_dir / "results.txt").write_text(
        txt_content,
        encoding="utf-8"
    )

    print("结果已保存:", output_dir)
