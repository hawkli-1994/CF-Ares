#!/usr/bin/env python3
"""Test which engine works for a target site."""
import sys
import argparse
import time


def test_curl(url: str) -> dict:
    """Test curl_cffi engine."""
    from curl_cffi import requests
    start = time.time()
    try:
        r = requests.get(url, impersonate="chrome120", timeout=15)
        return {
            "engine": "curl_cffi",
            "success": r.status_code == 200,
            "status": r.status_code,
            "time": round(time.time() - start, 2),
            "cf_challenge": any(k in r.text.lower() for k in [
                "cf-browser-verification", "cf-im-under-attack", 
                "challenge platform", "just a moment"
            ]),
        }
    except Exception as e:
        return {"engine": "curl_cffi", "success": False, "error": str(e), "time": round(time.time() - start, 2)}


def test_ares_curl(url: str) -> dict:
    """Test CF-Ares with curl only (no browser)."""
    from cf_ares import AresClient
    start = time.time()
    client = AresClient()
    try:
        r = client.get(url)
        return {
            "engine": "cf-ares (curl)",
            "success": r.status_code == 200,
            "status": r.status_code,
            "time": round(time.time() - start, 2),
            "browser_init": client._browser_engine is not None,
        }
    except Exception as e:
        return {"engine": "cf-ares (curl)", "success": False, "error": str(e), "time": round(time.time() - start, 2)}
    finally:
        client.close()


def test_ares_browser(url: str) -> dict:
    """Test CF-Ares with browser engine."""
    from cf_ares import AresClient
    start = time.time()
    client = AresClient(browser_engine="undetected", headless=True)
    try:
        r = client.solve_challenge(url)
        return {
            "engine": "cf-ares (browser)",
            "success": r.status_code == 200,
            "status": r.status_code,
            "time": round(time.time() - start, 2),
        }
    except Exception as e:
        return {"engine": "cf-ares (browser)", "success": False, "error": str(e), "time": round(time.time() - start, 2)}
    finally:
        client.close()


def main():
    parser = argparse.ArgumentParser(description="Test CF-Ares engines")
    parser.add_argument("url", help="Target URL")
    parser.add_argument("--engines", default="all", help="curl,ares,all")
    args = parser.parse_args()
    
    results = []
    
    if args.engines in ("all", "curl"):
        print("Testing curl_cffi...")
        results.append(test_curl(args.url))
    
    if args.engines in ("all", "ares"):
        print("Testing CF-Ares (curl only)...")
        results.append(test_ares_curl(args.url))
        
        print("Testing CF-Ares (browser)...")
        results.append(test_ares_browser(args.url))
    
    print("\n" + "="*60)
    print(f"{'Engine':<25} {'Status':<10} {'Time':<8} {'Success':<10}")
    print("="*60)
    for r in results:
        success = "✅" if r.get("success") else "❌"
        status = r.get("status", r.get("error", "ERR"))
        print(f"{r['engine']:<25} {str(status):<10} {r['time']:<8} {success:<10}")
    print("="*60)
    
    # Recommend best engine
    for r in results:
        if r.get("success") and r["engine"] == "cf-ares (curl)":
            print(f"\nRecommendation: Use AresClient() — curl handles this site")
            return
        elif r.get("success") and r["engine"] == "cf-ares (browser)":
            print(f"\nRecommendation: Use AresClient(browser_engine='undetected')")
            return
    
    print("\nRecommendation: No engine succeeded. Check proxy or site restrictions.")


if __name__ == "__main__":
    main()
