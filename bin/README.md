# Chrome Binary Directory

This directory is used to store Chrome/Chromium binary files for CF-Ares.

## Supported Binary Names

The following binary names are supported:
- `chrome`
- `google-chrome`
- `chromium`

## How to Set Up

1. Download Chrome/Chromium binary for your platform:
   - For Linux: Download from [Google Chrome](https://www.google.com/chrome/) or [Chromium](https://www.chromium.org/getting-involved/download-chromium/)
   - For Windows: Download from [Google Chrome](https://www.google.com/chrome/) or [Chromium](https://www.chromium.org/getting-involved/download-chromium/)
   - For macOS: Download from [Google Chrome](https://www.google.com/chrome/) or [Chromium](https://www.chromium.org/getting-involved/download-chromium/)

2. Place the binary file in this directory with one of the supported names:
   ```bash
   # For Linux/macOS
   cp /path/to/chrome bin/chrome
   # or
   cp /path/to/google-chrome bin/google-chrome
   # or
   cp /path/to/chromium bin/chromium

   # For Windows
   copy C:\path\to\chrome.exe bin\chrome.exe
   # or
   copy C:\path\to\google-chrome.exe bin\google-chrome.exe
   # or
   copy C:\path\to\chromium.exe bin\chromium.exe
   ```

3. Make the binary executable (Linux/macOS only):
   ```bash
   chmod +x bin/chrome  # or bin/google-chrome or bin/chromium
   ```

## Usage

You can specify the Chrome binary path when creating an AresClient:

```python
from cf_ares import AresClient

# Use default Chrome binary from bin directory
client = AresClient(browser_engine="undetected")

# Or specify custom path
client = AresClient(
    browser_engine="undetected",
    chrome_path="/path/to/your/chrome"
)
```

## Notes

- The binary must be compatible with your operating system
- For Linux, make sure the binary has execute permissions
- The binary should be a complete Chrome/Chromium installation, not just the executable
- If you're using a custom Chrome binary, make sure it's compatible with undetected-chromedriver 