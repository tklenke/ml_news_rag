import os, re, time
import chromadb, ollama
from f_misc import get_id_from_path, get_filepaths_list



def readtextfile(path):
  text_contents = {}
  with open(path, "r", encoding="utf-8") as file:
    content = file.read()
  text_contents[path] = content
  return text_contents

class Embedder():
    def __init__(self, chromahost="localhost", chromaport='8000', \
                ollamahost="localhost", ollamaport="11434"):
        self.ollamaclient = ollama.Client(f"http://{ollamahost}:{ollamaport}")
        self.chromaclient = chromadb.HttpClient(chromahost, chromaport)
        #set initial model,prefix and collection to defaults, which can be changed
        #after init if need be
        self.set_collection()
        self.set_model()
        self.set_prefix()
        self.set_chunk_size()

    def set_collection(self, dbname="defaultdb", initialize=False):
      print(f"embdr:opening {dbname}...")
      if initialize:
          if any(dbname == collection.name for collection in self.chromaclient.list_collections()):
            print(f"embdr:found duplicate collection {dbname}. Removing...")
            self.chromaclient.delete_collection(dbname)
      self.chromacollection = self.chromaclient.get_or_create_collection(dbname, metadata={"hnsw:space": "cosine"}  )
      return
    
    def set_model(self, model="nomic-embed-text"):
      self.model = model
      return
      
    def set_prefix(self, prefix=""):
      self.prefix=prefix
      return
    
    def set_chunk_size(self, chunk_size=100):
      self.chunk_size = chunk_size
      return
    
    def get_collection_count(self):
      return (self.chromacollection.count())

    def get_embedding(self, chunks):
      #print(f"  ef:embeding with {model}")
      t0 = time.time()
      embeds = self.ollamaclient.embed(self.model, input=chunks)
      t1 = time.time()-t0
      #print(f"  ef:done {t1 } secs")
      return embeds.get('embeddings', [])
    
    def get_chroma_get(self):
      return self.chromacollection.get(include=["documents","metadatas"])
    
    def chunksplitter(self, text):
      words = re.findall(r'\S+', text)

      chunks = []
      current_chunk = [self.prefix]
      word_count = 0

      for word in words:
        current_chunk.append(word)
        word_count += 1

        if word_count >= self.chunk_size:
          chunks.append(' '.join(current_chunk))
          current_chunk = [self.prefix]
          word_count = 0

      if current_chunk:
        chunks.append(' '.join(current_chunk))

      return chunks

    def embed_file(self, textdocspath): 
      text_data = readtextfile(textdocspath)

      for filename, text in text_data.items():
        chunks = self.chunksplitter(text)
        if len(chunks) == 0:
          print(f"  zero chunks, skipping embed")
          continue
        #else:
        #  print(f"{textdocspath} {len(chunks)} chunks {self.chunk_size}")
        embeds = self.get_embedding(chunks)
        chunknumber = list(range(len(chunks)))
        ids = [get_id_from_path(filename) + str(index) for index in chunknumber]
        metadatas = [{"source": filename} for index in chunknumber]
        self.chromacollection.add(ids=ids, documents=chunks, embeddings=embeds, metadatas=metadatas)
      return


if __name__ == "__main__":  
  print(f"testing embed funtions...")
  files = get_filepaths_list("../data/test_min")
  embdr = Embedder()

  embdr.set_prefix("prefix:")
  embdr.set_chunk_size(75)
  for file in files:
    embdr.embed_file(textdocspath=file)
  print(f"Collection count: {embdr.get_collection_count()}")

  #below will print out all the records in the db...so be careful or you'll get a 
  # screen full!
  #r = embdr.get_chroma_get()
  #for rec in r:
  #  print(f"{rec}")
  #  print(f"{r[rec]}")

  print(f"done")