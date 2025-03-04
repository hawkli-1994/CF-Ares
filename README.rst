CF-Ares
=======

下一代Cloudflare对抗框架 | 智能切换浏览器引擎与高性能请求

**突破Cloudflare防护的新范式**，通过两阶段协同工作：

1. **浏览器引擎突破** - 使用 SeleniumBase/undetected-chromedriver 突破初始防护
2. **高性能请求维持** - 获取有效凭证后切换到 curl_cffi 保持高并发性能

特性亮点
--------

- 自动处理5秒盾、CAPTCHA验证、JavaScript质询
- 支持浏览器指纹混淆 + TLS指纹模拟
- 智能代理轮换与请求特征随机化
- 可作为Python库轻松集成到其他项目中

安装
----

.. code-block:: bash

    pip install cf-ares

基本使用
--------

.. code-block:: python

    from cf_ares import AresClient

    # 创建客户端实例
    client = AresClient()

    # 访问受Cloudflare保护的网站
    response = client.get("https://受保护网站.com")
    print(response.text)

    # 使用代理
    client = AresClient(proxy="socks5://user:pass@gateway:port")
    response = client.get("https://受保护网站.com")

更多信息请访问 `GitHub 仓库 <https://github.com/yourusername/CF-Ares>`_。 