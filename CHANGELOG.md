# 更新日志

所有对 CF-Ares 的显著更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### TODO

- 修复 Chrome 135 版本兼容性问题（undetected-chromedriver 适配）
- 准备 PyPI 发布（修复打包配置、完善文档）
- 优化 curl_cffi 错误处理机制
- 添加更多单元测试覆盖

## [0.1.0] - 2024-03-04

### 新增

- 初始版本发布
- 支持使用 SeleniumBase 和 undetected-chromedriver 突破 Cloudflare 防护
- 支持使用 curl_cffi 进行高性能请求
- 支持浏览器指纹管理
- 支持会话管理和复用
- 提供类似 requests 的 API 接口
- 添加基本示例和高级示例
