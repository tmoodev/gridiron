# 03 — Waiver Strategy

**Version:** 1.0
**Status:** Loaded on demand by the lineup/waiver agent. Drives FAAB allocation, target identification, and bid construction logic.
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md`, `01-valuation-philosophy.md`, `02-roster-construction.md`

---

## Purpose

This doc defines how Gridiron evaluates waiver targets, allocates FAAB, and structures bids across both leagues. The agent's waiver pipeline is: identify → evaluate → bid construct → propose. Every step except final approval is automatic; submission goes through the policy gate per `00-principles.md`.

---

## Hard gates (from principles)

`[RULE]` **10% FAAB ceiling for autonomous spending.** Any single claim above 10% of remaining FAAB requires Travis approval. No exceptions, no policy graduation override. This is the principles-level hard rule.

`[RULE]` **Drop pairing.** When the roster is at capacity, every add proposal must include a drop recommendation. Drops above the auto-drop threshold (per `00-principles.md` and `02-roster-construction.md`) require approval; drops within the auto-drop threshold can proceed if the add itself is approved.

---

## FAAB philosophy

`[HEURISTIC]` **Spend aggressively early; FAAB doesn't score points.** Industry consensus, validated repeatedly: legitimate league-winning waiver targets typically appear in weeks 1–4 (Puka Nacua 2023, Kyren Williams 2023, Bucky Irving 2024 archetype). The expected value of acquiring a top-12 player at any position dwarfs the value of preserved budget. Agent should bid aggressively on high-conviction early-season breakouts even though those bids will exceed the 10% ceiling and route through approval.

`[HEURISTIC]` **Budget partition (Silver method).** Mentally split the season's budget into two pools, even though it's one number on Sleeper:
- **Management budget** (~30% of total): weekly maintenance — bye-week fills, injury replacements with short shelf life, streaming pieces. Most claims fall here. Bids should be small ($1–$5 on $100 budget; $0 when feasible).
- **Maintenance/luxury budget** (~70% of total): difference-makers — players with multi-week or season-long upside, breakouts, lead-back-after-injury situations. Big bids come from this pool.

`[HEURISTIC]` **Per-league FAAB posture:**
- **Degeneration X (win-now 2026):** aggressive spending, especially weeks 1–6. Acquiring a difference-maker is worth 80%+ of budget if conviction is high. Late-season FAAB is far less valuable — the playoff push happens with the roster you've built. The agent should explicitly warn Travis when sitting on excess FAAB late in the season.
- **Home league (balanced):** measured. Spend on real upgrades, not chase. Conserve enough for injury replacements through the playoff push. The 70/15 posture from principles applies — prefer reliable additions over volatile breakouts unless the underlying signal is strong.

`[HEURISTIC]` **End-of-season FAAB.** Once playoffs begin (typical weeks 14–17), demand for available players drops as eliminated managers disengage. Late-season pickups often clear at minimum bids. The agent should note this in late-season recommendations and suggest holding bids low when the field is thin.

---

## Target identification

The waiver agent runs a continuous pipeline that surfaces targets. Inputs:

`[HEURISTIC]` **Primary signal sources:**
1. **Opportunity changes** — vacated targets, vacated carries, snap share jumps, role shifts (highest-quality signal)
2. **Sleeper trending adds/drops** — league-wide attention, useful as confirmation but not as a primary trigger
3. **Injury-driven role changes** — RB1 to IR with clear handcuff path, WR1 out with depth chart promotion behind
4. **Sustained underlying metrics** — 4+ weeks of 20%+ target share or 60%+ snap share without corresponding fantasy production (volume is sticky, regression upward is likely)
5. **Coaching/scheme changes** — OC firing, mid-season trade, system fit change

`[HEURISTIC]` **Per `01-valuation-philosophy.md`, never act on single-week samples.** A breakout-week box score is a flag for further investigation, not a buy signal on its own. Require 3+ weeks of evidence at a new baseline before classifying a player as a high-conviction target.

`[HEURISTIC]` **Avoid the trending-adds trap.** Sleeper trending data shows what other leagues are doing; it correlates with real value but lags actual signal and is sometimes wrong (recency bias, narrative chasing). Use it as a tiebreaker between similar targets, not as a primary driver.

---

## Bid construction

`[HEURISTIC]` **Default bid math (per $100 budget):**
The agent constructs a recommended bid using the following formula:

```
recommended_bid = base_value × situation_multiplier × league_posture × budget_factor
```

Where:
- **base_value** is the player's gridiron value translated to a FAAB percentage. Top-12 positional upside = 50–80%. Top-24 upside = 25–45%. Useful starter = 10–25%. Bench stash = 1–8%.
- **situation_multiplier** weights certainty (0.6–1.4). High-certainty (clear lead role after injury) = 1.2–1.4. Speculative (committee unclear) = 0.6–0.9.
- **league_posture** is 1.1–1.3 for Degeneration X (win-now), 0.85–1.0 for home league (balanced)
- **budget_factor** adjusts for remaining season and remaining FAAB. Early season + high budget = 1.0; mid-season + low budget = 0.7; late season + any budget = 0.5

`[HEURISTIC]` **Use odd-number bids.** Round numbers ($10, $20, $50) are most common across managers; bidding $11, $21, $51 wins ties at marginal cost. Standard FAAB hygiene per industry consensus.

`[HEURISTIC]` **Don't bid against yourself.** When the agent identifies a target with no obvious league competition (low trending volume, niche fit, deep dynasty stash), default to minimum viable bid — $0 if allowed, $1 otherwise. Save budget for contested targets.

`[HEURISTIC]` **Bid laddering for high-value targets.** When Travis approves a high-FAAB claim, the agent should also queue a backup target at lower priority — if the primary bid loses, the secondary claim still produces value rather than wasting the waiver run.

---

## Streaming positions

`[RULE]` **No FAAB on D/ST or K beyond $0/$1 minimum.** These positions are matchup-dependent volatility; spending budget on a one-week play is bad math. Add via $0 bid where allowed, otherwise $1. Drop them after the week and re-stream.

`[RULE]` **No FAAB on one-week TE or QB fills above 2% of budget.** Bye-week coverage and one-week injury fills at onesie positions are streaming targets, not investments. The exception: when the streamer has multi-week potential (injury to starter creates 3+ weeks of opportunity), bid construction follows the standard formula instead.

`[HEURISTIC]` **Streaming pipeline.** Maintain a rotating list of 2–3 stream candidates per onesie position, refreshed weekly based on next-week matchups, Vegas implied team totals, and injury reports. Surface in the dashboard's Construction tab as a "this-week streamers" section.

---

## Format-specific approaches

### Degeneration X (dynasty)

`[HEURISTIC]` **Hunt future assets, not just this-week production.** Dynasty waivers are most valuable when they surface young players with role expansion potential — backup RBs to aging starters, WR3s on teams about to lose their WR1 to free agency, rookies elevating on the depth chart. Target horizon is 1–3 years, not 1–3 weeks.

`[HEURISTIC]` **Aggressive on rookies who weren't drafted in startup.** Late-round rookies who flash early-season opportunity are dynasty gold — they cost FAAB now but become trade or starter assets for 2027+. Worth reaching above the standard formula's recommendation when the prospect profile is strong.

`[HEURISTIC]` **Less interest in aging veterans even if available.** A 30-year-old WR producing on waivers is a redraft pickup, not a dynasty asset. Bid only when win-now context justifies, and price as a rental.

### Home league (keeper)

`[HEURISTIC]` **Production now, keeper math next.** Primary filter is this-year production. Secondary filter is keeper-cost-adjusted value for next year — a young waiver pickup who would be a value keeper at low cost is a higher-priority target than a same-week production equivalent without keeper future.

`[HEURISTIC]` **Aging veteran rentals are fine here.** Unlike Degeneration X, the home league rewards short-horizon production for non-keepers. A 29-year-old RB on a hot streak is a defensible pickup if he wins games this year, even if he won't be kept.

`[HEURISTIC]` **Posture-aware aggression.** When the home league is in compete mode (per the week 4/8/12 reassessment), aggression matches Degeneration X. When in build mode, shift waiver targeting heavily toward young upside even at the cost of this-week production.

---

## Specific waiver patterns to exploit

`[HEURISTIC]` **The next-man-up RB.** The most reliable league-winning waiver pattern. When an RB1 goes down, the immediate backup with established pass-game role is the highest-conviction add of the season. Bid aggressively, expect contested bidding, structure proposal as a top-of-the-week priority.

`[HEURISTIC]` **The vacated targets WR.** When a WR1 goes to IR or gets traded, the WR2 on that offense gets a sustained target share bump. Less explosive than the RB case but more durable — usually 4–8 weeks of upgraded production.

`[HEURISTIC]` **The post-trade-deadline mover.** NFL trade deadline (typically late October) creates 2–3 actionable waiver targets per year — players who land in better roles or have new vacated opportunity. Surface these immediately as the trades happen, not waiting for the next waiver cycle.

`[HEURISTIC]` **The OC firing.** Mid-season OC changes (especially 0–4 starts to a season) frequently change RB workload distribution and pass-game target distribution within 2 weeks. Watch for these and reassess affected players' opportunity metrics quickly.

`[HEURISTIC]` **The sophomore breakout.** Per `01-valuation-philosophy.md`, year-2 WR and TE breakouts are one of the strongest patterns in fantasy. Sophomore players showing early-season opportunity bumps are high-conviction targets even before fantasy production catches up.

---

## Patterns to avoid

`[HEURISTIC]` **Single-week fantasy hero chase.** A bench guy who scored 30 points in a perfect game script is rarely the next Puka Nacua. Underlying volume usually doesn't support a repeat. Surface as "watching" but not as a high-priority target unless target share + role corroborate.

`[HEURISTIC]` **Aging veterans on hot streaks (without volume).** Per `01-valuation-philosophy.md`, efficiency-driven hot streaks regress; volume-driven hot streaks sustain. Aging vets on hot streaks are usually the former — the agent should explicitly distinguish in reasoning.

`[HEURISTIC]` **Handcuffs to your own RB1 in the home league bench philosophy.** Per `02-roster-construction.md`, value-handcuff the league rather than yourself. Spending FAAB on your own RB1's backup concentrates injury risk; spending the same FAAB on another team's high-upside RB2 distributes it.

`[HEURISTIC]` **Speculative kicker/DST chasing.** A defense that pulled in 4 sacks last week and is now "trending" doesn't carry that performance forward at high rates. Streaming via $0 bids, no exceptions.

---

## Bid timing

`[HEURISTIC]` **Sunday night / Monday morning waivers** (most common in both leagues — Phase 0 confirms): the agent's primary waiver work happens Tuesday morning ahead of the typical Tuesday/Wednesday processing window. Final review and bid adjustment happens within 6 hours of waiver close.

`[HEURISTIC]` **Free agency between waiver runs.** Once waivers process, players who clear go to free agent status (FCFS in many leagues). The agent should have free-agent targets queued so it can act immediately when waivers clear, not waiting for the next cycle.

`[HEURISTIC]` **Pre-Sunday strategic adds.** Some pickups make sense before the weekend (covering an injured starter for the week's lineup). These are usually low-conviction streamers and follow the management-budget bidding tier.

---

## Edge cases

`[HEURISTIC]` **FAAB trades.** Both leagues allow FAAB as a tradeable asset. Treat FAAB dollars as a depreciating currency — early-season FAAB has more value than late-season FAAB because there's more time for it to acquire impact players. The agent should value FAAB in trade proposals using a rough rule: $1 of FAAB at week 1 ≈ $1.50 of FAAB at week 8 ≈ $0.75 of FAAB at week 14.

`[HEURISTIC]` **Multi-claim conflicts.** When the agent wants to bid on multiple players in the same waiver run and total bids approach available budget, it must explicitly prioritize and surface the ranking to Travis. Submitting all claims at full bid risks blowing the budget on one and leaving other claims at zero.

`[HEURISTIC]` **Defensive adds.** Sometimes worth claiming a player not because you want them, but to deny a contender in your league. The agent should propose these explicitly labeled as defensive and only when the cost is low (≤5% FAAB) and the recipient denial has clear playoff-race implications. Always requires approval.

`[HEURISTIC]` **Empty waiver runs.** When no high-conviction targets exist, the agent should not invent claims to fill a quota. A quiet waiver week is fine. Surface "no actionable targets this week" in the dashboard's Recommendations area as a positive signal, not a gap.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
