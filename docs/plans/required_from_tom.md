# Required From Tom

**Last Updated:** 2026-11-21

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

- [x] LLM provider: stay with OpenAI for this version (2026-11-21)
- [x] Keep two tiers: cheap first answer, better model for dig deeper (2026-11-21)
- [x] Chunk size decided by experiment (2026-11-21)
- [x] Work order: models, chunking, website, then reference links and gallery (2026-11-21)
- [x] `CozyRAG_rev1_Back_Test.pdf` superseded (2026-11-21)
- [x] Website refresh scope: reference links and images only (2026-11-21)
- [x] Model evaluation checked at 10, 20 and 30 questions (2026-11-21)
- [x] Site review findings are to be fixed; schedule in plan Phase 3 (2026-11-21)
- [x] No password on the jobs page; a full email address is never sent to a web page (2026-11-21)
- [x] Chunk experiment question set: same 30 plus about 10 new (2026-11-21)
- [~] How is the production nginx config managed? The copy in the repo does not match
      production (needed for S2 rate limit and S7). Tom provided the live file on
      2026-11-21: it is `~/site_2024/server/nginx_all_apps.conf` on the server, i.e. the
      same path as the repo copy, edited in place. Differences from the repo copy: the
      certbot, HTTPS redirect and HTTPS server blocks are uncommented, and `/cgimages/`
      uses `root /var/www/;` with `try_files $uri $uri/ =404;` instead of the repo's
      `alias /home/admin/www/cgimages/`. Still open: how Tom wants changes delivered.
- [x] DokuWiki sites (`/dokucozy/`, `/dokuN657CZ/`) are removed in this refresh; they
      are not used (2026-11-21)

## Work items

- [x] Evaluation questions: all 52 candidates approved; Architect ordered them (2026-11-21)
- [x] Give the production nginx config to the Programmer at the start of their first session (2026-11-21)
- [ ] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5)
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)
- [ ] Confirm OpenAI account has access to `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol`
- [ ] Set a monthly spend cap on the OpenAI account (S2)
- [ ] Confirm the `OPENAI_KEY` value in the tracked `.env_flask` was never a real key (S9)
