# 🕷️ NovelTracker

一个基于 Python 的小说更新追踪与网页信息采集项目。

当前版本：**v2.2.0 ✅ Stable**

## 功能特性

- HTTP 请求
- HTML 解析
- SQLite 数据库存储
- GitHub Actions 自动运行
- 最新章节增量检测
- 小说更新时间检测
- 页面结构 Hash 检测
- 页面结构变化自动生成 `results/warning`
- 当前页面可见章节记录
- 7 天结果数据清理
- 失败后重试 3 次，每次间隔 2 分钟
- HTTPS 请求使用 `verify=False`

## v2.2 更新检测逻辑

每次获取小说主页后，按照以下顺序判断小说是否更新：

```text
1. 最新章节
       ↓
2. 更新时间
       ↓
3. 页面结构 Hash
```

### 1. 最新章节

首先比较页面中的最新章节标题和最新章节 URL。

只要最新章节发生变化，就判定小说已更新。

### 2. 更新时间

如果最新章节没有变化，再比较页面中的 `更新：` 字段。

如果更新时间发生变化，也判定页面发生了更新，并继续检查当前可见章节。

### 3. 页面结构 Hash

页面结构 Hash **不参与小说章节更新判断**。

它只用于检测依赖的页面 DOM 结构是否发生变化。

如果结构 Hash 发生变化：

```text
results/warning
```

会被创建或覆盖，并记录旧 Hash、新 Hash 和检查时间。

结构变化不会自动停止爬虫；程序会继续使用当前解析规则运行，同时写入 warning 日志。

## 当前章节范围

v2.2.0 只处理小说主页 `ul.chapter` 中当前可见的章节。

不会：

- 扫描完整历史目录
- 自动补齐更早章节
- 重新爬取已经记录的章节

当前页面中已经存在于数据库的章节会直接跳过；只有数据库中不存在的章节才会作为新章节记录。

历史章节补全将在后续版本、待当前页面和章节页面解析逻辑稳定后再实现。

## 数据库

数据库文件：

```text
crawler.db
```

主要数据表：

```text
pages
 ├── url
 ├── title
 ├── status
 ├── content_hash
 ├── crawl_time
 ├── update_time
 ├── html_path
 ├── latest_chapter_title
 ├── latest_chapter_url
 ├── page_update_time
 └── structure_hash

chapters
 ├── page_id
 ├── title
 ├── url
 ├── position
 ├── crawl_time
 ├── content_hash
 ├── content_path
 └── status
```

`content_hash` 仍然保存页面 Hash，但 v2.2.0 不再使用它判断小说是否更新。

## HTML 归档策略

只有首次采集或检测到小说更新时，才保存新的 `page.html`。

如果最新章节和更新时间均没有变化，则不会重复保存 HTML。

## 页面结构 Warning

如果依赖的 DOM 结构发生变化，会生成：

```text
results/warning
```

## 重试机制

每次请求首先执行一次，失败后最多重试 3 次，每次间隔 2 分钟。

因此一次 URL 最多请求 4 次。

## 项目结构

```text
NovelTracker/
├── crawler.py
├── parser.py
├── database.py
├── crawler.db
├── results/
└── .github/workflows/
```

## 版本路线

### v2.2.0 ✅ Stable

- 增加小说基本信息解析
- 使用最新章节作为第一优先级更新依据
- 使用更新时间作为第二优先级更新依据
- 页面结构 Hash 独立用于结构变化检测
- 结构变化生成 `results/warning`
- 记录当前页面可见章节
- 已存在章节跳过
- 暂不扫描历史目录
- 暂不补齐历史章节

### 后续版本

- worktest 手动测试 workflow
- 状态持久化优化
- 章节正文解析
- 新章节正文保存
- 章节内容 Hash
- 历史章节补全
- 更完善的增量更新机制

## 本地运行

```bash
pip install requests beautifulsoup4 lxml
python crawler.py
```
