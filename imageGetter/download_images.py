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
from tqdm import tqdm


def create_selenium_driver():
    """
    Create Selenium WebDriver connected to Chrome debug port.

    Requires Chrome to be running with: chrome.exe --remote-debugging-port=9222
    Chrome instance must be logged into Google Groups.

    Returns:
        WebDriver instance connected to existing Chrome session
    """

    service = Service(executable_path='C:\\Users\\tom\\Documents\\projects\\chromedriver-win64\\chromedriver.exe')
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


def download_batch(strIndexPath: str, strOutputDir: str, intLimit: Optional[int] = None, seleniumDriver=None) -> Dict[str, int]:
    """
    Download all images from image index with progress tracking.

    Checks Content-Length before downloading and skips images < 3KB (tracking pixels/emojis).
    Updates index with size_bytes and too_small flag for each image.
    Skips images that already exist in the output directory (resume functionality).
    Displays progress stats every 100 images and saves index periodically.

    Args:
        strIndexPath: Path to image_index.json file
        strOutputDir: Directory to save downloaded images
        intLimit: Optional limit on number of images to download
        seleniumDriver: Optional Selenium driver (for testing). If None, creates new one.

    Returns:
        Dict with statistics: {"total": int, "success": int, "failed": int, "skipped": int, "too_small": int}
    """
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
        "skipped": 0,
        "too_small": 0
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
            seleniumDriver = create_selenium_driver()
            boolCloseDriver = True
        except Exception as e:
            print(f"Failed to create Selenium driver: {e}")
            # Mark all as failed
            dctStats["failed"] = dctStats["total"]
            return dctStats

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

        # Check Content-Length before downloading
        intSizeBytes = None
        boolTooSmall = False
        try:
            response = requests.head(strUrl, timeout=5)
            if 'Content-Length' in response.headers:
                intSizeBytes = int(response.headers['Content-Length'])
                # Skip images smaller than 3KB (likely tracking pixels or emojis)
                if intSizeBytes < 3072:  # 3KB = 3072 bytes
                    boolTooSmall = True
                    dctStats["too_small"] += 1
                    # Update index
                    dctImageRef["size_bytes"] = intSizeBytes
                    dctImageRef["too_small"] = True
                    continue
        except Exception:
            # If HEAD request fails, proceed with download anyway
            pass

        # Download image
        boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=seleniumDriver, intRetries=3)

        # Update index with size and too_small flag
        dctImageRef["size_bytes"] = intSizeBytes
        dctImageRef["too_small"] = boolTooSmall

        if boolSuccess:
            dctStats["success"] += 1
            # Update size with actual file size if we didn't get it from HEAD
            if intSizeBytes is None and pathOutputFile.exists():
                dctImageRef["size_bytes"] = pathOutputFile.stat().st_size
        else:
            dctStats["failed"] += 1

        # Increment processed counter
        intProcessedCount += 1

        # Display stats every 100 images and save index
        if intProcessedCount % 100 == 0:
            print(f"\n--- Progress Update ({intProcessedCount}/{dctStats['total']}) ---")
            print(f"  Success: {dctStats['success']}")
            print(f"  Too small: {dctStats['too_small']}")
            print(f"  Skipped: {dctStats['skipped']}")
            print(f"  Failed: {dctStats['failed']}")
            print()

            # Save index
            with open(strIndexPath, 'w', encoding='utf-8') as f:
                json.dump(dctIndex, f, indent=2, ensure_ascii=False)

    # Save final index
    with open(strIndexPath, 'w', encoding='utf-8') as f:
        json.dump(dctIndex, f, indent=2, ensure_ascii=False)

    # Close driver if we created it
    if boolCloseDriver:
        try:
            seleniumDriver.quit()
        except:
            pass

    return dctStats
