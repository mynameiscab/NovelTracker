# 🕷️ Python Web Crawler

一个基于 Python 的自动化网页信息采集项目。

当前版本：**v2.1.2**

## 功能特性

- HTTP 请求
- HTML 解析
- SQLite 数据库存储
- GitHub Actions 自动运行
- URL 去重
- 内容 Hash 检测
- 网页变化历史记录

## 数据库

数据库文件：

```
crawler.db
```

数据表：

```
pages
 ├── url
 ├── title
 ├── status
 ├── content_hash
 ├── crawl_time
 ├── update_time
 └── html_path

history
 ├── page_id
 ├── old_hash
 ├── new_hash
 ├── time
 └── html_path

logs
 ├── time
 ├── url
 ├── result
 └── message
```

## 状态说明

|状态|说明|
|-|-|
|new|首次发现网页|
|updated|网页内容发生变化|
|unchanged|内容没有变化|
|failed|爬取失败|

## 项目结构

```
python-test/
├── crawler.py
├── database.py
├── crawler.db
├── results/
└── .github/workflows/
```

## 版本路线

### v2.1.2 ✅

- 增加网页变化历史记录
- 保存旧 Hash 与新 Hash
- 保留 HTML 版本路径

### v2.2

- 章节识别
- 正文解析
- 小说目录解析

## 本地运行

```bash
pip install requests beautifulsoup4 lxml
python crawler.py
```
