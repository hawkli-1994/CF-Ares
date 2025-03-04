"""
Undetected ChromeDriver engine implementation for CF-Ares.
"""

import time
import os
from typing import Any, Dict, List, Optional

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from cf_ares.engines.base import BaseEngine
from cf_ares.exceptions import BrowserError, CloudflareError
from cf_ares.utils.fingerprint import FingerprintManager


class UndetectedEngine(BaseEngine):
    """
    Undetected ChromeDriver engine implementation.
    Uses undetected-chromedriver to handle advanced Cloudflare challenges.
    """

    # Default Chrome binary paths
    CHROME_PATHS = [
        # System paths
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/usr/local/bin/chrome",
        "/usr/local/bin/google-chrome",
        "/usr/local/bin/chromium",
        "/usr/local/bin/chromium-browser",
        # Project bin directory
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bin", "chrome"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bin", "google-chrome"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bin", "chromium"),
    ]

    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        timeout: int = 30,
        fingerprint: Optional[str] = None,
        chrome_path: Optional[str] = None,
    ):
        """
        Initialize the Undetected ChromeDriver engine.

        Args:
            headless: Whether to run in headless mode.
            proxy: Proxy to use.
            timeout: Request timeout in seconds.
            fingerprint: Browser fingerprint to use.
            chrome_path: Custom path to Chrome binary. If not provided, will search in default locations.
        """
        super().__init__(headless, proxy, timeout, fingerprint)
        self.driver: Optional[uc.Chrome] = None
        self.fingerprint_manager = FingerprintManager()
        self.chrome_path = chrome_path
        self._initialize_driver()

    def _initialize_driver(self) -> None:
        """Initialize the Undetected ChromeDriver."""
        try:
            # Prepare Chrome options
            options = Options()
            
            # Set user agent if fingerprint is specified
            if self.fingerprint:
                user_agent = self.fingerprint_manager.get_user_agent(self.fingerprint)
                options.add_argument(f"--user-agent={user_agent}")
            
            # Set proxy if specified
            if self.proxy:
                options.add_argument(f"--proxy-server={self.proxy}")
            
            # Add common options
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            
            # Set Chrome binary location
            chrome_path = self.chrome_path
            if not chrome_path:
                for path in self.CHROME_PATHS:
                    if os.path.exists(path):
                        chrome_path = path
                        break
                    
            if not chrome_path:
                # If no Chrome binary found, let undetected-chromedriver handle it
                chrome_path = None
                
            # Create driver
            self.driver = uc.Chrome(
                options=options,
                headless=self.headless,
                use_subprocess=True,
                browser_executable_path=chrome_path,
            )
            
            # Set timeout
            self.driver.set_page_load_timeout(self.timeout)
            
            # Apply fingerprint if specified
            if self.fingerprint:
                self._apply_fingerprint()
        except Exception as e:
            raise BrowserError(f"Failed to initialize Undetected ChromeDriver: {e}")

    def _apply_fingerprint(self) -> None:
        """Apply fingerprint to the browser."""
        if not self.driver:
            return

        fingerprint = self.fingerprint_manager.get_fingerprint(self.fingerprint)
        
        # Apply basic fingerprint properties
        js_script = """
        // Override screen properties
        Object.defineProperty(screen, 'width', {
            get: function() { return %d; }
        });
        Object.defineProperty(screen, 'height', {
            get: function() { return %d; }
        });
        
        // Override timezone
        Object.defineProperty(Intl.DateTimeFormat.prototype, 'resolvedOptions', {
            get: function() { 
                return function() { 
                    return { timeZone: 'UTC', timeZoneOffset: %d }; 
                }
            }
        });
        """ % (
            fingerprint.get("screenResolution", [1920, 1080])[0],
            fingerprint.get("screenResolution", [1920, 1080])[1],
            fingerprint.get("timezoneOffset", 0),
        )
        
        try:
            self.driver.execute_script(js_script)
        except Exception as e:
            # Non-critical error, just log it
            print(f"Warning: Failed to apply fingerprint: {e}")

    def get(self, url: str) -> Any:
        """
        Visit a URL.

        Args:
            url: URL to visit.

        Returns:
            Any: Response object.

        Raises:
            BrowserError: If browser automation fails.
        """
        if not self.driver:
            self._initialize_driver()

        try:
            self.driver.get(url)
            return self.driver
        except Exception as e:
            raise BrowserError(f"Failed to visit URL: {e}")

    def wait_for_cloudflare(self) -> bool:
        """
        Wait for Cloudflare challenge to complete.

        Returns:
            bool: True if challenge was completed successfully.

        Raises:
            CloudflareError: If Cloudflare challenge fails.
        """
        if not self.driver:
            raise BrowserError("Driver not initialized")

        # Common Cloudflare challenge selectors and patterns
        cf_selectors = [
            "#cf-challenge-running",
            "#cf-please-wait",
            "#cf-content",
            "div.cf-browser-verification",
            "#challenge-form",
            "#challenge-running",
            "#challenge-error-title",
        ]

        # Wait for initial challenge page to load
        time.sleep(2)

        # Check if we're on a Cloudflare challenge page
        is_cloudflare = False
        for selector in cf_selectors:
            try:
                if self.driver.find_elements(By.CSS_SELECTOR, selector):
                    is_cloudflare = True
                    break
            except:
                pass

        if not is_cloudflare:
            # No Cloudflare challenge detected
            return True

        # Wait for the challenge to be solved
        max_wait = self.timeout
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            # Check if we're still on a challenge page
            still_on_challenge = False
            for selector in cf_selectors:
                try:
                    if self.driver.find_elements(By.CSS_SELECTOR, selector):
                        still_on_challenge = True
                        break
                except:
                    pass
            
            if not still_on_challenge:
                # Challenge completed
                # Wait a bit more to ensure page is fully loaded
                time.sleep(2)
                return True
            
            # Check for error messages
            try:
                error_elem = self.driver.find_elements(By.CSS_SELECTOR, "#challenge-error-title")
                if error_elem:
                    raise CloudflareError(f"Cloudflare challenge failed: {error_elem[0].text}")
            except:
                pass
            
            # Wait before checking again
            time.sleep(1)
        
        # Timeout reached
        raise CloudflareError("Cloudflare challenge timed out")

    def get_cookies(self) -> Dict[str, str]:
        """
        Get cookies from the current session.

        Returns:
            Dict[str, str]: Cookies as a dictionary.

        Raises:
            BrowserError: If browser automation fails.
        """
        if not self.driver:
            raise BrowserError("Driver not initialized")

        try:
            cookies_list = self.driver.get_cookies()
            return {cookie["name"]: cookie["value"] for cookie in cookies_list}
        except Exception as e:
            raise BrowserError(f"Failed to get cookies: {e}")

    def get_headers(self) -> Dict[str, str]:
        """
        Get headers from the current session.

        Returns:
            Dict[str, str]: Headers as a dictionary.

        Raises:
            BrowserError: If browser automation fails.
        """
        if not self.driver:
            raise BrowserError("Driver not initialized")

        # Extract user agent
        try:
            user_agent = self.driver.execute_script("return navigator.userAgent")
        except:
            user_agent = self.fingerprint_manager.get_user_agent(self.fingerprint)

        # Basic headers that should be included
        headers = {
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
        }

        return headers

    def close(self) -> None:
        """Close the engine and release resources."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            finally:
                self.driver = None 