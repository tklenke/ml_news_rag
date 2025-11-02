#!/usr/bin/env python
# ABOUTME: Test script to generate thumbnails for first 10 downloaded images
# ABOUTME: Validates thumbnail generation recipe before processing full corpus

import os
import sys
from pathlib import Path
from generate_thumbnails import generate_thumbnail

# Get first 10 images
full_dir = Path("../data/images/full")
thumbs_dir = Path("../data/images/thumbs")

# Create thumbs directory if needed
thumbs_dir.mkdir(parents=True, exist_ok=True)

# Get first 10 image files
image_files = sorted(list(full_dir.glob("*")))[:10]

print(f"Testing thumbnail generation on {len(image_files)} images...")
print()

success_count = 0
failed_count = 0

for img_path in image_files:
    # Generate thumbnail filename (add _thumb before extension)
    thumb_name = img_path.stem + "_thumb.jpg"
    thumb_path = thumbs_dir / thumb_name

    print(f"Processing: {img_path.name}...")
    result = generate_thumbnail(str(img_path), str(thumb_path))

    if result:
        # Check thumbnail exists and size
        if thumb_path.exists():
            from PIL import Image
            thumb = Image.open(thumb_path)
            size = thumb.size
            file_size_kb = thumb_path.stat().st_size / 1024
            thumb.close()
            print(f"  ✓ Created: {thumb_name} ({size[0]}x{size[1]}, {file_size_kb:.1f}KB)")
            success_count += 1
        else:
            print(f"  ✗ Failed: File not created")
            failed_count += 1
    else:
        print(f"  ✗ Failed: Error during generation")
        failed_count += 1

print()
print(f"Results: {success_count} successful, {failed_count} failed")
print()
print(f"Thumbnails saved to: {thumbs_dir.absolute()}")
