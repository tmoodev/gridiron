# 05 — Lineup Strategy

**Version:** 1.0
**Status:** Loaded on demand by the lineup/waiver agent for weekly start/sit optimization and lineup lock decisions.
**Owner:** Travis Moore
**Last updated:** 2026-04-30
**See also:** `00-principles.md`, `01-valuation-philosophy.md`, `02-roster-construction.md`

---

## Purpose

This doc defines how Gridiron sets weekly lineups. The lineup agent runs Sunday at 9am CT to lock starters, plus continuous monitoring through Sunday morning for late inactive news. Lineup decisions are mostly low-stakes (one or two borderline calls per week per league) but compound — getting the marginal calls right is the difference between making playoffs and missing.

---

## Core principle

`[HEURISTIC]` **Start your studs. Always.** The biggest mistake in lineup management is benching a known top-12 player against a tough matchup in favor of a hot bench player. Talent + role beats matchup almost every time at RB and WR. The agent should require strong evidence (specific injury, scheme-driven shadow coverage, weather extreme) to bench a top-12 starter regardless of opponent.

`[HEURISTIC]` **Volume is the strongest single predictor.** Per `01-valuation-philosophy.md`, target share and snap share stick week-to-week. A player with high established volume has a high projection floor regardless of matchup. The agent's lineup math weights volume heavily.

---

## The four-input framework

The agent evaluates every borderline start/sit through four inputs, in this priority order:

1. **Volume / role** — established target share, snap share, route participation, carry share. Highest weight. The "is this player going to be on the field doing things" question.
2. **Matchup quality** — opponent defensive rank vs position, scheme fit, specific coverage assignments where applicable. Material but not dominant for RB/WR; dominant for QB/TE/DST/K.
3. **Game script projection** — Vegas implied team total, spread, expected pace. A player on a big home favorite has different upside than the same player on a road underdog.
4. **Recent performance** — last 3 games trend, weighted toward most recent. Used for confirmation, not as a primary driver. Single-game outliers are noise.

`[HEURISTIC]` **Position-specific weighting:**
- **RB / WR:** volume dominates. Matchup is a tiebreaker between similar-volume options.
- **QB / TE:** matchup dominates. These positions have higher week-to-week variance; matchup-driven streaming is mathematically correct.
- **DST / K:** matchup is the only thing. Stream weekly per `03-waiver-strategy.md`.

---

## Floor vs. ceiling

`[HEURISTIC]` **The lineup posture depends on projected matchup outcome:**
- **Heavy favorite (>10 projected pt margin):** lean to floor. Don't blow the win chasing a ceiling that's unnecessary.
- **Toss-up matchup (within 5 pts):** lean to ceiling at one or two FLEX-eligible spots. Your studs play; the marginal slot picks the higher-variance option.
- **Heavy underdog (>10 projected pt deficit):** lean to ceiling everywhere except your locked top-3. Need boom outcomes to flip the matchup.

`[HEURISTIC]` **Project the matchup outcome first, then set lineup.** The agent computes the projected score margin (using gridiron projections for both rosters) before optimizing the lineup. The posture decision flows from that projection, not from gut feel.

`[HEURISTIC]` **Per-league posture nudges from `00-principles.md`:**
- Degeneration X (win-now): when matchup is toss-up, lean ceiling. Concentrate upside.
- Home league (balanced): when matchup is toss-up, lean floor. Reliability over variance.

---

## Specific lineup patterns

`[HEURISTIC]` **The "running back monsoon" rule.** Workhorse RBs (>70% snap share, both run game and receiving role) start every week. No matchup is bad enough to bench them. The volume floor is too high.

`[HEURISTIC]` **The "TE matchup roulette" rule.** Outside of the top-3 dynasty TEs, every other TE is a matchup play. The agent should not be loyal to a roster TE in a bad matchup when a better-matchup TE is available on the bench, on waivers, or via streaming.

`[HEURISTIC]` **The "high-volume slot WR PPR floor" rule.** A high-volume slot WR in PPR (8+ targets per game baseline) maintains a high floor even in tough matchups because catch-rate efficiency on short routes is more stable than yardage-dependent production. Start them in floor-needed weeks.

`[HEURISTIC]` **The "deep threat ceiling" rule.** Boom-or-bust deep threat WRs (high aDOT, low catch %) are ceiling plays. Use in underdog weeks; bench in must-win-floor weeks.

`[HEURISTIC]` **The "primary read concentration" rule.** Per `01-valuation-philosophy.md`, first-read target share is highly predictive. WRs with both high target share AND high first-read share are the safest starts available — start them everywhere, every week.

`[HEURISTIC]` **The "running back catching passes" PPR adjustment.** Pass-catching RBs (>4 targets per game baseline) get a meaningful PPR bump. In PPR formats, prefer pass-catching RBs over higher-projected pure rushers when the projection gap is within 2 points.

---

## Handling injury question marks

`[HEURISTIC]` **The "Q designation" reality check.** "Questionable" tag in the modern NFL is mostly noise — most players tagged Q play. The agent should not bench Q players preemptively. The decision point is the inactive list (~90 minutes pre-game).

`[HEURISTIC]` **The "doubtful" downgrade.** Doubtful players play roughly 25% of the time, usually at reduced workload. The agent should plan a backup starter and surface a flip-decision proposal that resolves at inactives.

`[HEURISTIC]` **The "out" replacement rule.** Player ruled out → identify the highest-projected replacement on the bench, factor in the secondary effect (e.g., RB1 out → backup RB workload spikes; WR1 out → WR2 target share rises). Both effects are starter-eligible.

`[HEURISTIC]` **The "game-time decision" lockout problem.** Some game-time decisions resolve too late for normal lineup adjustment. The agent should pre-set a contingency lineup with the backup-if-out flip-spot identified, so the swap is mechanical when news drops.

`[HEURISTIC]` **The "playing through injury" caveat.** A player labeled active but practicing limited all week is a downgrade even if not officially Q/D. Reduce projections by 15–25% for these cases. Do not bench by default — the talent and role often still produce starter-tier output even at reduced capacity.

---

## Late-week monitoring

`[HEURISTIC]` **Continuous Sunday morning sweep.** From 7am CT through the first kickoff window, the agent monitors:
- Inactives lists (released ~90 min pre-game)
- Pre-game weather updates
- Beat reporter status updates (via Grok-on-Bedrock per `00-principles.md`)
- Late scratches and last-minute role changes

`[HEURISTIC]` **Inactive-driven flip-decisions** are the agent's most time-sensitive moves. When a starter is declared inactive, the pre-staged contingency fires automatically (within the policy gate — emergency-flip falls under "lineup_set: propose" by default; once graduated, automatic).

`[HEURISTIC]` **Weather impact rules:**
- Wind > 15 mph sustained reduces passing-game projections by ~15% (QB, WRs)
- Heavy rain reduces overall scoring by 10–15%; favors RBs and possession WRs over deep threats
- Cold (<25°F) and snow have smaller measurable effects than wind/rain in modern NFL data — don't overweight
- Dome/retractable-roof games closed: no weather adjustment

---

## Bye week management

`[HEURISTIC]` **Plan bye weeks 2–3 weeks ahead.** The agent surfaces bye-week conflicts in the dashboard's Recommendations area. Most are addressable via roster moves (waivers) before the bye hits.

`[HEURISTIC]` **Bye-week philosophy:** prefer high-floor replacements over upside swings during bye weeks. The goal is to not lose the week, not to win it spectacularly. Per `03-waiver-strategy.md`, no FAAB above 2% on one-week bye fills.

`[HEURISTIC]` **Multi-bye weeks** (multiple starters out same week) are construction red flags surfaced as far in advance as possible — usually during draft analysis but also during in-season trade decisions.

---

## Playoff push (weeks 14–17)

`[HEURISTIC]` **Schedule analysis matters more.** During fantasy playoff weeks, opponent matchups deserve heavier weighting since the sample of remaining games is small. A player with a great playoff schedule is worth more than equivalent talent with a brutal playoff schedule.

`[HEURISTIC]` **Lean ceiling more aggressively.** Single-elimination bracket math — you need to win three weeks straight in most leagues. The variance of needing one ceiling outcome per week pushes toward upside picks. Especially in DX where win-now is the entire posture.

`[HEURISTIC]` **Avoid resting players on locked teams.** When NFL teams have locked their playoff seed by week 17, starters get rested. The agent should flag these scenarios proactively in week 16 and prep contingencies.

---

## What the agent does NOT do

`[HEURISTIC]` Does not bench top-12 dynasty-tier players because of matchup. Talent + role wins.

`[HEURISTIC]` Does not chase a "hot hand" off a single big game. Per `01-valuation-philosophy.md`, single-game samples are noise.

`[HEURISTIC]` Does not optimize lineup for the median outcome when the matchup posture (favorite/underdog) calls for floor or ceiling deliberately.

`[HEURISTIC]` Does not bench players in good matchups for backup options just because the backup got hot last week.

`[HEURISTIC]` Does not start a player based purely on yards-after-catch or yards-per-carry efficiency without underlying volume to back it up.

---

## Changelog

| Date       | Version | Change                                  | Author |
|------------|---------|-----------------------------------------|--------|
| 2026-04-30 | 1.0     | Initial draft                           | Travis + Claude |
