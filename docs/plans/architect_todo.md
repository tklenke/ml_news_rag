# Architect Todo

**Last Updated:** 2026-11-22

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

Plan revised on 2026-11-22 (ninth revision: D33, D34, from the code review of the follow-on
deploy). Phase 0 and the Phase 1 code change are deployed (`3278e9e`). Next for the Programmer
is the rest of the follow-on deploy (D33, the open review findings R1 to R3, then the deploy),
then the evaluation (1.3 to 1.6), with Phase 2 overlapping. Nothing is waiting on Architect,
unless the Programmer finds that a used-up budget does not arrive as `insufficient_quota`
(D33).

## Open

- [ ] If the evaluation shows a candidate failing or too slow at its default reasoning
      effort: read OpenAI's documentation for the reasoning setting and take the question
      of a `site.ini` setting to Tom (plan 1.3).
- [ ] Have `ml/requirements.txt` created when Phase 2 adds tests to `embedder/` (the
      role files tell every session to read it; it does not exist).
- [ ] Design reference links (plan 4.1) and image gallery (4.2) once the model choice is known.

## Notes from Programmer

Earlier notes are answered in the plan; they are in the git history of this file.

**NOTE FROM PROGRAMMER (2026-11-22): D32b, certbot with a changed list of names.** The
documentation only says the default is to ask. From the source of certbot 5.10.0 (the version
pip gives; the server's `certbot/certbot:latest` may be another):

- With a certificate whose names are a subset of the new list, `certonly` asks "Do you want to
  expand and replace this existing certificate", in the dry run as well. Cancel ends it with
  an error, so the script stops. Expand adds the next numbered files to the archive directory
  of that certificate. No new directory is made.
- Among several such certificates of equal size it takes the first by name, so the lowest
  `-NNNN`. The script takes the highest, so with more than one usable certificate on the server
  it would install an older one, as the plan feared; the check in D32c would stop it, at every
  run. With one usable certificate that is also the highest `-NNNN`, the two agree.
- A certificate whose `live/` files are not all symlinks is skipped as broken. The script
  replaces them in `live/m24tom.com`, so that one is skipped, which explains the `-NNNN`
  directories. With no usable one, a new `-NNNN` certificate is made under the first free name
  in `renewal/`; it fails if that name's archive or live directory already holds files.
- `--cert-name` of a usable certificate names the one that is updated, and asks to confirm the
  changed names. That would remove the guess, if the choice of directory is redesigned.

Tom's output (2026-11-22): no redesign needed. `m24tom.com-0010` is the only usable certificate
(names: `m24tom.com`; files numbered to 3) and the highest directory. `-0001` to `-0009` and
`m24tom.com` are reported as broken. D32c is done as planned.

The two S12 gaps the Programmer left as they are (2026-11-22) are in
`docs/notes/opportunities_for_improvement.md`.

## Notes from Code Reviewer

R4 and R5 of the code review of 2026-11-22 are decided: D33 and D34 in the plan.

## Completed

Phase 0, the Phase 1 code change and the nine plan revisions through 2026-11-22 are done:
planning, question set, site review, the designs of both deploys and of the follow-on deploy,
decisions D1 to D34, the Programmer's notes through the Phase 1 deploy, and the review
findings R4 and R5. The item list is in
the git history of this file.

## Facts worth keeping

- The refresh spans two repositories: `ml/` (chunking, embedding, image database) and
  `../site_2024/` (retrieval, prompts, LLM calls, pages, deployment). See the plan.
- Production RAG settings (`site_2024/fwww/site.ini`): `EMBED = nomic-embed-text`,
  `PREFIX = search_query:` (documents are embedded with `search_document:`; the
  asymmetry is correct, and the missing space after the colon changes nothing: plan 1.1), `LLM_DRAFT = gpt-4o-mini`, `LLM_REVISE = gpt-4.1`,
  `MAX_DISTANCE = .35`, `MIN_DOCUMENTS = 5`, `MAX_DOCUMENTS = 60`,
  `MAX_DRAFT_DOCUMENTS = 15`.
- `site.ini` holds real keys until S10 is done. Read settings from it with a pattern
  that names the setting; never print the file.
- `ml/asker/` and `ml/modelTesting/` are stale harnesses that query an `all-minilm`
  collection. They are not the production path.
- Production job log (2026-11-21): about 850 questions, about 45 rated (roughly 20 of
  those `n/a`; the scale changed over time). Typical first answer: about 4,500 tokens
  in, 300 out, 5 s. A sampled follow-up: about 21,000 tokens in.
- The server runs `main` at `3278e9e`, delivered by `git pull`. The rollbacks to `bed83f4`
  and to the state before Phase 0 (`906ffd8` plus a stash) are kept there until the server
  cleanup (`programmer_todo.md`).
- The server has 1.9 GiB of memory, 2 CPUs, a 2 GB swap file, Docker 29.10.0 and Compose
  5.8.0. gunicorn runs 2 workers. With the model loaded, 771 MiB is available. 36 GB of
  disk was free before the Phase 0 deploy.
- The site stays down after a server reboot until `docker compose up -d` is run, until
  the follow-on deploy adds the restart policy (D31).
- `www.m24tom.com` resolves to the server and nginx answers for it, redirecting HTTP to
  HTTPS on the same host name (`$host`), not to `m24tom.com`. The certificate covers
  `m24tom.com` only, so `https://www.m24tom.com` shows a certificate warning. The
  follow-on deploy changes both (D32).
- `ml/docker-compose.yaml` mounts `../site_2024/data/chroma`, the same directory the
  site's Chroma uses locally. Both compose files must name the same Chroma version.
- Local Chroma data has been opened by 1.5.9. The 1.1.1 backup is
  `site_2024/data/chroma_backup_1.1.1`; rehearsal baseline and probe script are in
  `site_2024/data/rehearsal/`. Both old images are kept locally under the tag `old-stack`.
- The live certificate expires 2027-02-20.
