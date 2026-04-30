# 09 — League-Specific Notes

**Version:** 1.0 (initial structure; living document)
**Status:** Continuously updated by the agent throughout the season as patterns emerge. Loaded on demand by trade and waiver agents when evaluating decisions involving specific managers or league-specific patterns.
**Owner:** Travis Moore (with agent-generated additions)
**Last updated:** 2026-04-30
**See also:** `00-principles.md` (per-manager rules)

---

## Purpose

This is a **living document** — it grows over the season as the agent learns league-specific patterns and individual manager tendencies. The other docs cover universal principles; this one captures the local quirks that shape how those principles apply in your specific leagues.

The agent updates this doc autonomously when it observes patterns that meet a confidence threshold (multiple data points, consistent behavior). Travis can add manual notes at any time. Both types of additions are tagged.

---

## Document conventions

Tags:
- `[CONFIRMED]` — observed pattern with multiple data points
- `[OBSERVED]` — single data point or developing pattern
- `[TRAVIS]` — manually added by Travis
- `[HISTORICAL]` — context from prior seasons (decay over time)

Each entry includes:
- Date observed/added
- Source (decision log reference, manual note, or pattern analysis)
- Confidence level
- Implication for agent behavior

---

## Degeneration X (dynasty, league_id `1331779473430810624`)

### League-wide patterns

*This section will populate as the agent observes patterns in trade volume, waiver bidding aggression, lineup-setting patterns, and other league-wide tendencies.*

Initial baseline (to be updated):
- Trade frequency: TBD (Phase 0 will sync historical transactions)
- Average trade size: TBD
- Waiver competitiveness (FAAB usage patterns): TBD
- Common roster construction philosophies among members: TBD

### Manager profiles

Per `00-principles.md`, the agent maintains a profile per manager covering: typical roster posture, trade openness, recent activity patterns, value tendencies (pays premium for X, undervalues Y), communication style preferences.

#### amoore324 (Travis's brother)

`[TRAVIS]` 2026-04-30: Travis's brother. Wide latitude per principles — concentration plays, position swaps, weird pick structures all on the table. Enjoys trading; will engage with creative offers. Dinner-defense test does not apply. Standard 7-day cooldown still applies.

`[OBSERVED]` Profile to be developed from observed trade patterns and historical data.

#### Other managers

*To be populated as the agent observes patterns. Phase 0 will pull historical transaction data to seed initial profiles.*

For each manager, the agent tracks:
- **Posture** (contender / rebuilder / balanced) — derived from recent roster moves
- **Trade willingness** — frequency of accepted offers, average response time, counter rate
- **Value tendencies** — positions/archetypes they overpay for, ones they fade
- **Veto behavior** — has this manager voted to veto trades in the past
- **Communication patterns** — does the manager use league chat, prefer brief proposals, etc.

---

## Home league (keeper, league_id `1183557197018804224`)

### League history and culture

`[TRAVIS]` 2026-04-30: 10-year history. Group of long-time friends. Trade scrutiny is real — every trade should be defensible at the league dinner. No funny business. Joke-rejection of bad offers is NOT appropriate here; use straight polite declines.

### League-wide patterns

*Same structure as DX. To be populated.*

### Keeper trends

`[TRAVIS]` 2026-04-30: Picks and FAAB are tradeable in this league.

*Specific keeper rules (count, cost basis, escalation) read from Phase 0 discovery. Trends to be tracked:*
- *Common keeper choices across the league*
- *Whether managers tend to keep stars at premium cost or chase late-round bargains*
- *Veteran retention patterns (does the league hold stars too long?)*

### Manager profiles

*To be populated. Initial structure same as DX section.*

---

## Cross-league observations

*Patterns observed across both leagues that don't fit cleanly in either section. Examples could include:*
- *Same-named managers in both leagues (none currently known)*
- *Industry-wide trends affecting both (rookie class strength, post-NFL-draft value shifts)*
- *Travis's own roster patterns and tendencies — what the agent learns about Travis's preferences over time*

---

## Update log

This section is the agent's running log of what it has learned and added.

| Date | League | Type | Note | Source |
|------|--------|------|------|--------|
| 2026-04-30 | Both | Initialization | Doc structure created | Manual |

---

## How the agent uses this doc

`[HEURISTIC]` Before generating any trade proposal, the agent loads this doc and checks for relevant manager-specific notes. A proposal to a manager with a "rejects all 2-for-1s" tag should not be a 2-for-1.

`[HEURISTIC]` Before evaluating any incoming offer, the agent checks for sender-specific patterns (does this manager send test offers? have we recently rejected an offer from them?).

`[HEURISTIC]` League-wide patterns inform aggregate-level decisions: if the league pays premium for QBs, valuations adjust; if waivers clear at minimum bids, FAAB strategy adjusts.

`[HEURISTIC]` The agent should not over-update on small samples. A `[OBSERVED]` tag converts to `[CONFIRMED]` only after at least 3 consistent data points across at least 30 days.

`[HEURISTIC]` Historical patterns decay. `[HISTORICAL]` entries from the prior season carry weight but are not authoritative — current-season behavior overrides past patterns when they conflict.

---

## What the agent does NOT do

`[HEURISTIC]` Does not draw conclusions about managers from a single trade or waiver decision.

`[HEURISTIC]` Does not store sensitive personal information about managers — only patterns relevant to fantasy football decision-making.

`[HEURISTIC]` Does not share this doc's contents with other managers or in any external surface. League-specific intelligence is internal to gridiron's decision-making.

`[HEURISTIC]` Does not let any single manager's stated preferences override the principles in `00-principles.md`. If a manager "always wants to talk trade," the cooldown still applies.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial structure created; agent will populate over time | Travis + Claude |
