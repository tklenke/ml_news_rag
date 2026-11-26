# Phase 2.6: blind scores of the answers

Written by Claude on 2026-11-26 from the sheets of `site_2024/evaluation/output/chunk_answers/sheets/`
(git-ignored), before `key.json` was opened. Letters U to Z are per question; the key says
which run each letter is. Rule and scale: plan 2.6. Each answer was judged against the pooled
text of its question; claims were checked by searching that text.

Scores: correct / complete / useful, total.

## Q17: plies on the forward face of the firewall

The pool has "the lower firewall piece was never covered with 1 bid on the fwd face. Cpt 4.2".
All six say one ply of BID; the remarks about later layups are generic and match the pool.

| Letter | Correct | Complete | Useful | Total |
|---|---|---|---|---|
| U | 2 | 2 | 2 | 6 |
| V | 2 | 2 | 2 | 6 |
| W | 2 | 2 | 2 | 6 |
| X | 2 | 2 | 2 | 6 |
| Y | 2 | 2 | 2 | 6 |
| Z | 2 | 2 | 2 | 6 |

## Q13: fuselage stations of the instrument panel, pilot seat back and firewall

The pool holds the forward face of the instrument panel at ~41.25" (the flight test
protocol, listing stations per the POH) and names the seat back and firewall with no station.
It also has "the firewall was moved forward 2-½ inches" (N83MZ manual).

| Letter | Correct | Complete | Useful | Total | Why |
|---|---|---|---|---|---|
| U | 2 | 2 | 2 | 6 | IP ~FS 41.25; says the other two are not given |
| V | 2 | 0 | 1 | 3 | says no station is given; misses 41.25 |
| W | 2 | 0 | 1 | 3 | as V; adds the 2½" move (in the pool) |
| X | 0 | 2 | 1 | 3 | IP 41.25, but seat back FS 76 and firewall FS 150 are made up ("typical estimates") |
| Y | 2 | 0 | 1 | 3 | as V |
| Z | 2 | 0 | 1 | 3 | as V |

## Q02: throttle and mixture cable length with a Bendix RSA-5A

What the pool holds that answers it: no fixed length; mock the route up with house wire
(Atkinson); route along the side of the tub, avoid a 180°; reports of 96" (Cozy III), 108",
8 ft, 9 ft, and the plans' Cablecraft 109"; the cable must never be the stop; anchor the
engine end to the engine if possible; the ball stud at the servo is unsafe (a fatal
disconnect is reported). All six are sound and differ in which of these they carry.

| Letter | Correct | Complete | Useful | Total | Why |
|---|---|---|---|---|---|
| U | 2 | 1 | 2 | 5 | no ball-stud warning beyond "properly retained", no engine-end anchoring |
| V | 2 | 1 | 2 | 5 | engine-end anchoring; ball stud only as "secure connections" |
| W | 2 | 2 | 2 | 6 | ball stud named; 96" and 9 ft |
| X | 2 | 2 | 2 | 6 | 96/109/9 ft, conduit or side route, ball joint |
| Y | 2 | 1 | 2 | 5 | engine movement, travel; no ball-stud warning |
| Z | 2 | 2 | 2 | 6 | house wire, conduit, 180° wrap, over-centre, engine-end support, ball fitting |

## Q28: moving the Cozy by trailer

The pool: widths 13+ ft (IV spar), 11'6", just shy of 137" wingless, 9'3" (III spar); 102"
limit, permits, escort, wide-load sign by day; tilt or raise one wheel per the plans, or an
angled cradle; nose damaged on a 2x4; tie the main wheels at axle or brake disc, not over the
rear fuselage; 14' trailer barely enough for a III, 20' better for a IV; winch; loading is
the hardest part; construction zones.

| Letter | Correct | Complete | Useful | Total | Why |
|---|---|---|---|---|---|
| U | 2 | 2 | 2 | 6 | width, permits, 2x4, engine-mount support, 14–16' trailers, loading |
| V | 2 | 2 | 2 | 6 | III and IV widths, 14' trailer, winch, 2x4, permits |
| W | 2 | 2 | 2 | 6 | axle/brake-disc tie-down and gear leg as suspension (only one), winch, 2x4 |
| X | 2 | 2 | 2 | 6 | 13 ft, construction zones, 14' and 20' trailers, 2x4, fore/aft blocks |
| Y | 2 | 2 | 2 | 6 | 102", 13 ft, 14', 2x4, blocks, time-of-day rules, loading |
| Z | 2 | 1 | 1 | 4 | width and cradle only; no nose warning, tie-down points, trailer size or loading |

## Q51: AeroElectric endurance bus, rationale and components

The pool: renamed from "essential"; minimum loads for comfortable arrival after alternator
failure, then use what is left after a clearance to land; main bus feeds it through a diode
(~0.6 V drop, Schottky option); alternate feed from the battery bypasses the contactor;
examples (minimal panel lighting, turn coordinator, voltmeter; Gomez list with transponder);
3–4 A maximum; 4.5 A × 3 h → 13.5 Ah → 17 Ah new; fuel, not battery, should limit endurance;
test and log battery-only endurance; flaps and pumps are not e-bus loads by default; a second
alternator changes the picture; no avionics master.

| Letter | Correct | Complete | Useful | Total | Why |
|---|---|---|---|---|---|
| U | 2 | 2 | 2 | 6 | rename, diode, alternate feed bypassing contactor, loads, clearance to land |
| V | 2 | 2 | 2 | 6 | adds 0.6 V, the 4.5 A sizing example, testing, avionics master |
| W | 2 | 2 | 2 | 6 | as V, with a diagram and the fuel-limits-endurance goal |
| X | 2 | 2 | 2 | 6 | Schottky, fuel-limits goal, second alternator, flaps/pumps |
| Y | 2 | 2 | 2 | 6 | full power-path sequence, end-of-life capacity |
| Z | 2 | 1 | 2 | 5 | good on loads (3–4 A, Gomez list); vague on the feeds, contactor not named |

## Totals by letter

| Question | U | V | W | X | Y | Z |
|---|---|---|---|---|---|---|
| Q02 | 5 | 5 | 6 | 6 | 5 | 6 |
| Q13 | 6 | 3 | 3 | 3 | 3 | 3 |
| Q17 | 6 | 6 | 6 | 6 | 6 | 6 |
| Q28 | 6 | 6 | 6 | 6 | 6 | 4 |
| Q51 | 6 | 6 | 6 | 6 | 6 | 5 |
