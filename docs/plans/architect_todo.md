# Architect Todo

**Last Updated:** 2026-11-24

Active workstream: the annual RAG / website refresh. The plan is
`annual_refresh_plan.md`; read it first. The finished image database work is in
`docs/archive/architect_todo_image_database.md`.

## Resume point

The plan is at its twentieth revision (2026-11-24), decisions D1 to D60. Everything through
the pictures of an answer is deployed (`site_2024` `4f85f9e`, `ml` `72957f4`). No decision
waits for Tom and nothing waits to be designed. The Programmer's order: the report on the
chunk experiment's embedding (2.2d), the collapsed posts (CP1 to CP8, D58, with the 60
unfetched threads, D59), the reference links (RL1 to RL8, D60), then the rest of Phase 2.
Architect's next work is reading the Programmer's reports, listed under "Open".

The citations were decided after a probe by Architect. Its scripts, records and pages are in
the git history: `docs/notes/citation_probe/` at commit `342be36`, deleted in the commit
after it.

## Open

- [ ] Read the Programmer's report of the overnight embedding (plan 2.2a, five checks) and decide
      whether the five collections are fit for the labelling (2.3).
- [ ] Read the Programmer's report of the cause of the collapsed posts (CP2), if the
      Programmer stops there, and the closing report (CP8); record both in the plan.
- [ ] Read the Programmer's report of the citation run (RL4), read the answers without a
      number, apply the rule of 4.1a (form only, D60) and record in the plan whether the
      setting may be switched on. Then read the report of the deploy (RL8).

## Notes from Programmer

**NOTE FROM PROGRAMMER (2026-11-24): the five checks of the overnight embedding (plan 2.2a,
2.2d).** Every check passed; nothing to explain away. Read only: the script is
`data/chunk_experiment/check_variants.py` (git-ignored), its full output
`data/chunk_experiment/checks.json`, run from `embedder/` against the 11,388 files. No source
file changed after the run started (none newer than 2026-11-22 18:25), and the chunker and
embedder code are unchanged since the commit the queue ran (`50bf516`).

1. **Counts.** Each collection holds exactly the chunks the chunker makes of the files: the
   same ids and, id for id, the same text; every `source` matches its id. Each count equals
   the plan's table.

   | Variant | Collection | Plan | Chunker | Collection |
   |---|---|---|---|---|
   | A | `words250_overlap0` | 42,234 | 42,234 | 42,234 |
   | B | `words150_overlap0` | 65,877 | 65,877 | 65,877 |
   | C | `words400_overlap0` | 29,054 | 29,054 | 29,054 |
   | D | `words250_overlap50` | 48,982 | 48,982 | 48,982 |
   | E | `words400_overlap80` | 32,718 | 32,718 | 32,718 |

2. **Failed and not done.** No `FAILED` line in the log and `Failed: 0` in every closing
   statistic. Every progress file lists all 11,388 files once and nothing else.
3. **A against production.** 100 random chunks of A (fixed seed), each found by its text
   among the production chunks of the same source: all 100 found, lowest cosine 0.999992.
   None of the 100 drawn was over 512 tokens, so none was passed over.
4. **Long chunks.** Over 6,000 characters: A 0, B 0, C 2, D 0, E 2. Of the 20 longest (by
   characters) in each variant, 3 are at 2,048 tokens, so cut, in every variant, B included.
   All of them are chunks of `cb__docs_-_Cozy-MKIV_Flight_Test_Protocol___pdf`, except one of
   C, `cb__ref_info_-_Pro-set_125_MSDS___pdf#2`. These are PDF text full of form lines; a
   chunk of 2,983 characters (B) is already over 2,048 tokens, so the 6,000-character mark
   does not find every cut chunk. How many chunks in all are cut was not measured: it needs
   one call per chunk.
5. **Hours.** Wall clock from the queue log; seconds per chunk include storing.

   | Variant | Sessions | Hours | Plan | s per chunk |
   |---|---|---|---|---|
   | A | 11-22 18:25 to about 20:37, 21:48 to 22:23 | about 2.77 | 2.6 | 0.236 |
   | C | 11-22 22:23 to 11-23 00:55 | 2.53 | 2.3 | 0.313 |
   | B | 11-23 00:55 to 03:52 | 2.96 | 2.8 | 0.162 |
   | D | 11-23 03:52 to 07:10 | 3.29 | 3.0 | 0.242 |
   | E | 11-23 07:10 to about 08:25, 10:57 to 11:47, 21:02 to 21:57 | about 2.99 | 2.6 | 0.329 |

   About 14.5 hours in all against the plan's 13.3, which left out storing. The plan's rates
   were 0.153, 0.220 and 0.288 s at 150, 250 and 400 words.

**The stops, as the log shows them.** Three, not two as `programmer_todo.md` had it:

- About 20:37 on 11-22, during A, and about 08:25 on 11-23, during E: no line in the log. The
  stop command wrote nothing to the log until `eb6a66f` (11-23 08:51), after both. The times
  are Tom's; the embedder's own figures agree (A had 33,296 chunks at 0.2356 s, which is
  2.18 hours from 18:25; E 13,727 chunks at 0.3298 s, 1.26 hours from 07:10).
- 11-23 10:57 to 11:47: the queue was started, passed over A to D, embedded 3,176 files of
  E (4,647 to 7,823), and was ended by the stop command (logged). This session was not in
  the todo; who started it is not in the log. The evening run at 21:02 went on from 7,823.

**Also:** the GPU Ollama container (`chunk_experiment_ollama`) is removed (Tom, 2026-11-24).
The experiment's Chroma stays for 2.3.

**NOTE FROM PROGRAMMER (2026-11-24): the cause of the collapsed posts (CP2, plan "Collapsed
posts" step 2). It is not one of timing, so I stopped before the fix, as step 2 says.**

**Cause: the "Expand all" click has no effect while the Chrome window is minimized.** The
click is found and raises no error, but the posts stay collapsed, also 15 seconds later.
With the window on screen the same click opens every post at once.

How it was shown (Tom ran a probe, `data/collapsed_probe/probe_collapsed.py`, git-ignored;
the page was read at 0 to 15 s after the click, outputs in `data/collapsed_probe/out_*`):

| Run | Wait before the click | Chrome | Fetches | Collapsed after the click |
|---|---|---|---|---|
| `out_random` | 1 to 3 s at random, as the fetch | on screen | 24 | 0 |
| `out_fixed` | 0.5, 1, 2 and 4 s | on screen | 23 | 0 |
| `out_minimized` | 2 s | minimized | 5 | 4, unchanged for 15 s |

- The first fetch of the minimized run expanded; most likely Chrome was not yet minimized
  (Tom minimized it as the run started). Not confirmed.
- Before the click, every thread shows all posts but the last collapsed: the pattern of the
  24 threads. So the saved files are the page before the click took effect; nothing was
  lost on the way to markdown.
- `QbzfRr94y7Y` (first 3 of 11 collapsed) fits a window brought back on screen part way
  through the expansion. Read from the pattern, not tried.
- The wait before the click is not a cause: Selenium's `driver.get` returns after the page
  has loaded, and 0.5 s was enough in every fetch on screen. Tom's random wait is there to
  pace the fetch so that Google does not take it for scraping; it stays.
- Why Chrome does this: Chrome slows or stops the rendering of a window that is minimized or
  covered, and the page's own code that opens the posts does not run. That is what Chrome is
  known to do, not something I looked into in the page. A window covered by another, not
  minimized, was not tried.

**The count, corrected.** The check of `msgGetter/README.md` step 8 takes any line starting
with `### ` for a post, and a heading inside a post looks the same. 15 of its 40 files are
that: all 13 older ones, and `sklLflSc-Q8` and `Lyutjnqv9K0` of 2026. A collapsed post shows
as a `### name` line followed straight by the date; an expanded one by its `<address>`
line. Counted that way, **25 threads of 2026 are affected and none older**. The three older
files of the plan (`1FZkFhlGOTU`, `EmgEPIPGuN8`, `y_XqX-aiid0`) hold an address line for
each of the 6, 14 and 8 posts that the thread has now: they are whole.

**For Architect: the plan's points for the fix do not fit as written.** Waiting for the
state of the page does not help while the window is minimized: nothing changes. What does
still fit: a thread saved only with no post collapsed, otherwise not saved, printed and
counted; one function for the check (the sign above), used by the fetch and a command.
What is open is how the page is made to expand. Options I see, none tried:

1. Tom keeps the debug Chrome on screen during the fetch, written in the README; the check
   catches a thread fetched while it was not. Costs no code beyond the check.
2. `chrome_with_debug.bat` starts Chrome with the switches that stop it slowing hidden
   windows (`--disable-backgrounding-occluded-windows`, `--disable-renderer-backgrounding`,
   `--disable-background-timer-throttling`). Whether they make a minimized window expand is
   not known; one short probe run would show it.
3. The fetch brings the window to the front before each thread (Selenium can
   `maximize_window`). Not known whether that is enough, and it takes the screen while Tom
   works.

With any of them, a thread still collapsed after a set time is left unsaved and the next run
tries it again. My preference is 2 with the check, if a probe run shows the switches work,
because it does not depend on Tom remembering; otherwise 1.

**Option 2 tried (2026-11-25): the switches do not help.** Chrome started by
`chrome_with_debug.bat` with the three switches (`ac01080`), minimized, probe `short`: all 5
threads stayed collapsed for 15 s, the first one too. The button still read "Expand all"
after the click, so the page did not take the click at all. On screen it turns to "Collapse
all". Run in `data/collapsed_probe/out_minimized_switches`. Tom's normal Chrome was open too, and
`chrome://version` was not checked.

Rerun the same day with the debug Chrome the only Chrome, minimized: all 5 threads expanded
by 2 s, the button read "Collapse all" each time (`out_minimized_switches_only_chrome`).
Not yet known which made the difference, the switches or no other Chrome; a run without
the switches and no other Chrome would tell.

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
- The fetch had saved posts collapsed (D58). Check that the yearly steps still hold the
  check for collapsed posts, and run it on the new threads before anything is embedded.
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
