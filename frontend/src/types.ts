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
}
