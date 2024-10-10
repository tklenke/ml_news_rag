import os
import re
import ollama
import time

def readtextfile(path):
  text_contents = {}

  with open(path, "r", encoding="utf-8") as file:
    content = file.read()

  text_contents[path] = content

  return text_contents


def chunksplitter(text, chunk_size=100):
  words = re.findall(r'\S+', text)

  chunks = []
  current_chunk = []
  word_count = 0

  for word in words:
    current_chunk.append(word)
    word_count += 1

    if word_count >= chunk_size:
      chunks.append(' '.join(current_chunk))
      current_chunk = []
      word_count = 0

  if current_chunk:
    chunks.append(' '.join(current_chunk))

  return chunks

def getembedding(chunks, model):
  #print(f"  ef:embeding with {model}")
  t0 = time.time()
  embeds = ollama.embed(model, input=chunks)
  t1 = time.time()-t0
  #print(f"  ef:done {t1 } secs")
  return embeds.get('embeddings', [])


