# Required From Tom

**Last Updated:** 2026-11-21

Items the annual refresh needs from Tom. See `annual_refresh_plan.md`.

## Decisions

- [x] LLM provider: stay with OpenAI for this version (2026-11-21)
- [x] Keep two tiers: cheap first answer, better model for dig deeper (2026-11-21)
- [x] Chunk size decided by experiment (2026-11-21)
- [x] Work order: models, chunking, website, then reference links and gallery (2026-11-21)
- [x] `CozyRAG_rev1_Back_Test.pdf` superseded (2026-11-21)
- [ ] Is the public `/cozyrag/jobs` page intended to be readable without login?
- [ ] Scope of the website refresh (Phase 3)

## Work items

- [ ] Pick the 30 evaluation questions from the production log (Architect proposes a shortlist)
- [ ] Rate model answers, blind, `perfect` / `ok` / `not_good` plus factual errors (Phase 1.4)
- [ ] Label pooled retrieval candidates `y` / `n`, about 450 to 750 rows (Phase 2.3)
- [ ] Confirm OpenAI account has access to `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol`
