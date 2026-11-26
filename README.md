# ml_news_rag
Python based RAG implementation for expert system based on newgroup corpus




### Procedure to Update Tool/website

The yearly update, written 2026-11-24 after the update of 2026. Read it from the top. Steps
1, 2 and 4 send you to a module's "Yearly Update" section, which has every command, what to
expect and what to do when it goes wrong; come back here at its end. Everything that touches
the server is here, and is done once, together, at the end.

Server work is done over ssh as `admin`, in `~/site_2024`; files go up with `scp`. Run the
server blocks one at a time and read the output before the next. Local notes of the run go
to `~/update_records`:

```bash
mkdir -p ~/update_records
```

#### 1. Fetch the year's messages (Windows cmd and WSL)

`msgGetter/README.md`, steps 1 to 9. Needs Chrome, ChromeDriver and a sign-in to Google
Groups. Ends with new `.md` files in `data/msgs_md`, `.txt` files in `data/msgs`, and
`data/refetch_ids.txt`.

**Other sites** (`webGetter`) were not fetched in 2026 (every file in `data/aeroelectric`,
`data/news` and `data/cozybuilders` is from 2025-10-08), and there are no step-by-step
instructions for it. Skip it unless there is a reason; then it needs instructions first.

#### 2. The pictures (Windows cmd and WSL)

`imageGetter/README.md`, steps 1 to 8. Needs the `.md` files of step 1 and your review of the
new pictures. Ends with a new gallery index and the list of its thumbnails.

#### 3. Check that the server has the same collection as this machine (WSL and server)

The deploy replaces the server's collection with the local one. That is only right if they
are the same before the embedding changes the local one, so this comes before step 4.

Locally, in WSL:

```bash
cd ~/projects/ml/embedder
../venv/bin/python - <<'PY' | tee ~/update_records/before.txt
import chromadb
from f_collection import get_all_ids, hash_ids
col = chromadb.HttpClient('localhost', '8000').get_collection('nomic-embed-text')
print(col.count(), hash_ids(get_all_ids(col)))
PY
```

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

- Each prints the number of chunks and a hash of all their ids. The two lines must be equal.
  On 2026-11-24 both gave `42276 92d43eedddf498273275f0d2f0765d4c4da14e826ac43c60ce94f06e945be4a6`
  (the server's snippet was run in the local flask container, the same image).
- If they differ, **stop**: the server holds something this machine does not, and the
  deploy would lose it. Find out why first.

#### 4. The embedding (WSL)

`embedder/README.md`, steps 1 to 3. Needs the `.txt` files of step 1 and step 3 above. Ends
with `~/update_records/after.txt`, the line the server must show after the deploy, and a
question whose answer lists a new thread.

#### 5. Package everything for the server (WSL)

One directory, `~/update_deploy`, holds all that goes up: the collection, the thumbnails, the
gallery index, and the checksums.

```bash
mkdir ~/update_deploy
G=$(ls -t ~/projects/ml/data/images/gallery*.idx | head -1); echo $G
L=$(ls -t ~/projects/ml/data/images/thumbs*.txt | head -1); echo $L
```

`echo` must show the files of `imageGetter` steps 7 and 8 (2026: `gallery261123b.idx` and
`thumbs261123b.txt`). If not, set `G=` and `L=` to their full names.

The thumbnails (about 100 names start with `-`; `--verbatim-files-from` keeps tar from taking
them for options):

```bash
cd ~/projects/ml/data/images/thumbs
tr '\n' '\0' < $L | xargs -0 sha256sum -- > ~/update_deploy/thumbs.sha256
wc -l < ~/update_deploy/thumbs.sha256
tar -cf ~/update_deploy/thumbs.tar --verbatim-files-from -T $L
cp $G ~/update_deploy/gallery.idx
```

`wc -l` prints the number of thumbnails (2026: 5661); `tar` prints nothing. Run 2026-11-24.

The collection; the local Chroma is stopped while it is packed, so the copy is whole:

```bash
cd ~/projects/site_2024
docker compose stop chroma-rag
tar -czf ~/update_deploy/chroma.tar.gz -C data chroma
docker compose start chroma-rag
```

Rehearsed 2026-11-24: the tar, unpacked and served by a throwaway Chroma, gave the same
count and hash.

The checksums of the whole upload, and the code's state:

```bash
cd ~/update_deploy
sha256sum chroma.tar.gz thumbs.tar thumbs.sha256 gallery.idx > upload.sha256
ls -la
cd ~/projects/site_2024 && git status --short && git log --oneline -1 origin/main
```

- `ls` shows five files (2026 sizes: `chroma.tar.gz` 320 MB, `thumbs.tar` 62 MB).
- If the site's code changed this year, it must be merged into `main` and pushed by now
  (`site_2024` README, "Deploy a change of the code", first block). `git log` shows the
  commit the server will get. `git status` shows nothing.

#### 6. Deploy (server)

Copy it up, from WSL: `scp -r ~/update_deploy <server>:~`. Then on the server, one block at a
time.

**6a. The upload arrived whole.**

```bash
df -h /
cd ~/update_deploy
sha256sum -c upload.sha256
```

Four lines, each `OK`. A `FAILED`: copy again.

**6b. The thumbnails.** Visitors see no change yet: no page names the new ones.

```bash
mkdir -p ~/www/cgimages/pictures/thumbs
cd ~/www/cgimages/pictures/thumbs
tar -xf ~/update_deploy/thumbs.tar
sha256sum -c --quiet ~/update_deploy/thumbs.sha256 2>&1 | wc -l
ls -A | wc -l
```

- The check prints `0`. Any other number: a file is missing or different; unpack again.
- The count is at least the number `wc -l` printed in step 5 (thumbnails of earlier years
  stay; they harm nothing). Run 2026-11-24: `0` and `5661`.

**6c. Write down what runs now, and keep it for going back.**

```bash
cd ~/site_2024
git status --short
git branch --show-current
git log --oneline -1
```

- No change but the untracked `server/old.nginx_all_apps.conf`; branch `main`.
- Write down the commit `git log` shows (2026-11-24: `775692d`): the way back needs it. Then
  keep its image:

```bash
OLD=$(git log --format=%h -1); echo $OLD
docker tag site_2024-flask:latest site_2024-flask:$OLD
docker images site_2024-flask
```

`docker images` lists `latest` and `$OLD` with the same ID.

**6d. The code, only if it changed.** The site keeps running on the old image meanwhile.

```bash
git pull
git log --oneline -1
docker compose build flask
```

`git log` shows the commit of step 5.

**6e. Swap in the data and start.** The site is down from the first line to `up -d`, about a
minute.

```bash
D=$(date +%y%m%d); echo $D
docker compose stop flask chroma-rag
sudo mv data/chroma ~/chroma_before_$D
sudo tar -xzf ~/update_deploy/chroma.tar.gz -C data
sudo cp data/gallery/gallery.idx ~/gallery_before_$D.idx
sudo cp ~/update_deploy/gallery.idx data/gallery/gallery.idx
docker compose up -d
docker compose restart nginx
docker compose ps
```

- Write down `$D`: the way back uses it.
- `ps` lists four containers, all up. nginx is restarted last because it looks up the name
  `flask` only when it starts.

#### 7. Checks (server and a browser)

1. The collection is the local one: step 3's server command again. It must print the line of
   `~/update_records/after.txt`.
2. The gallery index is the one uploaded:
   ```bash
   sha256sum ~/site_2024/data/gallery/gallery.idx
   grep gallery.idx ~/update_deploy/upload.sha256
   ```
   The two hashes are equal.
3. No `No pictures` line: `docker compose logs flask | grep "No pictures"` prints nothing
   once a page with pictures has been shown.
4. In a browser: the question of `embedder` step 3.3 lists the new thread among its sources;
   an answer about something with pictures shows thumbnails under Provided Docs; "All
   pictures for this answer" opens; a thumbnail opens the picture at Google Groups when you
   are signed in to the group; whatever the code change is for.

Each part was checked like this in 2026 on its own deploy (the collection on 2026-11-22, the
pictures on 2026-11-24). This combined deploy, in one session, has not been run yet.

**The way back,** for one part or all. Set `OLD` and `D` to what you wrote down in 6c and 6e
(the values below are examples):

```bash
cd ~/site_2024
OLD=775692d; D=271125
docker compose stop flask chroma-rag
sudo mv data/chroma ~/chroma_rejected
sudo mv ~/chroma_before_$D data/chroma
sudo cp ~/gallery_before_$D.idx data/gallery/gallery.idx
git checkout $OLD
docker tag site_2024-flask:$OLD site_2024-flask:latest
docker compose up -d --force-recreate flask chroma-rag
docker compose restart nginx
```

- Leave out the lines of a part that stays: the two `mv` lines are the collection, the `cp`
  line the gallery index, `git checkout` and `docker tag` the code. The thumbnails stay
  either way.
- Forward again after going back on the code: `git checkout main`, `docker compose build
  flask`, then the last three lines of 6e.
- The collection's way back was written for 2026-11-22 and not run; the code's was not run.

#### 8. Clean up, after a few days of the site running well

On the server, with `OLD` and `D` set to what you wrote down in 6c and 6e (examples below).
First look at what is to be removed:

```bash
cd ~/site_2024
OLD=775692d; D=271125
ls -d ~/chroma_before_$D ~/gallery_before_$D.idx ~/update_deploy
docker images site_2024-flask
```

- `ls` lists all three, with no `No such file or directory`.
- `docker images` lists `latest` and `$OLD`. Their IDs differ when 6d built the code.
- If anything is missing or not as described, **stop** and find out why before removing
  anything.

Then remove them, in the same shell, so that `OLD` and `D` are still set:

```bash
docker image rm site_2024-flask:$OLD
sudo rm -r ~/chroma_before_$D
sudo rm ~/gallery_before_$D.idx
rm -r ~/update_deploy
```

Locally:

```bash
rm -r ~/update_deploy ~/update_records ~/projects/ml/data/refetch_backup
```

### TODO NOTES

 - convert existing dokucozy to docker image
    - copy dokucozy data
    - install docker
    - install docuwiki docker
    - install dokucozy data
- add front end to server to send to separate dockers
    - dokucozy
    - DokuN657cz
    - TkBlog
    - CozyRAG
     - msg search
        - index
        - chromaDB
     - CozyChat

