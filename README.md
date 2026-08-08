# 🕷️ Python Web Crawler

一个基于 Python 的自动化网页信息采集项目。

本项目用于学习和实践：

- HTTP 请求
- HTML 解析
- 数据保存
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

---

## 📁 项目结构

```
python-test/
├── crawler.py                 # 爬虫主程序
├── results/                   # 数据保存目录
│   └── YYYYMMDD/
│       ├── 0800/
│       │   ├── results.txt
│       │   └── results.json
│       └── 1200/
│           ├── results.txt
│           └── results.json
└── .github/
    └── workflows/
        └── crawler.yml        # 自动运行配置
```

---

## ⏰ 自动运行

通过 GitHub Actions 自动执行：

| 时间 | 任务 |
|---|---|
| 08:00 | 第一次采集 |
| 12:00 | 第二次采集 |

每次运行后：

1. 保存当天数据
2. 自动清理 15 天以前的数据
3. 自动提交最新结果

---

## 📄 数据格式

### results.txt

适合直接阅读。

### results.json

适合程序进一步处理和分析。

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
