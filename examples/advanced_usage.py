"""
Advanced usage example for CF-Ares.
"""

import time
from cf_ares import AresClient


def main():
    """Demonstrate advanced usage of CF-Ares."""
    # Create a client with custom settings
    client = AresClient(
        browser_engine="undetected",  # Use undetected-chromedriver for better evasion
        headless=False,               # Show browser for debugging
        fingerprint="chrome_120",     # Use Chrome 120 fingerprint
        proxy="http://user:pass@host:port",  # Use a proxy (replace with actual proxy)
        timeout=60,                   # Longer timeout for challenging sites
        max_retries=5,                # More retries for reliability
        debug=True,                   # Enable debug logging
    )

    try:
        # Visit a heavily protected site
        print("Visiting heavily protected site...")
        response = client.get("https://example.com")  # Replace with an actual CF-protected site
        
        print(f"Status code: {response.status_code}")
        
        # Extract and print some data from the response
        if response.status_code == 200:
            print("Successfully bypassed protection!")
            
            # Parse and use the response data
            if "application/json" in response.headers.get("Content-Type", ""):
                data = response.json()
                print(f"Received JSON data: {data}")
            else:
                # Extract title as an example
                title = response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else 'No title'
                print(f"Page title: {title}")
        
        # Demonstrate session reuse for high-performance requests
        print("\nDemonstrating session reuse for high-performance requests...")
        start_time = time.time()
        
        for i in range(10):
            resp = client.get(f"https://example.com/api/endpoint?page={i}")  # Replace with actual API endpoint
            print(f"Request {i+1} status: {resp.status_code}")
        
        elapsed = time.time() - start_time
        print(f"Completed 10 requests in {elapsed:.2f} seconds (avg: {elapsed/10:.2f}s per request)")
        
        # Demonstrate POST request with JSON data
        print("\nDemonstrating POST request...")
        post_response = client.post(
            "https://example.com/api/submit",  # Replace with actual API endpoint
            json={
                "username": "test_user",
                "action": "test_action",
                "timestamp": time.time()
            },
            headers={"X-Custom-Header": "CustomValue"}
        )
        
        print(f"POST response status: {post_response.status_code}")
        if post_response.status_code == 200:
            print(f"POST response data: {post_response.json()}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Always close the client to release resources
        client.close()
        print("\nClient closed and resources released.")


if __name__ == "__main__":
    main() 