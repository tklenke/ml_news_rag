# Architect Todo

**Last Updated:** 2026-11-23

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-23 (seventeenth revision: the reference links, plan 4.1, designed as a
trial and then the display, D56; the sixteenth designed the pictures of an answer, 4.2, D52 to D55; the fifteenth recorded the image update, 4.0, as run). Everything through the answer
display, the corpus update and the model change is deployed (`775692d`) and every check passed.
The embedding of the Phase 2 variants runs at night from 2026-11-22, stopped each morning and
continued each evening (plan 2.2a): A, C, B and D are done, E was not finished on 2026-11-23, and
the Programmer's report of the five checks (2.2d) is not written yet. The Programmer builds the pictures first, then the citation trial. No design is open.

## Open

- [ ] Read the Programmer's report of the pictures of an answer (PA9).
- [ ] Read the Programmer's report of the citation trial (RL5), read the answers without a
      number, apply the rule of 4.1a and record the result in the plan. Only then write the
      Programmer's tasks for the display (4.1b).
- [ ] Read the Programmer's report of the overnight embedding (plan 2.2a, five checks) and decide
      whether the five collections are fit for the labelling (2.3).

## Notes from Programmer

- [ ] **NOTE FROM PROGRAMMER (2026-11-23): Tom amended D55 at the local check (PA7).** The
      pictures section of the results page is no longer under the answer and its short
      disclaimer. Order of the page now: answer, short disclaimer, ask another / dig deeper /
      follow-up, Provided Docs, pictures (up to 12 and "All pictures (N)"), Other Related Docs,
      statistics, full disclaimer. Tom's reason, as discussed: the pictures come from the
      provided threads and belong beside that list; the actions follow the answer directly.
      Cost accepted by Tom: on a phone the pictures are below the actions and a table of up to
      15 rows. Built in `site_2024` (`cozyrag_results.html`, test in `test_pictures.py`). Plan
      4.2 and D55 still say "directly under the answer": please record the amendment.
- [ ] **NOTE FROM PROGRAMMER (2026-11-23): the upload of 4.2 uses tar and `scp`, not `rsync`
      (PA8).** Tom moves files to the server with tar and `scp`, as for the Chroma tar, and
      `rsync` is not installed locally. The thumbnails go up as one 62 MB tar with a
      SHA-256 per file. The check is `sha256sum -c` on the server, which covers the size the
      plan asks for. What is lost is the plan's reason for `rsync`, that an upload can be
      stopped and continued; at 62 MB a failed `scp` is run again. Plan 4.2 "Delivery"
      step 3 still names `rsync`: please record the change, or say if you want `rsync`.
- [ ] **NOTE FROM PROGRAMMER (2026-11-24): "Pictures of an answer" (4.2) is deployed (PA9).**
      `site_2024` `4f85f9e`, `ml` `72957f4`, both merged to `main`. Tom waived the rest of
      the code review (the check of R1 and the PA8 todo commits). All checks of plan 4.2
      "Delivery" passed as Tom saw them; not signed in to Google, a thumbnail gives Google's
      sign-in page, as D53 accepted. On the server: 5,661 thumbnails in
      `~/www/cgimages/pictures/thumbs`, the index in `~/site_2024/data/gallery/gallery.idx`
      (root's `data/`), 27 GB free on `/`. Left for "Server cleanup" (not before
      2026-12-01): the image tag `site_2024-flask:775692d` and `~/pictures_deploy`. Did not
      fit the design: the base address setting is the thumbnails' own address
      (`/cgimages/pictures/thumbs`, PA3); the pictures sit after Provided Docs (D55, note
      above); the upload is tar and `scp` (note above). Seen on the server, not acted on:
      `~/site_2024`, `~/www` and `~/chroma_before_corpus_update` are world-writable.

## Notes from Code Reviewer

None open (R4 and R5 of 2026-11-22 are D33 and D34 in the plan).

## Completed

Everything through the seventeenth plan revision (2026-11-23) and decisions D1 to D56. The item
list is in the git history of this file.

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
- The gallery reads `data/images/gallery261123.idx` (2,368 threads, 5,661 pictures, every one
  with a thumbnail). Decisions are by content hash in `imageGetter/image_decisions.json`. The
  server still has the static pages of 2025 under `/cgimages/`; they are to be replaced by the
  pictures of an answer and are not deleted yet (D54).
- Tom wants to run the yearly message and image fetch himself next year, from written steps
  (`programmer_todo.md`, "Yearly update instructions"). He finds running the getters from the
  Windows clone brittle.
- The chunk experiment has a Chroma of its own: port 8010, `ml/data/chunk_experiment/chroma`.
