# 01 — Valuation Philosophy

**Version:** 1.0
**Status:** Loaded on demand by the valuation agent (`valuation_agent.py`) and referenced by trade and waiver agents when evaluating player value.
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md` (always-loaded posture and gates)

---

## Purpose

This doc defines how Gridiron computes and reasons about player value. It produces three outputs per player per league context: dynasty value, keeper-cost-adjusted value, redraft value. This doc covers the principles behind those numbers and where the agent should defer to its own model versus the market.

---

## Core stance

`[HEURISTIC]` **Production > volume > efficiency.** When predicting future fantasy output, weight in this order: actual production (what they did), volume/opportunity (targets, carries, target share, TPRR), efficiency (YPRR, YPC, YAC). Efficiency regresses hard year-over-year; volume sticks; production sticks most of all when sustained. A player with high target share and average efficiency is more reliable than the inverse.

`[HEURISTIC]` **Opportunity-first refinement.** Among volume metrics, prefer in order: first-read target share (where available) > target share > targets per route run (TPRR) > raw targets > snap share. For RBs: weighted opportunity (red zone and goal-line carries valued higher) > raw touches.

`[CONTEXT]` 20%+ target share over 4+ games is the rough threshold for "primary option" designation. 1–2 game samples are dominated by game script and don't move valuation meaningfully. The agent should not chase one-week breakouts; require sustained signal.

---

## Age curves and decline framing

`[HEURISTIC]` Maintain **both** the age-curve view and the mortality-table view for every aging player, and use them for different purposes:
- **Age curve** (expected production at age N) → use for trade-value math. Answers "what will I get next year if I hold?"
- **Mortality table** (probability of remaining fantasy-relevant at age N+1) → use for sell decisions. Answers "what's the binary risk of falling off a cliff?"

When the two views disagree materially on a specific player (e.g., age curve says hold, mortality says sell), surface both in the player drawer's reasoning so Travis can choose.

### Position-specific curves (modern era, post-2010)

`[HEURISTIC]` **RB peak: 24–28. Sell window: 26–27.** This is more aggressive than older consensus and reflects current data — peak seasons cluster tightly, the cliff at 29 is real, and ~6–8% of post-2010 peak seasons come from age 29+. RBs who fail to break out by year 2 should be downgraded.

`[RULE]` **One-year-too-early instinct applies to RBs only.** For an RB at the late edge of the sell window (age 26+), the agent should lean toward selling rather than holding, even at a slight discount to current market. This rule does not apply to WR, TE, or QB — they age more gracefully and the same instinct produces avoidable losses at those positions.

`[CONTEXT]` Travis is willing to trade aging RBs for early-round draft picks in the following season. This is a default acceptable structure for selling 26+ RBs.

`[HEURISTIC]` **WR peak: 25–28. Sell window: 29–30.** Decline begins in earnest at 30. Elite separators (Hopkins, Adams, Mike Evans archetype) sometimes sustain into 31–32, but they're outliers — don't plan around being one.

`[HEURISTIC]` **Late-career WR posture: aggressive fade at 30+ regardless of pedigree.** Same posture for injury-prone stars and durable aging stars. Treat aging WRs as trade vehicles — buy on dips, sell on heaters. Surface arbitrage opportunities (player on a hot streak whose age makes them a sell-high target) as recommendations. Per principles, this is especially salient in the home league.

`[HEURISTIC]` **TE peak: years 5–6 in the league. Decline year 7.** Sophomore-year breakout (year 2) is one of the strongest patterns in fantasy — bias toward second-year TEs as buy candidates when draft capital and opportunity align.

`[HEURISTIC]` **QB plateau, not curve.** QBs are productive from 25 through mid-30s. Age does not meaningfully drive QB valuation until late 30s. In superflex contexts, this makes young QB1s the most stable dynasty asset class — value them accordingly.

---

## Power-law and concentration

`[HEURISTIC]` **Fantasy outcomes follow power laws, not normal distributions.** The top 5% of player-weeks dictate championship outcomes. Standard expected-value math underweights ceiling.

`[HEURISTIC]` **Per-league posture on power-law thinking:**
- **Degeneration X (win-now 2026):** lean into concentrated upside bets. Prefer ceiling over floor on borderline calls. Bet on the player who can win you a week, not the player who can't lose you one.
- **Home league (balanced):** prefer reliable production. Floor matters as much as ceiling. The 70/15 posture from principles applies here.

`[HEURISTIC]` Talent at the top is non-replaceable. The Jerry Rice / Tom Brady / Tony Gonzalez archetype ages more gracefully than averages suggest. When evaluating an aging elite player, weight their established production more heavily than the position-wide age curve.

---

## Buy-low / sell-high signal detection

`[HEURISTIC]` **Buy-low triggers (when underlying metrics support):**
- Player returning from injury whose pre-injury target share or workload was elite
- Player on a cold streak whose underlying opportunity metrics (target share, snap share, TPRR) remain stable or rising
- Player whose offense changed mid-season in a way the market hasn't priced in (new OC, new QB, vacated targets)
- Sophomore WR or TE not yet broken out who has trending opportunity signal

`[HEURISTIC]` **Sell-high triggers:**
- Aging player on a hot streak that outpaces underlying volume (efficiency-driven, likely to regress)
- One-year-wonder profile: career year by a player without prior top-12 finishes, especially if late-twenties+
- Aging RB at the edge of the sell window (per the one-year-too-early rule)
- Player whose team is likely to add competition for touches (high draft capital incoming, free agency adds)

`[HEURISTIC]` **Distinguish efficiency-driven hot streaks from volume-driven hot streaks.** Volume-driven streaks tend to sustain; efficiency-driven streaks tend to regress. The agent should explicitly call this out in trade reasoning.

---

## External value sources and the gridiron blend

`[CONTEXT]` Two market sources are pulled daily:
- **KeepTradeCut (KTC)** — crowdsourced, reflects market sentiment, slower to react to news
- **FantasyCalc** — more algorithmic, reacts faster, occasionally overreacts

Each is useful, neither is sufficient on its own. Crowdsourced values lag breaking news; algorithmic values overrespond to small samples.

`[HEURISTIC]` **Gridiron value blend (default weighting):**
- 40% KTC baseline
- 30% FantasyCalc baseline
- 30% gridiron-internal model (age curve + opportunity metrics + scoring-format adjustment)

The blend is the headline number routed to all decisions. The player drawer surfaces all three constituent values plus the blend, so disagreements between sources are visible.

`[HEURISTIC]` **When sources disagree by more than 20%**, the agent should surface the gap explicitly in any decision involving that player. Material disagreement is itself a signal — usually one source is reacting to recent news the other hasn't priced in yet.

`[HEURISTIC]` **Weighting may shift over time.** As the gridiron-internal model matures and gets validated against actual outcomes, its weight in the blend may increase. Travis approves any rebalancing of the blend before it ships.

---

## The three valuation views

`[RULE]` Every player carries three values keyed to league context:

### Dynasty value (used in Degeneration X)
- Long-horizon, age-weighted
- Rookie picks priced as comparable inventory (see `06-dynasty-rookie-draft.md` when written)
- Source blend: dynasty KTC + dynasty FantasyCalc + internal age-curve model
- Adjusted for Degeneration X scoring (read from `FF#LEAGUE#1331779473430810624`)

### Keeper-cost-adjusted value (used in home league)
- This-year production projection minus the league's keeper cost for that player
- A WR projected to finish round 3 kept at round 5 cost is high-value; the same WR kept at round 1 cost is a pass
- Source: redraft projections + league keeper cost formula (read from `FF#LEAGUE#1183557197018804224`)
- Used for keeper selection decisions and in-season trade evaluation of likely-kept players

### Redraft value (used in home league for non-keeper pieces)
- Pure this-season expected production, no carryover
- Used for evaluating non-keeper trade pieces (rentals) and for the home league snake/auction draft on non-kept slots
- Standard redraft rankings adjusted to league scoring

`[RULE]` **Scoring-format adjustments are automatic, not manual.** The agent reads `scoring_settings` and `roster_positions` from each league's `FF#LEAGUE#...` record (seeded in Phase 0) and adjusts values accordingly. PPR vs. half vs. standard, TE premium, superflex, 6-pt vs. 4-pt passing TDs, long TD bonuses, yardage thresholds — all automatic. Travis does not configure these per league.

`[CONTEXT]` Significant scoring sensitivities to be aware of in the adjustment logic:
- PPR vs. half-PPR shifts pass-catching RBs and slot WRs by ~10–15% relative to volume rushers and outside WRs
- TE premium (1.5 PPR for TEs) flattens the WR-TE gap at the top; mid-tier TEs become rosterable assets
- Superflex / 2QB ~3x QB values; QB scarcity becomes the dominant roster-construction force
- 6-pt passing TDs vs. 4-pt move QB1-vs-QB12 gap by ~30%
- Long TD and yardage bonuses tilt slightly toward boom/bust profiles

---

## Edge cases

`[HEURISTIC]` **Rookies in their first 6 weeks.** Insufficient signal to update valuation materially based on early-season production. Hold draft-capital-based prior valuation; let opportunity metrics (snap share, route participation) move the needle, not raw fantasy points.

`[HEURISTIC]` **Mid-season trades and depth chart changes.** When a player's environment changes materially (trade, OC firing, QB change, injury to a teammate that vacates touches), the agent should re-run that player's valuation within 24 hours of the change rather than waiting for the daily refresh.

`[HEURISTIC]` **Players returning from major injury.** Apply a recency discount until they've played 3+ games at expected workload. The market typically prices these correctly; the agent should not chase pre-injury values until the workload confirms.

`[HEURISTIC]` **Suspended players.** Discount value by the games suspended at full zero, plus a 15% additional discount for ramp-up uncertainty on return. Surface as a sell candidate if the manager has a contender posture and another roster spot would help win-now.

`[RULE]` **Never adjust a player's value based on a single game's outcome.** One-week swings up or down do not move the gridiron value. Trends require minimum 3 games of evidence at a new baseline.

---

## Validation and disagreement

`[HEURISTIC]` **The agent should track its own accuracy.** Log every valuation prediction (player, value, date) and compare against subsequent KTC/FantasyCalc movement and actual production outcomes. This becomes calibration data for adjusting the gridiron-internal model weights over time.

`[HEURISTIC]` **When the gridiron-internal model strongly disagrees with both KTC and FantasyCalc**, default to caution: surface the disagreement to Travis rather than acting on internal conviction alone. The market is sometimes wrong, but it's wrong less often than any single model. Ramp confidence in internal disagreement only after sustained validation.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
