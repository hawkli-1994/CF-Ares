# 引擎详解

## CurlEngine

基于 `curl_cffi` 的高性能请求引擎。

### 原理

curl_cffi 使用真实的 libcurl 绑定，通过模拟浏览器 TLS 指纹来绕过 Cloudflare 的 TLS 层检测。

```python
from cf_ares.engines.curl import CurlEngine

engine = CurlEngine()
response = engine.request("GET", "https://example.com")
```

### 支持的 impersonate 版本

- `chrome110`
- `chrome120`
- `firefox120`
- `safari17_0`

### 特点
- 启动极快（<0.1s）
- 内存占用低（~20MB）
- 高并发能力
- 不需要浏览器
- 可处理大多数 TLS 指纹检测

### 限制
- 无法处理需要 JS 执行的挑战（如 Turnstile）
- 某些站点需要完整的浏览器环境

---

## UndetectedEngine

基于 `undetected-chromedriver` 的浏览器引擎。

### 原理

通过修改 Chrome 启动参数和运行时行为，绕过 Selenium 检测。

```python
from cf_ares.engines.undetected import UndetectedEngine

engine = UndetectedEngine(headless=True, timeout=30)
engine.get("https://example.com")
engine.wait_for_cloudflare()
cookies = engine.get_cookies()
```

### 特点
- 最强的 CF 绕过能力
- 支持所有 JS 挑战
- 可处理 CAPTCHA 和 Turnstile

### 限制
- 启动慢（3-5s）
- 内存占用高（200MB+）
- 需要 Chrome 浏览器
- Chrome 版本需与 ChromeDriver 匹配

---

## SeleniumBaseEngine

基于 `seleniumbase` 的浏览器引擎。

### 原理

SeleniumBase 提供了更稳定的浏览器自动化框架，内置了多种反检测策略。

```python
from cf_ares.engines.selenium import SeleniumBaseEngine

engine = SeleniumBaseEngine(headless=True, timeout=30)
engine.get("https://example.com")
engine.wait_for_cloudflare()
cookies = engine.get_cookies()
```

### 特点
- 稳定可靠
- 丰富的 API
- 内置截图、日志等功能

### 限制
- 较容易被检测
- 启动较慢
- 依赖较多

---

## 引擎选择指南

```
目标站点 ┐
         ├─ 无 CF 防护 ──► CurlEngine（自动使用）
         │
         └─ 有 CF 防护 ┐
                        ├─ TLS 指纹检测 ──► CurlEngine ✅
                        │
                        └─ JS 挑战 ┐
                                   ├─ 5秒盾 ──► UndetectedEngine ✅
                                   ├─ Turnstile ──► UndetectedEngine ✅
                                   └─ CAPTCHA ──► UndetectedEngine ✅
```

---

## 自定义引擎

继承 `BaseEngine` 实现自定义引擎：

```python
from cf_ares.engines.base import BaseEngine
from typing import Any, Dict

class PlaywrightEngine(BaseEngine):
    def __init__(self, headless=True, proxy=None, timeout=30, fingerprint=None):
        super().__init__(headless, proxy, timeout, fingerprint)
        # 初始化 Playwright
        
    def get(self, url: str) -> Any:
        # 使用 Playwright 访问 URL
        pass
    
    def wait_for_cloudflare(self) -> bool:
        # 等待 CF 挑战完成
        pass
    
    def get_cookies(self) -> Dict[str, str]:
        # 获取 cookies
        return {}
    
    def get_headers(self) -> Dict[str, str]:
        # 获取 headers
        return {}
    
    def close(self) -> None:
        # 清理资源
        pass
```

---

## 性能对比

| 指标 | CurlEngine | UndetectedEngine | SeleniumBaseEngine |
|------|-----------|-----------------|-------------------|
| 启动时间 | 0.1s | 3-5s | 3-5s |
| 内存占用 | 20MB | 200MB+ | 200MB+ |
| 请求速度 | 快 | 慢 | 慢 |
| CF 绕过能力 | 部分 | 完全 | 中等 |
| 并发能力 | 1000+ | 1-5 | 1-5 |
| 浏览器依赖 | 否 | 是 | 是 |
| JS 执行 | 否 | 是 | 是 |
