# Browser Binaries Directory

This directory is used to store browser binary files and WebDrivers for CF-Ares.

## Supported Binary Names

The following binary names are supported for Chrome/Chromium:
- `chrome`
- `google-chrome`
- `chromium`

## Edge WebDriver

CF-Ares also supports Microsoft Edge WebDriver. The WebDriver should be placed in the following location:
```
bin/edgedriver_linux64/msedgedriver
```

## How to Set Up Chrome/Chromium

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

## How to Set Up Edge WebDriver

1. Download Microsoft Edge WebDriver for your platform from [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

2. Create the directory structure and place the WebDriver:
   ```bash
   # For Linux/macOS
   mkdir -p bin/edgedriver_linux64
   cp /path/to/msedgedriver bin/edgedriver_linux64/msedgedriver
   chmod +x bin/edgedriver_linux64/msedgedriver

   # For Windows
   mkdir bin\edgedriver_win64
   copy C:\path\to\msedgedriver.exe bin\edgedriver_win64\msedgedriver.exe
   ```

## Configuring WebDriver Paths

### Default Path Configuration

By default, CF-Ares will look for WebDrivers in the following locations:

1. For Chrome/Chromium:
   - System paths (`/usr/bin/google-chrome`, `/usr/bin/chromium`, etc.)
   - Project bin directory (`bin/chrome`, `bin/google-chrome`, `bin/chromium`)

2. For Edge:
   - Project bin directory (`bin/edgedriver_linux64/msedgedriver` for Linux)
   - Project bin directory (`bin/edgedriver_win64/msedgedriver.exe` for Windows)

### Custom Path Configuration

You can specify custom paths for WebDrivers when creating an AresClient:

```python
from cf_ares import AresClient

# For Chrome/Chromium with custom path
client = AresClient(
    browser_engine="undetected",
    chrome_path="/custom/path/to/chrome"
)

# For Edge WebDriver
client = AresClient(
    browser_engine="undetected",
    use_edge=True
)
```

### Environment Variables

You can also set the following environment variables to configure WebDriver paths:

```bash
# For Chrome/Chromium
export CHROME_BIN="/custom/path/to/chrome"

# For Edge WebDriver (Linux)
export EDGE_DRIVER="/custom/path/to/msedgedriver"

# For Edge WebDriver (Windows)
set EDGE_DRIVER=C:\custom\path\to\msedgedriver.exe
```

Example usage with environment variables:

```python
import os
from cf_ares import AresClient

# Set environment variables in code (optional)
os.environ["CHROME_BIN"] = "/custom/path/to/chrome"
os.environ["EDGE_DRIVER"] = "/custom/path/to/msedgedriver"

# Create client (will use environment variables if set)
client = AresClient(browser_engine="undetected", use_edge=True)
```

## Usage

You can specify the browser type and binary path when creating an AresClient:

```python
from cf_ares import AresClient

# Use default Chrome binary from bin directory
client = AresClient(browser_engine="undetected")

# Use Edge WebDriver
client = AresClient(
    browser_engine="undetected",
    use_edge=True
)

# Or specify custom Chrome path
client = AresClient(
    browser_engine="undetected",
    chrome_path="/path/to/your/chrome"
)

# Or specify both Chrome and Edge WebDriver
client = AresClient(
    browser_engine="undetected",
    chrome_path="/custom/path/to/chrome",
    use_edge=True
)
```

## Troubleshooting WebDriver Issues

If you encounter issues with WebDrivers, try the following:

1. **Check permissions**: Ensure the WebDriver has execute permissions
   ```bash
   chmod +x bin/edgedriver_linux64/msedgedriver
   ```

2. **Check compatibility**: Make sure the WebDriver version matches your browser version

3. **Check path**: Verify the WebDriver path is correct
   ```python
   import os
   print(os.path.exists("/path/to/your/webdriver"))
   ```

4. **Manual testing**: Try running the WebDriver manually to check if it works
   ```bash
   ./bin/edgedriver_linux64/msedgedriver --version
   ```

5. **System dependencies**: Install required system dependencies
   ```bash
   # For Ubuntu/Debian
   sudo apt-get install -y libglib2.0-0 libnss3 libx11-6
   
   # For CentOS/RHEL
   sudo yum install -y glib2 nss libX11
   ```

## Notes

- The binary must be compatible with your operating system
- For Linux, make sure the binary has execute permissions
- The binary should be a complete browser installation, not just the executable
- If you're using a custom Chrome binary, make sure it's compatible with undetected-chromedriver 