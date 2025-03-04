"""
Basic usage example for CF-Ares.
"""

from cf_ares import AresClient


def main():
    """Demonstrate basic usage of CF-Ares."""
    # Create a client with default settings
    client = AresClient(
        browser_engine="auto",  # Automatically choose the best engine
        headless=True,          # Run browser in headless mode
        timeout=30,             # Set timeout to 30 seconds
    )

    try:
        # Visit a Cloudflare-protected site
        print("Visiting Cloudflare-protected site...")
        response = client.get("https://example.com")  # Replace with an actual CF-protected site
        
        print(f"Status code: {response.status_code}")
        print(f"Title: {response.text.split('<title>')[1].split('</title>')[0] if '<title>' in response.text else 'No title'}")
        
        # Make additional requests using the same session
        print("\nMaking additional requests...")
        for i in range(3):
            resp = client.get(f"https://example.com/page/{i+1}")  # Replace with actual URLs
            print(f"Request {i+1} status: {resp.status_code}")
    
    finally:
        # Always close the client to release resources
        client.close()


if __name__ == "__main__":
    main() 