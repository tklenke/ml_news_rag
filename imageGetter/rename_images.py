# ABOUTME: Renames downloaded images and their thumbnails to local names that hold the attachment id
# ABOUTME: Each file on disk takes the name of the first index entry that has its present name (D51)

import os
from collections import defaultdict
from pathlib import Path
from typing import Dict, Set, Tuple
from urllib.parse import urlparse
from extract_image_urls import generate_filename


def thumbnail_name(strLocalFilename: str) -> str:
    """Name of the thumbnail of a picture, as generate_thumbnails_cli writes it."""
    return strLocalFilename.rsplit('.', 1)[0] + '_thumb.jpg'


def count_shared_names(dctIndex: Dict) -> Tuple[int, int]:
    """
    Count present local names that more than one attachment had.

    Attachments are told apart by their attachment id, so one attachment
    linked twice (with different query strings) does not count as sharing.

    Returns:
        (names shared, attachments that shared them)
    """
    dctAttachments = defaultdict(set)
    for dctEntry in dctIndex.values():
        for dctImage in dctEntry.get("images", []):
            strAttachmentId = urlparse(dctImage["url"]).path.split('/')[-2]
            dctAttachments[dctImage.get("local_filename", "")].add(strAttachmentId)
    lstShared = [setIds for setIds in dctAttachments.values() if len(setIds) > 1]
    return len(lstShared), sum(len(setIds) for setIds in lstShared)


def plan_renames(dctIndex: Dict, setPresentNames: Set[str]) -> Dict[str, str]:
    """
    Choose the new name of each file on disk.

    The index is walked in its order. A file takes the name of the first entry
    whose present local_filename is its name, since that entry is the one that
    was downloaded; later entries with the same present name get nothing.

    Args:
        dctIndex: Image index keyed by message id, with the present local_filename in each image
        setPresentNames: Names of the files on disk

    Returns:
        Dict of present name to new name, in index order
    """
    dctRenames = {}
    for strMessageId, dctEntry in dctIndex.items():
        for dctImage in dctEntry.get("images", []):
            strPresent = dctImage.get("local_filename", "")
            if strPresent in setPresentNames and strPresent not in dctRenames:
                dctRenames[strPresent] = generate_filename(strMessageId, dctImage["url"], dctImage["part"])
    return dctRenames


def apply_renames(dctRenames: Dict[str, str], strFullDir: str, strThumbsDir: str) -> Tuple[int, int]:
    """
    Rename pictures and their thumbnails.

    Every new name is checked first; if any is already taken, nothing is renamed.

    Args:
        dctRenames: Dict of present name to new name
        strFullDir: Directory of the pictures
        strThumbsDir: Directory of the thumbnails

    Returns:
        (pictures renamed, thumbnails renamed)

    Raises:
        FileExistsError: A new name is already taken
    """
    pathFull = Path(strFullDir)
    pathThumbs = Path(strThumbsDir)

    lstMoves = []
    lstTargets = []
    for strPresent, strNew in dctRenames.items():
        lstMoves.append((pathFull / strPresent, pathFull / strNew))
        pathThumb = pathThumbs / thumbnail_name(strPresent)
        pathNewThumb = pathThumbs / thumbnail_name(strNew)
        if pathThumb.exists():
            lstMoves.append((pathThumb, pathNewThumb))
        # A thumbnail already under the new name would be taken for this picture's
        lstTargets += [pathFull / strNew, pathNewThumb]

    lstTaken = [str(pathTarget) for pathTarget in lstTargets if pathTarget.exists()]
    if lstTaken:
        raise FileExistsError(f"New names already taken, nothing renamed: {', '.join(lstTaken)}")

    intPictures = 0
    intThumbs = 0
    for pathSource, pathTarget in lstMoves:
        os.rename(pathSource, pathTarget)
        if pathSource.parent == pathFull:
            intPictures += 1
        else:
            intThumbs += 1
    return intPictures, intThumbs
