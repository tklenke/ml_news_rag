# ABOUTME: Generate 200x200px center-cropped thumbnails from full-resolution images
# ABOUTME: Uses PIL/Pillow for image processing with JPEG output at quality=85

from PIL import Image
import os
from pathlib import Path


def generate_thumbnail(strInputPath: str, strOutputPath: str, intSize: int = 200) -> bool:
    """
    Generate a center-cropped square thumbnail from an image.

    Args:
        strInputPath: Path to source image
        strOutputPath: Path to save thumbnail
        intSize: Target size (default 200x200)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Open image
        img = Image.open(strInputPath)

        # Convert to RGB if needed (handles PNG with transparency, etc.)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Get dimensions
        width, height = img.size

        # Calculate center crop to square
        if width > height:
            # Landscape - crop width
            left = (width - height) // 2
            top = 0
            right = left + height
            bottom = height
        elif height > width:
            # Portrait - crop height
            left = 0
            top = (height - width) // 2
            right = width
            bottom = top + width
        else:
            # Square - no crop needed
            left = 0
            top = 0
            right = width
            bottom = height

        # Crop to square
        img_cropped = img.crop((left, top, right, bottom))

        # Resize to target size
        img_thumbnail = img_cropped.resize((intSize, intSize), Image.Resampling.LANCZOS)

        # Create output directory if needed
        output_dir = os.path.dirname(strOutputPath)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Save as JPEG with quality=85
        img_thumbnail.save(strOutputPath, 'JPEG', quality=85)

        img.close()
        return True

    except Exception as e:
        print(f"Error generating thumbnail for {strInputPath}: {e}")
        return False
