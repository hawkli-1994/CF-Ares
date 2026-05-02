# Troubleshooting Reference

## ChromeDriver Version Mismatch

**Error:**
```
session not created: This version of ChromeDriver only supports Chrome version 148
Current browser version is 147.0.7727.137
```

**Fix:**
```bash
pip install --upgrade undetected-chromedriver
# or specify chrome path
client = AresClient(chrome_path="/usr/bin/google-chrome-stable")
```

## Linux Headless — No Display

**Error:**
```
WebDriverException: unknown error: Chrome failed to start
```

**Fix:**
```bash
# Install xvfb
sudo apt-get install xvfb

# Run with xvfb
xvfb-run python script.py
```

## Request Timeout

**Error:**
```
TimeoutError: Timed out receiving message from renderer
```

**Fix:**
```python
client = AresClient(timeout=60, headless=True)
```

## Challenge Failed

**Symptoms:** `CloudflareChallengeFailed` or infinite challenge loop

**Checklist:**
1. Chrome version ≥ 130 (`google-chrome --version`)
2. Proxy not blacklisted (test with `curl -x proxy url`)
3. Site uses Turnstile/CAPTCHA? → Use `browser_engine="undetected"`
4. Try visible mode: `headless=False`

## curl_cffi Import Error

**Error:**
```
ModuleNotFoundError: No module named 'curl_cffi'
```

**Fix:**
```bash
pip install --upgrade cf-ares
# or explicitly
pip install curl_cffi
```

## AttributeError on CurlEngine

**Error:**
```
AttributeError: 'CurlEngine' object has no attribute 'get_cookies'
```

**Fix:** Upgrade to cf-ares ≥ 0.1.1
```bash
pip install --upgrade cf-ares
```
