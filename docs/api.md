# API 参考

## AresClient

### 初始化

```python
AresClient(
    browser_engine="auto",      # str: "auto" | "undetected" | "seleniumbase"
    headless=True,                # bool: 是否无头模式
    fingerprint=None,             # str | None: 浏览器指纹标识
    proxy=None,                   # str | None: 代理 URL
    timeout=30,                   # int: 请求超时(秒)
    max_retries=3,                # int: 最大重试次数
    debug=False,                  # bool: 调试日志
    chrome_path=None,             # str | None: Chrome 二进制路径
    use_edge=False,               # bool: 使用 Edge 代替 Chrome
)
```

### HTTP 方法

#### `get(url, params=None, headers=None, **kwargs) -> AresResponse`

发送 GET 请求。

```python
response = client.get("https://api.example.com/data")
print(response.status_code)  # 200
print(response.text)           # 响应文本
print(response.json())         # JSON 解析
```

#### `post(url, data=None, json=None, headers=None, **kwargs) -> AresResponse`

发送 POST 请求。

```python
response = client.post(
    "https://api.example.com/login",
    json={"username": "user", "password": "pass"}
)
```

#### `put(url, data=None, headers=None, **kwargs) -> AresResponse`

发送 PUT 请求。

#### `delete(url, headers=None, **kwargs) -> AresResponse`

发送 DELETE 请求。

#### `head(url, headers=None, **kwargs) -> AresResponse`

发送 HEAD 请求。

#### `options(url, headers=None, **kwargs) -> AresResponse`

发送 OPTIONS 请求。

#### `patch(url, data=None, headers=None, **kwargs) -> AresResponse`

发送 PATCH 请求。

### Cloudflare 挑战

#### `solve_challenge(url, max_retries=3) -> AresResponse`

显式执行 Cloudflare 挑战。

```python
try:
    response = client.solve_challenge("https://protected.com")
    print("挑战成功!")
except CloudflareChallengeFailed as e:
    print(f"挑战失败: {e}")
```

### 会话管理

#### `get_session_info(url=None) -> dict`

获取当前会话信息。

```python
# 获取指定 URL 的会话
info = client.get_session_info("https://protected.com")
print(info["cookies"])
print(info["headers"])

# 获取所有会话
all_info = client.get_session_info()
```

#### `set_session_info(session_info, url=None) -> None`

设置会话信息。

```python
client.set_session_info({
    "cookies": {"cf_clearance": "xxx"},
    "headers": {"User-Agent": "..."},
    "url": "https://protected.com"
})
```

#### `save_session(file_path, url=None) -> None`

保存会话到文件。

```python
client.save_session("session.json")
```

#### `load_session(file_path) -> None`

从文件加载会话。

```python
client.load_session("session.json")
```

### 属性

#### `cookies -> dict`

获取当前 curl 引擎的所有 cookies。

```python
print(client.cookies)
# {'cf_clearance': 'xxx', 'session': 'yyy'}
```

#### `headers -> dict`

获取当前 curl 引擎的所有 headers。

```python
print(client.headers)
# {'User-Agent': '...', 'Accept': '...'}
```

### 上下文管理器

```python
with AresClient() as client:
    response = client.get("https://example.com")
    # 自动关闭所有引擎
```

#### `close() -> None`

手动关闭所有资源。

```python
client.close()
```

## AresResponse

HTTP 响应对象，兼容 `requests.Response` 接口。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `status_code` | `int` | HTTP 状态码 |
| `headers` | `dict` | 响应头 |
| `cookies` | `dict` | 响应 cookies |
| `content` | `bytes` | 响应内容(二进制) |
| `text` | `str` | 响应内容(文本) |
| `url` | `str` | 最终 URL |

### 方法

#### `json() -> Any`

解析 JSON 响应。

```python
data = response.json()
```

## 异常

### `AresError`

基础异常，所有 CF-Ares 异常的基类。

### `CloudflareError`

Cloudflare 相关错误的基类。

### `CloudflareChallengeFailed`

挑战失败异常。当浏览器无法通过 Cloudflare 的 JS 挑战时抛出。

```python
from cf_ares import CloudflareChallengeFailed

try:
    client.solve_challenge("https://protected.com")
except CloudflareChallengeFailed:
    print("无法通过验证")
```

### `CloudflareSessionExpired`

会话过期异常。当已获取的会话 cookies 失效时抛出。

```python
from cf_ares import CloudflareSessionExpired

try:
    client.get("https://protected.com/api")
except CloudflareSessionExpired:
    # 重新执行挑战
    client.solve_challenge("https://protected.com")
```

### `RequestError`

请求失败异常。curl 引擎请求出错时抛出。

## 引擎

### CurlEngine

```python
from cf_ares.engines.curl import CurlEngine

engine = CurlEngine(
    proxy=None,
    timeout=30,
    fingerprint=None,
)

# 发送请求
response = engine.request("GET", "https://example.com")

# 获取 cookies/headers
cookies = engine.get_cookies()
headers = engine.get_headers()

# 设置 cookies/headers
engine.set_cookies({"key": "value"})
engine.set_headers({"X-Custom": "header"})

# 关闭
engine.close()
```

### BaseEngine (浏览器引擎基类)

```python
from cf_ares.engines.base import BaseEngine

class MyEngine(BaseEngine):
    def get(self, url):
        # 实现请求逻辑
        pass

    def wait_for_cloudflare(self):
        # 实现等待逻辑
        pass

    def get_cookies(self):
        return {}

    def get_headers(self):
        return {}

    def close(self):
        pass
```

## SessionManager

```python
from cf_ares.utils.session import SessionManager

sm = SessionManager(session_ttl=3600)  # 1小时过期

# 更新会话
sm.update("https://example.com", cookies={"a": "1"}, headers={"H": "V"})

# 获取
print(sm.get_cookies("https://example.com"))   # {"a": "1"}
print(sm.get_headers("https://example.com"))   # {"H": "V"}

# 检查有效性
print(sm.has_valid_session("https://example.com"))  # True

# 清除
sm.clear("https://example.com")  # 清除指定
sm.clear()                       # 清除全部
```
