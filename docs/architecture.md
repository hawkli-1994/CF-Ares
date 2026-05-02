# 架构设计

## 概述

CF-Ares 采用**两阶段协同**架构：

```
┌─────────────────────────────────────────────────────────────┐
│                        AresClient                           │
│                                                             │
│  ┌───────────────┐      ┌───────────────┐                │
│  │  CurlEngine   │      │ BrowserEngine │                │
│  │  (curl_cffi)  │◄────►│ (uc/sbase)    │                │
│  │               │      │               │                │
│  │  TLS指纹模拟   │      │ JS挑战解决     │                │
│  │  高性能请求    │      │ Cookie提取    │                │
│  │               │      │               │                │
│  └──────┬────────┘      └───────┬───────┘                │
│         │                       │                          │
│         └──────────┬────────────┘                          │
│                    │                                        │
│              SessionManager                                  │
│         (Cookie/Header/过期管理)                            │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. CurlEngine

基于 `curl_cffi` 的高性能请求引擎：
- TLS 指纹模拟（伪装成 Chrome/Firefox/Safari）
- HTTP/2 支持
- 异步并发
- 零浏览器依赖

**适用场景：** 大多数 Cloudflare 站点的 TLS 层防护绕过。

### 2. BrowserEngine

基于浏览器的完整 JS 挑战解决引擎：
- `UndetectedEngine` — undetected-chromedriver，针对 CF 5秒盾优化
- `SeleniumBaseEngine` — seleniumbase，通用浏览器自动化

**适用场景：** 需要完整 JS 执行和 DOM 交互的站点（Turnstile、复杂 CAPTCHA）。

### 3. SessionManager

会话状态管理：
- 按域名隔离 cookies/headers
- TTL 过期自动清理
- 序列化/反序列化支持

## 请求流程

```
用户请求
  │
  ▼
AresClient.get()
  │
  ▼
_request()
  │
  ├─► _initialize() → 仅创建 CurlEngine
  │
  ├─► 检查 SessionManager 是否已有有效会话
  │   ├─ 有 → 直接 curl 请求
  │   └─ 无 → 继续
  │
  ├─► curl 请求 → 获取响应
  │
  ├─► _is_cloudflare_challenge()? → 检测响应
  │   ├─ 否 → 返回结果 ✅
  │   └─ 是 → 继续
  │
  ├─► _init_browser_engine() → 惰性创建浏览器
  │
  ├─► _handle_cloudflare() → 浏览器解决 JS 挑战
  │
  ├─► 提取 cookies/headers → 存入 SessionManager
  │
  ├─► 应用会话到 CurlEngine
  │
  └─► curl 重试请求 → 返回结果 ✅
```

## 惰性初始化策略

```python
# ❌ 旧实现：每次请求都启动 Chrome
client = AresClient()          # → 启动 Curl + Browser
client.get("example.com")       # → 已经初始化浏览器

# ✅ 新实现：只在需要时启动浏览器
client = AresClient()          # → 只启动 Curl
client.get("example.com")       # → 纯 curl，零浏览器开销
client.get("cf-protected.com")  # → curl 先试 → 发现挑战 → 启动浏览器
```

## 浏览器引擎选择

| 引擎 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| `auto` (默认) | 智能选择，省心 | 略慢于纯 curl | 未知站点 |
| `undetected` | 最强 CF 绕过 | 启动慢、内存大 | 重度防护站点 |
| `seleniumbase` | 稳定可靠 | 容易被检测 | 开发调试 |

## 指纹管理

```python
# 内置指纹
"chrome_110", "chrome_120", "firefox_120", "safari_17"

# 自定义指纹
client = AresClient(
    fingerprint="chrome_120",
    # 内部映射到 curl_cffi impersonate="chrome120"
)
```

## 代理支持

```python
# HTTP 代理
client = AresClient(proxy="http://host:port")

# 带认证
client = AresClient(proxy="http://user:pass@host:port")

# SOCKS5
client = AresClient(proxy="socks5://host:port")
```

## 性能对比

| 指标 | 纯 curl | 纯浏览器 | CF-Ares (curl + lazy browser) |
|------|--------|----------|------------------------------|
| 启动时间 | 0.1s | 3-5s | 0.1s |
| 内存占用 | 20MB | 200MB+ | 20MB (curl) / 220MB (browser) |
| 并发能力 | 1000+ | 1-5 | 1000+ (curl) |
| CF 绕过 | 部分 | 完全 | 完全 |

## 扩展性

```python
# 自定义引擎
from cf_ares.engines.base import BaseEngine

class MyEngine(BaseEngine):
    def get(self, url):
        # 自定义请求逻辑
        pass

# 注入到 AresClient
client = AresClient()
client._browser_engine = MyEngine()
```
