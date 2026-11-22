# ABOUTME: Repairs the chunks of a collection without changing the ids it holds
# ABOUTME: Adds chunks missing from a source and replaces vectors Ollama does not reproduce

import os
from collections import Counter

import numpy as np

from f_collection import get_all_ids
from f_embed import readtextfile
from f_misc import get_chunk_id, get_id_from_path, get_ids_list_from_file

# A chunk with fewer characters than this cannot have more than 512 tokens
MIN_CHARACTERS = 513
MIN_COSINE = 0.999
PAGE_SIZE = 100


def add_missing_chunks(embdr, path):
    """
    Adds the chunks of a file that are not stored under its source.

    :param embdr: An Embedder set to the collection, model, prefix and chunk size.
    :param path: The path of the file.
    :return: The number of chunks added.
    """
    source = get_id_from_path(path)
    dctStored = embdr.chromacollection.get(where={"source": source}, include=["documents"])
    cntStored = Counter(dctStored["documents"])
    intAdded = 0
    for intNumber, chunk in enumerate(embdr.chunksplitter(readtextfile(path)[path])):
        if cntStored[chunk] > 0:
            cntStored[chunk] -= 1
            continue
        embdr.chromacollection.add(ids=[get_chunk_id(source, intNumber)], documents=[chunk],
                                   embeddings=embdr.get_embedding([chunk]),
                                   metadatas=[{"source": source}])
        intAdded += 1
    return intAdded


def get_cosine(vector1, vector2):
    """Returns the cosine of the angle between two vectors."""
    return float(np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2)))


def refresh_vectors(embdr, donefile):
    """
    Embeds every long chunk of a collection again and replaces the vectors that differ.

    :param embdr: An Embedder set to the collection and model.
    :param donefile: The file of the ids already checked; it is continued.
    :return: The number of chunks checked and the number of vectors replaced.
    """
    setDone = set(get_ids_list_from_file(donefile)) if os.path.exists(donefile) else set()
    lstIds = [id for id in get_all_ids(embdr.chromacollection) if id not in setDone]
    intChecked = 0
    intReplaced = 0
    for intStart in range(0, len(lstIds), PAGE_SIZE):
        dctRows = embdr.chromacollection.get(ids=lstIds[intStart:intStart + PAGE_SIZE],
                                             include=["documents", "embeddings"])
        for id, document, vector in zip(dctRows["ids"], dctRows["documents"],
                                        dctRows["embeddings"]):
            if len(document) >= MIN_CHARACTERS:
                intChecked += 1
                current = embdr.get_embedding([document])[0]
                if get_cosine(vector, current) < MIN_COSINE:
                    embdr.chromacollection.update(ids=[id], embeddings=[current])
                    intReplaced += 1
        with open(donefile, "a") as f:
            f.writelines(id + "\n" for id in dctRows["ids"])
        print(f"To go: {max(len(lstIds) - intStart - PAGE_SIZE, 0)} Checked: {intChecked} "
              f"Replaced: {intReplaced}", flush=True)
    return intChecked, intReplaced
