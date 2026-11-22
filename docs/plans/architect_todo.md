# Architect Todo

**Last Updated:** 2026-11-22

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-22 (tenth revision: D35 to D38, the evaluation as it ran, the D33
budget rule). Everything through the follow-on fixes is deployed (`c311cda`). The models are
chosen and committed (`1e72014` in `site_2024`, not merged); their deploy waits for the UI
changes (D38). Next for Architect: design those UI changes with Tom. Phase 2 is free for the
Programmer to start.

## Open

- [~] Design the UI changes that deploy with the model change (D38), with Tom. To decide:
      how answers with tables and lists without a blank line are displayed, what S3's
      allow-list permits, and whether reference links (4.1) and the image gallery (4.2) are
      part of this deploy. Inputs are in "For the UI design" below.
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design whichever of reference links (plan 4.1) and image gallery (4.2) the UI deploy
      does not cover.

## For the UI design

From the Programmer's notes of 2026-11-22; the notes themselves are in the git history of
this file.

- 4 of the 90 evaluation answers hold a Markdown table (`gpt-6-luna` Q32, Q34;
  `gpt-6.1-terra` Q03, Q32). The site's `markdown.Markdown()` has no table extension, so a
  visitor sees raw `|` lines. Tried by the Programmer, not built: with Python-Markdown's
  `tables` extension all four become tables: 2 to 3 columns, up to 7 rows, longest cell 357
  characters, so a narrow screen needs checking.
- A list that follows a text line with no blank line is shown as run-on text (`gpt-6-luna`
  Q09; `gpt-4o-mini` Q32, all 14 list lines, and part of Q09). No other answer has an
  unrendered list.
- No answer has code, quotes, HTML, math or strikethrough.
- Samples: all 30 answers of each model in `docs/archive/gpt6_luna_candidate_answers`,
  `gpt6_1_terra_candidate_answers` and `gpt4o_mini_baseline_answers`.
- There are no samples of the dig-deeper model, `gpt-6.2-sol`: Tom declined them. Dig-deeper
  and follow-up answers are designed for without samples. One local dig-deeper answer was
  read in part (no table).
- `README.md` of `site_2024` still recommends `gpt-4o-mini`, `gpt-4o` and `gpt-5`.

## Notes from Programmer

All notes through 2026-11-22 are answered in the plan (tenth revision) or carried in "For the
UI design"; they are in the git history of this file. The two S12 gaps the Programmer left as
they are (2026-11-22) are in `docs/notes/opportunities_for_improvement.md`.

## Notes from Code Reviewer

R4 and R5 of the code review of 2026-11-22 are decided: D33 and D34 in the plan.

## Completed

Phase 0, the Phase 1 code change, the follow-on fixes and the ten plan revisions through
2026-11-22 are done: planning, question set, site review, the designs of the three deploys,
decisions D1 to D38, the Programmer's notes through the evaluation, and the review findings
R4 and R5. The evaluation showed no candidate slow at its default reasoning effort, so no
reasoning setting was taken to Tom (plan 1.3). The item list is in the git history of this
file.

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct, and the missing space after the colon changes nothing: plan 1.1), `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1`
  (`gpt-6-luna` and `gpt-6.2-sol` once `1e72014` is deployed),
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- `site.ini` holds real keys until S10 is done. Read settings from it with a pattern
  that names the setting; never print the file.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server runs `main` at `c311cda`, delivered by `git pull` (reported by the Programmer;
  `main` in the repo is at `c311cda`). The rollbacks to `bed83f4`
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
- A job does not record which model answered it.
- `ml/docker-compose.yaml` mounts `../site_2024/data/chroma`, the same directory the
  site's Chroma uses locally. Both compose files must name the same Chroma version.
- Local Chroma data has been opened by 1.5.9. The 1.1.1 backup is
  `site_2024/data/chroma_backup_1.1.1`; rehearsal baseline and probe script are in
  `site_2024/data/rehearsal/`. Both old images are kept locally under the tag `old-stack`.
- The live certificate expires 2027-02-20.
- `gpt-4o-mini` and `gpt-4.1` shut down on 2027-01-14.
