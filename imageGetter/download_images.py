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
            # Check if URL has &view=1 (returns HTML wrapper with embedded image)
            if '&view=1' in strUrl or '?view=1' in strUrl:
                # HTML wrapper approach - use Selenium to parse HTML
                seleniumDriver.get(strUrl)
                time.sleep(2)

                # Parse HTML to extract real image URL from <img src>
                imgElement = seleniumDriver.find_element(By.TAG_NAME, "img")
                strSrc = imgElement.get_attribute("src")

                # Download from the extracted src URL
                response = requests.get(strSrc)
                with open(strOutputPath, 'wb') as f:
                    f.write(response.content)
            else:
                # Direct binary download approach - use requests with cookies
                # Extract cookies from Selenium session for authentication
                dctCookies = {}
                for cookie in seleniumDriver.get_cookies():
                    dctCookies[cookie['name']] = cookie['value']

                # Download directly with requests (avoids Chrome Downloads folder)
                response = requests.get(strUrl, cookies=dctCookies)
                with open(strOutputPath, 'wb') as f:
                    f.write(response.content)

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
    # Open debug log file
    fileDebug = open('download_debug.log', 'w', encoding='utf-8')
    fileDebug.write("=== Image Download Debug Log ===\n\n")

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

    # Track file sizes to detect duplicate downloads
    intLastFileSize = None
    strLastFilename = None

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
            fileDebug.write(f"\n[HEAD] {strLocalFilename}\n")
            fileDebug.write(f"  URL: {strUrl}\n")
            fileDebug.write(f"  Status: {response.status_code}\n")
            fileDebug.write(f"  Content-Length present: {'Content-Length' in response.headers}\n")

            # Log all headers for debugging
            fileDebug.write(f"  All headers:\n")
            for strHeader, strValue in response.headers.items():
                fileDebug.write(f"    {strHeader}: {strValue}\n")

            if 'Content-Length' in response.headers:
                intSizeBytes = int(response.headers['Content-Length'])
                fileDebug.write(f"  Content-Length: {intSizeBytes} bytes ({intSizeBytes / 1024:.2f} KB)\n")

                # Skip images smaller than 3KB (likely tracking pixels or emojis)
                if intSizeBytes < 3072:  # 3KB = 3072 bytes
                    boolTooSmall = True
                    dctStats["too_small"] += 1
                    fileDebug.write(f"  DECISION: SKIPPED - Too small (< 3KB)\n")
                    # Update index
                    dctImageRef["size_bytes"] = intSizeBytes
                    dctImageRef["too_small"] = True
                    fileDebug.flush()  # Ensure written to disk
                    continue
                else:
                    fileDebug.write(f"  DECISION: Size OK, proceeding with download\n")
            else:
                fileDebug.write(f"  DECISION: Content-Length not available, proceeding with download\n")

            fileDebug.flush()  # Ensure written to disk
        except Exception as e:
            # If HEAD request fails, proceed with download anyway
            fileDebug.write(f"\n[HEAD] {strLocalFilename}\n")
            fileDebug.write(f"  URL: {strUrl}\n")
            fileDebug.write(f"  HEAD request failed: {e}\n")
            fileDebug.write(f"  DECISION: Proceeding with download anyway\n")
            fileDebug.flush()  # Ensure written to disk
            pass

        # Download image
        boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=seleniumDriver, intRetries=3)

        # Update index with size and too_small flag
        dctImageRef["size_bytes"] = intSizeBytes
        dctImageRef["too_small"] = boolTooSmall

        if boolSuccess:
            dctStats["success"] += 1
            # Get actual file size from downloaded file
            if pathOutputFile.exists():
                intActualSize = pathOutputFile.stat().st_size
                dctImageRef["size_bytes"] = intActualSize

                # Check for duplicate file sizes (potential problem)
                if intLastFileSize is not None and intActualSize == intLastFileSize and strLocalFilename != strLastFilename:
                    fileDebug.write(f"\n⚠️  WARNING: Duplicate file size detected!\n")
                    fileDebug.write(f"  Previous: {strLastFilename} ({intLastFileSize} bytes)\n")
                    fileDebug.write(f"  Current:  {strLocalFilename} ({intActualSize} bytes)\n")
                    fileDebug.write(f"  This may indicate the same image was downloaded twice.\n")
                    fileDebug.flush()
                    print(f"\n⚠️  WARNING: Duplicate file size!")
                    print(f"  {strLastFilename} and {strLocalFilename} both {intActualSize} bytes")

                # Update tracking
                intLastFileSize = intActualSize
                strLastFilename = strLocalFilename
        else:
            dctStats["failed"] += 1

        # Increment processed counter
        intProcessedCount += 1

        # Display stats every 100 images and save index
        if intProcessedCount % 10 == 0:
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

    # Close debug log
    fileDebug.write(f"\n=== Download Complete ===\n")
    fileDebug.write(f"Total: {dctStats['total']}\n")
    fileDebug.write(f"Success: {dctStats['success']}\n")
    fileDebug.write(f"Too small: {dctStats['too_small']}\n")
    fileDebug.write(f"Skipped: {dctStats['skipped']}\n")
    fileDebug.write(f"Failed: {dctStats['failed']}\n")
    fileDebug.close()

    # Close driver if we created it
    if boolCloseDriver:
        try:
            seleniumDriver.quit()
        except:
            pass

    return dctStats
