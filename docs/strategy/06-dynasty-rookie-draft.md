# 06 — Dynasty Rookie Draft Prep

**Version:** 1.0
**Status:** Loaded on demand by valuation, trade, and (eventually) rookie draft agents. Active primarily February through rookie draft (typically May–August in dynasty leagues).
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md`, `01-valuation-philosophy.md`, `04-trade-strategy.md`. Applies to **Degeneration X only** (dynasty league, league_id `1331779473430810624`).

---

## Purpose

This doc defines how Gridiron evaluates rookie prospects, prices rookie picks as tradeable assets, and (when implemented in Phase 7) executes the rookie draft for Degeneration X. Rookie evaluation is the engine of long-term dynasty asset accumulation; getting it right is how rosters get rebuilt for cheap.

---

## Core stance

`[HEURISTIC]` **Draft capital is king.** The single most predictive variable in rookie evaluation is where the NFL drafted the player. Round 1 and Round 2 NFL draft capital have the highest fantasy hit rates — when an NFL team commits high capital, they signal organizational belief that drives opportunity. Per industry consensus, this single input outpredicts most college production metrics.

`[HEURISTIC]` **Talent + draft capital beats landing spot.** "Bad landing spot" narratives consistently push talented prospects down rookie ADP boards. Dynasty managers who fade these reaches systematically outperform. Situations change; talent is constant. Don't let crowded depth charts depress prospects with strong athletic profiles and Round 1–2 NFL capital.

`[HEURISTIC]` **Avoid talent reaches for landing spot only.** The inverse is also true: a Round 4–6 NFL pick who landed in a "great spot" is rarely worth a high rookie pick. Hype creates draft-day reaches that look bad in retrospect (the "Rashod Bateman in a great spot" pattern). Anchor on talent + capital before situation.

---

## The four-factor evaluation framework

The agent evaluates every rookie through four factors, in priority order:

1. **NFL draft capital** — round and overall pick. Highest single weight. Round 1 = top tier; Round 2 = strong tier; Round 3 = situational; Round 4+ = lottery ticket.
2. **Athletic profile** — combine results, prospect models (RAS / NextGen Stats / PFF athleticism scores). Captures the "what does this player physically project as" signal.
3. **College production** — adjusted to opponent quality, system, and age. Production at younger ages is more valuable (early declarees outproduce late declarees in fantasy).
4. **Landing spot** — depth chart competition, offensive scheme fit, projected target/touch share. Material but applied last; can move a player up or down within their tier, rarely across tiers.

`[HEURISTIC]` **Position-specific hit rates** (industry consensus, post-2010 data):
- **RB:** highest immediate-year hit rate among skill positions. Round 1–2 NFL RBs frequently produce as RB2 or better as rookies. Strong fit for contender win-now needs.
- **WR:** slow burn. Most successful WRs break out in year 2 or 3, not year 1. Patience required. Round 1 NFL WR picks have the strongest dynasty profile across all positions over a 3–5 year horizon.
- **TE:** historically slow-developing position. Sophomore-year breakout pattern (per `01-valuation-philosophy.md`) is real. Early-round TE picks are stash-and-wait.
- **QB:** longest development curve. In superflex formats, Round 1 NFL QBs are top-tier dynasty assets regardless of immediate-year production. In single-QB, deprioritize unless format pressures demand it.

---

## Rookie pick valuation

`[HEURISTIC]` **Picks are dynasty inventory.** Per `01-valuation-philosophy.md`, picks are valued as comparable rookie inventory. Maintain `FF#PICK#{league_id}#{year}#{round}#{slot}` records with weekly-updated values. Picks are not abstract — they're tradeable assets with concrete current value.

`[HEURISTIC]` **Pick value curve (post-NFL-draft, pre-rookie-draft):**
- 1.01 — value of the consensus 1.01 player (typically the top-tier rookie of the class)
- 1.02–1.04 — value of the second-tier of consensus first-rounders
- 1.05–1.08 — meaningful step down; varies by class strength
- 1.09–1.12 — late-first territory, often comparable to early seconds in weak classes
- 2nds — wide range; mid-2nds are often the most-traded asset in dynasty trade markets
- 3rds — lottery tickets; valued at ~25% of an early second
- 4ths — minimum-value sweeteners

`[HEURISTIC]` **Pre-NFL-draft pick valuation** (offseason before NFL draft): apply a class-strength discount of 15–25% to reflect uncertainty. The 2026 class is reportedly thinner than 2024–2025; 2027's class is too far out for confident assessment.

`[HEURISTIC]` **Future-year pick discount.** Per `04-trade-strategy.md`, future-year picks carry an 80% multiplier vs. equivalent next-year picks. A 2027 1st is worth ~80% of a 2026 1st of the same projected slot.

---

## Class strength assessment

`[HEURISTIC]` **Class strength materially affects pick value.** Strong classes inflate all picks; weak classes deflate them. Sources for class strength assessment:
- DLF, Dynasty Nerds, PFF, Draft Sharks consensus rankings — pull pre-NFL-draft and post-NFL-draft rankings as inputs
- NFL draft capital distribution (how many skill players went in rounds 1–2)
- Industry "strong class" / "weak class" qualitative assessments from at least 3 analysts

`[HEURISTIC]` **Strong class signals:**
- 8+ skill players in NFL Round 1
- 3+ RBs in NFL Round 1 or 2
- Multiple consensus top-3 prospects at the same position
- Pre-draft rookie ADP shows tight clustering at the top (high agreement)

`[HEURISTIC]` **Weak class signals:**
- Fewer than 6 skill players in NFL Round 1
- No RBs in NFL Round 1 or 2 (per the 2026 class — only Love went R1)
- High variance in pre-draft rookie ADP (low agreement, suggests no consensus elite)

---

## Trade strategy around the rookie draft

`[HEURISTIC]` **Pre-NFL-draft picks are leverage.** Before the NFL draft, your owned picks have unknown identity (you don't know which player you'll get). This uncertainty is exploitable in trades — managers fearing a weak class will discount picks; managers fearing a strong class will overpay.

`[HEURISTIC]` **Trade up when conviction is high.** If the agent's prospect model identifies a clear "smash buy" near the top of the rookie draft and Travis owns picks lower than the target slot, surface a trade-up proposal — typically requires giving up the receiving pick + a sweetener (mid-round future pick or low-value veteran).

`[HEURISTIC]` **Trade down when conviction is muddy.** If the agent's tier breaks suggest a tier of comparable players spans 4+ slots, trade down within that tier and pick up additional capital. Common pattern: trade 1.05 for 1.08 + an early 2027 2nd in a weak class.

`[HEURISTIC]` **Per `00-principles.md`, all 1st-round rookie pick trades require Travis approval.** No exceptions.

`[HEURISTIC]` **Rookie picks as currency in veteran trades.** Per `04-trade-strategy.md`, contenders pay premium for veterans using rookie picks. The agent should propose contender-rebuilder symmetry trades using picks as the contender's outgoing currency. With DX in win-now mode for 2026, this means trading 2027/2028 firsts for win-now veteran production — within the gates of `00-principles.md`'s "don't torch the future entirely" guardrail.

---

## Drafting on the day

This section becomes operational in Phase 7 (rookie draft execution). Pre-draft preparation is active in Phases 0–6.

`[HEURISTIC]` **Pre-draft board.** The agent maintains a continuously-updated rookie ranking board for DX, sourcing from: PFF, DLF, Dynasty Nerds, FantasyPros consensus, plus the gridiron-internal model. Final board produced 24 hours before draft start.

`[HEURISTIC]` **Tier construction over linear ranking.** Group rookies into tiers (e.g., "elite class," "strong starters," "sleeper upside," "lottery"). When on the clock, take BPA within tier; consider trade-down opportunities when multiple tier-equivalent players remain.

`[HEURISTIC]` **Roster fit applies as tiebreaker, not primary driver.** When two players are tier-equivalent, take the one who fits the roster need. But do not reach across tiers for need — Round 2 talent at a position of need is worse than Round 1 talent at a less-needed position.

`[HEURISTIC]` **Draft-day execution requires Travis approval per pick.** This is a high-stakes synchronous event. The agent surfaces the recommended pick + 1–2 alternatives + reasoning, and Travis confirms before submission. Cowork actuator handles the actual pick submission.

`[HEURISTIC]` **Live trade offers during the draft.** Other managers sometimes propose trades on the clock. The agent evaluates incoming offers using `04-trade-strategy.md` framework with extra urgency — surfaces immediately, recommends accept/reject/counter, requires approval before action.

---

## Taxi squad usage post-draft

`[RULE]` Per `02-roster-construction.md`, taxi squad is for rookies and second-year players only. Never veterans.

`[HEURISTIC]` **Default taxi placement:** any rookie not making the immediate active starting lineup goes to taxi if eligible. Active roster slots are for production; taxi is for development.

`[HEURISTIC]` **Taxi exit triggers** (move from taxi to active roster):
- Rookie ascends to clear starting role on NFL team
- Injury to active roster player at the same position creates immediate need
- Trade interest from another manager exceeds expected long-term value (sell)

---

## Common evaluation mistakes the agent avoids

`[HEURISTIC]` **Drafting based on college fantasy production alone.** College stats without context (system, opponents, age) are noise. NFL draft capital tells you what scouts who watched the tape concluded.

`[HEURISTIC]` **Drafting based on combine results alone.** Athleticism scores correlate with NFL success but don't predict it on their own. Combine plus draft capital plus production is the framework.

`[HEURISTIC]` **Anchoring on pre-NFL-draft rookie rankings.** Rankings published before the NFL draft assume average landing spots. Once landing spots are known, the entire board re-orders. Don't anchor on stale data.

`[HEURISTIC]` **Falling for landing-spot narratives.** "He's stuck behind X" narratives often fade by year 2 (X gets injured, X gets traded, depth chart shifts). The agent should weight talent + capital over current depth chart by ~70/30.

`[HEURISTIC]` **Reaching for QB in single-QB formats.** DX format will be confirmed in Phase 0. If single-QB, rookie QBs are mostly draft fodder unless elite-tier (consensus top-2 in their class). If superflex, rookie QBs are premium assets.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
