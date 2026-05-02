---
name: cf-ares
description: Use CF-Ares library to bypass Cloudflare protection. Covers engine selection (curl/browser), proxy setup, fingerprint configuration, session management, and troubleshooting. Trigger when: (1) user needs to scrape Cloudflare-protected sites, (2) user asks about CF bypass, TLS fingerprinting, or anti-bot, (3) user wants to configure AresClient, (4) user encounters Cloudflare challenge errors, (5) any mention of 'cf-ares', 'Cloudflare bypass', 'undetected chromedriver', 'curl_cffi'.
---

# CF-Ares Skill

CF-Ares is a two-stage Cloudflare bypass framework: curl_cffi for TLS fingerprinting + lazy browser engine for JS challenges.

## Quick Start

```python
from cf_ares import AresClient

# Basic usage — curl engine only, zero browser overhead
with AresClient() as client:
    r = client.get("https://example.com")
    print(r.status_code, r.text)
```

## Engine Selection

| Scenario | Engine | Code |
|----------|--------|------|
| Most sites (TLS only) | auto (default) | `AresClient()` |
| Heavy JS challenge | undetected | `AresClient(browser_engine="undetected")` |
| Debugging | seleniumbase | `AresClient(browser_engine="seleniumbase")` |

## Configuration Patterns

### Proxy
```python
client = AresClient(proxy="http://user:pass@host:port")
# or socks5://, or None
```

### Fingerprint
```python
client = AresClient(fingerprint="chrome_120")
# Maps to curl_cffi impersonate="chrome120"
```

### Headless / Visible
```python
client = AresClient(headless=True)   # servers/CI
client = AresClient(headless=False)  # debugging
```

### Chrome Path
```python
client = AresClient(chrome_path="/usr/bin/google-chrome-stable")
```

## Session Management

```python
# Save session after challenge
client.solve_challenge("https://protected.com")
client.save_session("session.json")

# Load in another script
new_client = AresClient()
new_client.load_session("session.json")
r = new_client.get("https://protected.com/api")
```

## Error Handling

```python
from cf_ares import CloudflareChallengeFailed, CloudflareSessionExpired

try:
    r = client.solve_challenge("https://protected.com")
except CloudflareChallengeFailed:
    # Browser couldn't solve — try different engine or proxy
    client = AresClient(browser_engine="undetected", proxy=new_proxy)
    r = client.solve_challenge("https://protected.com")
except CloudflareSessionExpired:
    # Cookies expired — re-challenge
    client.solve_challenge("https://protected.com")
```

## Architecture (Lazy Browser Init)

```
AresClient.get() 
  → _initialize() → CurlEngine only
  → curl request 
  → detect CF challenge? 
    → No → return ✅
    → Yes → lazy init BrowserEngine → solve → retry ✅
```

Browser engine is **never** initialized for sites that curl_cffi can handle.

## Troubleshooting

See [references/troubleshooting.md](references/troubleshooting.md) for:
- ChromeDriver version mismatch
- Linux headless setup
- Timeout issues
- Challenge failures

## API Reference

See [references/api.md](references/api.md) for complete API docs.

## Scripts

- `scripts/detect_cf.py` — detect if a site uses Cloudflare protection
- `scripts/test_engine.py` — test which engine works for a target site
