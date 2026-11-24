# ABOUTME: Makes the index the gallery reads from the full image index, its measures and Tom's decisions
# ABOUTME: Drops missing files and removed contents, lists a content once per thread, leaves out empty threads

from pathlib import Path
from typing import Dict, List, Tuple
from rename_images import thumbnail_name


def build_gallery_index(dctIndex: Dict, dctDecisions: Dict[str, str], strFullDir: str) -> Tuple[Dict, Dict[str, int]]:
    """
    Make the gallery index.

    An entry whose file is not on disk is dropped; a content marked remove is dropped;
    a content is listed once per thread and stays in each thread it is in; a thread left
    with no picture is left out. Undecided contents stay. Each picture names its thumbnail.

    Raises:
        ValueError: a file is on disk but its entry has not been measured

    Returns:
        (gallery index in the shape of the full index, counts: threads, pictures,
         removed, missing, repeated_in_thread, undecided_contents)
    """
    pathFull = Path(strFullDir)
    dctGallery = {}
    dctStats = {"threads": 0, "pictures": 0, "removed": 0, "missing": 0, "repeated_in_thread": 0}
    setUndecided = set()
    for strMessageId, dctEntry in dctIndex.items():
        lstImages = []
        setSeen = set()
        for dctImage in dctEntry.get("images", []):
            if not (pathFull / dctImage["local_filename"]).is_file():
                dctStats["missing"] += 1
                continue
            strHash = dctImage.get("content_hash")
            if strHash is None:
                raise ValueError(f"Not measured, measure first: {dctImage['local_filename']}")
            if dctDecisions.get(strHash) == "remove":
                dctStats["removed"] += 1
                continue
            if strHash in setSeen:
                dctStats["repeated_in_thread"] += 1
                continue
            setSeen.add(strHash)
            if strHash not in dctDecisions:
                setUndecided.add(strHash)
            lstImages.append({**dctImage, "thumbnail_filename": thumbnail_name(dctImage["local_filename"])})
        if lstImages:
            dctGallery[strMessageId] = {**dctEntry, "images": lstImages}
            dctStats["pictures"] += len(lstImages)
    dctStats["threads"] = len(dctGallery)
    dctStats["undecided_contents"] = len(setUndecided)
    return dctGallery, dctStats


def thumbnail_filenames(dctGallery: Dict) -> List[str]:
    """
    The thumbnails the gallery index names, sorted, one per picture.

    Raises:
        ValueError: a name holds a line break, so a list of one name per line cannot hold it
    """
    lstNames = sorted(dctImage["thumbnail_filename"]
                      for dctEntry in dctGallery.values() for dctImage in dctEntry["images"])
    for strName in lstNames:
        if "\n" in strName or "\r" in strName:
            raise ValueError(f"Thumbnail name has a line break: {strName!r}")
    return lstNames


def thumbnails_not_on_disk(lstNames: List[str], strThumbsDir: str) -> List[str]:
    """The names of the list that are not a file in strThumbsDir, in the order of the list."""
    return [strName for strName in lstNames if not (Path(strThumbsDir) / strName).is_file()]
