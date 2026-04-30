# 02 — Roster Construction

**Version:** 1.0
**Status:** Loaded on demand by lineup/waiver and trade agents when evaluating roster fit, depth, and construction problems.
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md`, `01-valuation-philosophy.md`

---

## Purpose

This doc defines what a healthy roster looks like in each format and how the agent diagnoses construction problems (positional gaps, age imbalance, depth weaknesses) that should drive trade and waiver recommendations. The "Construction" tab in the dashboard renders directly from these heuristics.

---

## Core principles

`[HEURISTIC]` **WR is the foundation, RB is the accelerator.** WRs have longer shelf life, more predictable production, and stickier opportunity. Build the WR room first, anchor the RB position with one-to-two elite pieces, and treat RB depth as a churning concern (waivers, trades, handcuffs).

`[HEURISTIC]` **Talent over situation.** When evaluating a player vs. a comparably-priced alternative, weight talent and draft capital more heavily than current team context. Situations change — talent is the constant. The Jonathan Taylor vs. Clyde Edwards-Helaire archetype is canonical: bet on the prospect, not the depth chart.

`[HEURISTIC]` **Power-law roster shape per league** (per `00-principles.md`):
- Degeneration X (win-now): stars + scrubs. Concentrate value in 4–5 elite pieces. Bench is upside lottery tickets.
- Home league (balanced): wider distribution. Reliable contributors over concentrated stars. Bench is mix of upside and reliable backups.

---

## Target roster shapes

Both targets are diagnostic — the Construction tab compares actual roster against these defaults and surfaces gaps. They are not hard requirements.

### Degeneration X (dynasty, 2026 win-now)

`[HEURISTIC]` **Age mix target:** 50% of starters age ≤25, 50% age 26+. Win-now posture justifies older proven production; dynasty floor still demands a young core for 2027+.

`[HEURISTIC]` **Position priority order:**
1. Elite WR room — minimum 3 startable WRs, minimum 1 in the top 12 dynasty WR tier
2. RB1 anchor — one top-12 dynasty RB; everything else at the position is upside chase
3. QB — superflex format (per Phase 0 confirmation) elevates QB to top priority alongside WR. In single-QB, QB drops to fourth priority
4. TE — one startable, one stash. TE premium (if confirmed in Phase 0) elevates this further

`[HEURISTIC]` **Bench philosophy:** upside lottery tickets. Prefer 22-year-old WR3-on-his-team breakout candidates over 28-year-old reliable RB3 handcuffs. The bench is where dynasty leagues are won, and reliability is for the starting lineup.

`[HEURISTIC]` **Taxi squad:** rookies and second-year players only. Never veterans, never injured veterans. The taxi is dynasty inventory storage; using it on a veteran wastes the slot.

`[HEURISTIC]` **IR slot usage:** aggressive. Any IR-eligible player with non-trivial future value gets stashed. The opportunity cost of an active roster spot is higher than the opportunity cost of an IR slot.

### Home league (keeper, balanced)

`[HEURISTIC]` **Age mix target on the kept portion:** 70% age ≤26, 30% older. Young keepers extend value year-over-year; older keepers should be high-conviction win-now pieces or low-cost value plays only.

`[HEURISTIC]` **Position priority order:**
1. Elite WR room — minimum 3 startable WRs
2. RB1 anchor with at least one viable RB2
3. QB tier appropriate to format (read from Phase 0)
4. TE — one startable

`[HEURISTIC]` **Bench philosophy:** reliable backups + bye-week coverage + a handful of upside fliers. The home league's redraft component means most non-keeper bench players are rentals — fewer lottery tickets, more functional pieces.

`[HEURISTIC]` **Keeper rotation:** with cost escalation in most keeper leagues (Phase 0 will confirm specifics), favor cycling fresh value plays into keeper slots rather than holding the same core indefinitely. A young player kept at low cost outperforms an aging star kept at premium cost over 2–3 year horizons. Exception: when escalation is mild and the player remains elite, hold.

---

## RB strategy

`[HEURISTIC]` **Default approach: situation-dependent, Hero RB as the prior.** Hero RB is the analytically-strongest single strategy per industry consensus, but rigid adherence is suboptimal — actual roster decisions should adapt to current roster shape, available trade partners, and league context.

`[HEURISTIC]` **Operational rules:**
- Anchor with at least one top-12 dynasty RB in each league. If you don't have one, target one via trade.
- Prefer pass-catching RBs over plodders in PPR formats — higher floor, survives committee splits, better trade liquidity.
- After the anchor, build RB depth aggressively from waivers and middle-round dynasty trades. The position has high turnover; depth is the win.
- Avoid concentrating dynasty capital in 28+ RBs (per `01-valuation-philosophy.md` sell window). One older RB on a contender is fine; two is a roster-design problem.

`[HEURISTIC]` **Handcuff philosophy: value-handcuff the league, not yourself.** Roster other teams' high-upside RB2s — backs with clear paths to lead roles if the starter goes down. These are bench assets that double as trade leverage when the lead back gets hurt. Self-handcuffing concentrates injury risk on a single backfield instead of distributing it.

Exception: in Degeneration X (win-now), if your RB1 is a workload-dependent star with injury history, self-handcuffing for one season is defensible insurance. The agent should propose this only when explicitly justified.

---

## Diagnostic heuristics for the Construction tab

The dashboard's Construction tab surfaces roster problems automatically. Diagnostic rules:

`[HEURISTIC]` **Positional value heatmap.** For each position, compute roster's total positional value vs. league median. Color hot/cold. Surface explicit gaps as text ("WR is 18% below league median; bottom-3 in league at the position").

`[HEURISTIC]` **Age curve diagnostic.** Plot roster value by age bucket (≤22, 23–25, 26–28, 29+). Compare against league average. Surface imbalances — "you're old at RB" or "you have no WRs over 26" — as natural-language flags.

`[HEURISTIC]` **Starter dependency score.** What percentage of weekly projected points comes from your top 3 starters? High dependency (>55%) = fragile roster, one injury away from collapse. Surface as a risk flag with implied trade need.

`[HEURISTIC]` **Trade need diagnosis.** Generate a one-paragraph natural-language summary per league: "You're WR-heavy with three top-30 WRs but thin at RB depth. Top 2 RBs combine for 38% of weekly points — a single injury collapses the lineup. Targets: middle-tier RB2s, especially pass-catchers in PPR-friendly offenses."

`[HEURISTIC]` **Bench score.** Evaluate bench quality on two axes — upside (young, breakout potential, value trending up) and reliability (functional starter if needed). Per league bench philosophy, score the actual bench against the target axis.

`[HEURISTIC]` **Rookie pick inventory (Degeneration X only).** Track owned rookie picks (1sts, 2nds, 3rds, by year). Surface as Construction tab summary alongside player roster. Picks are dynasty inventory and roster shape evaluation must include them.

---

## Roster churn and bench management

`[HEURISTIC]` **Target bench turnover:** 30–40% annually. Successful dynasty managers cycle the bottom of the roster aggressively. The agent should treat this as a default — if bench composition has been static for >6 months, surface it as a flag.

`[HEURISTIC]` **Drop hierarchy** (informs what gets surfaced as drop candidates first):
1. Players outside startable depth at their position AND age 25+ AND no keeper case (home league only)
2. Players with declining opportunity metrics over 4+ weeks
3. Players whose role has been displaced (rookie ascended, depth chart change, trade)
4. Aging veterans whose age curve view shows steep decline imminent
5. Functional but unexciting bench pieces, only when a higher-upside replacement is available

`[RULE]` Per `00-principles.md`, drops in tier 4 and above always require approval regardless of policy graduation.

`[HEURISTIC]` **Roster spot scarcity.** Track roster utilization continuously. When roster is full and a high-value waiver target appears, the drop recommendation must come paired with the add. Never propose adds without an explicit drop suggestion when the roster is at capacity.

---

## Construction red flags

These trigger immediate proposal generation rather than waiting for the daily/weekly cadence:

`[HEURISTIC]` **Injury creates positional starvation.** A starter goes to IR and the bench has no replacement at that position — surface waiver targets and/or trade-from-strength proposals within 24 hours.

`[HEURISTIC]` **Age cliff event.** A rostered RB hits the age 27 threshold during the season — surface a sell-window flag. Per `01-valuation-philosophy.md`, RBs at the late edge of the sell window should lean toward sell, particularly in exchange for early-round picks.

`[HEURISTIC]` **Concentration risk crossing threshold.** Top-3 starter dependency rises above 60% — surface as a fragility warning with implied trade for depth.

`[HEURISTIC]` **Bye week gap.** A position has insufficient bye week coverage 3+ weeks ahead — surface as a low-stakes waiver/streamer opportunity.

---

## Format-specific adjustments

`[HEURISTIC]` **Superflex / 2QB (if confirmed in Phase 0):** QB construction priority elevates dramatically. Target two startable QBs minimum, three preferred. Young QB1s become the most valuable asset class on the roster — protect them, build around them.

`[HEURISTIC]` **TE premium (if confirmed in Phase 0):** target two startable TEs in two-TE formats; one elite + one bench stash in single-TE formats. Mid-tier TEs become rosterable assets; the WR/TE gap flattens at the top.

`[HEURISTIC]` **Standard scoring (if either league is non-PPR):** weight workload-based RB profiles over receiving backs. Possession WRs (Hopkins archetype) lose value relative to deep threats.

`[CONTEXT]` Phase 0 discovery seeds the actual scoring profile per league into `FF#LEAGUE#...` records. The agent reads from those records — never assumes scoring profile.

---

## Edge cases

`[HEURISTIC]` **Posture transitions.** If the home league shifts from balanced to rebuild mid-season (per the week 4/8/12 reassessment in `00-principles.md`), construction targets shift accordingly: bench philosophy moves from reliable-backups to upside-lottery-tickets, and aging veterans become sell candidates regardless of current production.

`[HEURISTIC]` **Trading with amoore324 (Travis's brother, Degeneration X).** Per `00-principles.md`, the agent has wide latitude with this manager. Construction-driven trades to him can be more aggressively shaped — concentration plays, weird position swaps, off-meta archetype trades.

`[HEURISTIC]` **End-of-season teardown.** If a team is mathematically eliminated from playoff contention with 3+ weeks remaining, shift construction priorities immediately to next year — sell aging pieces for picks, audition young bench players in starting roles for evaluation purposes.

---

## What the agent does NOT do

`[RULE]` The agent does not propose moves that produce roster construction violations of `00-principles.md` hard gates (FAAB ceiling, drop gates, rookie pick gate, trade approval gate). Construction logic is constrained by those gates, never overrides them.

`[HEURISTIC]` The agent does not aggressively force a single roster construction philosophy. Real rosters are constrained by the players actually available; the agent works with the inventory it has and gradually optimizes toward target shape rather than demanding an immediate overhaul.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
