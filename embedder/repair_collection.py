# ABOUTME: Repairs the collection: adds missing chunks, replaces vectors Ollama does not reproduce
# ABOUTME: Usage, from embedder/: python repair_collection.py [Ollama port]; can be continued

import sys

from embedder_settings import CHUNKSIZE, COMPLETEDEMBEDFILE, EMBEDMODEL, EMBED_PREFIX, \
    SOURCEDOCPATHS
from f_embed import Embedder
from f_misc import get_filepaths_list, get_id_from_path, get_ids_list_from_file
from f_repair import add_missing_chunks, refresh_vectors

CHECKEDFILE = "embedstatus_vectors_checked.txt"

strOllamaPort = sys.argv[1] if len(sys.argv) > 1 else "11434"
embdr = Embedder(ollamaport=strOllamaPort)
embdr.set_collection(EMBEDMODEL)
embdr.set_chunk_size(CHUNKSIZE)
embdr.set_model(EMBEDMODEL)
embdr.set_prefix(EMBED_PREFIX)

setEmbedded = set(get_ids_list_from_file(COMPLETEDEMBEDFILE))
intAdded = 0
for directory in SOURCEDOCPATHS:
    for path in get_filepaths_list(directory):
        if get_id_from_path(path) in setEmbedded:
            intMissing = add_missing_chunks(embdr, path)
            if intMissing:
                print(f"{path}: {intMissing} chunks added", flush=True)
            intAdded += intMissing
print(f"Chunks added: {intAdded}", flush=True)

intChecked, intReplaced = refresh_vectors(embdr, CHECKEDFILE)
print(f"Vectors checked: {intChecked} Replaced: {intReplaced}")
