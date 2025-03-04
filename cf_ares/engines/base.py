"""
Base engine interface for CF-Ares.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseEngine(ABC):
    """
    Base class for all engines.
    Defines the interface that all engines must implement.
    """

    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        timeout: int = 30,
        fingerprint: Optional[str] = None,
    ):
        """
        Initialize the engine.

        Args:
            headless: Whether to run in headless mode.
            proxy: Proxy to use.
            timeout: Request timeout in seconds.
            fingerprint: Browser fingerprint to use.
        """
        self.headless = headless
        self.proxy = proxy
        self.timeout = timeout
        self.fingerprint = fingerprint

    @abstractmethod
    def get(self, url: str) -> Any:
        """
        Visit a URL.

        Args:
            url: URL to visit.

        Returns:
            Any: Response object.
        """
        pass

    @abstractmethod
    def wait_for_cloudflare(self) -> bool:
        """
        Wait for Cloudflare challenge to complete.

        Returns:
            bool: True if challenge was completed successfully.
        """
        pass

    @abstractmethod
    def get_cookies(self) -> Dict[str, str]:
        """
        Get cookies from the current session.

        Returns:
            Dict[str, str]: Cookies as a dictionary.
        """
        pass

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """
        Get headers from the current session.

        Returns:
            Dict[str, str]: Headers as a dictionary.
        """
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the engine and release resources."""
        pass 