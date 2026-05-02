---
hide:
  - navigation
---

# CF-Ares 🔥

**下一代 Cloudflare 对抗框架 | 智能切换浏览器引擎与高性能请求**

<p align="center">
  <a href="https://pypi.org/project/cf-ares/">
    <img src="https://img.shields.io/pypi/v/cf-ares.svg" alt="PyPI">
  </a>
  <a href="https://pypi.org/project/cf-ares/">
    <img src="https://img.shields.io/pypi/pyversions/cf-ares.svg" alt="Python Versions">
  </a>
  <a href="https://github.com/hawkli-1994/CF-Ares/actions/workflows/ci.yml">
    <img src="https://github.com/hawkli-1994/CF-Ares/workflows/CI/badge.svg" alt="CI">
  </a>
  <a href="https://hawkli-1994.github.io/CF-Ares/">
    <img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue" alt="Documentation">
  </a>
  <a href="https://github.com/hawkli-1994/CF-Ares/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </a>
</p>

---

## 核心特性

- 🛡️ **自动处理** 5秒盾、CAPTCHA 验证、JavaScript 质询
- ⚡ **高性能** curl_cffi TLS 指纹模拟 + 浏览器惰性初始化
- 🔒 **智能代理** 轮换与请求特征随机化
- 📦 **轻松集成** 可作为 Python 库嵌入任何项目
- 🧠 **会话管理** 显式挑战执行与会话持久化

---

## 快速开始

### 安装

```bash
pip install cf-ares
```

### 基本使用

```python
from cf_ares import AresClient

# 创建客户端 — 只初始化 curl 引擎，零浏览器开销
client = AresClient()

# 访问站点（自动绕过 Cloudflare）
response = client.get("https://example.com")
print(response.status_code)  # 200
print(response.text)         # 页面内容

# 自动关闭
client.close()
```

### 上下文管理器

```python
with AresClient() as client:
    response = client.get("https://example.com")
    # 自动释放资源
```

---

## 文档导航

| 文档 | 说明 |
|------|------|
| [安装指南](installation.md) | 详细安装步骤与环境要求 |
| [快速开始](basic_usage.md) | 基本用法与示例 |
| [高级配置](advanced_usage.md) | 自定义引擎、代理、指纹 |
| [会话管理](session_management.md) | Cookie 持久化与跨程序共享 |
| [架构设计](architecture.md) | 两阶段协同架构详解 |
| [引擎详解](engines.md) | CurlEngine / BrowserEngine 对比 |
| [API 参考](api.md) | 完整 API 文档 |
| [配置参考](configuration.md) | 所有配置参数说明 |
| [故障排查](troubleshooting.md) | 常见问题与解决方案 |
| [更新日志](changelog.md) | 版本变更记录 |

---

## GitHub 仓库

👉 [hawkli-1994/CF-Ares](https://github.com/hawkli-1994/CF-Ares)

## 许可证

MIT License — 详见 [LICENSE](https://github.com/hawkli-1994/CF-Ares/blob/main/LICENSE)
