# Phase 2.6: what the chunk-size variants give in answers

Run and judged by Claude on 2026-11-26 (plan 2.6, D65). Harness `site_2024/evaluation/chunk_answers.py`
(`site_2024` `fdb666b`); answers, prompts, sheets and key in `site_2024/evaluation/output/chunk_answers/`
(git-ignored). Blind scores in `phase2_answer_scores.md`, committed (`fa841a6`) before the key was
opened.

## Result

**No variant is a candidate. By the rule fixed in 2.6, chunking stays as it is and Phase 2 closes.**

Only one variant was clearly better than A (2 or more points above both answers of A) on any
question: D, on Q13. The rule asks for 3 of 5.

| Question | A | A again | B (150) | C (400) | D (250/50) | E (400/80) |
|---|---|---|---|---|---|---|
| Q02 cable length, RSA-5A | 6 | 5 | 6 | 5 | 5 | 6 |
| Q13 fuselage stations | 3 | 3 | 3 | 3 | **6** | 3 |
| Q17 firewall plies | 6 | 6 | 6 | 6 | 6 | 6 |
| Q28 trailer | 6 | 6 | 6 | 6 | 4 | 6 |
| Q51 endurance bus | 6 | 6 | 5 | 6 | 6 | 6 |
| **Total of 30** | 27 | 26 | 26 | 26 | 27 | 27 |

Noise: the two answers of A differ by 1 on Q02 and 0 on the rest. Every gap between variants
except Q13 is 1 or 2 points in either direction, and no variant is ahead on more than one
question.

## What the answers showed

- **The answers are good everywhere.** 25 of 30 scored 5 or 6. Given the same amount of text,
  `gpt-6-luna` writes much the same answer from any of the five chunkings: same facts, same
  structure, same caveats. Q17 got the same one-line answer six times.
- **Q13 is a retrieval miss, not a writing difference.** The only line in the pool that answers
  it (instrument panel at ~41.25" in the flight test protocol) was in the text of B and D only.
  D used it and said the other two stations are not given (6). B used it but made up the seat
  back (FS 76) and firewall (FS 150) as "typical estimates" (3). A, C and E did not have it and
  said so (3). One question, and it moves with which chunk lands in the top results, so I read
  it as luck of the cut, not a property of overlap.
- **Lower scores came from omissions, not errors.** The only made-up fact in 30 answers was
  B's on Q13. The others lost a point for leaving something out: the ball-stud warning on Q02,
  the tie-down points and nose support on Q28 (D), detail on the feeds on Q51 (B).

## Speed and cost

Same text in, so these differ only by how long the answer is. The differences are noise: A and
the same prompt asked again differ more (801 vs 934 output tokens) than most variants do from A.

| Run | Chunks | Words given | Tokens in | Tokens out | of them reasoning | Seconds | Cost of 5 |
|---|---|---|---|---|---|---|---|
| A | 16.2 | 3,594 | 4,799 | 801 | 486 | 7.1 | $0.0044 |
| A again | 16.2 | 3,594 | 4,799 | 934 | 597 | 7.9 | $0.0047 |
| B | 25.2 | 3,692 | 4,959 | 822 | 482 | 7.5 | $0.0045 |
| C | 11.4 | 3,614 | 4,736 | 767 | 474 | 6.7 | $0.0043 |
| D | 16.0 | 3,560 | 4,778 | 884 | 600 | 7.8 | $0.0046 |
| E | 11.2 | 3,643 | 4,776 | 858 | 499 | 7.5 | $0.0045 |

Averages per answer except the last column. The run cost $0.027 in all.

**At each variant's own 15 chunks** (computed, no call; mean words per chunk from 3,000 chunks
of each collection, 1.33 tokens per word as measured): A ~3,200 words, B ~2,000, C ~4,600,
D ~3,300, E ~5,100. Input is $0.10 per million tokens, so the most expensive (E) costs about
$0.0003 more per first answer than A: under 30 cents a year at about 850 questions.

## What this does not show

- Five questions and one judge. A difference of a point or two on a question is within what
  one judge can tell apart; what the run can show is that no variant is far ahead, and it
  shows that.
- "Correct" is correct to the corpus, not to the airplane. I know nothing about the aircraft
  beyond the text.
- The rule judged answers, not retrieval. Where retrieval matters (Q13), five questions are
  too few to say which chunking finds more. That is what the labelling of 2.3 measured, and it
  is not run.
