#!/usr/bin/env python3
"""Detect if a site uses Cloudflare protection."""
import sys
import argparse
from curl_cffi import requests


def detect_cf(url: str, timeout: int = 15) -> dict:
    """Detect Cloudflare protection on a site."""
    result = {
        "url": url,
        "has_cf": False,
        "indicators": [],
        "status_code": None,
        "recommendation": "",
    }
    
    try:
        r = requests.get(url, impersonate="chrome120", timeout=timeout)
        result["status_code"] = r.status_code
        
        headers = dict(r.headers)
        text = r.text.lower()
        
        # Check CF headers
        if "cf-ray" in str(headers).lower():
            result["has_cf"] = True
            result["indicators"].append("CF-Ray header")
        
        if "cf-cache-status" in str(headers).lower():
            result["has_cf"] = True
            result["indicators"].append("CF-Cache-Status header")
        
        # Check challenge page
        if r.status_code in (403, 503):
            result["has_cf"] = True
            result["indicators"].append(f"Status {r.status_code}")
        
        challenge_markers = [
            "cf-browser-verification",
            "cf-im-under-attack",
            "challenge platform",
            "just a moment",
            "turnstile",
        ]
        for marker in challenge_markers:
            if marker in text:
                result["has_cf"] = True
                result["indicators"].append(f"Body marker: {marker}")
        
        # Recommendation
        if not result["has_cf"]:
            result["recommendation"] = "No Cloudflare detected. Use standard requests."
        elif "Body marker" in str(result["indicators"]):
            result["recommendation"] = "CF JS challenge detected. Use AresClient(browser_engine='undetected')."
        else:
            result["recommendation"] = "CF CDN detected. AresClient() should work with curl."
            
    except Exception as e:
        result["error"] = str(e)
        result["recommendation"] = f"Request failed: {e}"
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Detect Cloudflare protection")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()
    
    result = detect_cf(args.url, args.timeout)
    
    print(f"URL: {result['url']}")
    print(f"Has Cloudflare: {result['has_cf']}")
    print(f"Status Code: {result.get('status_code', 'N/A')}")
    print(f"Indicators: {', '.join(result['indicators']) or 'None'}")
    print(f"Recommendation: {result['recommendation']}")
    
    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
