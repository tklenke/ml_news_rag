# ABOUTME: Measures downloaded images and writes the measures into the image index
# ABOUTME: Size in bytes, width, height and a SHA-256 of the content, for each file on disk not yet measured

import hashlib
from pathlib import Path
from typing import Dict
from PIL import Image


def measure_file(pathFile: Path) -> Dict:
    """
    Measure one file.

    Returns:
        Dict with size_bytes, width, height and content_hash; width and height
        are None when the file is not a picture Pillow can open
    """
    bytesContent = pathFile.read_bytes()
    try:
        with Image.open(pathFile) as img:
            intWidth, intHeight = img.size
    except Exception:
        intWidth, intHeight = None, None
    return {
        "size_bytes": len(bytesContent),
        "width": intWidth,
        "height": intHeight,
        "content_hash": hashlib.sha256(bytesContent).hexdigest(),
    }


def measure_index(dctIndex: Dict, strFullDir: str) -> Dict[str, int]:
    """
    Write measures into each image entry whose file is on disk and has none yet.

    Args:
        dctIndex: Image index keyed by message id; changed in place
        strFullDir: Directory of the pictures

    Returns:
        Counts: measured, already_measured, missing, not_a_picture
    """
    pathFull = Path(strFullDir)
    dctStats = {"measured": 0, "already_measured": 0, "missing": 0, "not_a_picture": 0}
    for dctEntry in dctIndex.values():
        for dctImage in dctEntry.get("images", []):
            if "content_hash" in dctImage:
                dctStats["already_measured"] += 1
                continue
            pathFile = pathFull / dctImage["local_filename"]
            if not pathFile.is_file():
                dctStats["missing"] += 1
                continue
            dctMeasures = measure_file(pathFile)
            dctImage.update(dctMeasures)
            dctStats["measured"] += 1
            if dctMeasures["width"] is None:
                dctStats["not_a_picture"] += 1
    return dctStats
