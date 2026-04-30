# 08 — In-Season Management

**Version:** 1.0
**Status:** Loaded on demand by all agents during the active NFL season. Defines the weekly rhythm and seasonal arc of agent activity.
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** All other docs — this one orchestrates rather than introduces philosophy.

---

## Purpose

This doc defines the agent's seasonal rhythm — what happens when, what triggers what, and how the four agent loops coordinate across the NFL season. The other docs cover what to do; this doc covers when.

---

## The weekly cadence (in-season, weeks 1–17)

### Tuesday — Waiver day

The biggest day of agent activity. Per `03-waiver-strategy.md`:

- **6am CT:** Research agent runs comprehensive sweep on all rostered players + high-trending free agents
- **7am CT:** Daily digest email to Travis with overnight intel, pending waiver targets, and the day's recommendations queue
- **Throughout day:** Lineup/waiver agent constructs claim proposals with full reasoning; surfaces to dashboard's pending approvals sidebar
- **Pre-waiver-deadline (typically Wed 4am CT, league-specific from Phase 0):** Final claim review and bid adjustment based on late news
- **Post-waiver processing (Wed morning):** Decision log updated; dashboard reflects new roster state; trade agent re-scans for value mismatches created by the waiver wire shift

### Wednesday — Trade scanning

- **6am CT:** Trade agent runs daily scan across both leagues looking for value mismatches per `04-trade-strategy.md`
- **7am CT:** Daily digest includes any newly-surfaced trade opportunities
- **Throughout day:** Outgoing trade proposals drafted and surfaced; incoming offers from the past 24 hours evaluated
- Mid-week is the highest-acceptance window for trades — managers are thinking about their teams between waiver chaos and weekend prep

### Thursday — Lineup prep + TNF locks

- **6am CT:** Initial weekly lineup analysis. Lineup/waiver agent identifies borderline start/sit calls, surfaces to dashboard
- **TNF kickoff lockout:** Players in Thursday Night Football lock at game start — the agent flags any TNF participant in pending lineup decisions earlier in the day
- **Late Thursday:** Initial lineup proposals locked for non-TNF starters; revisions possible through Sunday morning

### Friday — Late-week monitoring

- **6am CT:** Refreshed practice report data ingested via research agent (Grok signal especially valuable here for beat reporter posts)
- **Throughout day:** Status changes (Q/D/Out designations) trigger lineup contingency planning per `05-lineup-strategy.md`
- **Fridays during the season are quieter than mid-week** — minimal proposals unless news warrants

### Saturday — Final intel sweep

- **Last full day before lineups lock.** Research agent runs continuous sweep for any final injury news or status changes
- Late-Friday/Saturday-morning Q-to-Out conversions are common in the modern NFL — the agent monitors aggressively

### Sunday — Game day

The most time-sensitive day. Per `05-lineup-strategy.md`:

- **7am CT:** Final injury sweep. Inactives lists release ~90 minutes pre-game in waves throughout the day
- **9am CT:** Lineup lock for early-window games. Agent submits any pending lineup proposals (within policy gate) or surfaces them as urgent approvals
- **Inactive-driven flips:** When a starter is declared inactive, the pre-staged contingency from Saturday's planning fires automatically (or surfaces as urgent approval)
- **Throughout the day:** Live monitoring of in-game injuries that affect next week's planning. Major injuries (ACL, Achilles) trigger immediate research agent deep-dives on backup situations
- **Sunday Night Football** is the final lineup window for the week; same monitoring continues

### Monday — Post-game analysis + reset

- **6am CT:** Performance analysis of the week. Decision log entries get outcome data attached (was the start/sit call right? did the waiver claim produce?)
- **Calibration data captured.** Per `01-valuation-philosophy.md`, predictions vs. outcomes feed the agent's self-validation loop
- **Monday Night Football** is the last game of the week; analysis runs after MNF
- **Posture reassessment** at week 4, week 8, week 12 for the home league per `00-principles.md`

---

## The seasonal arc

### Pre-season (weeks -4 to 0, late July through Week 1)

`[HEURISTIC]` **Highest trade volume window.** Markets are fluid, opinions shift on offseason news, depth charts settle. Per `04-trade-strategy.md`, the agent runs aggressive trade scanning here. Both leagues are in active prep mode.

`[HEURISTIC]` **Home league keeper deadline.** Confirmed in Phase 0; typically 1–2 weeks before draft. The agent surfaces final keeper analysis with full KRV/ADP/savings math per `07-keeper-selection.md` 2 weeks before deadline.

`[HEURISTIC]` **Home league redraft.** Once keepers lock, draft prep activates. See `07-keeper-selection.md` for adjusted-ADP and positional scarcity analysis.

`[HEURISTIC]` **Lineup setting for Week 1.** First-week lineups are highest-uncertainty — limited current-season data. Lean on offseason research and projections; expect more revisions than in later weeks.

### Early season (weeks 1–4)

`[HEURISTIC]` **Per `04-trade-strategy.md`, mostly DON'T trade in weeks 1–3.** Volatility is high; managers overreact to small samples. Let other managers tilt themselves into bad decisions; surface buy-low candidates starting week 4.

`[HEURISTIC]` **Per `03-waiver-strategy.md`, FAAB aggression peaks here.** Legitimate league-winning breakouts (Puka Nacua / Kyren Williams archetype) appear in this window. Agent should be ready to surface high-conviction targets immediately, knowing approvals will route through Travis given the 10% FAAB ceiling.

`[HEURISTIC]` **Research agent runs hot.** New season = new data. Snap shares, target distributions, scheme fit confirmations all happen now. Intel updates per player are at maximum frequency.

`[HEURISTIC]` **Week 4 home league posture reassessment.** First check-in. Reasonable to declare "compete," "build," or "still TBD." Affects all downstream decisions.

### Mid-season (weeks 5–9)

`[HEURISTIC]` **Prime in-season trading window.** Postures clarify. Buy-low / sell-high opportunities are most actionable. Per `04-trade-strategy.md`, the agent leans into proposals here in both leagues.

`[HEURISTIC]` **Roster construction reassessment.** By week 6, roster strengths and weaknesses are clear. The Construction tab's diagnostic flags become actionable rather than speculative.

`[HEURISTIC]` **Week 8 home league posture reassessment.** Second check-in. Posture often firms up here based on standings and roster health.

`[HEURISTIC]` **NFL trade deadline (typically late October / weeks 8–9).** Per `03-waiver-strategy.md`, NFL trades create 2–3 actionable waiver targets per year. Research agent monitors continuously during NFL trade window.

### Trade deadline approach (weeks 9 to fantasy trade deadline)

`[HEURISTIC]` **Maximum aggression for contenders.** Per `04-trade-strategy.md`, DX (win-now) gets aggressive. Home league only if in compete posture.

`[HEURISTIC]` **Trade deadline panic-mode trigger.** 7 days before deadline, if construction needs are unmet, the agent surfaces increased-urgency contender moves.

`[HEURISTIC]` **Sell windows close.** After the deadline, aging-RB sells per `01-valuation-philosophy.md` lose contender buyers. Window-aware sells happen pre-deadline.

`[HEURISTIC]` **Week 12 home league posture reassessment.** Final check-in. Posture is essentially locked at this point — decisions for the rest of the season follow this assessment.

### Playoff push (weeks 13–14, regular season end)

`[HEURISTIC]` **Trades shut off.** Most leagues hit deadline by week 13. Focus shifts entirely to lineup optimization and waivers.

`[HEURISTIC]` **Lineup analysis intensifies.** Per `05-lineup-strategy.md`, playoff-week scheduling matters more. Schedule strength analysis becomes a primary input for borderline calls.

`[HEURISTIC]` **End-of-season teardown for eliminated teams.** If either league is mathematically eliminated, posture flips to next-year prep. Aging veterans become sell candidates (where trades still allowed); young bench players audition in starting roles.

### Fantasy playoffs (weeks 15–17)

`[HEURISTIC]` **Lean ceiling more aggressively per `05-lineup-strategy.md`.** Single-elimination math; need ceiling outcomes weekly.

`[HEURISTIC]` **Week 17 NFL resting risk.** Locked-seed NFL teams rest starters in week 17. Agent flags scenarios proactively in week 16.

`[HEURISTIC]` **Waiver wire thins out.** Less competition for late-season pickups; bids clear at minimum. Streaming and bye-coverage easier to find.

### Postseason (post-week-17)

`[HEURISTIC]` **Decision log review.** Agent compiles full-season summary: best calls, worst calls, calibration metrics for the gridiron-internal valuation model.

`[HEURISTIC]` **Offseason trade window opens.** Per `04-trade-strategy.md`, second-best trade window after pre-season. Veteran sells and pick swaps around the rookie draft. Both leagues active.

---

## Standing job schedule

The agent runs the following automatically:

| Job | Frequency | Owner | Purpose |
|-----|-----------|-------|---------|
| Sync league state | Hourly during NFL hours | League sync job | Pull latest rosters, transactions, matchup state from Sleeper API |
| Player intel sweep | Every 30min during NFL hours, every 4hr otherwise | Research agent | Update intel records with news, injury, beat reporter signal |
| Daily digest email | 7am CT daily | Notification system | Compile pending approvals, new intel, recommendations |
| Valuation refresh | 6am CT daily | Valuation agent | Refresh KTC + FantasyCalc + internal model values |
| Trade scan | 6am CT daily | Trade agent | Scan all rosters for value mismatches |
| Waiver analysis | Tuesday 6am CT | Lineup/waiver agent | Build target list and bid recommendations |
| Lineup analysis | Thursday 6am CT, Sunday 9am CT | Lineup/waiver agent | Optimize starting lineups |
| Inactive monitoring | Sunday 7am CT through final kickoff | Research + lineup agent | Catch late scratches, fire contingencies |
| Posture reassessment | Weeks 4/8/12 (home league) | Coordination across agents | Re-evaluate compete vs build for home league |
| Decision outcome logging | Monday 6am CT | Decision log | Attach actual outcomes to past predictions |

---

## Cross-loop coordination

`[HEURISTIC]` **The four agent loops share state via the `FF#...` records.** A waiver decision generates a `FF#DECISION#...` record that the trade agent can reference when scanning. A trade affecting roster shape triggers the lineup agent to re-evaluate the starting lineup. The agents don't act in isolation — they share through the common state layer.

`[HEURISTIC]` **Conflict resolution.** When two agents would propose conflicting actions (e.g., trade agent wants to send Player X, but waiver agent wants to bid on a player whose drop replacement is X), the system surfaces both proposals together with the conflict noted. Travis decides.

`[HEURISTIC]` **Posture is ground truth.** All agents read current posture from `FF#LEAGUE#...`. When posture changes (week 4/8/12 reassessment for home league), all agents adjust their recommendations on the next cycle.

---

## Holidays and edge cases

`[HEURISTIC]` **Thanksgiving (week 12 or 13 depending on year).** Three games on Thursday. Lineup deadlines shift; agent monitors aggressively. Multi-game Thursday creates more inactive-driven flip-decisions than usual.

`[HEURISTIC]` **Christmas / week 16.** Often features Saturday games or scheduling oddities. Agent reads NFL schedule from Phase 0 sync; adjusts cadence per actual game days that week.

`[HEURISTIC]` **NFL bye weeks 5–14.** Roster bye-week conflicts surfaced 2–3 weeks ahead per `05-lineup-strategy.md`. Multi-bye weeks are construction red flags.

---

## Off-cycle activity

`[HEURISTIC]` **Major injury news mid-week.** ACL/Achilles/season-ending injuries to high-value players trigger immediate cross-loop activity:
- Research agent: deep-dive on backup situation
- Valuation agent: re-value the affected player and beneficiaries within 24 hours
- Trade agent: surface buy-low (injured player) and sell-high (backup) opportunities
- Lineup agent: re-evaluate any rosters with the affected player

`[HEURISTIC]` **NFL trades mid-season.** Same cross-loop trigger as injuries. Re-value affected players, re-scan trade opportunities, update construction analysis.

`[HEURISTIC]` **OC / coaching changes.** Mid-season firings happen. Surface affected players within 48 hours for re-evaluation.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
