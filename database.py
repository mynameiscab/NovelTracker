# Version: v2.1.3
# 功能：SQLite数据库管理模块
# 更新：修复历史记录、更新时间与数据库外键逻辑

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
        html_path TEXT
    )
    """)

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


def save_page(url, title, status, content_hash, html_path=None):
    conn = connect_database()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    old = None

    cursor.execute("SELECT * FROM pages WHERE url=?", (url,))
    old = cursor.fetchone()

    if old:
        # 每次成功爬取都更新 crawl_time；只有内容实际变化时才更新 update_time。
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
            "UPDATE pages SET title=?,status=?,content_hash=?,crawl_time=?,update_time=?,html_path=? WHERE url=?",
            (title, status, content_hash, now, update_time, final_html_path, url)
        )
    else:
        cursor.execute(
            "INSERT INTO pages(url,title,status,content_hash,crawl_time,update_time,html_path) VALUES(?,?,?,?,?,?,?)",
            (url, title, status, content_hash, now, now, html_path)
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
