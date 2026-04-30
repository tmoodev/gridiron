# Gridiron — League Discovery Report (Phase 0)

*Generated: 2026-04-30. All data sourced from Sleeper public API and manual discovery.*

---

## Keeper League — "Fantasy Football Season 9"

| Field | Value |
|-------|-------|
| **League ID** | `1183557197018804224` |
| **Platform** | Sleeper |
| **Format** | 12-team IDP, keeper |
| **Season** | 2025 complete; 2026 prep begins now |
| **Travis username** | `Travy2Chains` |

### Roster Construction

| Slot | Count |
|------|-------|
| QB | 1 |
| RB | 2 |
| WR | 3 |
| TE | 1 |
| FLEX (RB/WR/TE) | 1 |
| K | 1 |
| DL | 1 |
| LB | 1 |
| DB | 1 |
| IDP_FLEX | 1 |
| BN | 8 |

**Total active starters:** 13 (7 skill + 4 IDP + K + FLEX)

### Keeper Rules

- **3 keepers max** — declared before rookie/supplemental draft
- **Draft format:** 3-round snake redraft for remaining slots (non-keeper rounds)
- **Travis's 2025 draft position:** 4th overall
- **Travis's 2025 record:** 5-9-0

### Scoring (half-PPR)

| Category | Value |
|----------|-------|
| Passing TD | 4 pts |
| Passing yards | 0.04 pts/yd |
| Receiving yards | 0.1 pts/yd |
| Rushing yards | 0.1 pts/yd |
| Reception | **0.5 pts** (half-PPR) |
| Rushing/receiving TD | 6 pts |
| IDP sack | 2 pts |
| IDP tackle (solo) | 1 pt |
| IDP tackle (assist) | 0.5 pts |
| IDP INT | 4 pts |
| IDP FF | 3 pts |
| IDP safety | 2 pts |
| IDP pass deflection | 1 pt |

*(Full IDP scoring covers DL, LB, DB positions)*

### Waiver / FAAB

| Field | Value |
|-------|-------|
| FAAB budget | $80 |
| Travis remaining (2025) | $74 of $80 |
| Waiver clears | Wednesday |
| System | Blind-bid FAAB |

### Playoffs

| Field | Value |
|-------|-------|
| Playoff teams | 6 |
| Playoff start | Week 15 |
| Travis 2025 result | Missed playoffs (5-9-0) |

### 2026 Action Items

- [ ] Evaluate keeper candidates (max 3)
- [ ] Scout rookie draft class for 2026 redraft rounds
- [ ] Set lineup optimization rules for IDP slots
- [ ] Monitor FAAB opportunities as free agency opens

---

## Dynasty League — "Degeneration X"

| Field | Value |
|-------|-------|
| **League ID** | `1331779473430810624` |
| **Platform** | Sleeper |
| **Format** | 12-team full dynasty, no keeper cap |
| **Season** | Pre-draft for 2026 |
| **Travis username** | `Travy2Chains` |

### Roster Construction

| Slot | Count |
|------|-------|
| QB | 1 |
| RB | 2 |
| WR | 3 |
| TE | 1 |
| FLEX (RB/WR/TE) | 2 |
| SUPER_FLEX (any) | 1 |
| BN | 15 |
| TAXI | 4 |
| IR | 4 |

**Total roster:** 29 active + 3 taxi + 4 IR = 36 players
**Travis's current roster:** 29 players (3 on taxi, 4 on reserve)

### Draft Status (2026)

| Field | Value |
|-------|-------|
| Draft type | Linear (reversal at round 3) |
| Rounds | 4 |
| Clock | 12-hour per pick |
| Travis's draft position | **4th overall** |
| Status | Pre-draft — not yet started |

**Pick assets:** 42 traded picks exist across 2026–2027 windows. Pick asset tracking is critical for dynasty valuation.

### Scoring (full PPR + TE premium)

| Category | Value |
|----------|-------|
| Passing TD | 4 pts |
| Passing yards | 0.04 pts/yd |
| Reception | **1.0 pts** (full PPR) |
| TE reception bonus | **+0.5 pts** (TE premium) |
| Receiving yards | 0.1 pts/yd |
| Rushing yards | 0.1 pts/yd |
| Rushing/receiving TD | 6 pts |
| Kicker PAT | 1 pt |
| Kicker FG 0-39 | 3 pts |
| Kicker FG 40-49 | 4 pts |
| Kicker FG 50+ | 5 pts |

**SUPER_FLEX note:** Adds significant QB premium. QBs valued ~1.5–2x their 1-QB league value.

### Waiver / FAAB

| Field | Value |
|-------|-------|
| FAAB budget | $100 |
| Waiver clears | Daily |
| Trade deadline | **None** (can trade any time) |

### 2026 Action Items

- [ ] Analyze all 42 traded pick assets (2026–2027) — map which picks Travis owns vs. owes
- [ ] Finalize 4-round draft board for picks 4, 16, 28, 40 (standard 4th-position slots, linear/reversal)
- [ ] Evaluate taxi squad eligibility for rookie additions post-draft
- [ ] Identify TE premium targets (TE values inflated +30-50% vs. 1-QB leagues)
- [ ] QB depth: SUPER_FLEX means rostering 2 viable QBs minimum

---

## Cross-League Notes

### Valuation Stack

| Source | Scope | Notes |
|--------|-------|-------|
| KeepTradeCut | Dynasty, 1QB + SuperFlex values | Primary; scrapable `playersArray` JS var |
| FantasyCalc | Dynasty | Secondary; Playwright headless scrape |
| Sleeper projections | Both leagues | Weekly/redraft projections via public API |
| Claude (Bedrock) | Both leagues | Keeper-cost-adjusted value, IDP-specific valuation |

### IDP Coverage

The keeper league requires full IDP coverage:
- **DL**: Sacks, tackles, FF are primary scoring events
- **LB**: Tackles are high-volume; also sacks, INT, FF
- **DB**: INTs, pass deflections, tackles; safety (rare, high value)

Research and valuation agents must include IDP players in all pipelines.

### Infrastructure

| Component | Value |
|-----------|-------|
| Deploy target | `datatrav-mdc-prod` (107.23.69.25) |
| Deploy path | `/opt/gridiron/` |
| Docker service | `gridiron-backend` |
| Deploy method | `github_actions` (merge to main triggers deploy) |
| Email sender | `gridiron@datatrav.com` (SES, domain verified) |
| Email recipient | `travis@datatrav.com` |
| Frontend domain | `gridiron.datatrav.net` (Cloudflare Tunnel + Access) |
| DynamoDB table | `datatrav-ops` (PAY_PER_REQUEST, us-east-1) |
| Key prefix | `FF#` |
