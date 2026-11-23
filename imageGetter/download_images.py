# ABOUTME: Downloads images from Google Groups URLs using authenticated Selenium
# ABOUTME: Handles retry logic, validation, and progress tracking for batch downloads

import time
import json
import requests
from pathlib import Path
from typing import Optional, Dict
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm


# Seconds a request or a page load may take before the attempt fails
DEFAULT_TIMEOUT_SECONDS = 60


def create_selenium_driver(strChromedriverPath: str, fltTimeout: float = DEFAULT_TIMEOUT_SECONDS):
    """
    Create Selenium WebDriver connected to Chrome debug port.

    Requires Chrome to be running with: chrome.exe --remote-debugging-port=9222
    Chrome instance must be logged into Google Groups.

    Args:
        strChromedriverPath: Path of chromedriver.exe
        fltTimeout: Seconds a page may take to load

    Returns:
        WebDriver instance connected to existing Chrome session
    """

    service = Service(executable_path=strChromedriverPath)
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(fltTimeout)
    return driver


def fetch_to_file(strUrl: str, strOutputPath: str, dctCookies: Optional[Dict], fltTimeout: float):
    """
    Fetch a URL and write the response body to a file.

    Raises:
        requests.RequestException: The request failed or took longer than fltTimeout
        Exception: The response status is not 200; nothing is written
    """
    response = requests.get(strUrl, cookies=dctCookies, timeout=fltTimeout)
    if response.status_code != 200:
        raise Exception(f"HTTP status {response.status_code}")
    with open(strOutputPath, 'wb') as f:
        f.write(response.content)

def download_image(strUrl: str, strOutputPath: str, seleniumDriver=None, intRetries: int = 3, dctCookies: Optional[Dict] = None,
                   fltTimeout: float = DEFAULT_TIMEOUT_SECONDS, strChromedriverPath: Optional[str] = None) -> bool:
    """
    Download a single image from URL using Selenium.

    Args:
        strUrl: Full image URL (Google Groups attachment)
        strOutputPath: Local filesystem path to save image
        seleniumDriver: Optional Selenium driver (for testing). If None, creates new one.
        intRetries: Number of retry attempts (default 3)
        dctCookies: Optional pre-extracted cookies dict for direct binary downloads
        fltTimeout: Seconds each request may take
        strChromedriverPath: Path of chromedriver.exe, used when no driver is given

    Returns:
        True if successful, False otherwise; a failed download leaves no file
    """
    # Create output directory if needed
    pathOutput = Path(strOutputPath)
    pathOutput.parent.mkdir(parents=True, exist_ok=True)

    # Use provided driver or create new one
    boolCloseDriver = False
    if seleniumDriver is None:
        try:
            seleniumDriver = create_selenium_driver(strChromedriverPath, fltTimeout)
            boolCloseDriver = True
        except Exception as e:
            print(f"Failed to create Selenium driver: {e}")
            return False

    # Attempt download with retries
    for intAttempt in range(intRetries):
        try:
            # Check if URL has &view=1 (returns HTML wrapper with embedded image)
            if '&view=1' in strUrl or '?view=1' in strUrl:
                # HTML wrapper approach - use Selenium to parse HTML
                seleniumDriver.get(strUrl)

                # Wait for img element to be present (up to 10 seconds)
                wait = WebDriverWait(seleniumDriver, 10)
                imgElement = wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
                strSrc = imgElement.get_attribute("src")

                # Download from the extracted src URL
                fetch_to_file(strSrc, strOutputPath, None, fltTimeout)
            else:
                # Direct binary download approach - use requests with cookies
                # Use provided cookies or extract from Selenium session
                if dctCookies is None:
                    dctCookies = {}
                    for cookie in seleniumDriver.get_cookies():
                        dctCookies[cookie['name']] = cookie['value']

                # Download directly with requests (avoids Chrome Downloads folder)
                fetch_to_file(strUrl, strOutputPath, dctCookies, fltTimeout)

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
            # A failed attempt leaves no file behind
            if Path(strOutputPath).exists():
                Path(strOutputPath).unlink()
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


def download_batch(strIndexPath: str, strOutputDir: str, intLimit: Optional[int] = None, seleniumDriver=None,
                   strChromedriverPath: Optional[str] = None, strLogPath: Optional[str] = None,
                   fltTimeout: float = DEFAULT_TIMEOUT_SECONDS) -> Dict[str, int]:
    """
    Download all images from image index with progress tracking.

    Skips images that already exist in the output directory (resume functionality).
    Displays progress stats every 10 images and saves index periodically.

    Args:
        strIndexPath: Path to image_index.json file
        strOutputDir: Directory to save downloaded images
        intLimit: Optional limit on number of images to download
        seleniumDriver: Optional Selenium driver (for testing). If None, creates new one.
        strChromedriverPath: Path of chromedriver.exe, used when no driver is given
        strLogPath: Optional log file; lists each failed download and the totals
        fltTimeout: Seconds each request may take

    Returns:
        Dict with statistics: {"total": int, "success": int, "failed": int, "skipped": int}
    """
    # Open log file if one is given
    fileLog = None
    if strLogPath is not None:
        fileLog = open(strLogPath, 'w', encoding='utf-8')
        fileLog.write("=== Image Download Log ===\n\n")

    # Load image index
    with open(strIndexPath, 'r', encoding='utf-8') as f:
        dctIndex = json.load(f)

    # Collect all images from all messages (with reference to original dict for updates)
    lstAllImages = []
    for strMessageId, dctEntry in dctIndex.items():
        for dctImage in dctEntry["images"]:
            lstAllImages.append({
                "message_id": strMessageId,
                "url": dctImage["url"],
                "local_filename": dctImage["local_filename"],
                "image_ref": dctImage  # Reference to update size_bytes and too_small
            })

    # Apply limit if specified
    if intLimit is not None:
        lstAllImages = lstAllImages[:intLimit]

    # Initialize statistics
    dctStats = {
        "total": len(lstAllImages),
        "success": 0,
        "failed": 0,
        "skipped": 0
    }

    # Counter for periodic stats display and index saving
    intProcessedCount = 0

    # Create output directory
    pathOutputDir = Path(strOutputDir)
    pathOutputDir.mkdir(parents=True, exist_ok=True)

    # Create driver if not provided
    boolCloseDriver = False
    if seleniumDriver is None:
        try:
            seleniumDriver = create_selenium_driver(strChromedriverPath, fltTimeout)
            boolCloseDriver = True
        except Exception as e:
            print(f"Failed to create Selenium driver: {e}")
            # Mark all as failed
            dctStats["failed"] = dctStats["total"]
            if fileLog is not None:
                fileLog.write(f"Failed to create Selenium driver: {e}\n")
                fileLog.close()
            return dctStats

    # Extract cookies once at the beginning (for direct binary downloads)
    # Try to get cookies from current page first (Chrome is already logged in)
    print("Extracting authentication cookies from Chrome session...")
    dctCookies = {}
    try:
        # Try getting cookies from current page first
        lstCookies = seleniumDriver.get_cookies()
        for cookie in lstCookies:
            dctCookies[cookie['name']] = cookie['value']
        print(f"Extracted {len(dctCookies)} cookies from current page")

        # If no cookies found, navigate to Google Groups to get them
        if len(dctCookies) == 0:
            print("No cookies found, navigating to groups.google.com...")
            seleniumDriver.get("https://groups.google.com")
            time.sleep(2)  # Wait for page to load
            lstCookies = seleniumDriver.get_cookies()
            for cookie in lstCookies:
                dctCookies[cookie['name']] = cookie['value']
            print(f"Extracted {len(dctCookies)} cookies after navigation")
    except Exception as e:
        print(f"Warning: Failed to extract cookies: {e}")
        print("Will attempt to download without pre-extracted cookies (slower)")
        dctCookies = None  # Signal to extract cookies per-image

    # Download each image with progress bar
    for dctImageInfo in tqdm(lstAllImages, desc="Downloading images", unit="image"):
        strUrl = dctImageInfo["url"]
        strLocalFilename = dctImageInfo["local_filename"]
        strOutputPath = str(pathOutputDir / strLocalFilename)
        dctImageRef = dctImageInfo["image_ref"]

        # Skip if file already exists (resume functionality)
        pathOutputFile = Path(strOutputPath)
        if pathOutputFile.exists():
            dctStats["skipped"] += 1
            continue

        # Download image
        boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=seleniumDriver, intRetries=3, dctCookies=dctCookies,
                                     fltTimeout=fltTimeout)

        if boolSuccess:
            dctStats["success"] += 1
        else:
            dctStats["failed"] += 1
            if fileLog is not None:
                fileLog.write(f"FAILED {strLocalFilename} {strUrl}\n")
                fileLog.flush()

        # Increment processed counter
        intProcessedCount += 1

        # Display stats every 10 images and save index
        if intProcessedCount % 10 == 0:
            print(f"\n--- Progress Update ({intProcessedCount}/{dctStats['total']}) ---")
            print(f"  Success: {dctStats['success']}")
            print(f"  Skipped: {dctStats['skipped']}")
            print(f"  Failed: {dctStats['failed']}")
            print()

            # Save index
            with open(strIndexPath, 'w', encoding='utf-8') as f:
                json.dump(dctIndex, f, indent=1, ensure_ascii=False)

    # Save final index
    with open(strIndexPath, 'w', encoding='utf-8') as f:
        json.dump(dctIndex, f, indent=1, ensure_ascii=False)

    # Close log
    if fileLog is not None:
        fileLog.write(f"\n=== Download Complete ===\n")
        fileLog.write(f"Total: {dctStats['total']}\n")
        fileLog.write(f"Success: {dctStats['success']}\n")
        fileLog.write(f"Skipped: {dctStats['skipped']}\n")
        fileLog.write(f"Failed: {dctStats['failed']}\n")
        fileLog.close()

    # Close driver if we created it
    if boolCloseDriver:
        try:
            seleniumDriver.quit()
        except:
            pass

    return dctStats
