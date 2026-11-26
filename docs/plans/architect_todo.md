# Architect Todo

**Last Updated:** 2026-11-26

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

The plan is at its twenty-first revision (2026-11-25), decisions D1 to D63. The server runs
`site_2024` `4f85f9e` and `ml` `72957f4`. Nothing waits to be designed and no decision
waits for Tom.

Where the Programmer is: RL7, Tom's look at the local site with numbering on. Then one
deploy of the citations with the repaired collection (D63, by the top-level `README.md`),
the closing report of the collapsed posts (CP8), then the chunk experiment from 2.3. The
local collection is ahead of the server's until that deploy.

## Open

- [ ] Read the Programmer's report of the deploy (DP6 in `programmer_todo.md`) and record it
      in the plan. It is the first run of the combined deploy in one session: record what
      the README needed corrected, and bring "For the yearly update of 2027" below in line.
- [ ] Read the closing report of the collapsed posts (CP8) and record it in the plan.
- [ ] After the first batch of labels (2.3, 2.4): read the metrics and apply the stopping
      rule of plan 2.3 and the decision rule of 2.5.

## Notes from Programmer

Closed notes are in the git history of this file: those read on 2026-11-25 (the
embedding checks, the cause of the collapsed posts, the citation trial) at `9c7570b`.

**NOTE FROM PROGRAMMER (2026-11-26): the deploy of the citations and the repaired
collection (D63, DP6) is done.** Every check passed. Run by the top-level `README.md`,
steps 3 and 5 to 8, in one session, Tom at the server.

- **Before it.** RL7: Tom looked at the local site with numbering on and said "Looks good"
  and "let's deploy all to the server". His only remark, thumbnails not showing, was local:
  `site_local.ini` sends them to a server on port 8090 that was not running. DP1: one code
  review of `site_2024` `4f85f9e..dbfa93b` and the `ml` commits of the collapsed posts,
  done in the Code Reviewer role in the same session at Tom's request: Not approved on R1
  (step 8 of the README put the check and the deletions in one block). R1 fixed (`ml`
  `ac7f2bd`) and R2 fixed (`site_2024` `340d820`: a citation mark inside a link the answer
  writes itself made a link inside a link; it now stays as written). Tom accepted R3 (the
  line endings of `process_message.py` changed with the fix), R4 (an old `.md` with a
  collapsed post is never fetched again; for CP8's troubleshooting) and R5, and waived
  the check of R1.
- **Deployed.** `site_2024` `4bcdd79` (`NUMBER_DOCS = True`), merged to `main` and pushed,
  as is `ml` `247b98b`. The collection `42577 4e273635...` replaced `42276 92d43eed...`;
  `gallery261125.idx` (5,795 pictures) replaced `gallery261123b.idx`; 5,795 thumbnails
  unpacked beside the old ones (5,796 files).
- **Checks, as Tom saw them.** Step 3: the server gave the line of `before.txt` exactly.
  6a: four `OK`. 6b: `0` and `5796`. 6c: `main` at `4f85f9e`, its image kept under that
  name. 6d: fast-forward to `4bcdd79`; the build was all cached (below). 6e: four
  containers up. 7.1: the server gives the line of `after.txt`. 7.2: the gallery index
  hash equals the upload's. 7.3: no "No pictures" line. 4.1b: Tom reported each check as
  described, and I read the five pages on the live site: `GYOb5SZJF1` (first answer,
  `gpt-6-luna`), `QIPIZxYf82` (dig deeper, `gpt-6.2-sol`), `X70oBbo4zq` (first answer),
  `JySugRiWtU` (follow-up, `gpt-6.2-sol`), `N8XsIu8HGH` (N249PM). In each, every number
  leads to the address of the row with that number (22 links), and no unlinked `[n]` is
  left. `N8XsIu8HGH` lists `SVdmlqx3aco` as row 4 and cites it twice for the 3,000 AGL
  and CHT statements; it shows 9 thumbnails. `40WsuWAocT` (2026-11-24) is unchanged: no
  numbers, rows not numbered.
- **What the README needed** (`ml`, DP5):
  1. Step 3: both heredocs fail when pasted, and the cause is not wrapping, as the todo
     said. Tom's paste puts two spaces before every line, so the closing `PY` never
     matches, and Python sees an indented first line. Both blocks are now `python -c "if
     1:` with an indented body, every line under 60 characters, rehearsed with and
     without the two spaces.
  2. 6d and step 8: `fwww` is mounted into the container, not built into the image. The
     build changes the image only when the requirements or the dockerfile change; this
     time `latest` kept the ID of `4f85f9e`, and the new code ran from the restart in 6e.
     Step 8 said the IDs would differ.
  3. The 2026 example values are those of this run, and step 7 records that the combined
     deploy has now run.
  Not run: the ways back.
- **Left on the server**, in "Server cleanup", not before 2026-12-03:
  `~/chroma_before_261126`, `~/gallery_before_261126.idx`, `~/update_deploy`, the image
  name `site_2024-flask:4f85f9e`.
- **Seen, not acted on:** in the source list, the links of the rows write a `&` in an
  address bare (`2004_Forum_Q&A.htm`), while the citation links write `&amp;`. Browsers
  read both the same way; the rows' code (`originid_anchor`) is as it was before the
  citations.

## Notes from Code Reviewer

None open.

## For the yearly update of 2027

Read this before planning the next update.

- Tom runs the update himself from the READMEs (D57): "Yearly Update" in `msgGetter`,
  `imageGetter` and `embedder`, the order and all server work in the top-level `README.md`.
  Start there, not from this plan.
- Before he starts, read `docs/notes/opportunities_for_improvement.md`, "ml: yearly update",
  and ask Tom which of the hand steps he wants made into tested commands first. He put
  them off in 2026 because the steps worked and the next run was a year away. The time to
  build them is before the run, not during it.
- Three things were not proven in 2026, as far as this file knew on 2026-11-24: `webGetter`
  has no instructions; the Chroma upload in the top-level `README.md` (steps 5 to 7) was
  written from a rehearsal; the deploy of everything in one session had not been run. The
  deploy of the citations with the repaired collection (D63) is to be the first real run
  of the last two; read its report in the plan (4.1b, "Deploy") to see what it showed.
- The fetch had saved posts collapsed (D58), because the click on "Expand all" does nothing
  in a minimized Chrome (D61). The fetch now saves no thread with a collapsed post, and
  `msgGetter/f_collapsed.py` lists such threads. Check that the yearly steps still tell Tom
  to keep Chrome on screen and still run that command before anything is embedded. Its
  sign was wrong once for the older files; do not take a count of 0 as proof for them.
- The server rules are in `CLAUDE.md`, "Deploys and server work".

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct, and the missing space after the colon changes nothing: plan 1.1), `LLM_DRAFT = gpt-6-luna`, `LLM_REVISE = gpt-6.2-sol`,
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- The keys are in the git-ignored `site_2024/fwww/site_local.ini` (S10, deployed). Never
  print that file; read a setting with a pattern that names it.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server runs `main` at `4f85f9e`, delivered by `git pull`. Of the rollbacks only that
  of the corpus update is still kept there, to 2026-11-28 (`programmer_todo.md`, "Server
  cleanup").
- The server has 1.9 GiB of memory, 2 CPUs, a 2 GB swap file, Docker 29.10.0 and Compose
  5.8.0. gunicorn runs 2 workers. With the model loaded, 771 MiB is available. 36 GB of
  disk was free before the Phase 0 deploy.
- The containers come back after a server reboot with no command run (D31; checked on the
  server by a reboot).
- `www.m24tom.com` redirects to `m24tom.com` over HTTP and HTTPS, and the certificate covers
  both names (D32; checked on the live site). `m24tom.com-0010` is the only usable
  certificate on the server.
- A job's `result` holds the model name OpenAI returned, and the results page shows it.
- The Windows clone of the project is deleted (Tom, 2026-11-24). The getters run with the
  Windows Python from cmd in the WSL folder, and fetches arrive in `ml/data` (D57).
- The server's collection holds 42,276 chunks of 11,388 sources (2026-11-22, after the
  corpus update). The local one holds 42,577 of 11,448 since 2026-11-25 (the collapsed
  posts and the 60 threads of D59) and is not deployed yet (D62, D63).
- `ml/docker-compose.yaml` mounts `../site_2024/data/chroma`, the same directory the
  site's Chroma uses locally. Both compose files must name the same Chroma version.
- Local Chroma data has been opened by 1.5.9. The 1.1.1 backup is
  `site_2024/data/chroma_backup_1.1.1`; rehearsal baseline and probe script are in
  `site_2024/data/rehearsal/`. Both old images are kept locally under the tag `old-stack`.
- The live certificate expires 2027-02-20.
- `gpt-4o-mini` and `gpt-4.1` shut down on 2027-01-14.
- Ollama 0.40.17 reads a chunk up to 2,048 tokens and cuts a longer one without error
  (measured 2026-11-22). The local GPU is a GTX 1650 with 4 GB: 0.15 to 0.29 s per chunk.
- Attachment URLs of Google Groups need a login (tried 2026-11-23); image downloads run on
  Windows with Tom's Chrome. An image index entry is a thread, not a post.
- `data/images/footer_review.html` (git-ignored) is the page Tom judged the clutter rules on.
- The gallery index is `data/images/gallery261123b.idx` (2,368 threads, 5,661 pictures, every
  one with a thumbnail and its name); the server has it as `data/gallery/gallery.idx`. Decisions are by content hash in `imageGetter/image_decisions.json`. Made locally on
  2026-11-25 and not on the server yet: `gallery261125.idx` (2,407 threads, 5,795 pictures). The
  server still has the static pages of 2025 under `/cgimages/`; they are to be replaced by the
  pictures of an answer and are not deleted yet (D54).
- The chunk experiment has a Chroma of its own: port 8010, `ml/data/chunk_experiment/chroma`.
