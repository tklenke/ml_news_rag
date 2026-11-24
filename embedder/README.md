<!-- ABOUTME: How to embed the year's new threads into the site's collection and put it on the server -->
<!-- ABOUTME: The yearly steps come first; the earlier notes on the embedder follow -->

# embedder

## Yearly Update

Written 2026-11-24 for the next run, about a year later. Read it from the top; every step
says where it is run, what to type, what you should see and what to do if you do not.

### What this step is for

The site answers from a Chroma collection of chunks of text (250 words each), with a vector
for each made by Ollama's `nomic-embed-text`. This step adds the threads fetched this year
(`msgGetter`) to that collection on your machine, checks it, and then replaces the server's
collection with it. Nothing is embedded on the server.

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

In 2026, for scale: 227 new threads gave 727 chunks in 7 minutes (1.9 s a thread); 8 refetched threads, 57 old chunks deleted and 99 new ones. The collection went from
41,507 to 42,276 chunks of 11,388 files; the tar of it was 320 MB.

All steps are in a WSL terminal unless they say "server".

### Before you start

1. **The messages are fetched and checked:** `msgGetter/README.md`, "Yearly Update", up to
   step 8. `data/refetch_ids.txt` exists (it may be empty).
   ```bash
   cd ~/projects/ml
   wc -l < data/refetch_ids.txt
   ```
2. **The local containers run and have the model:**
   ```bash
   cd ~/projects/site_2024
   docker compose ps
   docker compose exec -T ollama-rag ollama list
   ```
   `ps` lists `site_2024-chroma-rag-1` and `site_2024-ollama-rag-1` as `Up`; if not,
   `docker compose up -d chroma-rag ollama-rag`. `ollama list` shows `nomic-embed-text:latest`;
   if not, `docker compose exec ollama-rag ollama pull nomic-embed-text`.
3. **The WSL Python of the project** is `/home/tom/projects/ml/venv`; the commands call it
   as `../venv/bin/python` from `embedder`.

Run 2026-11-24.

### Step 1: record the collection as it is now (WSL)

```bash
mkdir -p ~/chroma_deploy
cd ~/projects/ml/embedder
../venv/bin/python - <<'PY' | tee ~/chroma_deploy/before.txt
import chromadb
from f_collection import get_all_ids, hash_ids
col = chromadb.HttpClient('localhost', '8000').get_collection('nomic-embed-text')
print(col.count(), hash_ids(get_all_ids(col)))
PY
```

It prints the number of chunks and a hash of all their ids. On 2026-11-24:
`42276 92d43eedddf498273275f0d2f0765d4c4da14e826ac43c60ce94f06e945be4a6`.

### Step 2: check that the server has the same collection (server)

The local collection will replace the server's. That is only right if they are the same now.
On the server:

```bash
cd ~/site_2024
docker compose exec -T flask python - <<'PY'
import chromadb, hashlib
col = chromadb.HttpClient('chroma-rag', 8000).get_collection('nomic-embed-text')
ids = []
while True:
    page = col.get(limit=5000, offset=len(ids), include=[])['ids']
    if not page:
        break
    ids.extend(page)
print(col.count(), hashlib.sha256('\n'.join(sorted(ids)).encode()).hexdigest())
PY
```

- The line must equal step 1's. If it does not, **stop**: the server's collection holds
  something yours does not, and copying yours over would lose it. Find out why first.
- This snippet was run 2026-11-24 in the local flask container (same image as the server)
  and gave step 1's line.

### Step 3: delete the old chunks of the refetched threads (WSL)

Skip if `data/refetch_ids.txt` is empty.

```bash
cd ~/projects/ml/embedder
cp embedstatus.txt ~/chroma_deploy/embedstatus_before.txt
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
grep -v -x -F -f ../data/refetch_ids.txt ~/chroma_deploy/embedstatus_before.txt > embedstatus.txt
wc -l < ~/chroma_deploy/embedstatus_before.txt; wc -l < embedstatus.txt
```

- It prints the chunks deleted (2026: 57 for 8 threads, before their new posts were added).
- The two counts differ by the number of threads in `refetch_ids.txt`.
- Rehearsed 2026-11-24 on a throwaway Chroma: 7 chunks of 2 threads deleted and embedded
  again, the same count after. The counting half was run on the real collection
  (it would have deleted 99 chunks of the 8 threads of 2026).

### Step 4: embed (WSL)

```bash
cd ~/projects/ml/embedder
../venv/bin/python embedder.py | tee ~/chroma_deploy/embed.log
```

- First lines: `Embed:nomic-embed-text has <n> objects`, `Total embeddable files:`, `Files
  embedded:` and `Net to complete:` (the new threads plus the refetched ones; 2026: 227 and
  then 8).
- Then `embedding file: ...` for each, and every 10 a line with the files to go.
- The end: `-----STATS------` with `Failed: 0` and `Size of Collection`.
- It can be stopped (Ctrl+C) and run again; it goes on with what is not in `embedstatus.txt`.
  A file that fails prints `FAILED` and is tried again by the next run; 20 failures in a row
  end the run (then Ollama or Chroma is the problem: step "Before you start", 2).
- Run 2026-11-22 like this; its output is in `data/corpus_update/embed_new.log`.

### Step 5: check the collection (WSL and a browser)

1. Run step 1's command again, writing to `after.txt` instead:
   ```bash
   cd ~/projects/ml/embedder
   ../venv/bin/python - <<'PY' | tee ~/chroma_deploy/after.txt
   import chromadb
   from f_collection import get_all_ids, hash_ids
   col = chromadb.HttpClient('localhost', '8000').get_collection('nomic-embed-text')
   print(col.count(), hash_ids(get_all_ids(col)))
   PY
   ```
   The count is step 1's plus the chunks added, minus step 3's.
2. Every file is embedded: `Total embeddable files` and the lines of `embedstatus.txt` are
   the same number:
   ```bash
   wc -l < embedstatus.txt
   ```
3. On the local site, http://127.0.0.1:8001/, ask about the subject of one of this year's
   new threads (open one in `data/msgs_md` to pick it). The thread is listed among the
   sources of the answer.

### Step 6: pack the collection (WSL)

The local Chroma is stopped while it is packed, so the copy is whole.

```bash
cd ~/projects/site_2024
docker compose stop chroma-rag
tar -czf ~/chroma_deploy/chroma.tar.gz -C data chroma
docker compose start chroma-rag
cd ~/chroma_deploy
sha256sum chroma.tar.gz > chroma.sha256
ls -la
```

- `ls` shows `chroma.tar.gz` (2026: 320 MB) and `chroma.sha256`.
- Rehearsed 2026-11-24: the tar, unpacked and served by a throwaway Chroma, gave step 1's
  line exactly.

### Step 7: copy it to the server

From WSL, as for any upload: `scp ~/chroma_deploy/chroma.tar.gz ~/chroma_deploy/chroma.sha256 <server>:~`.
On the server:

```bash
df -h /
cd ~
sha256sum -c chroma.sha256
```

`chroma.tar.gz: OK`. A `FAILED`: copy again.

### Step 8: replace the server's collection (server)

This stops the site for a minute. If the site's code is deployed the same day, do this with
it, while the containers are stopped (top-level `README.md`).

```bash
cd ~/site_2024
docker compose stop flask chroma-rag
sudo mv data/chroma ~/chroma_before_$(date +%y%m%d)
sudo tar -xzf ~/chroma.tar.gz -C data
ls -ld data/chroma
docker compose up -d
docker compose restart nginx
docker compose ps
```

- `ls -ld` shows `data/chroma`; `ps` lists four containers, all up.
- Then step 2's command on the server again: it must now print the line of
  `~/chroma_deploy/after.txt` (step 5).
- Ask the site the question of step 5.3: the new thread is among the sources.
- In 2026 this ran with the deploy of 2026-11-22, by commands given at the time; the lines
  above follow the plan of that deploy and step 6's rehearsal, not a record of what was typed.

**To go back** (the old collection), on the server:

```bash
cd ~/site_2024
docker compose stop flask chroma-rag
sudo mv data/chroma ~/chroma_rejected
sudo mv ~/chroma_before_<date> data/chroma
docker compose up -d
docker compose restart nginx
```

`<date>` is the one in the name `ls -d ~/chroma_before_*` shows.

### Step 9: clean up, once the site has run well for a few days

- Server: `sudo rm -r ~/chroma_before_<date>` and `rm ~/chroma.tar.gz ~/chroma.sha256`.
- Local: `rm -r ~/chroma_deploy` and `rm -r ~/projects/ml/data/refetch_backup`.

### Troubleshooting

Each case says whether it was seen.

- **Step 2 does not match** (not seen in 2026): stop and find the difference; do not copy.
- **The embedder fails on every file** (not seen): Ollama or Chroma is not answering; check
  "Before you start", 2.
- **The answer does not list the new thread** (not seen): check the thread's `.txt` is not
  empty, and that its id is in `embedstatus.txt`.
- **The site gives 502 after step 8** (not seen; the reason nginx is restarted in step 8):
  `docker compose restart nginx`. nginx looks up `flask` only when it starts.

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
