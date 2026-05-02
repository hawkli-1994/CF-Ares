# 更新日志

所有对 CF-Ares 的显著更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增

- GitHub Actions CI 工作流 (`.github/workflows/ci.yml`)
- GitHub Pages 文档站点 (`mkdocs.yml`, `.github/workflows/pages.yml`)
- 完整文档：架构设计、API 参考、故障排查、配置指南、引擎详解
- 惰性浏览器引擎初始化 — `_init_browser_engine()` 只在需要 JS 挑战时调用
- `_is_cloudflare_challenge()` 检测函数 — 准确识别 CF 挑战页面

### 修复

- `CurlEngine` 缺失 `get_cookies()`、`get_headers()`、`close()` 方法 (commit `b4287ed`)
- `_is_cloudflare_challenge()` 误判 CF-Ray 头为挑战页面
- `AresClient` 每次请求都初始化浏览器引擎导致 Linux 无头环境超时

### 变更

- `README.md` 添加 PyPI、CI、文档 badges
- `_initialize()` 现在只创建 `CurlEngine`，浏览器引擎完全惰性
- `_request()` 先 curl 请求，根据响应内容判断是否需要浏览器

## [0.1.0] - 2026-05-02

### 新增

- 首次发布到 PyPI
- `AresClient` 两阶段协同架构
- `CurlEngine` 基于 curl_cffi
- `UndetectedEngine` 基于 undetected-chromedriver
- `SeleniumBaseEngine` 基于 seleniumbase
- 会话管理与会话持久化
- 浏览器指纹模拟
- 代理支持

## [0.1.0-alpha] - 2024-03-04

### 新增

- 初始版本开发
- 支持使用 SeleniumBase 和 undetected-chromedriver 突破 Cloudflare 防护
- 支持使用 curl_cffi 进行高性能请求
- 支持浏览器指纹管理
- 支持会话管理和复用
- 提供类似 requests 的 API 接口
- 添加基本示例和高级示例
