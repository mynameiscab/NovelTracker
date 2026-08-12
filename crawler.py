# Version: v2.1.4
# 功能：网页爬虫 + SQLite增量数据管理
# 更新：增加运行日志、异常详情，并按要求关闭HTTPS证书验证

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


def log(message):
    print(f"[{beijing_time().strftime('%Y-%m-%d %H:%M:%S')}] {message}", flush=True)


def clean_expired_data():
    results_dir = Path("results")
    if not results_dir.exists():
        log("[CLEANUP] results目录不存在，跳过清理")
        return
    now = beijing_time()
    removed = 0
    for date_dir in results_dir.iterdir():
        if date_dir.is_dir():
            try:
                old = datetime.strptime(date_dir.name, "%Y%m%d").replace(tzinfo=BEIJING_TZ)
                if (now - old).days >= DATA_EXPIRE_DAYS:
                    shutil.rmtree(date_dir)
                    removed += 1
                    log(f"[CLEANUP] 删除过期目录: {date_dir}")
            except ValueError:
                pass
    log(f"[CLEANUP] 清理完成，删除 {removed} 个目录")


def crawl_page(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    total_attempts = MAX_RETRIES + 1
    log(f"[CRAWL] 开始请求: {url}")

    for attempt in range(1, total_attempts + 1):
        log(f"[CRAWL] 请求尝试 {attempt}/{total_attempts}")
        try:
            r = requests.get(url, headers=headers, timeout=10, verify=False)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            html = r.text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
            log(f"[CRAWL] 请求成功，HTTP {r.status_code}，内容长度: {len(html)}")
            return {
                "url": url,
                "title": soup.title.text.strip() if soup.title else "无标题",
                "content_preview": text[:3000],
                "html": html,
                "hash": calculate_hash(text)
            }
        except requests.exceptions.Timeout as exc:
            error = f"Timeout: {exc}"
        except requests.exceptions.SSLError as exc:
            error = f"SSLError: {exc}"
        except requests.exceptions.ConnectionError as exc:
            error = f"ConnectionError: {exc}"
        except requests.exceptions.HTTPError as exc:
            error = f"HTTPError: {exc}"
        except requests.exceptions.RequestException as exc:
            error = f"RequestException: {exc}"
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"

        log(f"[ERROR] 请求失败 ({attempt}/{total_attempts}): {error}")
        if attempt < total_attempts:
            log(f"[RETRY] {RETRY_INTERVAL} 秒后进行第 {attempt} 次重试")
            time.sleep(RETRY_INTERVAL)

    log(f"[ERROR] 所有请求均失败，共尝试 {total_attempts} 次")
    return {"url": url, "error": "failed"}


if __name__ == "__main__":
    log("[START] Crawler v2.1.4 启动")
    init_database()
    clean_expired_data()

    old = get_page_by_url(TARGET_URL)
    if old is None:
        log("[DATABASE] 未找到历史记录，将执行首次采集")
    else:
        log(f"[DATABASE] 找到历史记录，上一状态: {old[3]}，上一Hash: {old[4]}")

    result = crawl_page(TARGET_URL)

    if "html" in result:
        status = "new" if old is None else ("unchanged" if old[4] == result["hash"] else "updated")
        log(f"[DATABASE] 本次状态: {status}")

        # 只有首次采集或内容发生变化时才生成新的 HTML 归档。
        html_path = old[7] if old is not None and status == "unchanged" else None
        output_dir = None
        if status != "unchanged":
            output_dir = Path("results") / beijing_time().strftime("%Y%m%d") / beijing_time().strftime("%H%M")
            output_dir.mkdir(parents=True, exist_ok=True)
            html_path = str(output_dir / "page.html")
            Path(html_path).write_text(result["html"], encoding="utf-8")
            log(f"[ARCHIVE] 已保存 HTML: {html_path}")

        save_page(result["url"], result["title"], status, result["hash"], html_path)
        add_log(TARGET_URL, status, "crawl success")

        result.pop("html")
        if output_dir is not None:
            (output_dir / "results.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
    else:
        add_log(TARGET_URL, "failed", f"crawl failed: {result.get('error', 'unknown error')}")
        log("[RESULT] 爬取最终失败，已写入数据库日志")

    log("[END] Crawler finished")
