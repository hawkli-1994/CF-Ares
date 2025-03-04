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

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件