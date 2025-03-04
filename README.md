<h1 align="center">CF-Ares 🔥</h1>
<p align="center">下一代Cloudflare对抗框架 | 智能切换浏览器引擎与高性能请求</p>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/hawkli-1994/CF-Ares/blob/main/LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**突破Cloudflare防护的新范式**，通过三重防御层协同工作：
1. 🛡️ ​**智能引擎路由**​ - 根据防护等级自动切换 SeleniumBase/undetected-chromedriver/curl_cffi
2. 🌐 ​**动态指纹系统**​ - 实时生成高可信度浏览器环境指纹
3. ⚡ ​**混合请求模式**​ - 首次验证使用浏览器，后续保持curl_cffi的并发性能

✨ 特性亮点：
- ✅ 自动处理5秒盾、CAPTCHA验证、JavaScript质询
- ✅ 支持浏览器指纹混淆 + TLS指纹模拟
- ✅ 智能代理轮换与请求特征随机化
- ✅ 可视化调试面板实时显示对抗过程

## 🚀 快速开始
```python
from cf_ares import AresClient

# 自动选择最佳穿透策略
with AresClient(fingerprint="chrome_120") as warrior:
    response = warrior.get("https://受保护网站.com")
    print(response.html)  # 自动解析的HTML对象

# 手动指定引擎模式
breaker = AresClient(
    engine_chain=["undetected", "curl"], 
    proxy="socks5://user:pass@gateway:port"
)
breaker.rotate_fingerprint()  # 切换新指纹
