# 🕷️ Python Web Crawler

一个基于 Python 的自动化网页信息采集项目。

当前版本：**v2.1.1**

本项目用于学习和实践：

- HTTP 请求
- HTML 解析
- 数据保存
- SQLite 数据库管理
- GitHub Actions 自动化运行
- 增量爬取设计

---

## ✨ 功能特性

当前支持：

- 网页标题提取
- 页面文本采集
- HTML 原始文件保存
- SQLite 历史记录
- URL 去重
- 内容 Hash 检测
- 状态跟踪

---

## 🗄️ 数据库支持

数据库文件：

```
crawler.db
```

数据表：

```
pages
├── id
├── url
├── title
├── status
├── content_hash
├── crawl_time
├── update_time
└── html_path

logs
├── id
├── time
├── url
├── result
└── message
```

状态说明：

|状态|说明|
|-|-|
|new|首次发现网页|
|updated|网页内容发生变化|
|unchanged|网页内容未变化|
|failed|爬取失败|

---

## 📁 项目结构

```
python-test/
├── crawler.py
├── database.py
├── crawler.db
├── results/
│   └── YYYYMMDD/HHMM/
│       ├── results.json
│       ├── results.txt
│       └── page.html
└── .github/workflows/
    └── crawler.yml
```

---

## 🔄 版本计划

### v2.1.1 ✅

- 增加首次采集 new 状态
- URL 唯一约束
- Hash 内容变化检测
- 数据库状态优化

### v2.2

- 自动识别章节
- 提取正文内容
- 小说目录解析

---

## 🚀 本地运行

安装依赖：

```bash
pip install requests beautifulsoup4 lxml
```

运行：

```bash
python crawler.py
```

## License

仅用于学习和个人研究用途。
