# 故障排查

## 常见问题

### 1. pip install cf-ares 失败

**现象：**
```
ERROR: Could not find a version that satisfies the requirement cf-ares
```

**原因：** Python 版本低于 3.12

**解决：**
```bash
python --version  # 确保 >= 3.12
pip install cf-ares
```

---

### 2. ChromeDriver 版本不匹配

**现象：**
```
session not created: This version of ChromeDriver only supports Chrome version 148
Current browser version is 147.0.7727.137
```

**原因：** Chrome 自动更新，但 ChromeDriver 没有同步更新。

**解决：**

```bash
# 更新 ChromeDriver
pip install --upgrade undetected-chromedriver

# 或指定 Chrome 路径
client = AresClient(chrome_path="/usr/bin/google-chrome-stable")

# 或使用 curl 模式（不需要浏览器）
client = AresClient(browser_engine="curl_only")  # 未来支持
```

---

### 3. 请求超时

**现象：**
```
TimeoutError: Message: timeout: Timed out receiving message from renderer
```

**原因：**
- 浏览器启动超时
- 目标站点加载极慢
- 代理延迟过高

**解决：**
```python
client = AresClient(
    timeout=60,       # 增加超时
    headless=True,    # 无头模式更快
)
```

---

### 4. 挑战失败（实例脚本无法通过）

**现象：**
```
CloudflareChallengeFailed: 无法通过 Cloudflare 挑战
```

**可能原因：**

| 原因 | 检查方法 | 解决 |
|------|---------|------|
| 目标站点使用 Turnstile | 手动打开站点看是否有 "Verify you are human" | 使用 `browser_engine="undetected"` |
| Chrome 版本过旧 | `chrome --version` | 更新到 130+ |
| 代理被拉黑 | 换代理测试 | 更换高质量代理 |
| 站点有额外验证 | 观察浏览器行为 | 手动模式调试 |

**调试步骤：**
```python
client = AresClient(
    headless=False,   # 显示浏览器窗口
    debug=True,       # 打印调试信息
)
response = client.solve_challenge("https://目标站点.com")
```

---

### 5. Linux 无头环境无法启动浏览器

**现象：**
```
WebDriverException: Message: unknown error: Chrome failed to start
```

**原因：** Linux 服务器没有显示环境。

**解决：**

```bash
# 安装 xvfb
sudo apt-get install xvfb

# 使用 xvfb-run 运行
xvfb-run python script.py
```

或者使用 `browser_engine` 参数限制为 curl 可用时不用浏览器：

```python
# 对于大多数站点，curl_cffi 已足够
client = AresClient()
# 内部自动判断，只有 JS 挑战才启动浏览器
```

---

### 6. `get_cookies` / `get_headers` / `close` AttributeError

**现象：**
```
AttributeError: 'CurlEngine' object has no attribute 'get_cookies'
```

**原因：** 使用了旧版本 CF-Ares（v0.1.0 之前的 bug）。

**解决：**
```bash
pip install --upgrade cf-ares
```

---

## 日志调试

```python
import logging

# 启用详细日志
logging.basicConfig(level=logging.DEBUG)

client = AresClient(debug=True)
response = client.get("https://example.com")
```

## 检查清单

提交 Issue 前请确认：

- [ ] Python >= 3.12
- [ ] `pip install --upgrade cf-ares` 已更新到最新版
- [ ] Chrome >= 130（`google-chrome --version`）
- [ ] 代理可用（`curl -x http://proxy:port https://example.com`）
- [ ] 目标 URL 可在浏览器正常访问
- [ ] 已尝试 `headless=False` 调试

## 提交 Issue 模板

```
**环境**
- OS: (e.g. Ubuntu 22.04)
- Python: (e.g. 3.12.3)
- Chrome: (e.g. 147.0.6943.98)
- cf-ares: (e.g. 0.1.1)

**目标 URL**
https://...

**代码**
```python
from cf_ares import AresClient
client = AresClient()
...
```

**错误信息**
完整 traceback

**预期行为**
...

**实际行为**
...
```
