import chromadb
from embed_functions import readtextfiles, chunksplitter, getembedding

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

def importdocs(textdocspath, model="nomic-embed-text", chromacollection=None, chunk_size=100 ): 
  if chromacollection is None:
    chromaclient = getclient()
    chromacollection = getcollection(chromaclient)

  print(f"  cf:reading text files from {textdocspath}...")
  text_data = readtextfiles(textdocspath)

  for filename, text in text_data.items():
    print(f"  cf: chuncking {filename}")
    chunks = chunksplitter(text, chunk_size)
    embeds = getembedding(chunks, model)
    print(f"  cf:embeded:{len(embeds)} of {len(chunks)} chunks")
    chunknumber = list(range(len(chunks)))
    ids = [filename + str(index) for index in chunknumber]
    metadatas = [{"source": filename} for index in chunknumber]
    chromacollection.add(ids=ids, documents=chunks, embeddings=embeds, metadatas=metadatas)

  if __name__ == "__main__":
    print(f"testing chroma funtions...")
    importdocs(textdocspath="../data/test")
    print(f"done")

