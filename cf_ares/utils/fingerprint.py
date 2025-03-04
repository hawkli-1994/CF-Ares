"""
Fingerprint management utilities for CF-Ares.
"""

import json
import os
import random
from typing import Dict, List, Optional, Union


class FingerprintManager:
    """
    Manages browser fingerprints for different engines.
    Provides methods to generate and customize fingerprints.
    """

    # Common user agents for different browsers and versions
    USER_AGENTS = {
        "chrome_120": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "chrome_119": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "firefox_120": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "firefox_119": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
        "edge_120": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
        "safari_17": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    }

    def __init__(self, fingerprint_dir: Optional[str] = None):
        """
        Initialize the fingerprint manager.

        Args:
            fingerprint_dir: Directory to store fingerprint data.
        """
        self.fingerprint_dir = fingerprint_dir or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "data", "fingerprints"
        )
        os.makedirs(self.fingerprint_dir, exist_ok=True)
        self.current_fingerprint: Optional[str] = None

    def get_user_agent(self, browser_type: Optional[str] = None) -> str:
        """
        Get a user agent string.

        Args:
            browser_type: Browser type to get user agent for.

        Returns:
            str: User agent string.
        """
        if browser_type and browser_type in self.USER_AGENTS:
            return self.USER_AGENTS[browser_type]
        
        # Return a random user agent if no specific type is requested
        return random.choice(list(self.USER_AGENTS.values()))

    def load_fingerprint(self, name: str) -> Dict:
        """
        Load a fingerprint from file.

        Args:
            name: Name of the fingerprint to load.

        Returns:
            Dict: Fingerprint data.
        """
        filepath = os.path.join(self.fingerprint_dir, f"{name}.json")
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
        
        # Return a default fingerprint if the requested one doesn't exist
        return self.generate_fingerprint(name)

    def save_fingerprint(self, name: str, data: Dict) -> None:
        """
        Save a fingerprint to file.

        Args:
            name: Name of the fingerprint to save.
            data: Fingerprint data to save.
        """
        filepath = os.path.join(self.fingerprint_dir, f"{name}.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    def generate_fingerprint(self, browser_type: Optional[str] = None) -> Dict:
        """
        Generate a new fingerprint.

        Args:
            browser_type: Browser type to generate fingerprint for.

        Returns:
            Dict: Generated fingerprint data.
        """
        # Get user agent
        user_agent = self.get_user_agent(browser_type)
        
        # Generate basic fingerprint data
        fingerprint = {
            "userAgent": user_agent,
            "screenResolution": random.choice([
                [1920, 1080],
                [2560, 1440],
                [1366, 768],
                [1440, 900],
                [1536, 864],
            ]),
            "availableScreenResolution": [1920, 1040],
            "timezoneOffset": random.choice([-480, -420, -360, -300, -240, -180, 0, 60, 120, 180, 240, 300, 360, 480]),
            "languages": ["en-US", "en"],
            "webgl_vendor": "Google Inc. (NVIDIA)",
            "webgl_renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3070 Direct3D11 vs_5_0 ps_5_0, D3D11)",
            "audio_fingerprint": random.uniform(0.1, 0.9),
            "canvas_fingerprint": random.randint(1000000000, 9999999999),
        }
        
        # Set the current fingerprint
        self.current_fingerprint = browser_type or "custom"
        
        return fingerprint

    def get_fingerprint(self, name: Optional[str] = None) -> Dict:
        """
        Get a fingerprint by name.

        Args:
            name: Name of the fingerprint to get.

        Returns:
            Dict: Fingerprint data.
        """
        if name:
            return self.load_fingerprint(name)
        
        if self.current_fingerprint:
            return self.load_fingerprint(self.current_fingerprint)
        
        # Generate a random fingerprint if no name is specified
        return self.generate_fingerprint()

    def get_tls_fingerprint(self, browser_type: Optional[str] = None) -> Dict:
        """
        Get TLS fingerprint settings for curl_cffi.

        Args:
            browser_type: Browser type to get TLS fingerprint for.

        Returns:
            Dict: TLS fingerprint settings.
        """
        # Default to Chrome 120 TLS settings
        tls_fingerprint = {
            "h2": True,
            "grease": True,
            "supported_signature_algorithms": [
                "ecdsa_secp256r1_sha256",
                "rsa_pss_rsae_sha256",
                "rsa_pkcs1_sha256",
                "ecdsa_secp384r1_sha384",
                "rsa_pss_rsae_sha384",
                "rsa_pkcs1_sha384",
                "rsa_pss_rsae_sha512",
                "rsa_pkcs1_sha512",
            ],
            "supported_versions": ["GREASE", "1.3", "1.2"],
            "key_share_curves": ["GREASE", "x25519"],
            "cert_compression_algo": "brotli",
            "record_size_limit": 16385,
            "additional_extensions": ["extended_master_secret", "renegotiation_info"],
        }
        
        return tls_fingerprint 