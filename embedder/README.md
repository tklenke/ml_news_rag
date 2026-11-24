<!-- ABOUTME: How to embed the year's new threads into the site's collection on this machine -->
<!-- ABOUTME: The yearly steps come first; the earlier notes on the embedder follow -->

# embedder

## Yearly Update

Written 2026-11-24 for the next run, about a year later. Read it from the top; every step
says where it is run, what to type, what you should see and what to do if you do not.

### What this step is for

The site answers from a Chroma collection of chunks of text (250 words each), with a vector
for each made by Ollama's `nomic-embed-text`. This step adds the threads fetched this year
(`msgGetter`) to that collection on your machine and checks it. Copying it to the server is
in the top-level `README.md`. Nothing is embedded on the server.

- The collection is `nomic-embed-text` in the local Chroma of `site_2024`, stored in
  `/home/tom/projects/site_2024/data/chroma`. The local containers `chroma-rag` (port 8000)
  and `ollama-rag` (port 11434) of `site_2024` serve it.
- The embedder reads every `.txt` under `data/msgs`, `data/news`, `data/aeroelectric` and
  `data/cozybuilders` (`embedder_settings.py`), and embeds those not listed in
  `embedder/embedstatus.txt`. A file is listed there once it is stored.
- A refetched thread (one with new replies, `msgGetter` step 5) already has chunks; they are
  deleted first, and the thread is embedded again.

**Check before you start:** the chunk size and the collection may have changed since this
was written (Phase 2 of the 2026 plan tests other chunk sizes). If `embedder_settings.py` no
longer says `CHUNKSIZE = 250`, or the site's settings name another collection, stop: these
steps were written for the collection as it is on 2026-11-24.

In 2026, for scale: 227 new threads gave 727 chunks in 7 minutes (1.9 s a thread); 8
refetched threads, 57 old chunks deleted and 99 new ones. The collection went from 41,507 to
42,276 chunks of 11,388 files.

All steps are in a WSL terminal.

### Before you start

1. **The messages are fetched and checked:** `msgGetter/README.md`, "Yearly Update", up to
   step 9. `data/refetch_ids.txt` exists (it may be empty).
   ```bash
   cd ~/projects/ml
   wc -l < data/refetch_ids.txt
   ```
2. **The server's collection was checked against yours,** before anything here changes it:
   top-level `README.md`, step 3. `~/update_records/before.txt` holds the line it recorded.
   ```bash
   cat ~/update_records/before.txt
   ```
3. **The local containers run and have the model:**
   ```bash
   cd ~/projects/site_2024
   docker compose ps
   docker compose exec -T ollama-rag ollama list
   ```
   `ps` lists `site_2024-chroma-rag-1` and `site_2024-ollama-rag-1` as `Up`; if not,
   `docker compose up -d chroma-rag ollama-rag`. `ollama list` shows `nomic-embed-text:latest`;
   if not, `docker compose exec ollama-rag ollama pull nomic-embed-text`. Run 2026-11-24.
4. **The WSL Python of the project** is `/home/tom/projects/ml/venv`; the commands call it
   as `../venv/bin/python` from `embedder`.

### Step 1: delete the old chunks of the refetched threads

Skip if `data/refetch_ids.txt` is empty.

```bash
cd ~/projects/ml/embedder
cp embedstatus.txt ~/update_records/embedstatus_before.txt
../venv/bin/python - ../data/refetch_ids.txt <<'PY'
import sys, chromadb
col = chromadb.HttpClient('localhost', '8000').get_collection('nomic-embed-text')
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
n = 0
for i in ids:
    k = len(col.get(where={'source': i}, include=[])['ids'])
    col.delete(where={'source': i}); n += k
print(n, 'chunks deleted of', len(ids), 'threads;', col.count(), 'left')
PY
grep -v -x -F -f ../data/refetch_ids.txt ~/update_records/embedstatus_before.txt > embedstatus.txt
wc -l < ~/update_records/embedstatus_before.txt; wc -l < embedstatus.txt
```

- It prints the chunks deleted (2026: 57 for 8 threads, before their new posts were added).
- The two counts differ by the number of threads in `refetch_ids.txt`.
- Rehearsed 2026-11-24 on a throwaway Chroma: 7 chunks of 2 threads deleted and embedded
  again, the same count after. The counting half was run on the real collection
  (it would have deleted 99 chunks of the 8 threads of 2026).

### Step 2: embed

```bash
cd ~/projects/ml/embedder
../venv/bin/python embedder.py | tee ~/update_records/embed.log
```

- First lines: `Embed:nomic-embed-text has <n> objects`, `Total embeddable files:`, `Files
  embedded:` and `Net to complete:` (the new threads plus the refetched ones; 2026: 227 and
  then 8).
- Then `embedding file: ...` for each, and every 10 a line with the files to go.
- The end: `-----STATS------` with `Failed: 0` and `Size of Collection`.
- It can be stopped (Ctrl+C) and run again; it goes on with what is not in `embedstatus.txt`.
  A file that fails prints `FAILED` and is tried again by the next run; 20 failures in a row
  end the run (then Ollama or Chroma is the problem: "Before you start", 3).
- Run 2026-11-22 like this; its output is in `data/corpus_update/embed_new.log`.

### Step 3: check the collection

1. Record the collection as it is now. The server must show this line after the deploy.
   ```bash
   cd ~/projects/ml/embedder
   ../venv/bin/python - <<'PY' | tee ~/update_records/after.txt
   import chromadb
   from f_collection import get_all_ids, hash_ids
   col = chromadb.HttpClient('localhost', '8000').get_collection('nomic-embed-text')
   print(col.count(), hash_ids(get_all_ids(col)))
   PY
   ```
   The count is `before.txt`'s plus the chunks added, minus step 1's. (Run 2026-11-24:
   `42276 92d43eed...`.)
2. Every file is embedded: `Total embeddable files` of step 2 and the lines of
   `embedstatus.txt` are the same number:
   ```bash
   wc -l < embedstatus.txt
   ```
3. On the local site, http://127.0.0.1:8001/, ask about the subject of one of this year's
   new threads (open one in `data/msgs_md` to pick it). The thread is listed among the
   sources of the answer. Keep the question: it is asked again on the server.

### Next: back to the top-level README

The packing and the copy of the collection to the server are in the top-level `README.md`.

### Troubleshooting

Each case says whether it was seen.

- **The embedder fails on every file** (not seen): Ollama or Chroma is not answering; check
  "Before you start", 3.
- **The answer does not list the new thread** (not seen): check the thread's `.txt` is not
  empty, and that its id is in `embedstatus.txt`.

## Background: the embedder (earlier notes)

# Embed Technical Corpus

Script will embed a corpus of test data via one embedding model and store 
the vector data into a ChromaDB. Script will build a list of documents to embed and start
embedding each file.  the order of files will be random, but a list will be kept such
that the script can be stopped and restarted saving progress.

## Workflow

### Set up Docker Containers

Build two docker containers required.  One for the ChromaDB and one for Ollama and the embedding models.
ChromaDB will store data persistantly and Ollama will download relevant models for embedding and 
answer testing.  Start docker desktop. Run the docker-compose from the parent directory using Windows Command prompt. 

```
docker-compose build
docker-compose up -d
docker-compose ps
docker exec modeltesting-ollama-1 ollama list
```
*might need to confirm the name of the ollama container for the list*

### Ensure python has required libraries
```
pip install -r requirements. txt
```

### Run the Embedder
```
python embedder.py
```

Without parameters it embeds into the production collection with the settings of
`embedder_settings.py`. With a collection of another name it takes a chunk size, an overlap
and ports, and lists the embedded files in `data/chunk_experiment/`:
```
python embedder.py --collection words400_overlap80 --chunk-size 400 --overlap 80 \
    --chroma-port 8010 --ollama-port 11998
```
A file that fails is printed with `FAILED` and the traceback, and is tried again by the next
run. 20 failures in a row end the run.
