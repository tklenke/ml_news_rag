import chromadb
from embed_functions import readtextfile, chunksplitter, getembedding

def getclient(host="localhost", port="8000"):
  print(f"  cf:opening chroma on {host}:{port}...")
  chromaclient = chromadb.HttpClient(host, port)
  return chromaclient

def getcollection(chromaclient, dbname="defaultdb", initialize=False):
  print(f"  cf:opening {dbname}...")
  if initialize:
      if any(dbname == collection.name for collection in chromaclient.list_collections()):
        print(f"  cf:found duplicate collection {dbname}. Removing...")
        chromaclient.delete_collection(dbname)
  collection = chromaclient.get_or_create_collection(dbname, metadata={"hnsw:space": "cosine"}  )
  return(collection)

#given a full path, return the filename without extension
def get_id(path):
    filename = path.split("/")[-1]

    # Split the filename based on the last dot (.)
    parts = filename.rsplit(".", 1)

    # Check if there's only one part (no extension)
    if len(parts) == 1:
        return filename
    # Otherwise, return the part before the dot
    else:
        return parts[0]


def embed_file(textdocspath, model="nomic-embed-text", chromacollection=None, chunk_size=100 ): 
  if chromacollection is None:
    chromaclient = getclient()
    chromacollection = getcollection(chromaclient)

  text_data = readtextfile(textdocspath)

  for filename, text in text_data.items():
    chunks = chunksplitter(text, chunk_size)
    if len(chunks) == 0:
       print(f"  zero chunks, skipping embed")
       continue
    embeds = getembedding(chunks, model)
    chunknumber = list(range(len(chunks)))
    ids = [get_id(filename) + str(index) for index in chunknumber]
    metadatas = [{"source": filename} for index in chunknumber]
    chromacollection.add(ids=ids, documents=chunks, embeddings=embeds, metadatas=metadatas)

  if __name__ == "__main__":
    print(f"testing chroma funtions...")
    embed_file(textdocspath="../data/test")
    print(f"done")