# 🕷️ Python Web Crawler

一个基于 Python 的自动化网页信息采集项目。

当前版本：**v2.0**

本项目用于学习和实践：

- HTTP 请求
- HTML 解析
- 数据保存
- SQLite 数据库管理
- GitHub Actions 自动化运行
- 数据版本管理

---

## ✨ 功能特性

### 自动网页采集

目标网页：

```
https://m.xsw.tw/1725663/
```

程序会自动获取：

- 网页标题
- 页面文本内容
- 页面链接
- 抓取时间
- 原始 HTML 页面

---

## 🗄️ 数据库支持（v2.0）

从 v2.0 开始，引入 SQLite 数据库用于保存历史爬取记录。

数据库文件：

```
crawler.db
```

当前数据表：

```
pages
├── id
├── url
├── title
├── status
├── crawl_time
└── html_path
```

数据库用于：

- 保存历史爬取记录
- 记录网页状态
- 为后续增量爬取和章节解析提供基础

---

## 📁 项目结构

```
python-test/
├── crawler.py                 # 爬虫主程序
├── database.py                # SQLite数据库模块
├── crawler.db                 # 爬取历史数据库
├── results/                   # 原始数据保存目录
│   └── YYYYMMDD/
│       └── HHMM/
│           ├── results.txt
│           ├── results.json
│           └── page.html
└── .github/
    └── workflows/
        └── crawler.yml        # GitHub Actions配置
```

---

## ⏰ 自动运行

通过 GitHub Actions 自动执行：

| 时间 | 任务 |
|---|---|
| 08:00 | 第一次采集 |
| 12:00 | 第二次采集 |

每次运行后：

1. 执行网页采集
2. 更新 SQLite 数据库
3. 保存 HTML 和结果文件
4. 自动清理过期数据
5. 自动提交最新数据

---

## 🔄 当前版本计划

### v2.0 ✅

- SQLite 数据库存储
- 历史数据记录
- GitHub Actions 持久化数据库

### v2.1（计划）

- URL 去重
- 增量爬取
- 网页变化检测

### v2.2（计划）

- 自动识别章节
- 提取正文内容
- 小说目录解析

---

## 📄 数据格式

### results.txt

适合直接阅读。

### results.json

适合程序进一步处理和分析。

### page.html

保存网页原始 HTML，用于后续结构分析。

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
