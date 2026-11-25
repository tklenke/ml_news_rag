# Architect Todo

**Last Updated:** 2026-11-24

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-24, last the twentieth revision (D60, below; eighteenth: the pictures of an answer, 4.2, recorded as
deployed, D55 amended; the yearly update recorded, D57). Everything through the pictures of an
answer is deployed (`site_2024` `4f85f9e`, `ml` `72957f4`) and `main` is level with
`wip/annual-refresh` in both repos. The overnight embedding finished all five variants on
2026-11-23 21:57 (read from `queue.log`); the Programmer's report of the five checks (2.2d) is
not written yet. The Programmer's next tasks are 2.2d and then "Collapsed posts" (CP1 to CP8, D58, nineteenth
revision); the reference links (RL1 to RL8) follow. The 60 unfetched threads join the refetch and the world-writable directories wait for the
server cleanup (D59). Tom decided on 2026-11-24 that the citations are built, by the most
reliable way (D60, twentieth revision): the model cites chunks, the page shows one number per
source, the run on the 30 questions checks the form only, and Tom's rating page is dropped.
The probes that led there are in the git history: `docs/notes/citation_probe/` at commit
`342be36`, deleted in the commit after it. The Programmer has RL1 to RL8 after "Collapsed posts". No decision waits for Tom.

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
- The fetch had saved posts collapsed (D58). Check that the yearly steps still hold the
  check for collapsed posts, and run it on the new threads before anything is embedded.
- The server rules are in `CLAUDE.md`, "Deploys and server work".

## Open

- [x] Read the Programmer's report of the pictures of an answer (PA9). Recorded in plan 4.2,
      "Result" (2026-11-24).
- [ ] Read the Programmer's report of the citation run (RL4), read the answers without a
      number, apply the rule of 4.1a (form only, D60) and record in the plan whether the
      setting may be switched on. Then read the report of the deploy (RL8).
- [ ] Read the Programmer's report of the overnight embedding (plan 2.2a, five checks) and decide
      whether the five collections are fit for the labelling (2.3).
- [x] Collapsed posts designed (plan "Collapsed posts", D58) and handed over (CP1 to CP8).
- [ ] Read the Programmer's report of the cause of the collapsed posts (CP2), if the
      Programmer stops there, and the closing report (CP8); record both in the plan.
- [x] Process suggestions and YU5 scripts: decided by Tom 2026-11-24 ("Notes from
      Programmer").

## Notes from Programmer

Recorded in the plan on 2026-11-24 and closed (the notes are in the git history of this
file): D55 amended at PA7, the upload by tar and `scp` (PA8), the report of the deploy
(PA9), the hand-off note, and the yearly update as written (D57).

Decided by Tom on 2026-11-24 and closed (the notes are in the git history of this file):

- Process suggestions 1, 2, 3, 4, 7 and 8 accepted; they are in `CLAUDE.md`, "Deploys and
  server work". Suggestion 5 accepted; it is in `CLAUDE.md`, "Code Review Hand-off",
  "Closing".
- The collapsed posts (D58) and the 60 unfetched threads (D59).
- The awkward yearly steps (YU5): none built; logged in
  `docs/notes/opportunities_for_improvement.md`, "ml: yearly update".

- Process suggestion 6 (a reason in place of the "not before" date of a cleanup entry): not
  taken. Tom, 2026-11-24: waiting a week before a cleanup is wise; faults show when the
  visitors use the site. The dates stay.

## Notes from Code Reviewer

None open (R4 and R5 of 2026-11-22 are D33 and D34 in the plan).

## Completed

Everything through the eighteenth plan revision (2026-11-24) and decisions D1 to D59. The item
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
- The gallery index is `data/images/gallery261123b.idx` (2,368 threads, 5,661 pictures, every
  one with a thumbnail and its name); the server has it as `data/gallery/gallery.idx`. Decisions are by content hash in `imageGetter/image_decisions.json`. The
  server still has the static pages of 2025 under `/cgimages/`; they are to be replaced by the
  pictures of an answer and are not deleted yet (D54).
- Tom runs the yearly update himself from written steps: the top-level `README.md` and the
  "Yearly Update" sections of the module READMEs (D57).
- The chunk experiment has a Chroma of its own: port 8010, `ml/data/chunk_experiment/chroma`.
