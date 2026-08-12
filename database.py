# Version: v2.2.0
# 功能：SQLite数据库管理模块 + 小说更新与章节记录
# 更新：增加最新章节、更新时间、页面结构Hash及章节表

import sqlite3
import hashlib
from datetime import datetime

DATABASE = "crawler.db"


def connect_database():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_database():
    conn = connect_database()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL,
        title TEXT,
        status TEXT,
        content_hash TEXT,
        crawl_time TEXT,
        update_time TEXT,
        html_path TEXT,
        latest_chapter_title TEXT,
        latest_chapter_url TEXT,
        page_update_time TEXT,
        structure_hash TEXT
    )
    """)

    # Backward-compatible migration for existing v2.1 databases.
    existing_columns = {row[1] for row in cursor.execute("PRAGMA table_info(pages)").fetchall()}
    for name, definition in [
        ("latest_chapter_title", "TEXT"),
        ("latest_chapter_url", "TEXT"),
        ("page_update_time", "TEXT"),
        ("structure_hash", "TEXT"),
    ]:
        if name not in existing_columns:
            cursor.execute(f"ALTER TABLE pages ADD COLUMN {name} {definition}")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        old_hash TEXT,
        new_hash TEXT,
        time TEXT,
        html_path TEXT,
        FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chapters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        page_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL UNIQUE,
        position INTEGER,
        crawl_time TEXT,
        content_hash TEXT,
        content_path TEXT,
        status TEXT,
        FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT,
        url TEXT,
        result TEXT,
        message TEXT
    )
    """)

    conn.commit()
    conn.close()


def get_page_by_url(url):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages WHERE url=?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result


def calculate_hash(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def save_page(url, title, status, content_hash, html_path=None, latest_chapter_title=None,
              latest_chapter_url=None, page_update_time=None, structure_hash=None):
    conn = connect_database()
    cursor = conn.cursor()
    now = datetime.now().isoformat()

    cursor.execute("SELECT * FROM pages WHERE url=?", (url,))
    old = cursor.fetchone()

    if old:
        # pages.update_time 表示页面检测状态发生变化的时间；
        # page_update_time 表示网站页面中的“更新：”字段。
        update_time = old[6]
        final_html_path = old[7]

        if status == "updated":
            update_time = now
            final_html_path = html_path
            cursor.execute(
                "INSERT INTO history(page_id,old_hash,new_hash,time,html_path) VALUES(?,?,?,?,?)",
                (old[0], old[4], content_hash, now, html_path)
            )
        elif status == "new":
            update_time = now
            final_html_path = html_path

        cursor.execute(
            """
            UPDATE pages
            SET title=?, status=?, content_hash=?, crawl_time=?, update_time=?, html_path=?,
                latest_chapter_title=?, latest_chapter_url=?, page_update_time=?, structure_hash=?
            WHERE url=?
            """,
            (title, status, content_hash, now, update_time, final_html_path,
             latest_chapter_title, latest_chapter_url, page_update_time, structure_hash, url)
        )
    else:
        cursor.execute(
            """
            INSERT INTO pages(
                url,title,status,content_hash,crawl_time,update_time,html_path,
                latest_chapter_title,latest_chapter_url,page_update_time,structure_hash
            ) VALUES(?,?,?,?,?,?,?,?,?,?,?)
            """,
            (url, title, status, content_hash, now, now, html_path,
             latest_chapter_title, latest_chapter_url, page_update_time, structure_hash)
        )

    conn.commit()
    conn.close()


def chapter_exists(url):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM chapters WHERE url=? LIMIT 1", (url,))
    result = cursor.fetchone() is not None
    conn.close()
    return result


def save_chapter(page_id, title, url, position, status="discovered"):
    conn = connect_database()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT OR IGNORE INTO chapters(page_id,title,url,position,crawl_time,status)
        VALUES(?,?,?,?,?,?)
        """,
        (page_id, title, url, position, now, status)
    )
    conn.commit()
    conn.close()


def add_log(url, result, message):
    conn = connect_database()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs(time,url,result,message) VALUES(?,?,?,?)",
        (datetime.now().isoformat(), url, result, message)
    )
    conn.commit()
    conn.close()
