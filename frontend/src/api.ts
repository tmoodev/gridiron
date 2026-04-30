import type {
  AnalyticsConstruction,
  AnalyticsPerformance,
  AnalyticsThisWeek,
  Decision,
  EnrichedRoster,
  IntelItem,
  League,
  Player,
  PolicyConfig,
  Proposal,
  Recommendation,
  RosterResponse,
} from "./types";

const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  // --- Health ---
  health: () => get<{ status: string; version: string }>("/health"),

  // --- Leagues ---
  leagues: () => get<League[]>("/leagues"),

  // --- Roster ---
  roster: (leagueId: string, week = 1) =>
    get<RosterResponse>(`/leagues/${leagueId}/roster?week=${week}`),

  myRoster: (leagueId: string, week = 1) =>
    get<EnrichedRoster>(`/leagues/${leagueId}/my-roster?week=${week}`),

  // --- Analytics ---
  analyticsPerformance: (leagueId: string) =>
    get<AnalyticsPerformance>(`/leagues/${leagueId}/analytics/performance`),

  analyticsConstruction: (leagueId: string) =>
    get<AnalyticsConstruction>(`/leagues/${leagueId}/analytics/construction`),

  analyticsThisWeek: (leagueId: string) =>
    get<AnalyticsThisWeek>(`/leagues/${leagueId}/analytics/this-week`),

  // --- Decisions (full log) ---
  decisions: (leagueId?: string, status = "pending") =>
    get<Decision[]>(
      `/decisions${leagueId ? `?league_id=${leagueId}&status=${status}` : `?status=${status}`}`
    ),

  decision: (decisionId: string, leagueId: string) =>
    get<Decision>(`/decisions/${decisionId}?league_id=${leagueId}`),

  // --- Proposals (pending approval queue) ---
  proposals: (leagueId?: string) =>
    get<Proposal[]>(`/proposals${leagueId ? `?league_id=${leagueId}` : ""}`),

  approveProposal: (id: string, leagueId: string) =>
    post<{ decision_id: string; status: string }>(
      `/proposals/${id}/approve?league_id=${leagueId}`
    ),

  rejectProposal: (id: string, leagueId: string) =>
    post<{ decision_id: string; status: string }>(
      `/proposals/${id}/reject?league_id=${leagueId}`
    ),

  modifyProposal: (id: string, leagueId: string, patch: Record<string, unknown>) =>
    post<{ decision_id: string; status: string }>(
      `/proposals/${id}/modify?league_id=${leagueId}`,
      patch
    ),

  // --- Legacy decision approve/reject ---
  approve: (decisionId: string, leagueId: string) =>
    post<{ decision_id: string; status: string }>(
      `/decisions/${decisionId}/approve?league_id=${leagueId}`
    ),

  reject: (decisionId: string, leagueId: string) =>
    post<{ decision_id: string; status: string }>(
      `/decisions/${decisionId}/reject?league_id=${leagueId}`
    ),

  // --- Players ---
  player: (playerId: string) => get<Player>(`/players/${playerId}`),

  playerIntel: (playerId: string, limit = 5) =>
    get<IntelItem[]>(`/players/${playerId}/intel?limit=${limit}`),

  // --- Policy ---
  policy: () => get<PolicyConfig>("/policy"),

  updatePolicy: (patch: Partial<PolicyConfig>) =>
    post<{ status: string }>("/policy", patch),

  // --- Recommendations ---
  recommendations: (leagueId?: string) =>
    get<Recommendation[]>(
      `/recommendations${leagueId ? `?league_id=${leagueId}` : ""}`
    ),

  promoteRecommendation: (id: string) =>
    post<{ status: string }>(`/recommendations/${id}/promote`),

  // --- Jobs ---
  triggerJob: (jobName: string) =>
    post<{ status: string; job: string }>(`/jobs/trigger/${jobName}`),
};
