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
- [ ] Which site review findings to fix (plan Phase 3, S1 to S9), and whether S1 and S2
      go in alongside Phase 1
- [ ] Is the public `/cozyrag/jobs` page intended to be readable without login? (part of S1)
- [ ] Confirm the chunk experiment question set: same 30 plus about 10 new (plan 2.3)

## Work items

- [ ] Pick the 30 evaluation questions from the production log (Architect proposes a shortlist)
- [ ] Rate model answers, blind, in batches of 10: `perfect` / `ok` / `not_good` plus
      factual errors (Phase 1.4, 1.5)
- [ ] Label pooled retrieval candidates `y` / `n` in batches of 10 questions, 150 to 250
      rows per batch (Phase 2.3)
- [ ] Confirm OpenAI account has access to `gpt-6-luna`, `gpt-6.1-terra`, `gpt-6.2-sol`
- [ ] Set a monthly spend cap on the OpenAI account (S2)
- [ ] Confirm the `OPENAI_KEY` value in the tracked `.env_flask` was never a real key (S9)
