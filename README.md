# 🕷️ Python Web Crawler

一个基于 Python 的自动化网页信息采集项目。

当前版本：**v2.1.3**

## 功能特性

- HTTP 请求
- HTML 解析
- SQLite 数据库存储
- GitHub Actions 自动运行
- URL 去重
- 内容 Hash 检测
- 网页变化历史记录
- 7 天结果数据清理
- 失败后重试 3 次，每次间隔 2 分钟
- 仅在网页首次采集或内容发生变化时保存新的 HTML 归档

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

`pages` 中：

- `crawl_time`：最近一次成功爬取时间
- `update_time`：网页内容最近一次实际发生变化的时间

`history` 只记录网页内容实际发生变化的版本，不记录 `unchanged` 状态。

## 状态说明

|状态|说明|
|-|-|
|new|首次发现网页|
|updated|网页内容发生变化|
|unchanged|内容没有变化|
|failed|爬取失败|

## HTML 归档策略

- `new`：保存 HTML
- `updated`：保存新的 HTML
- `unchanged`：不重复保存 HTML，继续使用之前的 HTML 路径

## 重试机制

每次运行首先进行一次请求。

如果请求失败：

```text
首次请求
  ↓失败
重试1 → 等待2分钟
  ↓失败
重试2 → 等待2分钟
  ↓失败
重试3
  ↓
最终失败
```

因此一次任务最多进行 **4 次请求**。

## 数据清理

`crawler.py` 会自动删除超过 7 天的数据目录。

GitHub Actions 不再重复执行清理逻辑，保证本地运行与 Actions 行为一致。

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

### v2.1.3 ✅

- 修复 history 错误记录 unchanged 的问题
- 修复 update_time 语义
- 增加 history 外键约束
- 优化 HTML 归档策略
- 明确首次请求 + 3 次重试
- 统一数据清理逻辑
- 同步 GitHub Actions 与项目版本

### v2.2

- 章节识别
- 正文解析
- 小说目录解析

## 本地运行

```bash
pip install requests beautifulsoup4 lxml
python crawler.py
```
