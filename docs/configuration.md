# 配置参考

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `CF_ARES_DEBUG` | 启用调试日志 | `1` 或 `true` |
| `CF_ARES_TIMEOUT` | 默认超时(秒) | `30` |
| `CF_ARES_HEADLESS` | 默认无头模式 | `1` 或 `0` |

```bash
export CF_ARES_DEBUG=1
export CF_ARES_TIMEOUT=60
```

## AresClient 参数

### browser_engine

选择浏览器引擎。

```python
# 自动选择（推荐）
client = AresClient(browser_engine="auto")

# undetected-chromedriver（最强 CF 绕过）
client = AresClient(browser_engine="undetected")

# seleniumbase（通用浏览器自动化）
client = AresClient(browser_engine="seleniumbase")
```

### headless

是否使用无头模式。

```python
# 无头模式（服务器/CI 推荐）
client = AresClient(headless=True)

# 显示浏览器窗口（调试）
client = AresClient(headless=False)
```

### fingerprint

浏览器指纹配置。

```python
# 内置指纹
client = AresClient(fingerprint="chrome_120")

# 自动选择
client = AresClient(fingerprint=None)
```

当前支持的指纹：
- `chrome_110` → Chrome 110
- `chrome_120` → Chrome 120
- `firefox_120` → Firefox 120
- `safari_17` → Safari 17

### proxy

代理设置。

```python
# HTTP 代理
client = AresClient(proxy="http://proxy.example.com:8080")

# 带认证
client = AresClient(proxy="http://user:pass@proxy.example.com:8080")

# SOCKS5
client = AresClient(proxy="socks5://proxy.example.com:1080")

# 带认证 SOCKS5
client = AresClient(proxy="socks5://user:pass@proxy.example.com:1080")
```

### timeout

请求超时时间（秒）。

```python
# 快速请求
client = AresClient(timeout=10)

# 慢速站点
client = AresClient(timeout=60)
```

### max_retries

最大重试次数。

```python
client = AresClient(max_retries=5)
```

### debug

启用调试输出。

```python
client = AresClient(debug=True)
```

### chrome_path

自定义 Chrome 路径。

```python
client = AresClient(chrome_path="/usr/bin/google-chrome-stable")
```

### use_edge

使用 Edge 代替 Chrome。

```python
client = AresClient(use_edge=True)
```

## 完整配置示例

```python
from cf_ares import AresClient

client = AresClient(
    browser_engine="undetected",
    headless=True,
    fingerprint="chrome_120",
    proxy="http://user:pass@proxy.example.com:8080",
    timeout=60,
    max_retries=3,
    debug=False,
    chrome_path="/usr/bin/google-chrome-stable",
    use_edge=False,
)
```

## 会话 TTL

SessionManager 的会话过期时间。

```python
from cf_ares.utils.session import SessionManager

# 自定义 TTL（默认 3600 秒 = 1小时）
sm = SessionManager(session_ttl=7200)  # 2小时
```

## Makefile 快捷命令

```bash
# 开发环境
make setup-dev

# 运行测试
make test

# 构建包
make build

# 清理
make clean
```
