# 04 — Trade Strategy

**Version:** 1.0
**Status:** Loaded on demand by the trade agent for proposal scanning, draft, evaluation of incoming offers, and counter construction.
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md` (hard gates and per-manager rules), `01-valuation-philosophy.md` (the three valuation views), `02-roster-construction.md` (roster shape), `03-waiver-strategy.md` (FAAB as currency)

---

## Purpose

This doc defines how Gridiron initiates, evaluates, structures, and responds to trades. Trades are the highest-leverage decisions the agent makes — and the most socially expensive ones. Per `00-principles.md`, trade actions ALWAYS propose, never auto-execute. This doc governs what gets proposed and how.

---

## Hard rules (from principles)

`[RULE]` **All trade actions require Travis approval.** Sending, accepting, countering, rejecting (formally — see "passive ignore" below for the case where no response is needed). No exceptions, no graduation override.

`[RULE]` **Never trade a 1st-round rookie pick without approval.** 2nds and later have agent latitude per this doc; 1sts always go to Travis.

`[RULE]` **Trade cooldown:** no more than one outgoing proposal to the same manager per 7 days, in either league.

`[RULE]` **Home league dinner-defense test:** every home league trade proposal — incoming or outgoing — must pass the "could this be defended at the league dinner" test. Both sides plausibly improve. Value gap is defensible. If a proposal would look like collusion or fleecing to a long-time league member, do not surface it.

`[RULE]` **amoore324 (Travis's brother, Degeneration X):** wide latitude — concentration plays, weird position swaps, off-meta archetype trades all on the table. The cooldown still applies but the dinner test does not.

---

## Posture drives everything

`[HEURISTIC]` **The agent classifies each league's current posture before evaluating any trade.** Posture is not static — it's reassessed per `00-principles.md` (DX is full win-now for 2026; home league reassesses at weeks 4/8/12). Trade evaluation logic differs by posture:

**Contender (DX 2026, home league when in compete mode):**
- Pay premium for win-now production (veterans, RBs, top performers this season)
- Trade future picks for current production aggressively, within rookie pick gates
- Sell young upside that won't help win this year for proven this-year producers
- Trade deadline timing matters — front-load aggression before deadline

**Rebuilder (home league when in build mode):**
- Trade aging veterans for picks and young upside
- Pay premium for rookies, draft picks, second-year players, players returning from injury whose pre-injury production was elite
- Avoid acquiring 28+ players unless at deeply discounted prices
- Don't sell young breakout candidates unless return is overwhelming

**Balanced / 2–3 year window (home league default):**
- Don't pay aggressive contender prices, don't accept rebuilder discounts
- Sweet spot is 2nd–3rd year players who are producing or about to
- Aging vets okay only as accretive pieces, not core assets
- Picks held strategically; trade them when value gap is clear

---

## Initiating outgoing trades

### Target identification

`[HEURISTIC]` **Daily roster scan across both leagues.** The trade agent compares every other team's roster against gridiron's valuation model and surfaces value mismatches. Three primary signals:

1. **Position imbalance.** Other team is RB-heavy, thin at WR; we're the inverse. Construction-driven trade — both sides plausibly improve.
2. **Age curve mismatch.** Other team has aging players we want to trade for value, or young upside we want at our price point.
3. **Posture mismatch.** Their roster shape suggests posture incompatibility (rebuilder still rostering 30-year-old WRs, contender hoarding rookies). Posture-mismatch managers are often the most willing trade partners — they don't yet know what they should be.

`[HEURISTIC]` **Roster fit comes before raw value.** A trade that's "fair" by KTC value but doesn't address a roster construction need is a low-priority surface. The agent should not propose value-equivalent trades that leave the roster shape unchanged.

### Structuring proposals

`[HEURISTIC]` **2-for-1 premium.** When trading two pieces for one better piece, charge a 10–15% premium on the values (industry standard). When receiving two pieces for one better piece, accept only if the package premium is at least 10% above straight value.

`[HEURISTIC]` **Picks as currency, valued by posture and timing:**
- A 2026 1st has high value to rebuilders, lower to contenders. Trade direction follows.
- Mid-late 2nds are the most-traded asset in dynasty — useful sweeteners and useful targets when buying veteran production
- Future-year picks (2027, 2028) carry uncertainty discount; the agent values them at ~80% of the equivalent next-year pick
- Per `03-waiver-strategy.md`, FAAB dollars are tradeable currency in both leagues with similar depreciation logic

`[HEURISTIC]` **Avoid round-numbered offers.** $11 beats $10 in FAAB; trade structure follows similar logic. A package that's "obviously fair" by surface math gets countered more often than one that's slightly unconventional. Mix asset types — a player + pick is harder to compare than two players, which gives the offer room to clear without negotiation.

`[HEURISTIC]` **Lead with the trade thesis, not the math.** When the agent surfaces a proposal, the first sentence should describe the strategic logic ("this trade gets us a top-12 RB at the cost of bench depth we don't need, and Carson — the receiving manager — has been thin at WR for three weeks"). Math is supporting evidence, not the headline.

### When NOT to initiate

`[HEURISTIC]` **Don't propose value-symmetric trades.** A trade where both sides see equal value movement is unlikely to be accepted and burns the cooldown for nothing.

`[HEURISTIC]` **Don't propose trades that move marginal value.** A trade that improves the roster by less than ~5% projected weekly points or less than ~3% dynasty value is not worth the social capital. Surface as "watching" rather than as a proposal.

`[HEURISTIC]` **Don't propose to recently-rejected counterparties.** If a manager has rejected the last two proposals, cool off for 14 days regardless of the standard 7-day cooldown.

`[HEURISTIC]` **Don't propose trades immediately after a player blow-up game.** The agent's value hasn't moved (per `01-valuation-philosophy.md`'s rule against single-game adjustments), but the counterparty's perception probably has. Wait 1–2 weeks for the market to settle.

---

## Evaluating incoming offers

### Decision framework

`[HEURISTIC]` **Three-pass evaluation:**

**Pass 1 — Construction fit.** Does this offer move the roster toward target shape per `02-roster-construction.md`? If no, default toward rejection regardless of value math.

**Pass 2 — Posture alignment.** Does the offer match current league posture? Contender accepting future picks for current production is a posture mismatch (likely reject). Rebuilder accepting an aging vet for young upside is a posture mismatch (likely reject).

**Pass 3 — Value math.** Run the trade against the gridiron valuation blend. Surface the gap as a percentage of total trade value. Apply 2-for-1 premium logic where applicable.

`[HEURISTIC]` **Counter offer construction.** When the offer is close but not quite there, the agent should propose a counter that:
- Moves value our way by 5–15% (not more — managers reject lopsided counters)
- Addresses the same construction need they identified (don't reject their thesis, refine it)
- Sometimes adjusts asset mix rather than total value (their player + our pick instead of their player + our worse player)

### Joke-rejection for clear test offers

`[HEURISTIC]` Per `00-principles.md`, lopsided incoming offers that look like manager tests get a joke reply with polite decline. The joke is at the situation's expense, never the manager's. Dry, self-aware, never mean.

The agent recognizes a test offer by these markers (any two suggest a test):
- Offered piece(s) total value <40% of requested piece(s) value
- Offered piece(s) are clearly stale assets (aging RB, 30+ WR, suspended player)
- Manager has sent a similarly-shaped offer to other managers in the league recently (where visible)
- Manager has historically sent test offers (track record, surfaced from decision log)

**Joke construction guidance:** keep it short, make the joke about the offer being lopsided in some absurd way, decline politely, leave the door open for a reasonable counter. Example tone (illustrative — agent generates fresh per situation): "I appreciate the creativity but I think you may have stapled the wrong page to your offer. Happy to talk if you've got something closer to even — what about [something reasonable]?"

`[HEURISTIC]` **Never joke-reject in the home league.** Per principles, the home league's social dynamics are different — even bad offers from long-time friends deserve a straight, polite decline with a brief reason. Save the joke replies for DX.

### Passive ignore

`[HEURISTIC]` **Some offers warrant no response.** Sleeper allows offers to expire without action. The agent should propose passive ignore (rather than active rejection) when:
- The offer is obvious spam/test in a league where joke rejection isn't appropriate (home league)
- The counterparty is on the recent-rejected cooldown list
- The offer would consume a turn of communication better used on a different proposal in flight

Passive ignore still requires Travis approval — the agent surfaces the offer, recommends "let expire," and explains why.

---

## Format-specific dynamics

### Degeneration X (full dynasty, win-now 2026)

`[HEURISTIC]` **Trade aggression mode: high.** Lean toward action over patience. Win-now means the marginal week of holding before the trade deadline costs more than getting 90% of the right deal now.

`[HEURISTIC]` **Picks vs. veterans calculus is contender-shaped.** Trade 2027 1sts for win-now production when the production tier is real (top-12 at position). Don't trade 2027 1sts for marginal upgrades. Per principles' "don't torch the future entirely" guardrail, the agent should never trade away every future 1st in a single window.

`[HEURISTIC]` **Aging RB sell window applies aggressively.** Per `01-valuation-philosophy.md`, RBs at 26–27 should lean toward sell. In DX, the natural buyer is another contender willing to pay current production prices. Surface these as outgoing proposals when win-now value can be secured at younger positions or via picks.

`[HEURISTIC]` **The amoore324 lane.** Travis's brother is in this league. Per `00-principles.md`, wide latitude. Specific applications:
- Concentration trades — package multiple bench pieces for one elite roster upgrade
- Position swaps that look weird on paper — RB-heavy team taking on more RB risk for a clear WR upgrade, etc.
- Pick swaps with unusual structures — multiple late-round picks for one early pick, or vice versa
- Speculative young-for-young trades (we like ours more, he likes his more, both can be right)

The dinner test does not apply here. Standard cooldown still applies.

### Home league (keeper, 10-year history)

`[HEURISTIC]` **Trade aggression mode: measured.** Patience over action. The home league rewards relationship preservation; rushed proposals burn social capital that costs more than the marginal trade gain.

`[HEURISTIC]` **Rentals are a thing.** In keeper format, non-keeper players are explicitly modeled as expiring contracts. Their value drops to zero at year-end. Trade implications:
- **Buy expiring contracts cheap from contenders eliminated from playoff race** — late-season pickups for next year's picks
- **Sell expiring contracts expensive to contenders making playoff push** — Travis's surplus rentals for picks, especially when the home league posture is build-mode
- The agent should explicitly track each player's keeper-cost-adjusted vs redraft value gap; large gaps signal rental status

`[HEURISTIC]` **Dinner-defense test is non-negotiable.** Every proposal — incoming or outgoing — must defensibly improve both sides. The agent surfaces this as part of the proposal reasoning: "Both sides improve because [X gets WR2 they need at fair value, Y gets RB depth they're thin on]."

`[HEURISTIC]` **Value gap ceiling for outgoing proposals.** No outgoing home league proposal where the gridiron value gap exceeds 12% in our favor. Above that threshold, the proposal won't pass the dinner test even if mathematically defensible. Reduce the gap to 12% or below before surfacing.

`[HEURISTIC]` **Picks and FAAB as the social-friendly currency.** Trades involving picks and FAAB dollars are easier to defend at the dinner than trades involving stars, because the value of picks/FAAB is more abstract. When in doubt, structure home league offers around picks/FAAB rather than headline-name swaps.

---

## Trade timing windows

`[HEURISTIC]` **Pre-season (June–August).** Prime trade season for dynasty. Markets are fluid, opinions are shifting based on offseason news (free agency, rookie draft, depth chart changes). Highest volume of agent proposals in this window.

`[HEURISTIC]` **Weeks 1–3.** Volatility is high; managers overreact to small samples. Mostly DON'T trade here — let managers tilt themselves into bad decisions, then surface buy-low candidates in week 4–6 once dust settles.

`[HEURISTIC]` **Weeks 4–8.** Prime in-season trading window. Postures clarify (per the home league reassessment cadence). Buy low / sell high opportunities are most actionable.

`[HEURISTIC]` **Weeks 9 to trade deadline (typically week 11–13).** Maximum aggression for contenders, especially DX. Last chance to trade for win-now. Surface trade deadline date prominently in the dashboard once Phase 0 confirms it per league.

`[HEURISTIC]` **Post-deadline through end of season.** Trades shut off. Focus shifts to lineup optimization and waivers.

`[HEURISTIC]` **Offseason after season ends.** Second-best window after pre-season for dynasty. Veteran sells while their value is freshest, picks trades around the rookie draft.

---

## Specific trade patterns

`[HEURISTIC]` **Sell-high on sustained efficiency, hold on sustained volume.** Per `01-valuation-philosophy.md`, efficiency regresses, volume sticks. A player on a hot streak driven by efficiency is a sell candidate; a player on a hot streak driven by target share growth is a hold.

`[HEURISTIC]` **Buy the dip on injured young players.** Pre-injury production was elite, market has discounted, recovery is on schedule — classic dynasty buy. Especially valuable when targeting a rebuilder.

`[HEURISTIC]` **Sell the post-injury bounce-back narrative.** Player returns from injury, plays one good game, market overcorrects upward. Sell into the spike before regression sets in.

`[HEURISTIC]` **Package depth into stars.** Per stars-and-scrubs roster shape in DX, consolidating two mid-tier players into one elite player at the same position is a high-leverage move. Use this aggressively in DX. In home league (balanced), use sparingly.

`[HEURISTIC]` **Trade for rookie picks in offseasons before strong rookie classes.** Rookie pick value is heavily class-dependent. The agent should flag known strength assessments of upcoming classes (e.g., "the 2027 RB class is reportedly thin") and adjust pick valuations accordingly.

`[HEURISTIC]` **The contender-rebuilder symmetry trade.** A contender selling future for now and a rebuilder selling now for future is the cleanest dynasty trade pattern. Both sides plausibly improve, both sides match posture. Highest acceptance rate. The agent should preferentially surface trades that fit this pattern.

---

## Communication style

`[HEURISTIC]` **Outgoing proposal messages.** Per principles, decision-engine voice — concise, conclusion-first. The Sleeper trade UI doesn't include free-form messaging by default, but if Travis wants to add context (typical for the home league), the agent drafts a 1–3 sentence note: trade thesis up front, why it works for both sides, leave space for counter.

`[HEURISTIC]` **Incoming offer reasoning.** The proposal card surfaces:
1. One-line conclusion ("Reject — value gap 18% in their favor with construction misalignment")
2. The construction analysis (does it move our roster toward target shape?)
3. The posture analysis (does it align with current league posture?)
4. The value math (gridiron value gap, with constituent KTC/FantasyCalc/internal disagreements surfaced if material)
5. The recommended counter, if any

`[HEURISTIC]` **Decision logging.** Per principles, every proposal goes to `FF#DECISION#...` with full reasoning. Trade decisions especially — six months later, "why did we accept that?" needs a real answer.

---

## Edge cases

`[HEURISTIC]` **Three-team trades.** Sleeper supports them. They're high-variance and hard to evaluate. Default agent posture: surface as "watching" rather than initiating, and require explicit Travis approval before any send. Incoming three-team offers get extra scrutiny — the third party is sometimes a fig leaf for an unbalanced two-way deal.

`[HEURISTIC]` **Trade deadline panic mode.** As the deadline approaches and contenders haven't made moves, the market gets desperate. Prices on win-now veterans spike; rebuilder leverage peaks. The agent should not let DX get caught flat-footed — propose contender moves no later than 7 days before deadline if construction needs aren't met.

`[HEURISTIC]` **Mid-trade injury news.** A player in an active proposal gets hurt. The agent immediately flags this to Travis with a recommendation to withdraw or hold. Never silently let a proposal continue when the underlying value has materially changed.

`[HEURISTIC]` **Veto risk in home league.** Long-running leagues sometimes have informal or formal veto culture. If a proposal looks lopsided enough that it might be vetoed, the agent should flag this proactively in the proposal reasoning. Better to make a smaller, defensible trade than a larger one that gets reversed and damages relationships.

`[HEURISTIC]` **Trade with eliminated team in home league.** Once a manager is mathematically eliminated from playoffs, they often disengage. Late-season trade attempts with eliminated managers have low acceptance rates but high value when accepted (rebuilder seller, contender buyer). Surface these aggressively in weeks 12–13.

---

## What the agent does NOT do

`[RULE]` Does not execute trade actions without Travis approval. Always.

`[HEURISTIC]` Does not propose trades that violate `00-principles.md` hard gates.

`[HEURISTIC]` Does not propose more than 3 outgoing trades per league per week, regardless of opportunity. Trade volume signals desperation; high-volume proposals get rejected even when individually fair.

`[HEURISTIC]` Does not propose trades to managers within 24 hours of any communication that suggests they're not in trading mode (e.g., recent league chat indicating they're "happy with the team," "not making moves until offseason," etc., where parseable from Sleeper league chat).

`[HEURISTIC]` Does not chase a trade after a counter has been rejected. One counter, then walk away. Pursuit signals desperation and lowers future acceptance odds.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
