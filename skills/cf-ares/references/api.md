# API Reference

## AresClient

### Constructor
```python
AresClient(
    browser_engine="auto",    # "auto" | "undetected" | "seleniumbase"
    headless=True,
    fingerprint=None,         # "chrome_110" | "chrome_120" | "firefox_120" | "safari_17"
    proxy=None,               # "http://user:pass@host:port"
    timeout=30,
    max_retries=3,
    debug=False,
    chrome_path=None,
    use_edge=False,
)
```

### HTTP Methods
```python
.get(url, params=None, headers=None, **kwargs) -> AresResponse
.post(url, data=None, json=None, headers=None, **kwargs) -> AresResponse
.put(url, data=None, headers=None, **kwargs) -> AresResponse
.delete(url, headers=None, **kwargs) -> AresResponse
.head(url, headers=None, **kwargs) -> AresResponse
.options(url, headers=None, **kwargs) -> AresResponse
.patch(url, data=None, headers=None, **kwargs) -> AresResponse
```

### Cloudflare Challenge
```python
.solve_challenge(url, max_retries=3) -> AresResponse
```

### Session Management
```python
.get_session_info(url=None) -> dict          # cookies, headers, timestamp
.set_session_info(session_info, url=None)    # set cookies/headers
.save_session(file_path, url=None)           # persist to JSON
.load_session(file_path)                     # restore from JSON
```

### Properties
```python
.cookies -> dict     # current curl engine cookies
.headers -> dict     # current curl engine headers
```

### Context Manager
```python
with AresClient() as client:
    r = client.get("https://example.com")
    # auto close
```

## AresResponse

| Attribute | Type | Description |
|-----------|------|-------------|
| status_code | int | HTTP status |
| headers | dict | Response headers |
| cookies | dict | Response cookies |
| content | bytes | Raw body |
| text | str | Decoded body |
| url | str | Final URL |

Methods:
```python
.json() -> Any
```

## Exceptions

```python
AresError                    # base
CloudflareError             # CF related
CloudflareChallengeFailed   # browser couldn't solve
CloudflareSessionExpired    # cookies expired
RequestError                # curl request failed
```
