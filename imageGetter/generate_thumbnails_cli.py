#!/usr/bin/env python
# ABOUTME: CLI tool to generate thumbnails for all images in a directory
# ABOUTME: Processes images from full/ directory and saves thumbnails to thumbs/ directory

import argparse
import sys
from pathlib import Path
from generate_thumbnails import generate_thumbnail
from tqdm import tqdm


def main():
    """Generate thumbnails for all images in input directory"""
    parser = argparse.ArgumentParser(
        description='Generate 200x200px center-cropped thumbnails from images'
    )
    parser.add_argument(
        'input_dir',
        type=str,
        help='Directory containing full-resolution images'
    )
    parser.add_argument(
        'output_dir',
        type=str,
        help='Directory to save thumbnails'
    )
    parser.add_argument(
        '--size',
        type=int,
        default=200,
        help='Thumbnail size in pixels (default: 200)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of images to process (for testing)'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force regeneration of existing thumbnails (default: skip existing)'
    )

    args = parser.parse_args()

    # Convert to Path objects
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)

    # Validate input directory
    if not input_dir.exists():
        print(f"Error: Input directory does not exist: {input_dir}")
        sys.exit(1)

    if not input_dir.is_dir():
        print(f"Error: Input path is not a directory: {input_dir}")
        sys.exit(1)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Get all image files (common extensions)
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    image_files = []
    for ext in image_extensions:
        image_files.extend(input_dir.glob(f'*{ext}'))
        image_files.extend(input_dir.glob(f'*{ext.upper()}'))

    # Sort for consistent ordering
    image_files = sorted(set(image_files))

    # Apply limit if specified
    if args.limit:
        image_files = image_files[:args.limit]

    if not image_files:
        print(f"No image files found in {input_dir}")
        sys.exit(0)

    print(f"Found {len(image_files)} images to process")
    print(f"Input:  {input_dir.absolute()}")
    print(f"Output: {output_dir.absolute()}")
    print()

    # Process images
    success_count = 0
    skipped_count = 0
    failed_count = 0

    for img_path in tqdm(image_files, desc="Generating thumbnails", unit="img"):
        # Generate thumbnail filename
        thumb_name = img_path.stem + "_thumb.jpg"
        thumb_path = output_dir / thumb_name

        # Skip if thumbnail exists (unless --force flag set)
        if not args.force and thumb_path.exists():
            skipped_count += 1
            continue

        # Generate thumbnail
        result = generate_thumbnail(str(img_path), str(thumb_path), intSize=args.size)

        if result:
            success_count += 1
        else:
            failed_count += 1

    # Print summary
    print()
    print("=" * 50)
    print("Summary:")
    print(f"  Total images:  {len(image_files)}")
    print(f"  Successful:    {success_count}")
    if skipped_count > 0:
        print(f"  Skipped:       {skipped_count}")
    if failed_count > 0:
        print(f"  Failed:        {failed_count}")
    print("=" * 50)

    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
