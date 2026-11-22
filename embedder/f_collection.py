# ABOUTME: Reads the ids of a whole Chroma collection
# ABOUTME: Makes a hash of ids, by which two collections can be compared

import hashlib


def get_all_ids(collection, page_size=5000):
    """
    Reads every id of a collection, page by page.

    :param collection: A Chroma collection.
    :param page_size: The number of ids read at once.
    :return: The sorted list of ids.
    """
    lstIds = []
    while True:
        lstPage = collection.get(limit=page_size, offset=len(lstIds), include=[])["ids"]
        if not lstPage:
            return sorted(lstIds)
        lstIds.extend(lstPage)


def hash_ids(ids):
    """
    Makes a hash of a set of ids that does not depend on their order.

    :param ids: A list of ids.
    :return: The SHA-256 of the sorted ids, one per line, as a hex string.
    """
    return hashlib.sha256("\n".join(sorted(ids)).encode()).hexdigest()
