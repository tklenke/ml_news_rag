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

- [ ] **NOTE FROM PROGRAMMER (2026-11-24): hand-off at the end of the session. Start here.**
      Done since the resume point: "Pictures of an answer" deployed and checked (PA9, note
      below); the server and local cleanup of the Phase 0, Phase 1 and pictures deploys, early
      at Tom's word (the corpus update's rollback stays to 2026-11-28); a reboot of the server,
      clean; the yearly update instructions written, restructured at Tom's request so that all
      server work is one deploy in the top-level `README.md`, and approved by Tom (YU4); the
      Windows clone deleted by Tom. `programmer_todo.md` pruned; the Programmer's next task is
      RL1, and 2.2d beside it. The notes below wait for you, most pressing first:
      1. The fetch saves some posts collapsed: 27 of the 237 threads of 2026 are on the site
         cut off. Decide on finding the cause, the fix and a refetch.
      2. Up to 60 threads of 2024-25 never fetched. Decide whether to fetch them.
      3. Record in the plan: D55 amended (pictures after Provided Docs), the upload by tar and
         `scp` (4.2 "Delivery" step 3), and the yearly update as written (who does what, one
         deploy).
      4. The process suggestions and the YU5 list of steps that could become small tested
         scripts: accept, reject or schedule.
      5. Seen on the server, not acted on: `~/site_2024`, `~/www` and
         `~/chroma_before_corpus_update` are world-writable.

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
- [ ] **NOTE FROM PROGRAMMER (2026-11-24): process suggestions from the pictures deploy and
      the cleanup.** Asked for by Tom. Each is a suggestion for Architect to accept or not.
      1. **Server work in steps with confirmation.** It worked: Tom ran each block, pasted
         the output, and the next block came only after it was read. Make it the rule for
         deploy, upload and cleanup: blocks of a few commands, each with what to expect and
         where to stop, no deletion in the same block as its checks.
      2. **Name a transfer tool only after checking both ends.** Plan 4.2 named `rsync`; it
         was not installed locally, and Tom moves files with tar and `scp`. Plans should say
         what is moved and how it is checked (SHA-256), and leave the tool to what Tom uses.
      3. **Rehearse every command Tom will paste,** against a scratch copy, including the
         names that break tools. The rehearsal found that GNU tar `-T` reads names starting
         with `-` as options (100 of them); without it the upload would have failed.
      4. **Merge to `main` at each deploy, in both repos.** `ml` `main` was 147 commits
         behind; Tom asked to merge all branches. Make "fast-forward `main` and push" a step
         of each deploy's delivery.
      5. **Close a review in the same session as its fixes,** or let Tom waive it there. The
         verdict stayed "Not approved" after R1 to R3 were fixed, since only a Code Reviewer
         session could close it; Tom waived it at deploy time.
      6. **Cleanup dates.** Tom brought three of four "not before" dates forward on the day.
         Consider giving each entry its reason (what its rollback protects against and when
         that would show) instead of a fixed date, so the call is easy to make early.
      7. **A reboot check after a deploy that changes the stack.** First done 2026-11-24: all
         came up on its own (notes in `programmer_todo.md`, Phase 0 "Still useful"). Worth a
         line in each such deploy's checks.
      8. **Expectations of Docker output.** Two of my "what to expect" lines were wrong:
         `docker images` sizes count shared layers (4.9 GB expected, 1 GB freed), and
         removing an image's last tag deletes it. Expected output should be read from a
         rehearsal, not predicted.

- [ ] **NOTE FROM PROGRAMMER (2026-11-24): the message fetch saves some posts collapsed
      (YU1 trial).** A refetch of `XxpI4Rhe3vY` saved 2 of its 3 posts as Google's cut-off
      preview, although "Expand all" was found and clicked. In the corpus, 40 markdown files
      hold such posts (164 posts), 27 of them among the 237 threads of 2026; they are embedded
      and on the site cut off. Details and examples: `docs/plans/yu1_fetch_trial.md`, "Result".
      Cause not investigated. Needs a decision: whether and when to find the cause and fix
      `process_message.py` (a check for a collapsed post would also catch it), and whether to
      refetch the 40 threads. The yearly instructions (YU2) will name the check either way.

- [ ] **NOTE FROM PROGRAMMER (2026-11-24): up to 60 threads of 2024-25 may never have been
      fetched (found writing YU2).** `msgGetter/msgids_2024-09-03_2025-10-02.txt` (in git since
      `a405976`, 328 lines) differs from `data/msgids_2024-09-03_2025-10-02.txt` (327 lines, the
      one the fetch reads): 60 ids are only in the `msgGetter` copy, are in no id file in `data`
      and have no `.txt`; 29 ids are only in the `data` copy. Probably two runs of the id search
      over the same dates. Not looked into further. Needs a decision: whether to fetch the 60
      (a fetch with that file in `data` would get them) and what to do with the `msgGetter`
      copy. The README says it is not used.

- [ ] **NOTE FROM PROGRAMMER (2026-11-24): the yearly update instructions (YU5 report).**
      Written: `msgGetter/README.md`, `imageGetter/README.md`, `embedder/README.md` ("Yearly
      Update" in each), the order in the top-level `README.md`, and "Deploy a change of the
      code" in `site_2024`'s README. Approved by Tom 2026-11-24 (YU4).
      **Settled in YU1 with Tom:** Windows Python from cmd, not PowerShell, in the WSL folder
      by `pushd`; Chrome by `msgGetter/chrome_with_debug.bat` (profile `C:\selenum\ChromeProfile`)
      for both modules; ChromeDriver in `/home/tom/projects/chromedriver-win64`; start date a
      day before the last end; Tom deletes the Windows clone once all is confirmed. Tom
      widened the task to the embedding and the deploy.
      **Awkward in the code, for Tom to do by hand each year** (code changes, not made):
      1. `get_msg_ids.py`: the start date is a constant to edit (step 3), and the id file is
         written into `msgGetter` and must be moved to `data` by hand (step 4).
      2. ChromeDriver's path is written into both `msgGetter` scripts as a relative path;
         `imageGetter` takes `--chromedriver`. One option in all three would remove the rule
         "ChromeDriver must sit in `/home/tom/projects`".
      3. The older threads with new replies (set aside, refetch, keep the longer copy), the
         deletion of their chunks, the collapsed-post check, the rebuild of `.txt` from `.md`
         and the count and hash of the collection are Python pasted from the READMEs. Each
         could be a small CLI with tests.
      4. The index, gallery and list names carry a date the steps carry in shell variables
         (`$IDX`, `$G`, `$L`); a new terminal means setting them again.
      **Later steps without instructions he could follow:** `webGetter` (not run in 2026; the
      top README says so). The Chroma upload was never written down in 2026 (given in chat);
      the top-level `README.md` steps 5 to 7 follow the plan and a local rehearsal, not a record.
      At Tom's request every server step is in the top-level `README.md` and done in one
      deploy (collection, thumbnails, gallery index, code); that combined deploy has not been
      run as one session.
      **Faults found and reported separately:** collapsed posts (note above), the 60 unfetched
      ids of 2024-25 (note above).

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
