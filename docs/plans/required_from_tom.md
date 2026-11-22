# Required From Tom

**Last Updated:** 2026-11-22

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

All decided: D1 to D44 in the plan's table. The dated list of what Tom decided and the
finished work items are in the git history of this file.

## Work items

- [x] For the Programmer, before the renewal script is changed: run `certbot certificates`
      on the server (the Programmer supplies the command).
- [ ] From 2026-11-28, if the site has run well: server cleanup with the Programmer
      (commands in `programmer_todo.md`, "Server cleanup").
- [ ] With the Programmer, before the answer display is reviewed: look at an answer with a
      table in a narrow browser window on the local site (AD6).
- [ ] Fetch again the 10 threads that were already in the corpus (D44), on Windows:
      1. In PowerShell, move the old copies aside:

             cd C:\Users\tom\Documents\projects\ml\data
             mkdir ..\refetch_backup\msgs, ..\refetch_backup\msgs_md
             $ids = 'IO1b3H0WdYI','Lu60jy3FfrA','MpitLWXIk7Q','TTKpCNYRMKQ','UklKWGIn43Q'
             $ids += 'XPOCFJsKWc0','cz4wErtIP8Y','kTX_pdn1mSg','mMGcXcR3RW0','x3XodjGpYTU'
             foreach ($i in $ids) {
               $d = $i.Substring(0,1).ToUpper()
               move "msgs\$d\$i.txt" ..\refetch_backup\msgs
               move "msgs_md\$d\$i.md" ..\refetch_backup\msgs_md
             }
             (dir ..\refetch_backup -Recurse -File).Count

         The last line must print 20.
      2. From `msgGetter`, as usual: `chrome_with_debug.bat`, then `python process_message.py`.
         Do not run `get_msg_ids.py`. It must say `Net to complete: 10`.
      3. Tell the Programmer. Do not copy anything to WSL; the Programmer does (CU6).
      If it goes wrong, move the files back from `refetch_backup`.
- [ ] With the Programmer, at the deploy: upload the Chroma tar to the server (CU8).
- [ ] Delete `~/site.ini.before_s10` on the local machine (the backup with the keys from S10).
- [x] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5). Done 2026-11-22, first answer only (D35).
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)

## Still true

- Tom waived the code review of the Phase 1 deploy (2026-11-21), the rest of that of the
  follow-on deploy (2026-11-22) and that of the model change (2026-11-22, D37). The UI
  changes are not covered by a waiver.
- The OpenAI account has a budget limit with no auto reload (S2).
- The account can call `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol` and `gpt-6.2-astra`.
- One OpenAI key serves the server and local runs.
- The certificate expires 2027-02-20.
