"""
Custom exceptions for CF-Ares.
"""


class AresError(Exception):
    """Base exception for all CF-Ares errors."""
    pass


class CloudflareError(AresError):
    """Exception raised when Cloudflare challenge fails."""
    pass


class BrowserError(AresError):
    """Exception raised when browser automation fails."""
    pass


class SessionError(AresError):
    """Exception raised when session management fails."""
    pass


class RequestError(AresError):
    """Exception raised when a request fails."""
    pass


class ProxyError(AresError):
    """Exception raised when proxy configuration fails."""
    pass 