# ABOUTME: imageGetter module extracts and downloads attachment images from Cozy Builders Google Groups messages
# ABOUTME: Filters URLs to include only attachment images, excluding profile photos and logos

# imageGetter Module

## Yearly Update

Written 2026-11-24 for the next run, about a year later. Read it from the top; every step
says where it is run, what to type, what you should see and what to do if you do not.

### What this step is for

It finds the pictures attached to the year's new messages, downloads the ones not yet on
disk, lets you throw out the clutter (signatures, logos, icons), and makes the two files the
site's "Pictures of an answer" use: the **gallery index** (which threads have which pictures)
and the **thumbnails** (200 x 200 JPEGs). The last step puts both on the server.

All files are under `/home/tom/projects/ml/data/images` in WSL
(`\\wsl.localhost\Debian\home\tom\projects\ml\data\images` from Windows):

| File | What it is |
|---|---|
| `indexYYMMDDhhmmss.idx` | every attachment of every message, made new each year in step 1 |
| `full/` | the downloaded pictures, one file each, never deleted by these steps |
| `thumbs/` | a thumbnail per picture |
| `galleryYYMMDD.idx` | what the site reads: threads and their kept pictures |
| `imageGetter/image_decisions.json` | your keep and discard choices, in git |

**The numbers of 2026, for scale:** 2,631 threads and 6,811 entries in the index; 591
downloaded, none failed; 346 new contents to review; 611 thumbnails made; 2,368 threads and
5,661 pictures in the gallery index; 5,661 thumbnails uploaded (62 MB).

### Before you start

1. **The messages are fetched.** This runs after `msgGetter` (its README, "Yearly Update").
   Check that the newest threads are there, in WSL:
   ```bash
   cd ~/projects/ml
   ls -t data/msgids_*.txt | head -1
   find data/msgs_md -name '*.md' -newer $(ls -t data/msgids_*.txt | sed -n 2p) | wc -l
   ```
   The first line is this year's id file; the count is the `.md` files written since last
   year's id file. On 2026-11-24 it showed 235: the 227 new threads and the 8 fetched again.
2. **Windows Python and its packages,** in cmd:
   ```
   python -c "import selenium, requests, PIL, tqdm; print('ok')"
   ```
   Expect `ok`. If not: `python -m pip install selenium requests pillow tqdm`. (Checked
   2026-11-24 with Python 3.13.7.)
3. **Chrome and ChromeDriver,** as for the messages: `msgGetter/README.md`, "Before you
   start", B. Same ChromeDriver, same place.
4. **The WSL Python** of the project is `/home/tom/projects/ml/venv`. Every WSL command below
   is run from `~/projects/ml/imageGetter` and calls it as `../venv/bin/python`.

### Step 1: build the index (WSL)

```bash
cd ~/projects/ml/imageGetter
../venv/bin/python extract_image_urls.py ../data/msgs_md ../data/images
IDX=$(ls -t ../data/images/index[0-9]*[0-9].idx | head -1); echo $IDX
```

- It reads every `.md` and prints `Results:` with `Messages with images` (2026: 2,631) and
  `Total image URLs` (2026: 6,811). It also writes `index_stats_<date>.txt`.
- `echo` shows the new index, named with today's date and time, for example
  `../data/images/index261123105058.idx`. Steps 2 to 7 use `$IDX`; if you open a new
  terminal, run the `IDX=...` line again.
- Run 2026-11-23.

### Step 2: measure what is already on disk (WSL)

```bash
../venv/bin/python measure_images_cli.py $IDX ../data/images/full
```

- It reads size and pixels of each picture in `full` into the index. It prints `Measured:`,
  `Already measured:` and `File not on disk:` (the pictures still to download), then
  `Wrote index:`.
- Run 2026-11-23.

### Step 3: download the new pictures (cmd on Windows)

Attachment links need a Google login, so this runs on Windows through the debug Chrome.

1. Start Chrome and check the port exactly as `msgGetter/README.md` steps 1 and 2 (close all
   Chrome windows, `chrome_with_debug.bat`, sign in, `curl`).
2. In a second cmd window, find the index name (the newest `index...idx` that `dir` lists
   last, without `_before`):
   ```
   pushd \\wsl.localhost\Debian\home\tom\projects\ml\imageGetter
   dir /o:d /b ..\data\images\index*.idx
   ```
3. Run the download with that name and today's date in the log name, all on one line. In
   2026 it was:
   ```
   python download_images_cli.py --chromedriver ..\..\chromedriver-win64\chromedriver.exe --log ..\data\images\download_261123.log ..\data\images\index261123105058.idx ..\data\images\full
   ```

- It prints the settings, `Extracting authentication cookies from Chrome session...`, a
  progress bar, and every so often `--- Progress Update ---` with Success, Skipped and Failed.
- It skips every picture already in `full`. In 2026: 6,811 in total, 591 downloaded, 6,220
  skipped, 0 failed, in about 40 minutes (from the file times).
- The log ends with the same totals. A failed picture is a line `FAILED <name> <url>`:
  ```
  findstr FAILED ..\data\images\download_261123.log
  ```
  If there are any, run the same download again: it fetches only what is missing. A
  picture that fails every time is left out of the gallery; nothing else is needed.
- Close the debug Chrome when it is done.

In 2026 this ran from PowerShell with ChromeDriver in `C:\Users\tom\Documents\projects`. The
cmd form above, with ChromeDriver in WSL, has been started (`--help`, 2026-11-24) but not yet
run to the end.

### Step 4: measure again, for the new pictures (WSL)

```bash
cd ~/projects/ml/imageGetter
IDX=$(ls -t ../data/images/index[0-9]*[0-9].idx | head -1); echo $IDX
../venv/bin/python measure_images_cli.py $IDX ../data/images/full
```

- Now `File not on disk` should be 0 (or the number of failed downloads).
- `Measured` minus `of them not a picture` are the new pictures. A file that is not a
  picture (Google sent a page instead) is left out of the gallery.
- Run 2026-11-23.

### Step 5: review the new pictures (WSL and a browser)

Every picture content (identical files count once) is decided once: keep or discard. Last
year's choices are in `image_decisions.json`, so only the new ones wait for you.

```bash
../venv/bin/python review_images_cli.py $IDX ../data/images/full ../data/images/thumbs \
  image_decisions.json image_suggestions.json
```

It prints `Review tool on http://127.0.0.1:8765/  (Ctrl+C to stop)`. Open that address in a
browser.

**How the tool works:**

- At the top: three lists with their counts. **Suggested** are the likely clutter: tiny
  files, small pictures, pictures in 2 or more threads, `imageNNN` names under 20 KB, and
  contents you removed in some places in 2025. **New** is every other undecided picture.
  **Decided** is everything already chosen. Do Suggested first, then New.
- The pictures are grouped by thread, with its date and subject. Under each: the number of
  threads it is in, its size, a `full` link to see it whole.
- **A click on a picture** switches it between keep (green frame) and discard (red frame,
  faded). The keep and discard buttons under it do the same. Each click is saved to
  `image_decisions.json` at once. A choice can be changed any time (on the Decided list);
  there is no undo button.
- A picture you have not clicked shows **keep with a dashed frame**: nothing is saved for it
  yet. The button at the end of a page, "Save every dashed picture as keep, then show the next
  pictures", saves them all as keep and loads the next page. So: click only the clutter, then
  press the button.
- 100 pictures a page. Closing the browser loses nothing.
- **You are finished** when Suggested (0) and New (0) show at the top.
- Stop the tool with Ctrl+C in the WSL terminal.

**What clutter looked like in 2026:** a company's signature logo, `image001.jpg` about 200 x
145 pixels, attached to every mail of one sender and so in dozens of threads; small icons and
smileys of 16 x 16 pixels, and 1 x 1 pixel tracking images; banners a few hundred pixels wide
and 50 high; a cartoon or a joke picture with nothing to do with building. A photo of a part,
a drawing or a screenshot of a manual is kept. In 2026: 5,401 contents kept, 333 discarded
(all years).

Then commit the choices, in WSL:

```bash
cd ~/projects/ml
git add imageGetter/image_decisions.json
git commit -m "Record this year's picture review"
git push
```

Run 2026-11-23 (346 contents reviewed).

### Step 6: make the thumbnails (WSL)

```bash
cd ~/projects/ml/imageGetter
../venv/bin/python generate_thumbnails_cli.py ../data/images/full ../data/images/thumbs
```

- A picture that has a thumbnail is skipped. The `Summary:` gives the total and how many were
  made (2026: 611).
- Run 2026-11-23.

### Step 7: make the gallery index (WSL)

```bash
G=~/projects/ml/data/images/gallery$(date +%y%m%d).idx; echo $G
../venv/bin/python gallery_index_cli.py $IDX ../data/images/full image_decisions.json $G
```

- It prints the threads and pictures in the gallery index (2026: 2,368 and 5,661), what it
  dropped (marked remove, not on disk, repeated in a thread), and `Wrote:`.
- `of them contents undecided` should be 0. If not, the review (step 5) is not finished:
  delete `$G`, finish it, and run this step again.
- It refuses an output file that exists (`Error: Already exists`): delete it first if you
  mean to make it again.
- Run 2026-11-23 (the file of 2026 is `gallery261123b.idx`).

### Step 8: list the thumbnails to upload (WSL)

Only the thumbnails the gallery index names go to the server.

```bash
L=~/projects/ml/data/images/thumbs$(date +%y%m%d).txt; echo $L
../venv/bin/python thumbnail_list_cli.py $G ../data/images/thumbs $L
```

- It prints `Thumbnails listed:` (the pictures of step 7) and their size, and `Wrote:`. It
  stops if a thumbnail is not on disk (`Error: Thumbnail not on disk`): run step 6 again.
- Run 2026-11-23 (`thumbs261123b.txt`, 5,661 names, 54.8 MB).

### Step 9: put the thumbnails and the gallery index on the server

This changes nothing a visitor sees until step 9d restarts the site's flask container. The
thumbnails go to `~/www/cgimages/pictures/thumbs` (served by nginx at
`/cgimages/pictures/thumbs`), the index to `~/site_2024/data/gallery/gallery.idx` (read by the
site). Run 2026-11-24 like this, except 9d (see there).

**9a. Pack (WSL).** `$G` and `$L` are from steps 7 and 8. In a new terminal set them again,
with the date those steps used: `G=~/projects/ml/data/images/gallery261124.idx` and
`L=~/projects/ml/data/images/thumbs261124.txt` (examples; `ls -t ~/projects/ml/data/images`
shows yours at the top).

```bash
cd ~/projects/ml/data/images/thumbs
mkdir ~/pictures_deploy
tr '\n' '\0' < $L | xargs -0 sha256sum -- > ~/pictures_deploy/thumbs.sha256
wc -l < ~/pictures_deploy/thumbs.sha256
tar -cf ~/pictures_deploy/thumbs.tar --verbatim-files-from -T $L
cp $G ~/pictures_deploy/gallery.idx
cd ~/pictures_deploy
sha256sum thumbs.tar thumbs.sha256 gallery.idx > upload.sha256
ls -la
```

- 2026 used `thumbs261123b.txt` and `gallery261123b.idx`.
- `wc -l` prints the number of thumbnails; `tar` prints nothing; `ls` shows four files.
- `--verbatim-files-from` matters: about 100 names start with `-`, and without it tar takes
  them for options.

**9b. Copy to the server (WSL).** As for any upload: `scp -r ~/pictures_deploy <server>:~`.
On the server, check it arrived whole:

```bash
df -h /
cd ~/pictures_deploy
sha256sum -c upload.sha256
```

Three lines, each `OK`. A `FAILED`: copy again.

**9c. Unpack and check (server).**

```bash
mkdir -p ~/www/cgimages/pictures/thumbs
cd ~/www/cgimages/pictures/thumbs
tar -xf ~/pictures_deploy/thumbs.tar
sha256sum -c --quiet ~/pictures_deploy/thumbs.sha256 2>&1 | wc -l
ls -A | wc -l
```

- The check prints `0`. Any other number: a file is missing or different; unpack again.
- The count is at least the number from 9a. Thumbnails of earlier years stay; they harm
  nothing. (2026, the first upload: exactly 5661.)

**9d. Replace the gallery index (server).** The site reads it once per worker, so the flask
container is restarted; nginx is restarted after it because it looks up `flask` only when it
starts.

```bash
cd ~/site_2024
sudo cp data/gallery/gallery.idx ~/gallery_before_$(date +%y%m%d).idx
sudo cp ~/pictures_deploy/gallery.idx data/gallery/gallery.idx
sha256sum data/gallery/gallery.idx
grep gallery.idx ~/pictures_deploy/upload.sha256
docker compose restart flask
docker compose restart nginx
docker compose ps
```

- The two hashes are equal; `ps` lists four containers, all up.
- In a browser: ask a question about something with pictures, and check that thumbnails show
  under Provided Docs, and that "All pictures for this answer" opens.
- In 2026 the index went in first and the code came after it, so the restarts above have not
  been run for an index alone.
- If the site shows no pictures: `docker compose logs flask | grep "No pictures"` names the
  problem. To go back: `sudo cp ~/gallery_before_<date>.idx data/gallery/gallery.idx` and the
  two restarts.

**9e. Clean up,** once the site has run well for a few days: on the server
`rm -r ~/pictures_deploy` and `sudo rm ~/gallery_before_<date>.idx`; locally
`rm -r ~/pictures_deploy`.

### Left alone on purpose

- These steps never delete anything in `data/images`. A discarded picture stays in `full`
  and `thumbs`; it is only left out of the gallery index.
- `full_before_rename` and `thumbs_before_rename` are copies from the one rename of 2026 (the
  files got names that cannot collide). They are not part of a yearly run.
- `rename_images_cli.py` and `load_removals_cli.py` were run once in 2026 and are not run
  again.
- The static pages under `/cgimages/` on the server (Phases 4 to 6 below) are the gallery of
  2025. They stay as they are and are not made again.

### Troubleshooting

Each case says whether it was seen.

- **Chrome, the debug port, ChromeDriver:** `msgGetter/README.md`, "Troubleshooting".
- **`pushd` works but `python` says it cannot open the file** (not seen): you are not in
  `imageGetter`; run the `pushd` line again.
- **Downloads fail** (not seen in 2026; 0 failed): run step 3 again. If the log shows many
  `FAILED` with the same cause, check you are signed in to Google Groups in the debug Chrome.
- **The review page does not open** (not seen): the tool runs in WSL on `127.0.0.1:8765`;
  Windows reaches it while the WSL terminal with the tool is open. Another program on the port:
  add `--port 8766` and open that address instead.
- **"Not saved" in the review page** (not seen): the tool was stopped. Start it again; what was
  saved before is kept.
- **The gallery index step refuses a picture "not measured"** (read from the code, not seen):
  a file in `full` was not measured. Run step 4.

## Reference: how the parts were built (2025 and 2026)

The sections from here on describe the build of 2025 (Phases 1 to 6) and the parts added in
2026 (the review and the gallery index). They are background: the yearly run is the section
above.

## Purpose

Extract and download attachment images from Cozy Builders Google Groups markdown files. This module:
1. Parses markdown files to find attachment image URLs
2. Filters out profile photos, logos, and tracking pixels
3. Downloads images using Selenium (authenticated via Chrome debug mode)
4. Generates 200x200px center-cropped thumbnails
5. Builds an index mapping message IDs to images

## Directory Structure

```
imageGetter/
├── README.md (this file)
├── requirements.txt
├── venv/ (local virtual environment, not committed)
├── tests/
│   ├── test_extract_urls.py
│   └── fixtures/
│       └── (sample markdown files for testing)
├── extract_image_urls.py (Phase 1: URL extraction)
├── download_images.py (Phase 2: Image download)
└── generate_thumbnails.py (Phase 3: Thumbnail generation)
```

## Setup

### 1. Create Virtual Environment

```bash
cd imageGetter
python -m venv venv
```

### 2. Activate Virtual Environment

**Linux/Mac:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Phase 1: Extract Image URLs

```bash
python extract_image_urls.py \
  ../data/msgs_md/A \
  ../data \
  --dry-run
```

**Note:** Creates `index{timestamp}.idx` in the output directory

### Phase 2: Download Images

The yearly run, with the command for cmd, is "Yearly Update", step 3.

- A picture already in `full` is not fetched again, so a run can be repeated.
- A request that takes longer than `--timeout` seconds (default 60), or answers with a
  status other than 200, or is not a picture, fails and leaves no file. Each failure is
  listed in the log as `FAILED <local name> <url>`.
- `--limit N` downloads only the first N pictures, for a trial.
- The download writes the index file back as it goes.

### Phase 3: Generate Thumbnails

```bash
python generate_thumbnails_cli.py \
  ../data/images/full \
  ../data/images/thumbs
```

## Image Curation Workflow

After downloading and processing images, use this workflow to dedupe, tag, review, and curate your image collection:

### Review Pictures by Content

Run in WSL from `imageGetter/`, then open `http://127.0.0.1:8765/` in a browser:

```bash
../venv/bin/python review_images_cli.py \
  ../data/images/indexYYMMDDhhmmss.idx \
  ../data/images/full \
  ../data/images/thumbs \
  image_decisions.json \
  image_suggestions.json
```

- One content (same SHA-256) is one picture, shown under its earliest thread.
- A click on a picture switches it between keep (green) and discard (red, stored as
  `remove`); the keep and discard buttons set the choice directly. Each choice is written
  to `image_decisions.json` at once and can be changed later.
- A picture not yet clicked shows keep with a dashed frame: nothing is saved for it. The
  button at the end of a page saves every dashed picture of the page as `keep`.
- **Suggested**: undecided pictures under 1,000 bytes, in 2 or more threads, with a
  shorter side under 200 pixels, named `imageNNN` under 20,000 bytes, or removed in some copies only in 2025.
  **New**: every other undecided picture. **Decided**: everything marked.
- Commit `image_decisions.json` after a session of review.

### Make the Gallery Index

After the review, run in WSL from `imageGetter/`:

```bash
../venv/bin/python gallery_index_cli.py \
  ../data/images/indexYYMMDDhhmmss.idx \
  ../data/images/full \
  image_decisions.json \
  ../data/images/galleryYYMMDD.idx
```

It drops entries whose file is not on disk and contents marked `remove`, lists a content
once per thread (it stays in every thread it is in), and leaves out threads with no
picture. Undecided contents stay, and are counted. It refuses a file on disk that has not
been measured, and an output file that already exists.

### Phase 4: Deduplicate Images

Remove duplicate images (based on file size) and missing files from the index:

```bash
python dedupe_images_cli.py \
  ../data/image_index.json \
  ../data/image_index_deduped.json \
  --images-dir ../data/images/full
```

**Example output:**
```
Loading index from ../data/image_index.json...
Loaded 1234 messages with 6789 images

Processing messages...
100%|████████████████████| 1234/1234 [00:15<00:00, 82.27 messages/s]

============================================================
DEDUPLICATION SUMMARY
============================================================
Total messages:          1234
Messages processed:      1234

Images before:           6789
Duplicates removed:      691
Missing files removed:   23
Images after:            6075
============================================================

Saving deduped index to ../data/image_index_deduped.json...
```

### Phase 5: Tag Images with Scored Keywords

Score keywords per image based on proximity to image URLs in message text (fast, deterministic):

```bash
python search_tag_messages_cli.py \
  ../data/image_index_deduped.json \
  ../data/image_index_tagged.json \
  --keywords aircraft_keywords.txt
```

**Example output:**
```
Tagging messages from ../data/image_index_deduped.json
Output file: ../data/image_index_tagged.json
Keywords: aircraft_keywords.txt
Limit: ALL messages (no limit)

Loading image index...
Loaded 1234 messages

Loading keywords...
Loaded 557 keywords

Scoring keywords for images...

============================================================
KEYWORD SCORING STATISTICS
============================================================
Total messages in index:     1234
Messages processed:          1234
Images scored:               6075
Messages with errors:        0

Keywords per image:
  Average:                   18.5
  Min:                       0
  Max:                       127
  Images with keywords:      6052

Score range:
  Min:                       12
  Max:                       847
  Average:                   156.3
============================================================

Results saved to: ../data/image_index_tagged.json
```

**Notes:**
- Scores based on keyword proximity to image URLs using exponential decay
- Subject line keywords get +200 bonus points
- Keywords stored as `[keyword, score]` tuples sorted by score descending
- Use `--limit N` to process only first N messages (for testing)
- Use `--verbose` to see detailed progress for each message
- Use `--no-clean` to skip invalid keyword filtering

### Phase 6: Generate Static HTML Site

Create a complete static HTML site for browsing images by keyword:

```bash
python generate_static_site_cli.py \
  ../data/image_index_tagged.json \
  ../data/site \
  --images-per-page 210 \
  --min-score 0
```

**Example output:**
```
Loading index from ../data/image_index_tagged.json...
Loaded 1234 messages

Generating index page...
  Generated index.html with 557 keywords

Preparing image list...
  Found 6075 total images
  Year distribution: {2024: 3245, 2023: 2830}

Generating all images pages...
  Generated all/page1.html (210 images)
  Generated all/page2.html (210 images)
  ...
  Generated all/page29.html (75 images)

Generating keyword pages...
  Generated 5 page(s) for 'firewall' (897 images)
  Generated 3 page(s) for 'cowling' (512 images)
  ...

Site generation complete!
Output: ../data/site
  - index.html
  - all/page1.html ... all/page29.html
  - keywords/ (557 keywords)
```

**Generated Site Structure:**
```
site/
├── index.html (keyword index with image counts)
├── all/
│   ├── page1.html (all images, newest first)
│   ├── page2.html
│   └── ...
└── keywords/
    ├── firewall_page1.html (images sorted by score)
    ├── firewall_page2.html
    ├── cowling_page1.html
    └── ...
```

**Notes:**
- Images on keyword pages sorted by score (highest first)
- Scores displayed on thumbnails: "firewall (245)"
- Use `--min-score N` to filter out low-scoring images
- Each page has First/Previous/Next/Last navigation
- Index page links to all keywords and "All Images" view

## Testing

```bash
# Activate venv first
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## Development Notes

- Follow TDD: Write tests first (RED), implement (GREEN), refactor (REFACTOR)
- Use Hungarian notation: `strVariableName`, `intCount`, `lstItems`, `dctMapping`
- Add ABOUTME comments to all new files
- Update `docs/plans/programmer_todo.md` as tasks are completed
- Commit frequently

## Related Documentation

- Architecture: `../docs/plans/image_database_architecture.md`
- Implementation Plan: `../docs/plans/image_database_implementation_plan.md`
- URL Patterns: `../docs/notes/image_url_patterns.md`
