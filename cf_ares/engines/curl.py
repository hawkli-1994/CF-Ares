"""
curl_cffi engine implementation for CF-Ares.
"""

from typing import Any, Dict, List, Optional, Union

from curl_cffi import requests

from cf_ares.engines.base import BaseEngine
from cf_ares.exceptions import RequestError
from cf_ares.utils.fingerprint import FingerprintManager


class CurlEngine:
    """
    curl_cffi engine implementation.
    Uses curl_cffi for high-performance requests with TLS fingerprinting.
    """

    def __init__(
        self,
        proxy: Optional[str] = None,
        timeout: int = 30,
        fingerprint: Optional[str] = None,
    ):
        """
        Initialize the curl_cffi engine.

        Args:
            proxy: Proxy to use.
            timeout: Request timeout in seconds.
            fingerprint: Browser fingerprint to use.
        """
        self.proxy = proxy
        self.timeout = timeout
        self.fingerprint = fingerprint
        self.fingerprint_manager = FingerprintManager()
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a new curl_cffi session.

        Returns:
            requests.Session: curl_cffi session.
        """
        # Get TLS fingerprint
        tls_fingerprint = self.fingerprint_manager.get_tls_fingerprint(self.fingerprint)
        
        # Create session
        session = requests.Session(
            timeout=self.timeout,
            impersonate="chrome110",  # Default to Chrome 110 impersonation
        )
        
        # Set proxy if specified
        if self.proxy:
            session.proxies = {"http": self.proxy, "https": self.proxy}
        
        # Set default headers
        user_agent = self.fingerprint_manager.get_user_agent(self.fingerprint)
        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
        })
        
        return session

    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """
        Set cookies for the session.

        Args:
            cookies: Cookies to set.
        """
        # Convert cookies to curl_cffi format
        for name, value in cookies.items():
            self.session.cookies.set(name, value)

    def set_headers(self, headers: Dict[str, str]) -> None:
        """
        Set headers for the session.

        Args:
            headers: Headers to set.
        """
        self.session.headers.update(headers)

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Make a request.

        Args:
            method: HTTP method.
            url: URL to request.
            params: Query parameters.
            data: Request data.
            json: JSON data.
            headers: Request headers.
            **kwargs: Additional arguments.

        Returns:
            Any: Response object.

        Raises:
            RequestError: If request fails.
        """
        try:
            # Prepare request arguments
            request_kwargs = {
                "params": params,
                "timeout": kwargs.get("timeout", self.timeout),
            }
            
            # Add data or JSON if specified
            if data is not None:
                request_kwargs["data"] = data
            if json is not None:
                request_kwargs["json"] = json
            
            # Add headers if specified
            if headers is not None:
                request_kwargs["headers"] = headers
            
            # Add additional arguments
            for key, value in kwargs.items():
                if key not in request_kwargs:
                    request_kwargs[key] = value
            
            # Make request
            response = self.session.request(method, url, **request_kwargs)
            
            return response
        except Exception as e:
            raise RequestError(f"Request failed: {e}")

    def close(self) -> None:
        """Close the engine and release resources."""
        if self.session:
            try:
                self.session.close()
            except:
                pass 