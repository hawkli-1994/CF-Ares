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
- ✅ 显式挑战执行与会话管理

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
    browser_engine="undetected",  # 选择浏览器引擎: "seleniumbase", "undetected" 或 "auto"
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

### 显式挑战执行与会话管理

```python
from cf_ares import AresClient, CloudflareSessionExpired, CloudflareChallengeFailed

# 创建客户端实例
client = AresClient(browser_engine="undetected")

try:
    # 显式执行 Cloudflare 挑战
    response = client.solve_challenge("https://受保护网站.com")
    print(f"挑战成功! 状态码: {response.status_code}")
    
    # 获取会话信息
    session_info = client.get_session_info("https://受保护网站.com")  # 指定URL参数
    print(f"获取到的 cookies: {session_info['cookies']}")
    
    # 保存会话到文件
    client.save_session("cf_session.json")
    
except CloudflareChallengeFailed as e:
    print(f"挑战失败: {e}")
    exit(1)

# 在另一个程序中加载会话
new_client = AresClient()
new_client.load_session("cf_session.json")

# 使用加载的会话发送请求
try:
    response = new_client.get("https://受保护网站.com/api/data")
    print(response.json())
except CloudflareSessionExpired:
    print("会话已过期，重新执行挑战...")
    new_client.solve_challenge("https://受保护网站.com")
    response = new_client.get("https://受保护网站.com/api/data")
    print(response.json())
```

### 突破验证后调用 API 示例

以下示例展示了如何使用显式挑战方法突破 Cloudflare 验证，然后调用目标网站的 API：

```python
import json
from cf_ares import AresClient, CloudflareSessionExpired, CloudflareChallengeFailed

# 创建客户端实例
client = AresClient(
    browser_engine="undetected",  # 使用 undetected-chromedriver 引擎
    headless=True,                # 无头模式
    timeout=60                    # 增加超时时间以应对复杂验证
)

try:
    # 步骤 1: 显式执行 Cloudflare 挑战
    print("正在执行 Cloudflare 挑战...")
    response = client.solve_challenge("https://api.受保护网站.com")
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
    
    # 发送 POST 请求到 API 端点 - 无需手动设置 headers，客户端会自动使用已验证的会话
    # 只添加必要的自定义头，不会覆盖已验证的会话头信息
    api_response = client.post(
        "https://api.受保护网站.com/v1/search",
        json=api_data,
        headers={"X-API-Key": "your-api-key"}  # 只添加必要的自定义头
    )
    
    # 处理 API 响应
    if api_response.status_code == 200:
        results = api_response.json()
        print(f"API 调用成功! 获取到 {len(results.get('items', []))} 条结果")
        
        # 处理返回的数据
        for i, item in enumerate(results.get("items", [])[:3]):
            print(f"结果 {i+1}: {item.get('title', 'N/A')}")
        
        # 保存会话以便后续使用
        client.save_session("cf_session.json")
        print("会话已保存到 cf_session.json")
        
        # 使用保存的会话信息进行更多 API 调用
        for i in range(3):
            try:
                data_response = client.get(f"https://api.受保护网站.com/v1/data?page={i}")
                print(f"页面 {i+1} 数据获取成功! 状态码: {data_response.status_code}")
            except CloudflareSessionExpired:
                print(f"页面 {i+1} 请求时会话已过期，重新执行挑战...")
                client.solve_challenge("https://api.受保护网站.com")
    else:
        print(f"API 调用失败! 状态码: {api_response.status_code}")
        print(f"错误信息: {api_response.text}")

except CloudflareChallengeFailed as e:
    print(f"Cloudflare 挑战失败: {e}")
    print("请检查网络连接或代理设置...")

except CloudflareSessionExpired as e:
    print(f"Cloudflare 会话已过期: {e}")
    print("请重新执行挑战...")

except Exception as e:
    print(f"发生未知错误: {e}")

finally:
    # 关闭客户端，释放资源
    client.close()
```

### 跨程序会话共享示例

以下示例展示了如何在不同程序之间共享 Cloudflare 会话：

```python
# 程序 1: 执行挑战并保存会话
from cf_ares import AresClient, CloudflareChallengeFailed

def save_cf_session():
    client = AresClient(browser_engine="undetected")
    try:
        print("执行 Cloudflare 挑战...")
        client.solve_challenge("https://受保护网站.com")
        
        # 保存会话到文件
        client.save_session("cf_session.json")
        print("会话已保存到 cf_session.json")
        return True
    except CloudflareChallengeFailed as e:
        print(f"挑战失败: {e}")
        return False
    finally:
        client.close()

# 程序 2: 加载会话并使用
from cf_ares import AresClient, CloudflareSessionExpired

def use_cf_session():
    client = AresClient()
    try:
        # 加载保存的会话
        client.load_session("cf_session.json")
        print("会话已加载")
        
        # 使用加载的会话发送请求
        try:
            response = client.get("https://受保护网站.com/api/data")
            print(f"请求成功! 状态码: {response.status_code}")
            return response.json()
        except CloudflareSessionExpired:
            print("会话已过期，需要重新执行挑战")
            return None
    finally:
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