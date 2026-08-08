# Version: v1.1
# 功能：自动爬取网页信息并保存结果
# 目标：m.xsw.tw
# 输出：results/result.txt

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

TARGET_URL = "https://m.xsw.tw"
OUTPUT_FILE = Path("results/result.txt")


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
            return f"请求失败: {response.status_code}"

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

        result = []
        result.append("网页标题:")
        result.append(title)
        result.append("\n正文预览:")
        result.append(text[:3000])
        result.append("\n链接:")
        result.extend(links)

        return "\n".join(result)

    except Exception as e:
        return f"错误: {e}"


if __name__ == "__main__":
    OUTPUT_FILE.parent.mkdir(exist_ok=True)

    result = crawl_page(TARGET_URL)

    OUTPUT_FILE.write_text(
        result,
        encoding="utf-8"
    )

    print("结果已保存:", OUTPUT_FILE)
