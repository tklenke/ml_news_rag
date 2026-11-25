# Architect Todo

**Last Updated:** 2026-11-25

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

The plan is at its twenty-first revision (2026-11-25), decisions D1 to D63. The server runs
`site_2024` `4f85f9e` and `ml` `72957f4`. Three reports of the Programmer were read on
2026-11-25 and are recorded in the plan: the citation trial passed its rule (4.1a,
"Result"), the five collections of the chunk experiment are fit for the labelling (2.2a,
"Result"), and the collapsed posts are repaired locally ("Collapsed posts", "As found and
built"). Nothing waits to be designed.

Where the Programmer is: RL7, Tom's look at the local site with numbering on. Then RL8 and CP7
as one deploy (D63: the citations with the repaired collection, by the top-level
`README.md`), CP8, then 2.3. The local collection is ahead of the server's until that
deploy. It is the first run of the combined deploy in one session; read in the reports what
the README needed corrected.

## Open

- [x] Read the Programmer's report of the overnight embedding (plan 2.2a, five checks) and decide
      whether the five collections are fit for the labelling (2.3). Done 2026-11-25: fit.
- [~] Read the Programmer's report of the cause of the collapsed posts (CP2), if the
      Programmer stops there, and the closing report (CP8); record both in the plan.
      The cause and the work through CP6 are recorded (2026-11-25). CP8 is not written yet.
- [~] Read the Programmer's report of the citation run (RL4), read the answers without a
      number, apply the rule of 4.1a (form only, D60) and record in the plan whether the
      setting may be switched on. Then read the report of the deploy (RL8).
      The rule holds and is recorded (2026-11-25). RL8 is not run yet.

## Notes from Programmer

None open.

Closed on 2026-11-25 (in this file at commit `9c7570b`; each is recorded in the
plan): the five checks of the overnight embedding, the cause of the
collapsed posts with Tom's decision for option 1, and the citation trial.

Closed on 2026-11-24 (in the git history of this file): the process suggestions
(1 to 5, 7 and 8 are in `CLAUDE.md`; 6 not taken, a cleanup waits its week), the collapsed
posts (D58), the 60 unfetched threads (D59), and the awkward yearly steps (logged in
`docs/notes/opportunities_for_improvement.md`, "ml: yearly update").

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
  deploy of the collapsed posts (D58) was to be the first real run of the last two; read
  its report (CP8) in the plan to see what it showed.
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
- Tom runs the yearly update himself from written steps: the top-level `README.md` and the
  "Yearly Update" sections of the module READMEs (D57).
- The chunk experiment has a Chroma of its own: port 8010, `ml/data/chunk_experiment/chroma`.
