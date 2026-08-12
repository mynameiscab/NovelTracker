# Version: v2.2.0
# 功能：解析小说主页中的更新信息、最新章节和页面结构

import hashlib
import json
from urllib.parse import urljoin

from bs4 import BeautifulSoup


def _text(node):
    return node.get_text(" ", strip=True) if node else ""


def _value_from_label(block, label):
    for p in block.find_all("p", recursive=False):
        text = _text(p)
        if text.startswith(label):
            link = p.find("a")
            if link:
                return _text(link), link.get("href", "")
            return text[len(label):].strip(), ""
    return "", ""


def _structure_node(node):
    """Create a structure-only representation; ignore text and dynamic URLs."""
    if not getattr(node, "name", None):
        return None
    children = [x for x in (_structure_node(child) for child in node.children) if x]
    return {
        "tag": node.name,
        "id": node.get("id", ""),
        "class": node.get("class", []),
        "children": children,
    }


def _structure_signature(cover):
    # Ignore chapter count/content so normal new-chapter updates do not trigger warnings.
    chapter = cover.select_one("ul.chapter")
    if chapter:
        clone = BeautifulSoup(str(chapter), "html.parser").select_one("ul.chapter")
        items = clone.find_all("li", recursive=False)
        for item in items[1:]:
            item.decompose()
        cover_copy = BeautifulSoup(str(cover), "html.parser").select_one(".cover")
        old_chapter = cover_copy.select_one("ul.chapter")
        if old_chapter:
            old_items = old_chapter.find_all("li", recursive=False)
            for item in old_items[1:]:
                item.decompose()
        structure = _structure_node(cover_copy)
    else:
        structure = _structure_node(cover)
    payload = json.dumps(structure, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.md5(payload.encode("utf-8")).hexdigest()


def parse_page(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    cover = soup.select_one("div.cover")
    if cover is None:
        raise ValueError("未找到 div.cover，页面结构可能已变化")

    block = cover.select_one("div.block_txt2")
    if block is None:
        raise ValueError("未找到 div.block_txt2，页面结构可能已变化")

    title_node = block.find("h2", recursive=False)
    title = _text(title_node)
    if not title:
        raise ValueError("未找到小说标题 h2")

    author, author_url = _value_from_label(block, "作者：")
    category, category_url = _value_from_label(block, "分類：")
    status, _ = _value_from_label(block, "狀態：")
    update_time, _ = _value_from_label(block, "更新：")
    latest_chapter_title, latest_chapter_url = _value_from_label(block, "最新：")

    chapter_list = cover.select_one("ul.chapter")
    if chapter_list is None:
        raise ValueError("未找到 ul.chapter，页面结构可能已变化")

    chapters = []
    for position, link in enumerate(chapter_list.select(":scope > li > a"), start=1):
        chapter_title = _text(link)
        href = link.get("href", "").strip()
        if not chapter_title or not href:
            continue
        chapters.append({
            "position": position,
            "title": chapter_title,
            "url": urljoin(base_url, href),
        })

    if not chapters:
        raise ValueError("ul.chapter 中未找到有效章节")

    latest_chapter_url = urljoin(base_url, latest_chapter_url) if latest_chapter_url else ""
    latest_chapter = chapters[0]
    if latest_chapter_url and latest_chapter_url != latest_chapter["url"]:
        raise ValueError("最新章节链接与最新章节预览第一项不一致")

    return {
        "title": title,
        "author": author,
        "author_url": urljoin(base_url, author_url) if author_url else "",
        "category": category,
        "category_url": urljoin(base_url, category_url) if category_url else "",
        "status": status,
        "update_time": update_time,
        "latest_chapter_title": latest_chapter_title or latest_chapter["title"],
        "latest_chapter_url": latest_chapter_url or latest_chapter["url"],
        "chapters": chapters,
        "structure_hash": _structure_signature(cover),
    }
