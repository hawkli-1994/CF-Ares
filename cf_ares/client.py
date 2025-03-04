"""
Main client implementation for CF-Ares.
"""

from typing import Any, Dict, List, Optional, Union

from cf_ares.engines.base import BaseEngine
from cf_ares.engines.curl import CurlEngine
from cf_ares.engines.selenium import SeleniumBaseEngine
from cf_ares.engines.undetected import UndetectedEngine
from cf_ares.exceptions import AresError, CloudflareError
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
        """
        self.browser_engine = browser_engine
        self.headless = headless
        self.fingerprint = fingerprint
        self.proxy = proxy
        self.timeout = timeout
        self.max_retries = max_retries
        self.debug = debug

        # Initialize engines
        self._browser_engine: Optional[BaseEngine] = None
        self._curl_engine: Optional[CurlEngine] = None
        self._session_manager = SessionManager()
        self._initialized = False

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
            )
        else:  # auto
            # Start with undetected, fallback to seleniumbase if needed
            self._browser_engine = UndetectedEngine(
                headless=self.headless,
                proxy=self.proxy,
                timeout=self.timeout,
                fingerprint=self.fingerprint,
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
            # If request fails, try to handle Cloudflare again
            if "cloudflare" in str(e).lower():
                self._handle_cloudflare(url)
                # Retry request
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
        """
        return self._request(
            "POST", url, data=data, json=json, headers=headers, **kwargs
        )

    def put(
        self,
        url: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> AresResponse:
        """
        Make a PUT request.

        Args:
            url: URL to request.
            data: Request data.
            json: JSON data.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            AresResponse: Response object.
        """
        return self._request(
            "PUT", url, data=data, json=json, headers=headers, **kwargs
        )

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
        """
        return self._request("DELETE", url, headers=headers, **kwargs)

    def close(self) -> None:
        """Close all resources."""
        if self._browser_engine:
            self._browser_engine.close()
        if self._curl_engine:
            self._curl_engine.close()
        self._initialized = False

    def __enter__(self) -> "AresClient":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exit context manager."""
        self.close() 