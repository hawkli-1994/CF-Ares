<h1 align="center">CF-Ares 🔥</h1>
<p align="center">下一代Cloudflare对抗框架 | 智能切换浏览器引擎与高性能请求</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hawkli-1994/CF-Ares/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**突破Cloudflare防护的新范式**，通过两阶段协同工作：
1. 🛡️ **浏览器引擎突破** - 使用 SeleniumBase/undetected-chromedriver 突破初始防护
2. ⚡ **高性能请求维持** - 获取有效凭证后切换到 curl_cffi 保持高并发性能

✨ 特性亮点：
- ✅ 自动处理5秒盾、CAPTCHA验证、JavaScript质询
- ✅ 支持浏览器指纹混淆 + TLS指纹模拟
- ✅ 智能代理轮换与请求特征随机化
- ✅ 可作为Python库轻松集成到其他项目中

## 🚀 快速开始

### 安装

```bash
pip install cf-ares
```

### 基本使用

```python
from cf_ares import AresClient

# 创建客户端实例
client = AresClient()

# 访问受Cloudflare保护的网站
response = client.get("https://受保护网站.com")
print(response.text)

# 使用代理
client = AresClient(proxy="socks5://user:pass@gateway:port")
response = client.get("https://受保护网站.com")
```

### 高级配置

```python
from cf_ares import AresClient

# 自定义配置
client = AresClient(
    browser_engine="undetected",  # 选择浏览器引擎: "seleniumbase" 或 "undetected"
    headless=False,               # 是否使用无头模式
    fingerprint="chrome_120",     # 浏览器指纹配置
    proxy="http://user:pass@host:port",  # 代理设置
    timeout=30,                   # 请求超时时间(秒)
    max_retries=3                 # 最大重试次数
)

# 执行请求
response = client.get("https://受保护网站.com")

# 会话复用 - 使用已验证的会话执行高性能请求
for i in range(10):
    resp = client.get(f"https://受保护网站.com/api/endpoint?page={i}")
    print(resp.json())
```

### 突破验证后调用 API 示例

以下示例展示了如何先使用 GET 请求突破 Cloudflare 验证，然后使用 POST 方法调用目标网站的其他 API：

```python
import json
from cf_ares import AresClient

# 创建客户端实例
client = AresClient(
    browser_engine="undetected",  # 使用 undetected-chromedriver 引擎
    headless=True,                # 无头模式
    timeout=60                    # 增加超时时间以应对复杂验证
)

# 步骤 1: 访问网站首页，突破 Cloudflare 验证
print("正在突破 Cloudflare 验证...")
response = client.get("https://api.受保护网站.com")

# 检查是否成功突破验证
if response.status_code == 200:
    print(f"成功突破验证! 状态码: {response.status_code}")
    
    # 打印获取到的 cookies
    print("获取到的 cookies:")
    for cookie_name, cookie_value in client.cookies.items():
        print(f"  {cookie_name}: {cookie_value[:10]}..." if len(cookie_value) > 10 else f"  {cookie_name}: {cookie_value}")
    
    # 步骤 2: 使用已验证的会话调用 API
    print("\n开始调用 API...")
    
    # 准备 API 请求数据
    api_data = {
        "username": "test_user",
        "query": "example search",
        "page": 1,
        "limit": 20
    }
    
    # 设置请求头
    headers = {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://受保护网站.com/search"
    }
    
    # 发送 POST 请求到 API 端点
    api_response = client.post(
        "https://api.受保护网站.com/v1/search",
        json=api_data,
        headers=headers
    )
    
    # 处理 API 响应
    if api_response.status_code == 200:
        results = api_response.json()
        print(f"API 调用成功! 获取到 {len(results.get('items', []))} 条结果")
        
        # 处理返回的数据
        for i, item in enumerate(results.get("items", [])[:3]):
            print(f"结果 {i+1}: {item.get('title', 'N/A')}")
        
        # 继续调用其他 API...
        user_info = client.post("https://api.受保护网站.com/v1/user/info")
        print(f"用户信息 API 状态码: {user_info.status_code}")
    else:
        print(f"API 调用失败! 状态码: {api_response.status_code}")
        print(f"错误信息: {api_response.text}")
else:
    print(f"突破验证失败! 状态码: {response.status_code}")
    print(f"错误信息: {response.text}")

# 关闭客户端，释放资源
client.close()
```

## 🛠️ 开发

```bash
# 克隆仓库
git clone git@github.com:hawkli-1994/CF-Ares.git
cd CF-Ares

# 安装开发依赖
make setup-dev

# 运行测试
make test

# 构建包
make build
```

### 发布到 PyPI

CF-Ares 提供了两种发布脚本，用于将包发布到 PyPI：

#### 使用 Bash 脚本

```bash
# 发布到 PyPI
./scripts/publish.sh

# 发布到 TestPyPI
./scripts/publish.sh --test

# 跳过测试
./scripts/publish.sh --skip-tests
```

#### 使用 Python 脚本（跨平台）

```bash
# 发布到 PyPI
python scripts/publish.py

# 发布到 TestPyPI
python scripts/publish.py --test

# 跳过测试并自动确认
python scripts/publish.py --skip-tests --no-confirm
```

更多详细信息，请查看 [scripts/README.md](scripts/README.md)。

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件