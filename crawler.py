# Version: v1.0
# 功能：通用网页信息爬取工具
# 支持：标题、文本、链接提取

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
            print("请求失败:", response.status_code)
            return

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.text.strip() if soup.title else "无标题"

        print("网页标题:")
        print(title)

        print("\n正文预览:")
        text = soup.get_text(separator="\n", strip=True)
        print(text[:1000])

        print("\n链接:")
        for link in soup.find_all("a")[:20]:
            href = link.get("href")
            if href:
                print(urljoin(url, href))

    except Exception as e:
        print("错误:", e)


if __name__ == "__main__":
    target = input("请输入网页地址:")
    crawl_page(target)
