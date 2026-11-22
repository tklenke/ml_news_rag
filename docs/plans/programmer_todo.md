# Programmer Todo

**Last Updated:** 2026-11-22

# ACTIVE: Annual RAG / Website Refresh

**READ FIRST: `docs/plans/annual_refresh_plan.md`.** Read the whole document before any
task, every session. The tasks below are only a checklist; section numbers refer to the plan.

**Branches:** `wip/annual-refresh` in `ml/` and in `../site_2024/`.

**Order:** Phase 0 is done. The Phase 1 code change and the site fixes are deployed; next is the
follow-on deploy below, then the evaluation (1.3 to 1.6). Phase 2 can overlap the evaluation. One session per
group; start each session fresh. Code review happens once per deploy, not per commit; Tom
waived it for this deploy (2026-11-21).

All code tasks follow TDD. Escalate design questions to Architect; do not resolve them yourself.

The finished image database tasks are in `docs/archive/programmer_todo_image_database.md`.

## Phase 0: Infrastructure refresh (done)

Deployed 2026-11-21 (`bed83f4`) and every plan 0.8 check passed; Tom waived the code review.
Certificate renewed to 2027-02-20. Task details are in the git history of this file.

Still useful:

- The server runs Docker 29.10.0 and Compose 5.8.0; the local rehearsals used 28.3.2 and 2.39.1.
- The server has a 2 GB swap file, and gunicorn runs 2 workers.
- The site stays down after a server reboot until `docker compose up -d` is run.
- `python-dotenv` stays in `requirements.txt` because `pydantic-settings` requires it.
- Known log warnings: gunicorn wants its config file to have a `.py` extension; Ollama reports
  the requested context (8192) exceeds the embedding model's 2048. Neither investigated.
- Not exercised on the server: the rollback in `sudo_renew_cert.sh`.

## Server cleanup (with Tom)

Leftovers kept on the server as the rollback for each deploy. Add to this list whenever a deploy
leaves something behind. Until an entry is done, no `docker system prune` on the server.

- [ ] **From the Phase 0 deploy (2026-11-21).** Not before 2026-11-28, and only if Tom says the
      site has run well. Ends the rollback to the stack before Phase 0. Check first:

          cd ~/site_2024
          git stash list
          docker ps -a
          docker images
          ls -la ~/site_backup_2026-11-21

      Expect one stash, `WIP on main: 906ffd8`, and no container using the images below. If
      a later deploy added a stash, use the number of the `906ffd8` one in the first command.

          git stash drop 'stash@{0}'
          docker image rm site_2024-flask:old-stack
          docker image rm site_2024-ollama-rag:old-stack
          docker image rm chromadb/chroma:1.1.1
          docker image rm nginx:latest
          sudo rm -r ~/site_backup_2026-11-21
          rm ~/deploy_logs.txt

      The backup directory holds the Chroma data from before the upgrade, the certbot
      directory with the private key, and the server's earlier `exclude_from_tar.txt` and
      `sudo_renew_cert.sh`. Afterwards `docker compose ps` lists the same four containers and a
      question is answered.

      Tom's choice, not part of the rollback: the untracked `server/old.nginx_all_apps.conf`,
      `server/certbot/conf/live/m24tom.old`, and the two untagged images from before Phase 0.

- [ ] **From the Phase 1 deploy (2026-11-21).** Not before 2026-11-28, and only if Tom says the
      site has run well. Ends the rollback to `bed83f4` given below. The directory holds the keys.
      Expect one file, `site.ini`:

          ls -la ~/site_ini_before_s10
          rm -r ~/site_ini_before_s10

## Phase 1 code change and site fixes (repo: `../site_2024/`, one deploy)

Deployed 2026-11-21 (`3278e9e`; Tom waived the code review): 1.0,
1.1a to 1.1j, S1, S2, S4, S5, S6, S10, S11. Task details are in the git history of this file.

Still useful:

- Found while testing S1 and fixed: the jobs page returned 500 while any job was unfinished.
  With it, `processid` of an unfinished job gives 404.
- S2: no nginx rate limit (D25). The job starts in the `query` POST; reading pages starts none.
- Found while doing 1.1j and fixed: a revise or follow-up of a job without an answer ended the
  job thread (`KeyError: 'result'`); it now redirects to the question form. Any other exception
  in the job thread (Chroma or Ollama unreachable) still ends it; for Architect, with S8.
- The tracked `site.ini` holds the server's values. The local file had differed in
  `MAX_QUERY_LEN` (1024; 512 on the server).
- Prompt tokens in the local paid check (Q44): question 4,504 (15 chunks), revise 17,438 (60),
  follow-up on the revise 22,652 (69), follow-up on that 24,780 (79). The follow-ups sent 6 and 5
  of their 15 additional chunks twice, as the plan is written (note with Architect).
- Checked on the live site: a question, a revise, the pages and that no full address is shown. A
  follow-up was checked locally only.

Commands for the server: keep lines short. A long line wrapped when pasted, broke a `grep`
pattern, and the comparison of two empty outputs then reported `same`. Print a line count beside
any such comparison.

Rollback until the cleanup (git and settings part rehearsed, containers not):

    cd ~/site_2024
    docker compose stop flask
    git checkout bed83f4
    cp -p ~/site_ini_before_s10/site.ini fwww/site.ini
    docker compose up -d

`site_local.ini` is then untracked and not ignored; leave it. Forward again:
`rm fwww/site.ini`, `git checkout main`.

Running the tests: `site_2024/README.md`. Use `site_2024/.venv`; `site_2024/venv` still holds
the old stack.

The tests that read the collection need the local Chroma (`docker compose up -d chroma-rag`); the
page tests use Flask's test client.

## Follow-on fixes (repo: `../site_2024/`, one deploy, before the evaluation)

Added 2026-11-22 (D29 to D32). Code review once for this deploy, unless Tom waives it.

- [x] 1.1k A follow-up's additional content leaves out chunks already in its previous
      content; cut first, then remove, no filling (plan 1.1 item 8, the paragraph on D29).
      The prompt reads sensibly with no additional content.
- [x] S12 An exception while processing a job marks it `error` and the thread carries on;
      the status response and the polling page tell the visitor and stop polling (plan
      "S12 design").
- [~] D31 `restart: unless-stopped` on the four services (plan "Restart after a reboot").
      Deploy check on the server: `systemctl is-enabled docker`. Ask Tom whether to reboot
      the server to prove it.
      Done and committed; the server check is left. Checked locally: flask started while
      Chroma was down, kept restarting, and served pages after Chroma came back.
- [x] D32a nginx: `www` redirects to `m24tom.com` on HTTP and HTTPS (plan "The `www` name").
- [x] D32b Before changing the script: read certbot's documentation on `certonly` with a
      changed `-d` list, and have Tom run `certbot certificates` on the server. Report to
      Architect if the choice of archive directory needs redesign.
      Documentation and source read, output received (2026-11-22): no redesign needed. The one
      usable certificate is `m24tom.com-0010`, which is also the highest directory. Certbot
      will ask to expand it, in the dry run and in the real run: answer Expand. The result
      should be `fullchain4.pem` in `archive/m24tom.com-0010`.
- [x] D32c `sudo_renew_cert.sh` asks for both names and checks the certificate it is about to
      install (both names, not older than the one in place) before replacing anything.
- [x] D33 A failed OpenAI call ends the job in `error`; a cause Tom has to fix is saved
      as `error_reason` and shown to the visitor (plan "OpenAI failures and the reason
      shown"; review finding R4). First confirm the `insufficient_quota` code from OpenAI's
      documentation. These commits join the commit range of the code review of this deploy.
      Done in `6ea9ece` and `d95f42e`. OpenAI documents other codes than `insufficient_quota`
      for a used-up budget; Tom approved the rule now in the code (2026-11-22). The plan's table
      still gives the old rule (note of 2026-11-22 in `architect_todo.md`). Not seen: a real
      response of a used-up budget.
- [~] Deploy, run the renewal script once, and make the checks in the plan. Add the rollback
      left on the server to "Server cleanup".
      Rehearsed locally (2026-11-22): the stack came up with the restart policy; with an
      invalid key the real OpenAI API answered 401 and the visitor was shown "OpenAI key
      rejected"; rollback to `3278e9e` and forward again. nginx and the renewal script were not
      in the rehearsal, only in the tests. No image needs a rebuild and no file is set aside, so
      nothing is left on the server to clean up. Steps on the server, after the merge and push:

          cd ~/site_2024
          git status -sb
          git log --oneline -1
          openssl version
          date --version | head -1
          systemctl is-enabled docker

      Expect no changed tracked file, `3278e9e`, OpenSSL 1.1.1 or later, GNU date, `enabled`.
      Any other answer: stop.

          git pull
          docker compose up -d
          docker compose ps
          docker exec site_nginx nginx -t
          docker logs site_flask 2>&1 | tail -20

      Then ask a question on the site. Then the certificate; answer Expand where certbot asks:

          sudo ./sudo_renew_cert.sh

      Checks: each of the three answers 301 with `Location: https://m24tom.com/x`, and the
      certificate names both:

          curl -sI http://www.m24tom.com/x
          curl -sI https://www.m24tom.com/x
          curl -sI http://m24tom.com/x

      Rollback (do not run the renewal script while rolled back):

          git checkout 3278e9e
          docker compose up -d

      Forward again: `git checkout main`, `docker compose up -d`.

Still useful:

- Commits `9c1d14f` to `c311cda` of `site_2024`: merged to `main` and pushed (2026-11-22), not
  yet pulled on the server. Tom will reboot the server at the end to prove D31.
- Found while doing S12 and fixed, each with a test: setting the status of an unreadable
  job file replaced its content; an unreadable job file made the jobs page answer 500;
  feedback on a missing or unreadable job left a file holding only the rating.
- Fixed: the test of the running job's status text failed one second in ten.
- S12: the Chroma and Ollama failures were reproduced with unreachable addresses, and ended
  the loop before the change. The polling page's script was run with node, before and after;
  that check is not in the test suite.
- The renewal script now needs `openssl` (with `x509 -ext`) and GNU `date` on the server. Check
  before the deploy: `openssl version` (1.1.1 or later). Without them it stops and replaces
  nothing. Its tests use real certificates; only the docker command is a stand-in.
- `tests/test_nginx_redirects.py` runs the nginx image of the compose file with docker.

### Code review results (2026-11-22)

**Tom waived the rest of this review (2026-11-22)**: the Code Reviewer's check of R1 and the
review of `09e3ca4..c311cda`. The deploy may go ahead.

Reviewed: `site_2024` `3278e9e..09e3ca4` (9 commits). **Not approved: R1 is open.** No bug
introduced by these commits was found. 188 tests pass with clean output; 36 of them fail
against the code at `3278e9e`. `programmer_todo.md` matches the code.

For Programmer:

- [x] R1 **MUST FIX** `fwww/templates/cozyrag_answer.html:23`: no test covers the polling page's
      handling of `error` (stop polling, show `status_text`). With the branch disabled
      (`data.status === 'never'`) all 188 tests pass; CLAUDE.md requires tests for all
      functionality. Suggested: run the page's script in node from a test. Done when that
      change to the branch makes a test fail. Tom may grant an exception instead; not decided.
      Tom will discuss it with the Programmer at the start of the next session: ask first.
      Fixed in `1c20078`; Tom chose the node test over an exception (2026-11-22). The
      reviewer's change to the branch now makes 2 tests fail. The tests need node.
- [x] R2 **SHOULD FIX** `fwww/src/site_functions.py:131`: `get_process_info` catches only
      `JSONDecodeError`. A job file holding `b"\xff"` or `[1]` gives 500 on `/cozyrag/jobs`,
      `/cozyrag/<id>/status`, `/cozyrag/<id>/processid` and the feedback POST (reproduced with
      the test client); `not json` gives 200, 404, 404 and a redirect. The job thread survives
      `b"\xff"` already. Suggested: catch `ValueError` and return `{}` for content that is not
      a dict. Unlikely outside disk corruption. Done when tests show that both contents are
      treated like `not json` on those four routes.
      Fixed in `ed99f81`.
- [x] R3 **SHOULD FIX** `docker-certbot.yaml:8`, and `README.md` "Renew ssl certificate", which
      sends the reader to it: the command asks for `m24tom.com` only. From the notes of D32b
      (not tried), a real run of it would make `m24tom.com-0011` without `www`, which the
      renewal script would then choose and refuse at every run. Suggested: both point to
      `sudo_renew_cert.sh`. Done when neither gives a command that asks for one name.
      Fixed in `0ea4908`. The manual steps that followed it in the README are gone too: the
      script does them, and one (renaming `-0001` over `m24tom.com`) no longer fits.

For Architect (both decided 2026-11-22):

- [x] R4 **SHOULD FIX** `fwww/src/llm_functions.py:246`, there since `4e2f8d5`: OpenAI failures do not reach
      S12. `process_question` catches `openai.APIError` and returns the error text as the
      answer, so the job ends `complete`. Reproduced on a revise with OpenAI unreachable and
      with a 429 for quota: the draft answer was replaced by the error text. The plan lists
      OpenAI among the causes in S12 and says a failed revise keeps its `result`. A used-up
      budget (D25) is a likely way to reach it. Preferably decided before the harness (1.3).
      Done when the Architect's decision is in the plan.
      Decided: D33 in the plan; the Programmer's task is D33 above.
- [x] R5 **CONSIDER** `fwww/src/llm_functions.py:306`, adds to the Programmer's S12 note in `architect_todo.md`: a job file read
      while still empty can also end as `error`, if it becomes readable before
      `mark_job_failed` reads it again. Seen by forcing the timing; 0 times in 12,000 jobs
      unforced. Done when the Architect has fixed or accepted it in the plan.
      Accepted by Tom: D34 in the plan. No Programmer work.

Checked: 9 of 10 deliberate breakages of the code were caught by the tests (the tenth is R1).
D31: with stand-in containers, nginx reached flask in 5 of 5 simulated boots in which flask
stopped twice; this does not replace the reboot of the server.

## Phase 1 evaluation (repo: `../site_2024/`)

- [ ] 1.3 Evaluation harness: reads `refresh_questions.csv`, retrieves once per question,
      sends the same documents to each model, records answer, tokens, latency, cost.
      Every model is called exactly as production calls it, with no reasoning setting.
      Reasoning tokens are recorded as a separate figure and not added to the cost a
      second time (plan 1.3, 1.4).
- [ ] 1.4 Capture the baseline with the current models (they shut down 2027-01-14)
- [ ] 1.5 Produce the blind review files and key file (plan 1.4) for Tom to rate, one batch
      of 10 questions at a time, with a per-tier tally after each batch (plan 1.5). The
      tally shows median latency, median reasoning tokens and cost per answer per model
- [ ] 1.6 After Tom's decision: update the tracked `site.ini` (S10 removes the template)

Questions: `docs/plans/refresh_questions.csv`, rows whose `use` is `batch1`, `batch2`,
`batch3`, in that order.

## Phase 2: Chunk-size experiment (repo: `ml/`)

Start after Phase 0 is deployed, so the variant collections are built on the upgraded
Chroma. Check that the `chromadb` client in the `ml` venv works with that server first.

- [ ] 2.1a Tests for `chunksplitter` covering current behaviour
- [ ] 2.1b Failing test, then fix: no prefix-only chunk when the word count is an exact
      multiple of the chunk size, or for an empty file
- [ ] 2.1c Add overlap to `chunksplitter` (default 0 reproduces current chunks)
- [ ] 2.1d `embedder.py` takes chunk size, overlap and collection name as parameters,
      with a progress file per collection
- [ ] 2.2 Embed variant B on the full corpus and report the time taken before running C, D, E
- [ ] 2.3 Pooling: write `chunk_labels.csv` for Tom, one batch of 10 questions at a time (plan 2.3)
- [ ] 2.4 Scoring: compute the four metrics per variant from Tom's labels, rerun after
      each batch (plan 2.4)
- [ ] 2.5 Question set is the three batches plus the `chunk_only` rows of
      `refresh_questions.csv` (40 questions, plan 2.3). `reserve` rows are not used unless
      Architect says so.

## Phase 4 (not yet designed)

- [ ] S3 Sanitise rendered answer HTML with an allow-list before it is marked safe.
      Wait for the reference-links design; it decides which tags and link targets are allowed.
