export interface League {
  league_id: string;
  league_name: string | null;
  season: string | null;
  status: string | null;
  format: string | null;
  total_rosters: number | null;
  faab_budget: number | null;
  faab_remaining: number | null;
}

export interface RosterPlayer {
  player_id: string;
  name: string | null;
  position: string | null;
  team: string | null;
  injury_status: string | null;
}

export interface Roster {
  roster_id: number;
  owner_id: string | null;
  players: string[];
  starters: string[];
  reserve: string[];
  taxi: string[];
}

export interface RosterResponse {
  league_id: string;
  week: number;
  rosters: Roster[];
}

export interface Decision {
  decision_id: string;
  league_id: string;
  type: string;
  summary: string;
  reasoning?: string;
  status: string;
  created_at: string;
  expires_at: string;
  proposed_action?: Record<string, unknown>;
  strategy_docs_loaded?: string[];
  strategy_doc_versions?: Record<string, string>;
}

// Alias for pending decisions shown in the approval queue
export type Proposal = Decision;

export interface PlayerValuations {
  keeper?: number | null;
  dynasty?: number | null;
  redraft?: number | null;
  reasoning?: string | null;
  idp?: Record<string, unknown> | null;
}

export interface Player {
  player_id: string;
  player_name: string | null;
  position: string | null;
  team: string | null;
  age: number | null;
  years_exp: number | null;
  status: string | null;
  injury_status?: string | null;
  valuations?: PlayerValuations | null;
  ktc_value_1qb?: number | null;
  ktc_value_sf?: number | null;
  ktc_trend_1qb?: number | null;
  updated_at?: string | null;
}

export interface EnrichedRosterPlayer {
  player_id: string;
  slot: string; // e.g. "QB", "RB1", "BN", "IR", "TAXI"
  is_starter: boolean;
  player: Player | null;
}

export interface EnrichedRoster {
  league_id: string;
  week: number;
  roster_id: number;
  players: EnrichedRosterPlayer[];
  total_dynasty_value: number;
  total_keeper_value: number;
}

export interface IntelItem {
  player_id: string;
  player_name: string | null;
  intel: {
    health?: string;
    role?: string;
    fantasy_outlook?: string;
    confidence?: string;
    raw?: string;
  };
  created_at: string;
}

export interface Recommendation {
  id: string;
  league_id: string;
  type: string;
  summary: string;
  player_id?: string | null;
  created_at: string;
  priority: "high" | "medium" | "low";
}

export interface PolicyConfig {
  policy: Record<string, string>;
  thresholds: Record<string, number>;
}

export interface AnalyticsPerformance {
  record: { wins: number; losses: number; ties: number };
  points_for: number;
  points_against: number;
  league_avg_points: number;
  playoff_odds: number | null;
  scoring_history: Array<{ week: number; points: number; opp_points: number }>;
  sos_remaining: number | null;
}

export interface AnalyticsConstruction {
  positional_values: Record<string, number>;
  age_curve: Array<{ age: number; value: number; name: string }>;
  starter_depth_split: { starter_pct: number; depth_pct: number } | null;
  trade_need: string | null;
  pick_inventory: Array<{ year: number; round: number; slot: string }>;
}

export interface AnalyticsThisWeek {
  matchup: {
    opponent_team: string;
    my_projected: number;
    opp_projected: number;
  } | null;
  win_probability: number | null;
  weather_flags: Array<{ player: string; flag: string }>;
  start_sit: Array<{ player_id: string; player: string; recommendation: string; reason: string }>;
}
