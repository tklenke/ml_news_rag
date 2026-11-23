# Architect Todo

**Last Updated:** 2026-11-23

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-23 (fourteenth revision, D49 to D51: the image update, plan 4.0). Everything through the answer
display, the corpus update and the model change is deployed (`775692d`) and every check passed.
The embedding of the Phase 2 variants runs at night from 2026-11-22, stopped each morning and
continued each evening (plan 2.2a); read the
Programmer's report of it first. Next design, after the image update: how the image database is used (4.2).

## Open

- [ ] Read the Programmer's report of the image update (IU9).
- [ ] Design the image gallery (plan 4.2), then reference links (4.1) (D41). Discuss with Tom
      first how the image database is to be used. The keyword scores match inside words
      (`king` in `making`); settle that there. A chunk names its thread, not its post, so a
      result can show the images of its threads but not of the posts the model read. The links are made
      by the site from ids, since answers are rendered with raw HTML off (D40).
- [ ] Read the Programmer's report of the overnight embedding (plan 2.2a, five checks) and decide
      whether the five collections are fit for the labelling (2.3).

## Notes from Programmer

All notes through 2026-11-22 are answered in the plan (eleventh revision); they are in the git
history of this file. The two S12 gaps the Programmer left as
they are (2026-11-22) are in `docs/notes/opportunities_for_improvement.md`.

- **NOTE FROM PROGRAMMER (2026-11-23):** Decided by Tom during IU6, a change to D50 for the
  plan: files under 1,000 bytes are no longer dropped without review. The review tool shows
  them on the Suggested list, and the gallery index (IU7) drops a picture only by its
  decision. 47 contents are under 1,000 bytes: 29 were `remove` from 2025, 18 undecided.
  Also decided by Tom: the 4,717 contents of the New list (the 2025 pictures he kept, in
  one thread only) were marked `keep` in one step, so New will hold only the downloads.
- **NOTE FROM PROGRAMMER (2026-11-23):** Decided by Tom during IU2, an addition to D51 for
  the plan: the local name of an image replaces each of `< > : " / \ | ? *` in the sender's
  file name with `_`. 21 names of the current index hold one. On Windows a `:` writes to an
  alternate data stream, so the download of 2025 left 11 of them as zero-byte files cut at
  the colon; those pictures were never saved. Also found in the rename (details in
  `programmer_todo.md`, IU2): 19 files on disk that no URL of `czindex.idx` names (the 11
  empty ones and 8 pictures), left as they are; and 10 thumbnails each shared by two
  pictures whose names differ only in the extension, made from one of the two.
  A second addition to D51, also decided by Tom during IU4: a local name is at most 180
  bytes, the sender's file name shortened with its extension kept (8 names; long Google
  photo ids, and Windows long paths are off).

## Notes from Code Reviewer

R4 and R5 of the code review of 2026-11-22 are decided: D33 and D34 in the plan.

## Completed

Phase 0, the Phase 1 code change, the follow-on fixes and the twelve plan revisions through
2026-11-22 are done: planning, question set, site review, the designs of the three deploys, of
the answer display, of the corpus update and of the overnight embedding (thirteenth revision),
decisions D1 to D48, the Programmer's notes through the evaluation, and the review findings
R4 and R5. The image update (plan 4.0) was designed on 2026-11-23 (fourteenth revision,
D49 to D51). The evaluation showed no candidate slow at its default reasoning effort, so no
reasoning setting was taken to Tom (plan 1.3). The item list is in the git history of this
file.

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct, and the missing space after the colon changes nothing: plan 1.1), `LLM_DRAFT = gpt-6-luna`, `LLM_REVISE = gpt-6.2-sol`,
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- `site.ini` holds real keys until S10 is done. Read settings from it with a pattern
  that names the setting; never print the file.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server runs `main` at `775692d`, delivered by `git pull`. The rollbacks to `bed83f4`
  and to the state before Phase 0 (`906ffd8` plus a stash) are kept there until the server
  cleanup (`programmer_todo.md`).
- The server has 1.9 GiB of memory, 2 CPUs, a 2 GB swap file, Docker 29.10.0 and Compose
  5.8.0. gunicorn runs 2 workers. With the model loaded, 771 MiB is available. 36 GB of
  disk was free before the Phase 0 deploy.
- The containers come back after a server reboot with no command run (D31; checked on the
  server by a reboot).
- `www.m24tom.com` redirects to `m24tom.com` over HTTP and HTTPS, and the certificate covers
  both names (D32; checked on the live site). `m24tom.com-0010` is the only usable
  certificate on the server.
- A job's `result` holds the model name OpenAI returned, and the results page shows it.
- The renderer trial of 2026-11-22 was run in a session scratchpad and is not kept; its
  results are in the plan ("Answer display").
- The Windows copy of the project (`/mnt/c/Users/tom/Documents/projects/ml`) is an older clone
  with uncommitted edits. On 2026-11-22 its `f_filter.py` and `process_message.py` were the
  same as in `ml`. Its `data/` is where Tom's fetches arrive.
- The collection holds 42,276 chunks of 11,388 sources (2026-11-22, after the corpus update).
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
- The chunk experiment has a Chroma of its own: port 8010, `ml/data/chunk_experiment/chroma`.
