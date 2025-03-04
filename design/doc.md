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
