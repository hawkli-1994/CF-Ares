"""
Session management utilities for CF-Ares.
"""

import time
from typing import Dict, Optional
from urllib.parse import urlparse


class SessionManager:
    """
    Manages session information for different domains.
    Handles cookies, headers, and session validity.
    """

    def __init__(self, session_ttl: int = 3600):
        """
        Initialize the session manager.

        Args:
            session_ttl: Time-to-live for sessions in seconds.
        """
        self.sessions: Dict[str, Dict] = {}
        self.session_ttl = session_ttl

    def _get_domain(self, url: str) -> str:
        """
        Extract domain from URL.

        Args:
            url: URL to extract domain from.

        Returns:
            str: Domain name.
        """
        parsed = urlparse(url)
        return parsed.netloc

    def update(
        self, url: str, cookies: Dict[str, str], headers: Dict[str, str]
    ) -> None:
        """
        Update session information for a domain.

        Args:
            url: URL associated with the session.
            cookies: Cookies to store.
            headers: Headers to store.
        """
        domain = self._get_domain(url)
        self.sessions[domain] = {
            "cookies": cookies,
            "headers": headers,
            "timestamp": time.time(),
        }

    def get_cookies(self, url: str) -> Optional[Dict[str, str]]:
        """
        Get cookies for a domain.

        Args:
            url: URL to get cookies for.

        Returns:
            Optional[Dict[str, str]]: Cookies or None if no session exists.
        """
        domain = self._get_domain(url)
        if domain in self.sessions:
            return self.sessions[domain]["cookies"]
        return None

    def get_headers(self, url: str) -> Optional[Dict[str, str]]:
        """
        Get headers for a domain.

        Args:
            url: URL to get headers for.

        Returns:
            Optional[Dict[str, str]]: Headers or None if no session exists.
        """
        domain = self._get_domain(url)
        if domain in self.sessions:
            return self.sessions[domain]["headers"]
        return None

    def has_valid_session(self, url: str) -> bool:
        """
        Check if a valid session exists for a domain.

        Args:
            url: URL to check session for.

        Returns:
            bool: True if a valid session exists.
        """
        domain = self._get_domain(url)
        if domain not in self.sessions:
            return False

        # Check if session is expired
        timestamp = self.sessions[domain]["timestamp"]
        if time.time() - timestamp > self.session_ttl:
            return False

        return True

    def clear(self, url: Optional[str] = None) -> None:
        """
        Clear session information.

        Args:
            url: URL to clear session for. If None, clear all sessions.
        """
        if url:
            domain = self._get_domain(url)
            if domain in self.sessions:
                del self.sessions[domain]
        else:
            self.sessions.clear() 