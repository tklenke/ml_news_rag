# ABOUTME: Downloads images from Google Groups URLs using authenticated Selenium
# ABOUTME: Handles retry logic, validation, and progress tracking for batch downloads

import time
from pathlib import Path
from typing import Optional
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_selenium_driver():
    """
    Create Selenium WebDriver connected to Chrome debug port.

    Requires Chrome to be running with: chrome.exe --remote-debugging-port=9222
    Chrome instance must be logged into Google Groups.

    Returns:
        WebDriver instance connected to existing Chrome session
    """
    service = Service(executable_path='../../chromedriver-win64/chromedriver.exe')
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def download_image(strUrl: str, strOutputPath: str, seleniumDriver=None, intRetries: int = 3) -> bool:
    """
    Download a single image from URL using Selenium.

    Args:
        strUrl: Full image URL (Google Groups attachment)
        strOutputPath: Local filesystem path to save image
        seleniumDriver: Optional Selenium driver (for testing). If None, creates new one.
        intRetries: Number of retry attempts (default 3)

    Returns:
        True if successful, False otherwise
    """
    # Create output directory if needed
    pathOutput = Path(strOutputPath)
    pathOutput.parent.mkdir(parents=True, exist_ok=True)

    # Use provided driver or create new one
    boolCloseDriver = False
    if seleniumDriver is None:
        try:
            seleniumDriver = create_selenium_driver()
            boolCloseDriver = True
        except Exception as e:
            print(f"Failed to create Selenium driver: {e}")
            return False

    # Attempt download with retries
    for intAttempt in range(intRetries):
        try:
            # Navigate to image URL
            seleniumDriver.get(strUrl)

            # Wait for page to load
            time.sleep(2)

            # Get page source and check if it's an image
            # Google Groups might display image directly or embed it
            try:
                # Try to find img tag with the actual image
                imgElement = seleniumDriver.find_element(By.TAG_NAME, "img")
                strSrc = imgElement.get_attribute("src")

                # If it's a data URL, extract the image
                if strSrc.startswith("data:image"):
                    import base64
                    # Extract base64 data
                    strData = strSrc.split(",")[1]
                    bytesData = base64.b64decode(strData)

                    # Save to file
                    with open(strOutputPath, 'wb') as f:
                        f.write(bytesData)
                else:
                    # It's a regular URL - download it
                    import requests
                    response = requests.get(strSrc)
                    with open(strOutputPath, 'wb') as f:
                        f.write(response.content)

            except Exception:
                # If no img tag, try to get the page content directly
                # (sometimes Google Groups serves the image directly)
                strPageSource = seleniumDriver.page_source

                # Check if this looks like binary image data
                if len(strPageSource) > 100 and not strPageSource.strip().startswith("<"):
                    # Might be raw image - save it
                    with open(strOutputPath, 'wb') as f:
                        f.write(strPageSource.encode('latin1'))
                else:
                    # Not an image - might need different approach
                    raise Exception("Could not extract image from page")

            # Validate image
            try:
                img = Image.open(strOutputPath)
                img.verify()  # Verify it's a valid image
                img.close()

                # Success!
                if boolCloseDriver:
                    seleniumDriver.quit()
                return True

            except Exception as e:
                # Invalid image
                if Path(strOutputPath).exists():
                    Path(strOutputPath).unlink()
                raise Exception(f"Downloaded file is not a valid image: {e}")

        except Exception as e:
            print(f"Download attempt {intAttempt + 1}/{intRetries} failed: {e}")
            if intAttempt < intRetries - 1:
                time.sleep(2 ** intAttempt)  # Exponential backoff
            continue

    # All retries failed
    if boolCloseDriver:
        try:
            seleniumDriver.quit()
        except:
            pass

    return False
