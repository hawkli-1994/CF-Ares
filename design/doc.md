# CF-Ares 技术设计文档

## 1. 项目概述

CF-Ares 是一个专门用于对抗 Cloudflare 防护的 Python 库，采用两阶段策略：首先使用浏览器引擎突破初始防护，然后使用高性能 HTTP 客户端维持会话。该库设计为可以轻松集成到其他 Python 项目中，提供简单易用的 API 接口。

### 1.1 核心目标

- 提供可靠的 Cloudflare 防护突破能力
- 保持高性能的请求处理能力
- 易于集成到其他 Python 项目中
- 提供灵活的配置选项

### 1.2 技术可行性分析

该方案的可行性基于以下几点：

1. **浏览器引擎突破**：SeleniumBase 和 undetected-chromedriver 已被证明能够有效绕过 Cloudflare 的 JavaScript 挑战和验证码。

2. **会话维持**：一旦通过初始验证，Cloudflare 会在客户端设置 cookies 和其他标识符。这些凭证可以被提取并用于后续请求。

3. **高性能请求**：curl_cffi 提供了与 libcurl 的绑定，能够处理高并发请求，同时支持 TLS 指纹模拟，可以维持与初始浏览器会话的一致性。

4. **技术集成**：这三种技术可以无缝集成，形成一个完整的解决方案。

## 2. 系统架构

### 2.1 整体架构

CF-Ares 采用分层架构设计：

```
+----------------------------------+
|           AresClient             |  <- 用户 API 层
+----------------------------------+
|                                  |
|  +------------+  +------------+  |
|  | 浏览器引擎  |  |  请求引擎   |  |  <- 引擎层
|  +------------+  +------------+  |
|                                  |
|  +------------+  +------------+  |
|  | 会话管理器  |  | 指纹管理器  |  |  <- 服务层
|  +------------+  +------------+  |
|                                  |
|  +------------+  +------------+  |
|  | 代理管理器  |  | 错误处理器  |  |  <- 基础设施层
|  +------------+  +------------+  |
+----------------------------------+
```

### 2.2 核心组件

#### 2.2.1 AresClient

主要客户端类，提供用户友好的 API 接口，封装底层复杂性。

#### 2.2.2 浏览器引擎

- **SeleniumBaseEngine**: 使用 SeleniumBase 框架处理基本的 Cloudflare 挑战
- **UndetectedEngine**: 使用 undetected-chromedriver 处理更复杂的防护

#### 2.2.3 请求引擎

- **CurlEngine**: 基于 curl_cffi 的高性能请求引擎，支持 TLS 指纹模拟

#### 2.2.4 会话管理器

负责从浏览器引擎提取会话信息（cookies、headers 等），并将其应用到请求引擎。

#### 2.2.5 指纹管理器

管理和生成浏览器指纹，确保与真实浏览器行为一致。

#### 2.2.6 代理管理器

处理代理配置、轮换和验证。

#### 2.2.7 错误处理器

处理各种错误情况，包括 Cloudflare 挑战失败、网络错误等。

## 3. 工作流程

### 3.1 基本工作流程

1. **初始化**：用户创建 AresClient 实例，配置所需参数
2. **请求处理**：
   - 首次请求时，使用浏览器引擎访问目标网站
   - 处理可能出现的 Cloudflare 挑战（5秒盾、JavaScript 挑战、验证码等）
   - 成功通过挑战后，提取会话信息（cookies、headers 等）
   - 将会话信息应用到 curl_cffi 引擎
   - 后续请求使用 curl_cffi 引擎，保持高性能
3. **会话维护**：
   - 定期检查会话有效性
   - 如果会话失效，自动使用浏览器引擎重新验证

### 3.2 挑战处理流程

```
+----------------+     +----------------+     +----------------+
| 发起初始请求   | --> | 检测 CF 挑战   | --> | 选择浏览器引擎 |
+----------------+     +----------------+     +----------------+
                                                      |
+----------------+     +----------------+     +----------------+
| 提取会话信息   | <-- | 通过 CF 挑战   | <-- | 执行浏览器操作 |
+----------------+     +----------------+     +----------------+
        |
+----------------+     +----------------+
| 应用到 curl    | --> | 执行后续请求   |
+----------------+     +----------------+
```

## 4. API 设计

### 4.1 AresClient 类

```python
class AresClient:
    def __init__(
        self,
        browser_engine="auto",  # "seleniumbase", "undetected", "auto"
        headless=True,
        fingerprint=None,
        proxy=None,
        timeout=30,
        max_retries=3,
        debug=False
    ):
        # 初始化代码...
    
    def get(self, url, params=None, headers=None, **kwargs):
        # GET 请求实现...
    
    def post(self, url, data=None, json=None, headers=None, **kwargs):
        # POST 请求实现...
    
    # 其他 HTTP 方法...
    
    def close(self):
        # 关闭资源...
```

### 4.2 响应对象

```python
class AresResponse:
    def __init__(self, response):
        self.status_code = response.status_code
        self.headers = response.headers
        self.cookies = response.cookies
        self._content = response.content
    
    @property
    def text(self):
        # 返回文本内容...
    
    @property
    def json(self):
        # 返回 JSON 解析结果...
    
    # 其他属性和方法...
```

## 5. 实现计划

### 5.1 项目结构

```
cf_ares/
├── __init__.py
├── client.py          # AresClient 实现
├── engines/
│   ├── __init__.py
│   ├── base.py        # 引擎基类
│   ├── selenium.py    # SeleniumBase 引擎
│   ├── undetected.py  # undetected-chromedriver 引擎
│   └── curl.py        # curl_cffi 引擎
├── utils/
│   ├── __init__.py
│   ├── fingerprint.py # 指纹管理
│   ├── session.py     # 会话管理
│   ├── proxy.py       # 代理管理
│   └── errors.py      # 错误处理
├── exceptions.py      # 自定义异常
└── version.py         # 版本信息
```

### 5.2 依赖管理

主要依赖项：
- seleniumbase
- undetected-chromedriver
- curl_cffi
- requests (用于类型兼容)

### 5.3 开发工具

- pytest: 单元测试和集成测试
- black: 代码格式化
- isort: 导入排序
- flake8: 代码质量检查
- mypy: 类型检查

## 6. 测试策略

### 6.1 单元测试

为每个核心组件编写单元测试，确保其独立功能正常。

### 6.2 集成测试

测试组件之间的交互，确保系统作为一个整体正常工作。

### 6.3 真实网站测试

使用已知受 Cloudflare 保护的网站进行测试，验证库的实际效果。

## 7. 部署和分发

### 7.1 打包

使用 setuptools 和 pyproject.toml 配置打包信息。

### 7.2 发布

将包发布到 PyPI，使用户可以通过 pip 安装。

### 7.3 文档

提供详细的文档，包括安装指南、使用示例和 API 参考。

## 8. 未来扩展

- 支持更多浏览器引擎
- 添加更多 Cloudflare 绕过策略
- 实现更高级的指纹管理
- 添加更多请求引擎选项
- 提供 Web 界面进行可视化调试

## 9. 结论

CF-Ares 项目通过结合浏览器自动化和高性能 HTTP 客户端，提供了一个强大而灵活的 Cloudflare 对抗解决方案。该方案技术可行，实现相对简单，可以满足各种应用场景的需求。

## 10. SeleniumBase UC Mode 集成问题分析

### 10.1 当前实现中的问题

在当前的实现中，我们发现了以下问题：

1. **SeleniumBaseEngine 中硬编码禁用了 UC Mode**：
   在 `cf_ares/engines/selenium.py` 文件中，我们看到以下代码：
   ```python
   options = {
       "headless": self.headless,
       "uc": False,  # Not using undetected mode here
       "incognito": True,
       "block_images": False,
       "user_agent": self.fingerprint_manager.get_user_agent(self.fingerprint),
       "do_not_track": True,
   }
   ```
   这里硬编码设置了 `"uc": False`，完全禁用了 SeleniumBase 的 UC Mode 功能。

2. **AresClient 中的引擎选择逻辑**：
   在 `cf_ares/client.py` 文件中，当 `browser_engine="auto"` 时，代码直接使用了 UndetectedEngine 而不是利用 SeleniumBase 的 UC Mode：
   ```python
   else:  # auto
       # Start with undetected, fallback to seleniumbase if needed
       self._browser_engine = UndetectedEngine(
           headless=self.headless,
           proxy=self.proxy,
           timeout=self.timeout,
           fingerprint=self.fingerprint,
       )
   ```

### 10.2 SeleniumBase UC Mode 的优势

根据 [SeleniumBase 官方文档](https://seleniumbase.io/help_docs/uc_mode/)，SeleniumBase 的 UC Mode 提供了以下优势：

1. **基于 undetected-chromedriver 但有增强**：SeleniumBase 的 UC Mode 是基于 undetected-chromedriver 的，但增加了多项更新、修复和改进。

2. **自动更改 user-agents**：可以防止检测。

3. **自动设置各种 Chromium 参数**：根据需要自动配置。

4. **特殊方法处理验证码**：提供了 `uc_*()` 方法用于绕过验证码。

5. **更好的多线程支持**：与 pytest 集成时提供了更好的多线程支持。

### 10.3 建议的改进方案

基于以上分析，我建议对当前实现进行以下改进：

1. **修改 SeleniumBaseEngine 以支持 UC Mode**：
   ```python
   options = {
       "headless": self.headless,
       "uc": self.use_uc_mode,  # 使用参数控制是否启用 UC Mode
       "incognito": True,
       "block_images": False,
       "user_agent": self.fingerprint_manager.get_user_agent(self.fingerprint),
       "do_not_track": True,
   }
   ```

2. **更新 AresClient 中的引擎选择逻辑**：
   ```python
   if browser_engine == "auto":
       # 使用 SeleniumBase 的 UC Mode 作为首选
       self._browser_engine = SeleniumBaseEngine(
           headless=self.headless,
           proxy=self.proxy,
           timeout=self.timeout,
           fingerprint=self.fingerprint,
           use_uc_mode=True  # 启用 UC Mode
       )
   elif browser_engine == "seleniumbase":
       self._browser_engine = SeleniumBaseEngine(
           headless=self.headless,
           proxy=self.proxy,
           timeout=self.timeout,
           fingerprint=self.fingerprint,
           use_uc_mode=False  # 不使用 UC Mode
       )
   elif browser_engine == "seleniumbase_uc":
       self._browser_engine = SeleniumBaseEngine(
           headless=self.headless,
           proxy=self.proxy,
           timeout=self.timeout,
           fingerprint=self.fingerprint,
           use_uc_mode=True  # 使用 UC Mode
       )
   elif browser_engine == "undetected":
       self._browser_engine = UndetectedEngine(
           headless=self.headless,
           proxy=self.proxy,
           timeout=self.timeout,
           fingerprint=self.fingerprint,
       )
   ```

3. **添加特殊方法处理验证码**：
   在 SeleniumBaseEngine 中添加对 SeleniumBase UC Mode 特殊方法的支持，如 `uc_gui_click_captcha()` 和 `uc_gui_handle_captcha()`。

### 10.4 实现计划

1. 修改 SeleniumBaseEngine 类，添加 `use_uc_mode` 参数。
2. 更新 AresClient 类中的引擎选择逻辑。
3. 在 SeleniumBaseEngine 中添加对 UC Mode 特殊方法的封装。
4. 更新文档，说明 SeleniumBase UC Mode 的使用方法和优势。
5. 添加测试用例，验证 SeleniumBase UC Mode 的有效性。

### 10.5 预期效果

通过以上改进，CF-Ares 将能够更好地利用 SeleniumBase 的 UC Mode 功能，提供更强大的 Cloudflare 防护突破能力。特别是在处理验证码和复杂的 JavaScript 挑战时，将有更好的表现。同时，用户也将有更多的选择，可以根据自己的需求选择不同的浏览器引擎。

## 11. 显式挑战方法和会话管理设计

### 11.1 需求分析

当前的 AresClient 实现中，Cloudflare 挑战的处理是隐式的，发生在第一次请求时。这种设计虽然简单，但存在以下问题：

1. **缺乏控制**：用户无法显式控制何时执行挑战，也无法知道挑战是否成功。
2. **会话管理不透明**：用户无法直接访问和管理会话信息（cookies、headers 等）。
3. **错误处理不明确**：当会话过期时，没有明确的错误提示，用户难以知道何时需要重新执行挑战。

为了解决这些问题，我们需要设计一个更显式的 API，让用户能够：

1. 显式执行 Cloudflare 挑战
2. 获取和管理会话信息
3. 在会话过期时得到明确的错误提示

### 11.2 设计方案

#### 11.2.1 新的异常类型

首先，我们需要定义一个新的异常类型，用于表示 Cloudflare 会话过期：

```python
class CloudflareSessionExpired(Exception):
    """当 Cloudflare 会话过期时抛出的异常"""
    pass
```

#### 11.2.2 AresClient 类的新方法

然后，我们需要在 AresClient 类中添加以下新方法：

```python
def solve_challenge(self, url, max_retries=3):
    """
    显式执行 Cloudflare 挑战
    
    参数:
        url (str): 要访问的 URL
        max_retries (int): 最大重试次数
        
    返回:
        AresResponse: 响应对象
        
    抛出:
        CloudflareChallengeFailed: 如果挑战失败
    """
    # 实现代码...
    
def get_session_info(self):
    """
    获取当前会话信息
    
    返回:
        dict: 包含 cookies、headers 等会话信息的字典
    """
    # 实现代码...
    
def set_session_info(self, session_info):
    """
    设置会话信息
    
    参数:
        session_info (dict): 包含 cookies、headers 等会话信息的字典
    """
    # 实现代码...
    
def save_session(self, file_path):
    """
    将当前会话保存到文件
    
    参数:
        file_path (str): 文件路径
    """
    # 实现代码...
    
def load_session(self, file_path):
    """
    从文件加载会话
    
    参数:
        file_path (str): 文件路径
    """
    # 实现代码...
```

#### 11.2.3 修改现有的请求方法

我们还需要修改现有的请求方法（get、post 等），使其在检测到 Cloudflare 会话过期时抛出 CloudflareSessionExpired 异常：

```python
def get(self, url, params=None, headers=None, **kwargs):
    """
    发送 GET 请求
    
    参数:
        url (str): 要访问的 URL
        params (dict): 查询参数
        headers (dict): 请求头
        **kwargs: 其他参数
        
    返回:
        AresResponse: 响应对象
        
    抛出:
        CloudflareSessionExpired: 如果 Cloudflare 会话过期
    """
    try:
        # 使用 curl_cffi 引擎发送请求
        # ...
    except SomeCurlException as e:
        # 检查是否是 Cloudflare 会话过期
        if "cloudflare" in str(e).lower() or "challenge" in str(e).lower():
            raise CloudflareSessionExpired("Cloudflare 会话已过期，请重新执行 solve_challenge 方法") from e
        raise
```

### 11.3 工作流程

使用新的 API，用户的工作流程将变为：

1. **初始化**：创建 AresClient 实例
2. **显式执行挑战**：调用 `solve_challenge` 方法，突破 Cloudflare 防护
3. **保存会话信息**（可选）：调用 `get_session_info` 或 `save_session` 方法，保存会话信息
4. **发送请求**：调用 `get`、`post` 等方法，发送请求
5. **处理会话过期**：捕获 `CloudflareSessionExpired` 异常，重新执行 `solve_challenge` 方法

示例代码：

```python
from cf_ares import AresClient, CloudflareSessionExpired

# 创建客户端实例
client = AresClient(browser_engine="seleniumbase_uc")

# 显式执行挑战
response = client.solve_challenge("https://example.com")
print(f"挑战成功！状态码: {response.status_code}")

# 保存会话信息（可选）
session_info = client.get_session_info()
print(f"获取到的 cookies: {session_info['cookies']}")

# 发送请求
try:
    response = client.get("https://example.com/api/data")
    print(response.json())
except CloudflareSessionExpired:
    print("会话已过期，重新执行挑战...")
    client.solve_challenge("https://example.com")
    response = client.get("https://example.com/api/data")
    print(response.json())

# 关闭客户端
client.close()
```

### 11.4 会话信息的内容

会话信息（`session_info`）应该包含以下内容：

```python
{
    "cookies": {
        "cf_clearance": "...",
        "other_cookie": "...",
        # 其他 cookies
    },
    "headers": {
        "User-Agent": "...",
        "Accept": "...",
        # 其他 headers
    },
    "fingerprint": {
        "user_agent": "...",
        "accept_language": "...",
        "platform": "...",
        # 其他指纹信息
    },
    "timestamp": 1234567890,  # 会话创建时间
    "url": "https://example.com"  # 会话对应的 URL
}
```

### 11.5 实现计划

1. 在 `exceptions.py` 中添加 `CloudflareSessionExpired` 异常类
2. 在 `AresClient` 类中添加新方法：`solve_challenge`、`get_session_info`、`set_session_info`、`save_session`、`load_session`
3. 修改 `AresClient` 类中的请求方法（`get`、`post` 等），使其能够检测 Cloudflare 会话过期并抛出相应的异常
4. 在 `SessionManager` 类中添加会话信息的序列化和反序列化方法
5. 更新文档，说明新 API 的使用方法

### 11.6 预期效果

通过这些改进，CF-Ares 将提供更加灵活和透明的 API，让用户能够：

1. 显式控制 Cloudflare 挑战的执行
2. 获取和管理会话信息
3. 在会话过期时得到明确的错误提示
4. 轻松实现会话的保存和加载

这将大大提高库的可用性和灵活性，特别是在需要长时间运行的应用中。
