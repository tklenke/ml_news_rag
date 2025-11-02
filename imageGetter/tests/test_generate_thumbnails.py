# ABOUTME: Tests for thumbnail generation - center crop and resize to 200x200px
# ABOUTME: Validates image dimensions, format, and quality of generated thumbnails

import pytest
import os
from pathlib import Path
from PIL import Image
import tempfile
import shutil

# Import from parent directory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from generate_thumbnails import generate_thumbnail


class TestThumbnailGeneration:
    """Test thumbnail generation with center crop and resize"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test outputs"""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)

    def test_generate_thumbnail_200x200(self, temp_dir):
        """Test thumbnail is exactly 200x200 pixels"""
        # Create a simple test image instead of using real file
        test_img_path = os.path.join(temp_dir, "test_input.jpg")
        img = Image.new('RGB', (300, 300), color='red')
        img.save(test_img_path)

        output_path = os.path.join(temp_dir, "thumb.jpg")
        result = generate_thumbnail(test_img_path, output_path, intSize=200)

        assert result == True
        assert os.path.exists(output_path)

        thumb = Image.open(output_path)
        assert thumb.size == (200, 200)
        thumb.close()

    def test_center_crop_landscape_image(self, temp_dir):
        """Test that landscape images are center-cropped"""
        # Create a test landscape image (400x200)
        test_img_path = os.path.join(temp_dir, "landscape.jpg")
        img = Image.new('RGB', (400, 200), color='red')
        # Add a blue vertical stripe in center to verify centering
        for x in range(180, 220):
            for y in range(200):
                img.putpixel((x, y), (0, 0, 255))
        img.save(test_img_path)

        output_path = os.path.join(temp_dir, "thumb.jpg")
        result = generate_thumbnail(test_img_path, output_path, intSize=200)

        assert result == True
        thumb = Image.open(output_path)
        assert thumb.size == (200, 200)

        # Center pixel should be blue (from center stripe)
        center_pixel = thumb.getpixel((100, 100))
        assert center_pixel[2] > 200  # Blue channel dominant
        thumb.close()

    def test_center_crop_portrait_image(self, temp_dir):
        """Test that portrait images are center-cropped"""
        # Create a test portrait image (200x400)
        test_img_path = os.path.join(temp_dir, "portrait.jpg")
        img = Image.new('RGB', (200, 400), color='red')
        # Add a green horizontal stripe in center
        for y in range(180, 220):
            for x in range(200):
                img.putpixel((x, y), (0, 255, 0))
        img.save(test_img_path)

        output_path = os.path.join(temp_dir, "thumb.jpg")
        result = generate_thumbnail(test_img_path, output_path, intSize=200)

        assert result == True
        thumb = Image.open(output_path)
        assert thumb.size == (200, 200)

        # Center pixel should be green (from center stripe)
        center_pixel = thumb.getpixel((100, 100))
        assert center_pixel[1] > 200  # Green channel dominant
        thumb.close()

    def test_handle_square_image(self, temp_dir):
        """Test that square images are simply resized"""
        # Create a test square image (400x400)
        test_img_path = os.path.join(temp_dir, "square.jpg")
        img = Image.new('RGB', (400, 400), color='blue')
        img.save(test_img_path)

        output_path = os.path.join(temp_dir, "thumb.jpg")
        result = generate_thumbnail(test_img_path, output_path, intSize=200)

        assert result == True
        thumb = Image.open(output_path)
        assert thumb.size == (200, 200)
        thumb.close()

    def test_handle_small_image(self, temp_dir):
        """Test that small images (<200x200) are upscaled"""
        # Create a small image (100x100)
        test_img_path = os.path.join(temp_dir, "small.jpg")
        img = Image.new('RGB', (100, 100), color='yellow')
        img.save(test_img_path)

        output_path = os.path.join(temp_dir, "thumb.jpg")
        result = generate_thumbnail(test_img_path, output_path, intSize=200)

        assert result == True
        thumb = Image.open(output_path)
        assert thumb.size == (200, 200)
        thumb.close()

    def test_save_thumbnail_as_jpeg(self, temp_dir):
        """Test that thumbnail is saved as JPEG"""
        test_img_path = os.path.join(temp_dir, "test.png")
        img = Image.new('RGB', (300, 300), color='purple')
        img.save(test_img_path)

        output_path = os.path.join(temp_dir, "thumb.jpg")
        result = generate_thumbnail(test_img_path, output_path, intSize=200)

        assert result == True
        thumb = Image.open(output_path)
        assert thumb.format == 'JPEG'
        thumb.close()
