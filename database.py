# Version: v2.1.2
# 功能：SQLite数据库管理模块
# 更新：增加网页历史记录支持

import sqlite3
import hashlib
from datetime import datetime

DATABASE = "crawler.db"


def init_database():
    conn = sqlite3.connect(DATABASE)
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
        page_id INTEGER,
        old_hash TEXT,
        new_hash TEXT,
        time TEXT,
        html_path TEXT
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
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pages WHERE url=?", (url,))
    result = cursor.fetchone()
    conn.close()
    return result


def calculate_hash(content):
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def save_page(url, title, status, content_hash, html_path):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    old = get_page_by_url(url)

    if old:
        cursor.execute("INSERT INTO history(page_id,old_hash,new_hash,time,html_path) VALUES(?,?,?,?,?)", (old[0], old[4], content_hash, now, html_path))
        cursor.execute("UPDATE pages SET title=?,status=?,content_hash=?,crawl_time=?,update_time=?,html_path=? WHERE url=?", (title,status,content_hash,now,now,html_path,url))
    else:
        cursor.execute("INSERT INTO pages(url,title,status,content_hash,crawl_time,update_time,html_path) VALUES(?,?,?,?,?,?,?)", (url,title,status,content_hash,now,now,html_path))

    conn.commit()
    conn.close()


def add_log(url, result, message):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs(time,url,result,message) VALUES(?,?,?,?)", (datetime.now().isoformat(), url, result, message))
    conn.commit()
    conn.close()
