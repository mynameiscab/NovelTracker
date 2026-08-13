# 🕷️ NovelTracker

一个基于 Python 的小说更新追踪与网页信息采集工具。

当前版本：**v2.2.0 Stable**

## 项目简介

NovelTracker 用于自动采集小说网站页面，检测小说更新，并记录最新章节信息。

当前目标站点：

```text
https://m.xsw.tw/1725663/
```

项目通过 GitHub Actions 可实现定时自动运行。

---

## 功能特性

### 网页采集

- Python Requests 请求
- HTML 页面解析
- HTTPS 请求兼容处理
- 请求失败自动重试
- 请求日志记录

### 更新检测

当前版本按照以下优先级判断小说是否更新：

```text
最新章节 URL
        ↓
最新章节标题
        ↓
更新时间
```

说明：

- 最新章节发生变化 → 判定更新
- 最新章节标题变化 → 判定更新
- 更新时间变化 → 判定更新
- 页面结构 Hash 变化不会直接判定小说更新

---

## 页面结构检测

NovelTracker 会保存页面结构 Hash，用于检测网站 DOM 是否变化。

如果发现结构变化，会生成：

```text
results/warning
```

用于提醒检查：

- page.html
- parser.py
- 网站页面结构

结构变化不会自动停止爬虫。

---

## 数据保存

### SQLite 数据库

数据库文件：

```text
crawler.db
```

记录内容包括：

- 页面信息
- 小说标题
- 最新章节
- 更新时间
- 页面 Hash
- 页面结构 Hash
- 已发现章节
- 运行日志

---

## HTML 与结果归档

只有检测到：

- 首次采集
- 小说更新

时才保存新的页面文件。

目录格式：

```text
results/
└── YYYYMMDD/
    └── HHMM/
        ├── page.html
        └── results.json
```

其中：

- `page.html` 保存原始页面
- `results.json` 保存解析后的结构化数据

---

## 自动清理

结果目录默认保存：

```text
7 天
```

超过时间的数据会自动删除。

---

## 请求重试机制

单次请求失败后：

```text
最大重试次数：3 次
间隔时间：120 秒
```

因此一次请求最多执行 4 次。

---

## 当前章节处理逻辑

当前版本只处理小说主页中可见章节。

支持：

- 发现新章节
- 避免重复记录已有章节
- 保存章节 URL 和标题

暂不支持：

- 自动扫描完整历史目录
- 自动补齐所有历史章节
- 自动解析章节正文

---

## 项目结构

```text
NovelTracker/
├── crawler.py        # 主爬虫流程
├── parser.py         # HTML 解析
├── database.py       # SQLite 数据管理
├── crawler.db        # 数据库
├── results/          # 运行结果
└── .github/
    └── workflows/    # GitHub Actions
```

---

## 本地运行

安装依赖：

```bash
pip install requests beautifulsoup4 lxml
```

运行：

```bash
python crawler.py
```

---

## 版本路线

### v2.2.0 Stable

已完成：

- 小说基本信息解析
- 最新章节更新检测
- 更新时间检测
- 页面结构 Hash 检测
- Warning 机制
- SQLite 数据存储
- 新章节发现
- HTML 归档
- JSON 结果输出
- 7 天数据清理
- 请求失败自动重试

后续计划：

- GitHub Actions 流程进一步优化
- 章节正文解析
- 章节内容 Hash
- 历史章节补全
- 多小说支持
