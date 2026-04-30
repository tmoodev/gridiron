import type { Decision, League, RosterResponse } from "./types";

const BASE = "/api";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

async function post<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: "POST" });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

export const api = {
  health: () => get<{ status: string; version: string }>("/health"),

  leagues: () => get<League[]>("/leagues"),

  roster: (leagueId: string, week = 1) =>
    get<RosterResponse>(`/leagues/${leagueId}/roster?week=${week}`),

  decisions: (leagueId?: string, status = "pending") =>
    get<Decision[]>(
      `/decisions${leagueId ? `?league_id=${leagueId}&status=${status}` : `?status=${status}`}`
    ),

  decision: (decisionId: string, leagueId: string) =>
    get<Decision>(`/decisions/${decisionId}?league_id=${leagueId}`),

  approve: (decisionId: string, leagueId: string) =>
    post<{ decision_id: string; status: string }>(
      `/decisions/${decisionId}/approve?league_id=${leagueId}`
    ),

  reject: (decisionId: string, leagueId: string) =>
    post<{ decision_id: string; status: string }>(
      `/decisions/${decisionId}/reject?league_id=${leagueId}`
    ),
};
