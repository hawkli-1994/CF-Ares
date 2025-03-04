"""
Main client implementation for CF-Ares.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional, Union

from cf_ares.engines.base import BaseEngine
from cf_ares.engines.curl import CurlEngine
from cf_ares.engines.selenium import SeleniumBaseEngine
from cf_ares.engines.undetected import UndetectedEngine
from cf_ares.exceptions import AresError, CloudflareError, CloudflareChallengeFailed, CloudflareSessionExpired
from cf_ares.utils.session import SessionManager


class AresResponse:
    """
    Response object returned by AresClient.
    Compatible with requests.Response interface.
    """

    def __init__(self, response: Any):
        self._response = response
        self.status_code = getattr(response, "status_code", None)
        self.headers = getattr(response, "headers", {})
        self.cookies = getattr(response, "cookies", {})
        self._content = getattr(response, "content", b"")
        self.url = getattr(response, "url", "")

    @property
    def text(self) -> str:
        """Get response text."""
        if hasattr(self._response, "text"):
            return self._response.text
        return self._content.decode("utf-8", errors="replace")

    @property
    def content(self) -> bytes:
        """Get response content as bytes."""
        return self._content

    def json(self) -> Any:
        """Parse response as JSON."""
        if hasattr(self._response, "json"):
            return self._response.json()
        import json
        return json.loads(self.text)

    def __repr__(self) -> str:
        return f"<AresResponse [{self.status_code}]>"


class AresClient:
    """
    Main client for CF-Ares.
    Handles Cloudflare challenges and provides a requests-like interface.
    """

    def __init__(
        self,
        browser_engine: str = "auto",  # "seleniumbase", "undetected", "auto"
        headless: bool = True,
        fingerprint: Optional[str] = None,
        proxy: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        debug: bool = False,
        chrome_path: Optional[str] = None,
    ):
        """
        Initialize AresClient.

        Args:
            browser_engine: Browser engine to use. One of "seleniumbase", "undetected", "auto".
            headless: Whether to run browser in headless mode.
            fingerprint: Browser fingerprint to use.
            proxy: Proxy to use.
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            debug: Enable debug logging.
            chrome_path: Custom path to Chrome binary. If not provided, will search in default locations.
        """
        self.browser_engine = browser_engine
        self.headless = headless
        self.fingerprint = fingerprint
        self.proxy = proxy
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug
        self.chrome_path = chrome_path

        # Initialize engines
        self._browser_engine: Optional[BaseEngine] = None
        self._curl_engine: Optional[CurlEngine] = None
        self._session_manager = SessionManager()
        self._initialized = False

    def __enter__(self) -> "AresClient":
        """Enter the context manager."""
        self._initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit the context manager."""
        self.close()

    def _initialize(self) -> None:
        """Initialize engines if not already initialized."""
        if self._initialized:
            return

        # Initialize curl engine
        self._curl_engine = CurlEngine(
            proxy=self.proxy,
            timeout=self.timeout,
            fingerprint=self.fingerprint,
        )

        # Initialize browser engine based on configuration
        if self.browser_engine == "seleniumbase":
            self._browser_engine = SeleniumBaseEngine(
                headless=self.headless,
                proxy=self.proxy,
                timeout=self.timeout,
                fingerprint=self.fingerprint,
            )
        elif self.browser_engine == "undetected":
            self._browser_engine = UndetectedEngine(
                headless=self.headless,
                proxy=self.proxy,
                timeout=self.timeout,
                fingerprint=self.fingerprint,
                chrome_path=self.chrome_path,
            )
        else:  # auto
            # Start with undetected, fallback to seleniumbase if needed
            self._browser_engine = UndetectedEngine(
                headless=self.headless,
                proxy=self.proxy,
                timeout=self.timeout,
                fingerprint=self.fingerprint,
                chrome_path=self.chrome_path,
            )

        self._initialized = True

    def _handle_cloudflare(self, url: str) -> None:
        """
        Handle Cloudflare challenge using browser engine.

        Args:
            url: URL to visit.

        Raises:
            CloudflareError: If Cloudflare challenge fails.
        """
        if not self._browser_engine:
            self._initialize()

        if not self._browser_engine:
            raise AresError("Browser engine not initialized")

        # Visit URL with browser engine
        self._browser_engine.get(url)

        # Wait for Cloudflare challenge to complete
        self._browser_engine.wait_for_cloudflare()

        # Extract session information
        cookies = self._browser_engine.get_cookies()
        headers = self._browser_engine.get_headers()

        # Update session manager
        self._session_manager.update(url, cookies, headers)

        # Apply session to curl engine
        if self._curl_engine:
            self._curl_engine.set_cookies(cookies)
            self._curl_engine.set_headers(headers)

    def solve_challenge(self, url: str, max_retries: int = 3) -> AresResponse:
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
        self._initialize()
        
        if not self._browser_engine:
            raise AresError("Browser engine not initialized")
            
        retries = 0
        last_error = None
        
        while retries < max_retries:
            try:
                # 使用浏览器引擎访问 URL
                self._browser_engine.get(url)
                
                # 等待 Cloudflare 挑战完成
                self._browser_engine.wait_for_cloudflare()
                
                # 提取会话信息
                cookies = self._browser_engine.get_cookies()
                headers = self._browser_engine.get_headers()
                
                # 更新会话管理器
                self._session_manager.update(url, cookies, headers)
                
                # 应用会话到 curl 引擎
                if self._curl_engine:
                    self._curl_engine.set_cookies(cookies)
                    self._curl_engine.set_headers(headers)
                
                # 使用 curl 引擎发送请求，验证会话是否有效
                response = self._curl_engine.request("GET", url)
                
                # 如果响应中包含 Cloudflare 挑战页面，则认为挑战失败
                if "challenge" in response.text.lower() or "cloudflare" in response.text.lower():
                    raise CloudflareChallengeFailed("Cloudflare 挑战失败，响应中包含挑战页面")
                
                return AresResponse(response)
            except Exception as e:
                last_error = e
                retries += 1
                if self.debug:
                    print(f"Cloudflare 挑战失败，重试 {retries}/{max_retries}: {str(e)}")
                time.sleep(2)  # 等待一段时间后重试
        
        # 所有重试都失败
        raise CloudflareChallengeFailed(f"无法通过 Cloudflare 挑战，最大重试次数已用尽: {str(last_error)}")

    def get_session_info(self, url: Optional[str] = None) -> Dict[str, Any]:
        """
        获取当前会话信息
        
        参数:
            url (str, optional): 要获取会话信息的 URL。如果为 None，则返回所有会话信息。
            
        返回:
            dict: 包含 cookies、headers 等会话信息的字典
        """
        if not self._initialized:
            self._initialize()
            
        if url:
            cookies = self._session_manager.get_cookies(url)
            headers = self._session_manager.get_headers(url)
            
            if not cookies or not headers:
                return {}
                
            return {
                "cookies": cookies,
                "headers": headers,
                "timestamp": time.time(),
                "url": url
            }
        else:
            # 返回所有会话信息
            result = {}
            for domain, session in self._session_manager.sessions.items():
                result[domain] = {
                    "cookies": session["cookies"],
                    "headers": session["headers"],
                    "timestamp": session["timestamp"],
                }
            return result

    def set_session_info(self, session_info: Dict[str, Any], url: Optional[str] = None) -> None:
        """
        设置会话信息
        
        参数:
            session_info (dict): 包含 cookies、headers 等会话信息的字典
            url (str, optional): 要设置会话信息的 URL。如果为 None，则使用 session_info 中的 url。
        """
        if not self._initialized:
            self._initialize()
            
        if not url and "url" in session_info:
            url = session_info["url"]
            
        if not url:
            raise ValueError("必须提供 url 参数或在 session_info 中包含 url 字段")
            
        cookies = session_info.get("cookies", {})
        headers = session_info.get("headers", {})
        
        # 更新会话管理器
        self._session_manager.update(url, cookies, headers)
        
        # 应用会话到 curl 引擎
        if self._curl_engine:
            self._curl_engine.set_cookies(cookies)
            self._curl_engine.set_headers(headers)

    def save_session(self, file_path: str, url: Optional[str] = None) -> None:
        """
        将当前会话保存到文件
        
        参数:
            file_path (str): 文件路径
            url (str, optional): 要保存会话的 URL。如果为 None，则保存所有会话。
        """
        session_info = self.get_session_info(url)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_info, f, indent=2)

    def load_session(self, file_path: str) -> None:
        """
        从文件加载会话
        
        参数:
            file_path (str): 文件路径
        """
        with open(file_path, "r", encoding="utf-8") as f:
            session_info = json.load(f)
            
        if isinstance(session_info, dict):
            if "cookies" in session_info and "url" in session_info:
                # 单个会话
                self.set_session_info(session_info)
            else:
                # 多个会话
                for domain, info in session_info.items():
                    if "cookies" in info and "headers" in info:
                        url = f"https://{domain}"
                        self.set_session_info({
                            "cookies": info["cookies"],
                            "headers": info["headers"],
                            "url": url
                        })

    def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a request with automatic Cloudflare handling.

        Args:
            method: HTTP method.
            url: URL to request.
            params: Query parameters.
            data: Request data.
            json: JSON data.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        self._initialize()

        if not self._curl_engine:
            raise AresError("Curl engine not initialized")

        # Check if we need to handle Cloudflare first
        if not self._session_manager.has_valid_session(url):
            self._handle_cloudflare(url)

        # Make request with curl engine
        try:
            response = self._curl_engine.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                **kwargs,
            )
            return AresResponse(response)
        except Exception as e:
            # If request fails, check if it's a Cloudflare issue
            error_str = str(e).lower()
            if "cloudflare" in error_str or "challenge" in error_str or "captcha" in error_str:
                raise CloudflareSessionExpired("Cloudflare 会话已过期，请重新执行 solve_challenge 方法") from e
            raise

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a GET request.

        Args:
            url: URL to request.
            params: Query parameters.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request("GET", url, params=params, headers=headers, **kwargs)

    def post(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a POST request.

        Args:
            url: URL to request.
            data: Request data.
            json: JSON data.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request(
            "POST", url, data=data, json=json, headers=headers, **kwargs
        )

    def put(
        self,
        url: str,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a PUT request.

        Args:
            url: URL to request.
            data: Request data.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request("PUT", url, data=data, headers=headers, **kwargs)

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a DELETE request.

        Args:
            url: URL to request.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request("DELETE", url, headers=headers, **kwargs)

    def head(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a HEAD request.

        Args:
            url: URL to request.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request("HEAD", url, headers=headers, **kwargs)

    def options(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make an OPTIONS request.

        Args:
            url: URL to request.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request("OPTIONS", url, headers=headers, **kwargs)

    def patch(
        self,
        url: str,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a PATCH request.

        Args:
            url: URL to request.
            data: Request data.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
            
        Raises:
            CloudflareSessionExpired: 如果 Cloudflare 会话过期
        """
        return self._request("PATCH", url, data=data, headers=headers, **kwargs)

    @property
    def cookies(self) -> Dict[str, str]:
        """
        Get all cookies from the current session.

        Returns:
            Dict[str, str]: All cookies.
        """
        if self._curl_engine:
            return self._curl_engine.get_cookies()
        return {}

    @property
    def headers(self) -> Dict[str, str]:
        """
        Get all headers from the current session.

        Returns:
            Dict[str, str]: All headers.
        """
        if self._curl_engine:
            return self._curl_engine.get_headers()
        return {}

    def close(self) -> None:
        """Close all resources."""
        if self._browser_engine:
            self._browser_engine.close()
        if self._curl_engine:
            self._curl_engine.close()
        self._initialized = False 