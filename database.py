# Version: v2.0
# 功能：SQLite数据库管理模块

import sqlite3
from datetime import datetime

DATABASE = "crawler.db"


def init_database():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        title TEXT,
        status TEXT,
        crawl_time TEXT,
        html_path TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_page(url, title, status, html_path):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO pages
        (url, title, status, crawl_time, html_path)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            url,
            title,
            status,
            datetime.now().isoformat(),
            html_path
        )
    )

    conn.commit()
    conn.close()
