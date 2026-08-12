# Version: v2.2.0
# 功能：网页爬虫 + 小说更新检测 + 最新章节记录
# 更新：按最新章节、更新时间判断更新；页面结构Hash仅用于warning

import json
import time
import requests
import shutil
from pathlib import Path
from datetime import datetime, timezone, timedelta

from database import (
    init_database,
    save_page,
    get_page_by_url,
    calculate_hash,
    add_log,
    chapter_exists,
    save_chapter,
)
from parser import parse_page

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
            log(f"[CRAWL] 请求成功，HTTP {r.status_code}，内容长度: {len(html)}")
            return {"url": url, "html": html, "hash": calculate_hash(html)}
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


def write_warning(message, old_hash=None, new_hash=None):
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    warning_path = results_dir / "warning"
    lines = [
        "[WARNING] 页面结构可能发生变化",
        f"Time: {beijing_time().isoformat()}",
        f"URL: {TARGET_URL}",
        f"Previous Structure Hash: {old_hash or 'None'}",
        f"Current Structure Hash: {new_hash or 'None'}",
        f"Message: {message}",
    ]
    warning_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    log(f"[WARNING] 已生成: {warning_path}")


def determine_update(old, parsed):
    if old is None:
        return "new", "首次采集"

    old_latest_url = old[9]
    old_latest_title = old[8]
    old_update_time = old[10]

    if parsed["latest_chapter_url"] != (old_latest_url or ""):
        return "updated", "最新章节发生变化"

    if parsed["latest_chapter_title"] != (old_latest_title or ""):
        return "updated", "最新章节标题发生变化"

    if parsed["update_time"] != (old_update_time or ""):
        return "updated", "更新时间发生变化"

    return "unchanged", "最新章节与更新时间均未变化"


if __name__ == "__main__":
    log("[START] Crawler v2.2.0 启动")
    init_database()
    clean_expired_data()

    old = get_page_by_url(TARGET_URL)
    if old is None:
        log("[DATABASE] 未找到历史记录，将执行首次采集")
    else:
        log(
            f"[DATABASE] 找到历史记录，上一最新章节: {old[8] or 'None'}，"
            f"上一更新时间: {old[10] or 'None'}，上一结构Hash: {old[11] or 'None'}"
        )

    result = crawl_page(TARGET_URL)

    if "html" not in result:
        add_log(TARGET_URL, "failed", f"crawl failed: {result.get('error', 'unknown error')}")
        log("[RESULT] 爬取最终失败，已写入数据库日志")
        raise SystemExit(1)

    try:
        parsed = parse_page(result["html"], TARGET_URL)
    except Exception as exc:
        message = f"解析失败: {type(exc).__name__}: {exc}"
        write_warning(message)
        add_log(TARGET_URL, "warning", message)
        log(f"[WARNING] {message}")
        raise SystemExit(1)

    old_structure_hash = old[11] if old is not None else None
    structure_changed = old_structure_hash is not None and old_structure_hash != parsed["structure_hash"]
    if structure_changed:
        write_warning(
            "页面结构Hash发生变化，请检查最新page.html及parser.py解析规则。",
            old_structure_hash,
            parsed["structure_hash"],
        )
        add_log(TARGET_URL, "warning", "page structure hash changed")
    else:
        log("[STRUCTURE] 页面结构Hash正常")

    status, reason = determine_update(old, parsed)
    log(f"[UPDATE] {reason}，本次状态: {status}")

    # 页面Hash只作为页面记录，不参与章节更新判断。
    html_path = old[7] if old is not None and status == "unchanged" else None
    output_dir = None
    if status != "unchanged":
        output_dir = Path("results") / beijing_time().strftime("%Y%m%d") / beijing_time().strftime("%H%M")
        output_dir.mkdir(parents=True, exist_ok=True)
        html_path = str(output_dir / "page.html")
        Path(html_path).write_text(result["html"], encoding="utf-8")
        log(f"[ARCHIVE] 已保存 HTML: {html_path}")

    save_page(
        result["url"],
        parsed["title"],
        status,
        result["hash"],
        html_path,
        parsed["latest_chapter_title"],
        parsed["latest_chapter_url"],
        parsed["update_time"],
        parsed["structure_hash"],
    )

    page = get_page_by_url(TARGET_URL)
    page_id = page[0]
    new_chapters = 0
    for chapter in parsed["chapters"]:
        if chapter_exists(chapter["url"]):
            continue
        save_chapter(page_id, chapter["title"], chapter["url"], chapter["position"], "discovered")
        new_chapters += 1
        log(f"[CHAPTER] 发现新章节: {chapter['title']}")

    log(f"[CHAPTER] 当前页面共 {len(parsed['chapters'])} 个章节，其中新增 {new_chapters} 个")
    add_log(TARGET_URL, status, f"crawl success; new_chapters={new_chapters}")

    if output_dir is not None:
        result_json = {
            "url": result["url"],
            "title": parsed["title"],
            "author": parsed["author"],
            "category": parsed["category"],
            "status": parsed["status"],
            "update_time": parsed["update_time"],
            "latest_chapter_title": parsed["latest_chapter_title"],
            "latest_chapter_url": parsed["latest_chapter_url"],
            "structure_hash": parsed["structure_hash"],
            "chapters": parsed["chapters"],
            "page_hash": result["hash"],
        }
        (output_dir / "results.json").write_text(
            json.dumps(result_json, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    log("[END] Crawler finished")
