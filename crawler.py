# Version: v1.2
# 功能：自动爬取网页信息并保存带时间戳的 txt/json 结果
# 目标：m.xsw.tw
# 输出：results/时间戳/results.txt, results.json

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
from datetime import datetime

TARGET_URL = "https://m.xsw.tw"


def crawl_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10
        )

        response.encoding = response.apparent_encoding

        if response.status_code != 200:
            return {
                "url": url,
                "error": f"请求失败: {response.status_code}"
            }

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.text.strip() if soup.title else "无标题"

        text = soup.get_text(
            separator="\n",
            strip=True
        )

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
            "time": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "url": url,
            "error": str(e)
        }


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_dir = Path("results") / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    result = crawl_page(TARGET_URL)

    # 保存 JSON
    (output_dir / "results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    # 保存 TXT
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
