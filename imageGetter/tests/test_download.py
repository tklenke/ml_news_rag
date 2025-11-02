# ABOUTME: Unit tests for image download functionality
# ABOUTME: Tests single image download, error handling, retry logic, and validation

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from tempfile import NamedTemporaryFile
import os

# Import function to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from download_images import download_image, create_selenium_driver


class TestDownloadImage:
    """Tests for downloading single image from URL."""

    def test_download_single_image_success(self):
        """Should download image using Selenium and save to file."""
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/test.jpg?part=0.1"

        with NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
            strOutputPath = f.name

        try:
            # Create a real tiny valid JPEG for testing
            from PIL import Image as PILImage
            import io
            img = PILImage.new('RGB', (10, 10), color='red')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            bytesValidJpeg = buffer.getvalue()

            # Create mock Selenium driver
            mockDriver = Mock()
            mockDriver.get = Mock()

            # Mock finding an img element with data URL
            mockImg = Mock()
            import base64
            strBase64 = base64.b64encode(bytesValidJpeg).decode('utf-8')
            mockImg.get_attribute = Mock(return_value=f"data:image/jpeg;base64,{strBase64}")
            mockDriver.find_element = Mock(return_value=mockImg)

            # Download image
            boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=mockDriver)

            # Should succeed
            assert boolSuccess == True
            assert Path(strOutputPath).exists()
            assert Path(strOutputPath).stat().st_size > 0

            # Verify it's a valid image
            img = PILImage.open(strOutputPath)
            assert img.size == (10, 10)
            img.close()

        finally:
            if os.path.exists(strOutputPath):
                os.unlink(strOutputPath)

    def test_handle_download_failure(self):
        """Should return False when download fails."""
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/nonexistent.jpg?part=0.1"

        with NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
            strOutputPath = f.name

        try:
            # Create mock Selenium driver that raises exception
            mockDriver = Mock()
            mockDriver.get = Mock(side_effect=Exception("Page not found"))

            # Download image
            boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=mockDriver, intRetries=1)

            # Should fail gracefully
            assert boolSuccess == False

        finally:
            if os.path.exists(strOutputPath):
                os.unlink(strOutputPath)

    @pytest.mark.skip(reason="TODO: Implement retry test with proper mocking")
    def test_retry_on_failure(self):
        """Should retry specified number of times on failure."""
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/test.jpg?part=0.1"

        with NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
            strOutputPath = f.name

        try:
            # Create mock that fails twice then succeeds
            # mockDriver = Mock()
            # mockDriver.get = Mock(side_effect=[Exception("Timeout"), Exception("Timeout"), None])

            # Download with 3 retries
            # boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=mockDriver, intRetries=3)

            # Should succeed on third try
            # assert boolSuccess == True
            # assert mockDriver.get.call_count == 3

            # RED: This test should fail
            pytest.fail("Function download_image() not yet implemented")
        finally:
            if os.path.exists(strOutputPath):
                os.unlink(strOutputPath)

    @pytest.mark.skip(reason="TODO: Implement validation test")
    def test_validate_image_after_download(self):
        """Should validate downloaded file is a valid image."""
        strUrl = "https://groups.google.com/group/cozy_builders/attach/hash/test.jpg?part=0.1"

        with NamedTemporaryFile(mode='wb', suffix='.jpg', delete=False) as f:
            strOutputPath = f.name
            # Write invalid image data
            f.write(b"<html>Not an image</html>")

        try:
            # Download should fail validation
            # mockDriver = Mock()
            # boolSuccess = download_image(strUrl, strOutputPath, seleniumDriver=mockDriver)

            # Should return False for invalid image
            # assert boolSuccess == False

            # RED: This test should fail
            pytest.fail("Function download_image() not yet implemented")
        finally:
            if os.path.exists(strOutputPath):
                os.unlink(strOutputPath)

    @pytest.mark.skip(reason="TODO: Implement directory creation test")
    def test_create_output_directory_if_needed(self):
        """Should create parent directory if it doesn't exist."""
        import tempfile

        # Create temp directory that we'll delete
        strTempDir = tempfile.mkdtemp()
        strSubDir = os.path.join(strTempDir, "subdir", "images")
        strOutputPath = os.path.join(strSubDir, "test.jpg")

        try:
            # Delete the temp dir
            import shutil
            shutil.rmtree(strTempDir)

            # Directory should not exist
            # assert not Path(strSubDir).exists()

            # Download should create directory
            # mockDriver = Mock()
            # boolSuccess = download_image("http://test.com/img.jpg", strOutputPath, seleniumDriver=mockDriver)

            # Directory should now exist
            # assert Path(strSubDir).exists()

            # RED: This test should fail
            pytest.fail("Function download_image() not yet implemented")
        finally:
            if os.path.exists(strTempDir):
                import shutil
                shutil.rmtree(strTempDir)


class TestSeleniumDriver:
    """Tests for Selenium driver creation."""

    @pytest.mark.skip(reason="Integration test - requires Chrome debug mode running")
    def test_create_selenium_driver(self):
        """Should create Selenium driver connected to Chrome debug port."""
        # This is integration test - will be mocked in unit tests

        # driver = create_selenium_driver()
        # assert driver is not None
        # driver.quit()

        # RED: This test should fail
        pytest.fail("Function create_selenium_driver() not yet implemented")


class TestBatchDownload:
    """Tests for batch downloading multiple images."""

    @patch('download_images.download_image')
    def test_download_batch_basic(self, mock_download_image):
        """Should download multiple images and track progress."""
        import tempfile
        import json

        # Mock download_image to always succeed
        mock_download_image.return_value = True

        # Create minimal image index
        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001", "subject": "Test 1"},
                "images": [
                    {
                        "url": "https://groups.google.com/group/test/attach/hash/img1.jpg?part=0.1",
                        "part": "0.1",
                        "filename": "img1.jpg",
                        "local_filename": "MSG001_part0_1_img1.jpg"
                    }
                ]
            },
            "MSG002": {
                "metadata": {"message_id": "MSG002", "subject": "Test 2"},
                "images": [
                    {
                        "url": "https://groups.google.com/group/test/attach/hash/img2.jpg?part=0.1",
                        "part": "0.1",
                        "filename": "img2.jpg",
                        "local_filename": "MSG002_part0_1_img2.jpg"
                    }
                ]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            # Save index to temp file
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            # Download batch
            from download_images import download_batch

            dctStats = download_batch(
                strIndexPath,
                f"{strTempDir}/images",
                intLimit=None,
                seleniumDriver=Mock()  # Mock driver
            )

            # Should track statistics
            assert dctStats["total"] == 2
            assert dctStats["success"] == 2
            assert dctStats["failed"] == 0

            # Should have called download_image twice
            assert mock_download_image.call_count == 2

    @patch('download_images.download_image')
    def test_download_batch_with_limit(self, mock_download_image):
        """Should respect limit parameter."""
        import tempfile
        import json

        # Mock download_image to always succeed
        mock_download_image.return_value = True

        # Create index with 3 images
        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001"},
                "images": [{"url": "http://test1.jpg", "local_filename": "test1.jpg"}]
            },
            "MSG002": {
                "metadata": {"message_id": "MSG002"},
                "images": [{"url": "http://test2.jpg", "local_filename": "test2.jpg"}]
            },
            "MSG003": {
                "metadata": {"message_id": "MSG003"},
                "images": [{"url": "http://test3.jpg", "local_filename": "test3.jpg"}]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            from download_images import download_batch

            # Download only 2 images
            dctStats = download_batch(
                strIndexPath,
                f"{strTempDir}/images",
                intLimit=2,
                seleniumDriver=Mock()
            )

            # Should only attempt 2 downloads
            assert dctStats["total"] == 2
            assert dctStats["success"] == 2
            assert mock_download_image.call_count == 2

    @patch('download_images.download_image')
    def test_download_batch_continue_on_failure(self, mock_download_image):
        """Should continue downloading even if some images fail."""
        import tempfile
        import json

        # Mock download_image to fail first, succeed second
        mock_download_image.side_effect = [False, True]

        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001"},
                "images": [{"url": "http://test1.jpg", "local_filename": "test1.jpg"}]
            },
            "MSG002": {
                "metadata": {"message_id": "MSG002"},
                "images": [{"url": "http://test2.jpg", "local_filename": "test2.jpg"}]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            from download_images import download_batch

            dctStats = download_batch(
                strIndexPath,
                f"{strTempDir}/images",
                intLimit=None,
                seleniumDriver=Mock()
            )

            # Should attempt both even if one fails
            assert dctStats["total"] == 2
            assert dctStats["success"] == 1
            assert dctStats["failed"] == 1

            # Should have called download_image twice
            assert mock_download_image.call_count == 2

    @patch('download_images.download_image')
    def test_skip_existing_files(self, mock_download_image):
        """Should skip files that already exist in output directory."""
        import tempfile
        import json
        from pathlib import Path

        # Mock download_image to always succeed
        mock_download_image.return_value = True

        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001"},
                "images": [{"url": "http://test1.jpg", "local_filename": "test1.jpg"}]
            },
            "MSG002": {
                "metadata": {"message_id": "MSG002"},
                "images": [{"url": "http://test2.jpg", "local_filename": "test2.jpg"}]
            },
            "MSG003": {
                "metadata": {"message_id": "MSG003"},
                "images": [{"url": "http://test3.jpg", "local_filename": "test3.jpg"}]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            # Create output directory and pre-create test1.jpg (already downloaded)
            strOutputDir = f"{strTempDir}/images"
            Path(strOutputDir).mkdir(parents=True, exist_ok=True)
            Path(f"{strOutputDir}/test1.jpg").write_text("fake image data")

            from download_images import download_batch

            dctStats = download_batch(
                strIndexPath,
                strOutputDir,
                intLimit=None,
                seleniumDriver=Mock()
            )

            # Should have 3 total images
            assert dctStats["total"] == 3
            # Should skip the existing one
            assert dctStats["skipped"] == 1
            # Should download the 2 that don't exist
            assert dctStats["success"] == 2
            assert dctStats["failed"] == 0

            # Should only call download_image twice (not for the existing file)
            assert mock_download_image.call_count == 2


class TestSizeFiltering:
    """Tests for filtering images by size."""

    @patch('download_images.requests.head')
    @patch('download_images.download_image')
    def test_skip_images_smaller_than_3kb(self, mock_download_image, mock_head):
        """Should skip images with Content-Length < 3KB."""
        import tempfile
        import json
        from pathlib import Path

        # Mock HEAD request to return small content-length
        mock_response = Mock()
        mock_response.headers = {'Content-Length': '2048'}  # 2KB
        mock_head.return_value = mock_response

        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001"},
                "images": [{"url": "http://test1.jpg", "local_filename": "test1.jpg"}]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            from download_images import download_batch

            dctStats = download_batch(
                strIndexPath,
                f"{strTempDir}/images",
                intLimit=None,
                seleniumDriver=Mock()
            )

            # Should mark as too_small
            assert dctStats["too_small"] == 1
            # Should not download
            assert mock_download_image.call_count == 0

            # Should update index with size info
            with open(strIndexPath, 'r') as f:
                dctUpdatedIndex = json.load(f)

            dctImageInfo = dctUpdatedIndex["MSG001"]["images"][0]
            assert dctImageInfo["size_bytes"] == 2048
            assert dctImageInfo["too_small"] == True

        # RED: This test should fail
        pytest.fail("Size filtering not yet implemented")

    @patch('download_images.requests.head')
    @patch('download_images.download_image')
    def test_download_images_larger_than_3kb(self, mock_download_image, mock_head):
        """Should download images with Content-Length >= 3KB."""
        import tempfile
        import json

        # Mock HEAD request to return large content-length
        mock_response = Mock()
        mock_response.headers = {'Content-Length': '50000'}  # 50KB
        mock_head.return_value = mock_response

        # Mock successful download
        mock_download_image.return_value = True

        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001"},
                "images": [{"url": "http://test1.jpg", "local_filename": "test1.jpg"}]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            from download_images import download_batch

            dctStats = download_batch(
                strIndexPath,
                f"{strTempDir}/images",
                intLimit=None,
                seleniumDriver=Mock()
            )

            # Should download
            assert dctStats["success"] == 1
            assert dctStats["too_small"] == 0
            assert mock_download_image.call_count == 1

            # Should update index with size info
            with open(strIndexPath, 'r') as f:
                dctUpdatedIndex = json.load(f)

            dctImageInfo = dctUpdatedIndex["MSG001"]["images"][0]
            assert dctImageInfo["size_bytes"] == 50000
            assert dctImageInfo["too_small"] == False

        # RED: This test should fail
        pytest.fail("Size filtering not yet implemented")

    @patch('download_images.requests.head')
    @patch('download_images.download_image')
    def test_handle_missing_content_length(self, mock_download_image, mock_head):
        """Should download if Content-Length header is missing."""
        import tempfile
        import json

        # Mock HEAD request without Content-Length header
        mock_response = Mock()
        mock_response.headers = {}  # No Content-Length
        mock_head.return_value = mock_response

        # Mock successful download
        mock_download_image.return_value = True

        dctIndex = {
            "MSG001": {
                "metadata": {"message_id": "MSG001"},
                "images": [{"url": "http://test1.jpg", "local_filename": "test1.jpg"}]
            }
        }

        with tempfile.TemporaryDirectory() as strTempDir:
            strIndexPath = f"{strTempDir}/index.json"
            with open(strIndexPath, 'w') as f:
                json.dump(dctIndex, f)

            from download_images import download_batch

            dctStats = download_batch(
                strIndexPath,
                f"{strTempDir}/images",
                intLimit=None,
                seleniumDriver=Mock()
            )

            # Should download anyway (can't determine size)
            assert dctStats["success"] == 1
            assert dctStats["too_small"] == 0
            assert mock_download_image.call_count == 1

            # Should record size as null
            with open(strIndexPath, 'r') as f:
                dctUpdatedIndex = json.load(f)

            dctImageInfo = dctUpdatedIndex["MSG001"]["images"][0]
            assert dctImageInfo["size_bytes"] is None
            assert dctImageInfo["too_small"] == False

        # RED: This test should fail
        pytest.fail("Size filtering not yet implemented")
