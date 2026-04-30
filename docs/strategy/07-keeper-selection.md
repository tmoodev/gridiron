# 07 — Keeper Selection + Redraft Prep

**Version:** 1.0
**Status:** Loaded on demand by valuation, trade, and (eventually) draft agents. Active primarily July through draft day (typically August–September in keeper leagues).
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md`, `01-valuation-philosophy.md`, `04-trade-strategy.md`. Applies to **home league only** (keeper format, league_id `1183557197018804224`).

---

## Purpose

This doc defines how Gridiron evaluates keeper selections and prepares for the home league's annual redraft of non-keeper slots. The keeper league is fundamentally a different problem from dynasty — value depends on cost, not just talent. Get this right and a single league-winning keeper can pay for itself for multiple seasons.

Specific keeper rules (count, cost basis, escalation) are read from `FF#LEAGUE#1183557197018804224` per Phase 0 discovery. This doc is rule-agnostic; the agent applies the framework to whatever rules are present.

---

## Core stance

`[HEURISTIC]` **Maximize value vs. cost, not raw player quality.** The goal is not to keep your best player — it's to keep the player whose production most exceeds their cost. A WR2-projected player kept at a Round 12 cost is more valuable than a WR1 kept at a Round 2 cost.

`[HEURISTIC]` **Round-of-savings curves matter, not raw rounds saved.** Per industry consensus: 2 rounds of savings on a Round 1 ADP player (keeping at Round 3) is far more valuable than 5 rounds of savings on a Round 10 ADP player (keeping at Round 15). The early-round savings cluster around scarce, high-tier talent. Quantify savings as ADP percentile improvement, not raw round count.

---

## The Keeper Round Value (KRV) framework

`[HEURISTIC]` **Per industry consensus terminology, KRV = the round you'd forfeit to keep this player.** The agent computes:
- **Player ADP** (current redraft consensus, league-scoring-adjusted)
- **KRV** (this player's keeper cost in your specific league, derived from rules in `FF#LEAGUE#...`)
- **Savings** = ADP - KRV (positive = bargain, negative = overpriced)

`[HEURISTIC]` **Per-tier savings thresholds for "keep" vs "let go":**

| ADP tier | Minimum savings to justify keep |
|----------|--------------------------------|
| Round 1 (1–12) | 1+ round (any savings) |
| Round 2 (13–24) | 2+ rounds |
| Round 3 (25–36) | 2+ rounds |
| Round 4–6 | 3+ rounds |
| Round 7–9 | 4+ rounds |
| Round 10–12 | 5+ rounds |
| Round 13+ | 6+ rounds, or strong upside |

The threshold widens as ADP gets later because late-round talent is plentiful — small savings on a Round 12 player don't outweigh the lost draft pick when many comparable players will be available at that pick anyway.

---

## Keeper rule format mapping

`[HEURISTIC]` **Apply the framework to the actual rules read from Phase 0.** Common formats and their adjustments:

**Original-round cost (no escalation):** keeper costs the round you drafted them. The framework applies directly. Most generous to keepers; favors holding the same core year over year.

**Round-with-penalty:** keeper costs original round minus 1 or 2 each year. Apply the penalty in the KRV calculation. Forces rotation — keepers get expensive over time.

**ADP-based cost:** keeper costs their current-year ADP rather than prior draft position. This format is harder for keepers — you forfeit market price each year. The savings calculation effectively measures whether the player's actual production exceeds their projected production.

**Salary cap:** keeper costs prior auction price + escalator. Apply the math equivalently — savings = projected market value vs. retention cost.

**Free-agent acquisition cost rules:** waiver pickups often cost a mid-round pick to keep (varies by league). Account for this when evaluating in-season pickups as future keeper candidates.

`[HEURISTIC]` **First-round-pick exclusion (common rule):** many keeper leagues prohibit keeping prior-year first-round picks (preventing forever-cheap-superstars). If this rule is present, automatically exclude prior R1 selections from the keeper-eligible set.

---

## Posture-aware keeper selection

`[HEURISTIC]` **The keeper decision flows from league posture per `00-principles.md`.** The home league reassesses posture at weeks 4/8/12 during the season; the offseason posture is set by the postseason context.

**Compete posture (made playoffs, want to push for title next year):**
- Lean toward keepers with high this-year production projection
- Acceptable to use keeper slots on aging veterans with limited future value if they help win now
- Round 1–4 ADP keepers preferred over deep-bargain late-round savings

**Build posture (missed playoffs, willing to lose a season for future):**
- Lean toward young keepers with multi-year value runways
- Prefer late-round bargains over early-round high-cost keepers
- Use keeper slots on players with breakout potential, even if production isn't yet there

**Balanced posture (default):**
- Mix of both. Prioritize ADP/KRV value first, then break ties on age and trajectory
- Avoid older keepers (28+) at premium cost

---

## Multi-year keeper math

`[HEURISTIC]` **Keep cost escalates over time in most leagues.** Even when the player's production stays elite, escalation eventually flips a bargain into a fair-value or overpriced retention. Project forward 2–3 years:

- **Year 1 keep:** raw KRV vs ADP
- **Year 2 keep:** KRV penalty applied, recompute
- **Year 3 keep:** further penalty + age curve adjustment (per `01-valuation-philosophy.md`)

`[HEURISTIC]` **The "right time to let go" is when projected savings drop below the tier threshold.** A player you've kept profitably for two years often hits this point in year 3 — at which point the right move is to let them go back to the pool, take the player at market price (if available) or move on, and use the keeper slot elsewhere.

`[HEURISTIC]` **Per `00-principles.md`, prefer cycling fresh value plays into keeper slots rather than holding the same core indefinitely.** Exception: when escalation is mild and the player remains elite, hold. The agent should explicitly model both paths and surface the comparison to Travis at keeper deadline.

---

## In-season pickups as future keeper candidates

`[HEURISTIC]` **Late-season waiver pickups can be the most valuable keepers.** A player picked up in October at FAAB minimum can become next year's keeper at minimum-round cost — the cleanest path to a Round 12+ savings keeper. Per `03-waiver-strategy.md`, the agent surfaces "keeper value if held" as a secondary signal during waiver evaluation in the home league.

`[HEURISTIC]` **Mid-season trade acquisitions warrant keeper-cost evaluation at trade time.** When trading for a player in the home league, the agent's evaluation should include "what would this player's keeper cost be next year, and is that retention path viable?" — material for trade decision making, especially with rentals vs. potential keepers.

---

## Pre-draft preparation (post-keeper-deadline)

`[HEURISTIC]` **Once keepers are locked, prep for the redraft of remaining slots.** Standard redraft strategy applies, with one critical adjustment: **the available player pool is smaller and tier-distorted because all keepers are off the board.**

`[HEURISTIC]` **Adjusted ADP analysis.** Standard ADP rankings include all players. For your league's draft, recompute "draft-board ADP" = standard ADP minus all kept players. Tiers shift, runs happen at different rounds, and your draft strategy adapts accordingly.

`[HEURISTIC]` **Position-by-position scarcity check.** Some leagues see early RB runs because most managers keep RBs; others see WR runs. The agent reads kept players from each league member (visible in Sleeper after keeper deadline) and projects positional run timing. Adapt strategy:
- Position drained by keepers? Reach earlier than ADP for remaining quality
- Position deep in remaining pool? Wait, take advantage of the depth

`[HEURISTIC]` **Account for missing draft picks.** Keepers consume draft picks per league rules. Your draft order has gaps. Plan around them — if you forfeit Round 4 and Round 7, your "best player" decisions in adjacent rounds matter more.

---

## Draft-day strategy in the home league

`[HEURISTIC]` **Best player available within tier, with construction awareness.** Per `02-roster-construction.md`, draft toward target roster shape — but don't reach across tiers for need. Within tiers, lean to fill construction gaps.

`[HEURISTIC]` **Build for keeper next year, too.** Late-round picks should bias toward upside (young, high-ceiling) over reliability — these are next year's keeper candidates. The Round 14 pick today is the Round 14 keeper next year if it hits.

`[HEURISTIC]` **Trade picks more aggressively than in dynasty.** Picks that won't be used (because of keepers) or that are mid-range have less keeper-future value than dynasty picks do. Trading them for late-round upside or for FAAB is often defensible.

---

## Common keeper mistakes the agent avoids

`[HEURISTIC]` **Keeping the best player rather than the best value.** Most common manager error. The framework's KRV/ADP comparison directly counters this.

`[HEURISTIC]` **Holding aging stars past their value window.** The escalation curve plus age decline (per `01-valuation-philosophy.md`) often makes year-3+ keeps of 28+ players actively bad even when production is still real.

`[HEURISTIC]` **Keeping for sentiment.** Players you've held for years often deserve to be released. The agent's recommendation is rule-based, not loyalty-based.

`[HEURISTIC]` **Maximum-savings chasing on late-round players.** Saving 6 rounds on a Round 18 player is almost always worse than saving 2 rounds on a Round 3 player. Late-round keeper bargains exist but rarely move the needle.

`[HEURISTIC]` **Ignoring opportunity cost of keeper slots.** Each keeper used is a draft pick foregone. If keeping all 3 allowed slots is marginal, keeping 2 and gaining the extra pick may be optimal — surface this analysis when applicable.

---

## What the agent does NOT do

`[HEURISTIC]` Does not recommend keepers without showing the full KRV/ADP/savings/tier-threshold math.

`[HEURISTIC]` Does not anchor on prior-year keeper decisions. Each year is reassessed from scratch.

`[HEURISTIC]` Does not assume Phase 0 keeper rules — reads them from the league config record every time.

`[HEURISTIC]` Does not finalize keeper decisions without Travis approval, regardless of policy graduation.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
