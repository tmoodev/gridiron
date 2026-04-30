import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../api";
import type { League, Roster } from "../types";

const POSITION_COLOR: Record<string, string> = {
  QB:  "bg-red-900/40 text-red-300",
  RB:  "bg-blue-900/40 text-blue-300",
  WR:  "bg-green-900/40 text-green-300",
  TE:  "bg-orange-900/40 text-orange-300",
  K:   "bg-slate-700 text-slate-300",
  DL:  "bg-purple-900/40 text-purple-300",
  LB:  "bg-purple-900/40 text-purple-300",
  DB:  "bg-purple-900/40 text-purple-300",
};

function PlayerChip({ playerId, isStarter, isReserve, isTaxi }: {
  playerId: string;
  isStarter: boolean;
  isReserve: boolean;
  isTaxi: boolean;
}) {
  const tag = isStarter ? "STR" : isReserve ? "IR" : isTaxi ? "TX" : "BN";
  const tagColor = isStarter
    ? "text-field-400"
    : isReserve || isTaxi
    ? "text-slate-500"
    : "text-slate-600";

  return (
    <div className="flex items-center gap-2 py-2 border-b border-field-800/50 last:border-0">
      <span className={`font-mono text-xs w-7 ${tagColor}`}>{tag}</span>
      <span className="text-sm text-slate-300 font-mono">{playerId}</span>
    </div>
  );
}

function RosterPanel({ roster }: { roster: Roster }) {
  const starterSet = new Set(roster.starters);
  const reserveSet = new Set(roster.reserve);
  const taxiSet = new Set(roster.taxi);

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-semibold text-slate-100 text-sm">
          Roster #{roster.roster_id}
          {roster.owner_id && (
            <span className="ml-2 text-xs text-slate-500 font-mono">{roster.owner_id}</span>
          )}
        </h3>
        <span className="text-xs text-slate-500">{roster.players.length} players</span>
      </div>
      <div className="max-h-64 overflow-y-auto">
        {roster.players.map((pid) => (
          <PlayerChip
            key={pid}
            playerId={pid}
            isStarter={starterSet.has(pid)}
            isReserve={reserveSet.has(pid)}
            isTaxi={taxiSet.has(pid)}
          />
        ))}
      </div>
    </div>
  );
}

export default function LeaguePage() {
  const { id } = useParams<{ id: string }>();
  const [league, setLeague] = useState<League | null>(null);
  const [rosters, setRosters] = useState<Roster[]>([]);
  const [week, setWeek] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    Promise.all([api.leagues(), api.roster(id, week)])
      .then(([leagues, rosterResp]) => {
        setLeague(leagues.find((l) => l.league_id === id) ?? null);
        setRosters(rosterResp.rosters);
      })
      .catch((e) => setError(String(e)))
      .finally(() => setLoading(false));
  }, [id, week]);

  if (loading) return <div className="text-slate-500 py-12 text-center">Loading...</div>;
  if (error) return <div className="card border-red-900 text-red-400 text-sm">{error}</div>;
  if (!league) return <div className="text-slate-500">League not found.</div>;

  return (
    <div className="space-y-6">
      {/* League header */}
      <div className="card">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-xl font-bold text-slate-100">{league.league_name}</h1>
            <p className="text-sm text-slate-500 mt-1 font-mono">{league.league_id}</p>
          </div>
          <div className="text-right">
            <div className="text-sm text-slate-400">
              {league.season} &bull; {league.total_rosters} teams
            </div>
            <div className="text-xs text-slate-500 mt-0.5">
              {league.status?.replace("_", " ")}
            </div>
          </div>
        </div>

        {league.faab_budget != null && (
          <div className="mt-4 p-3 bg-field-950 rounded-lg">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs text-slate-500">FAAB</span>
              <span className="text-xs font-mono text-slate-300">
                ${league.faab_remaining} / ${league.faab_budget}
              </span>
            </div>
            <div className="h-1.5 bg-field-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-field-500 rounded-full"
                style={{
                  width: `${
                    league.faab_remaining != null
                      ? Math.round((league.faab_remaining / league.faab_budget) * 100)
                      : 0
                  }%`,
                }}
              />
            </div>
          </div>
        )}
      </div>

      {/* Week selector */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-slate-500">Week</span>
        {Array.from({ length: 18 }, (_, i) => i + 1).map((w) => (
          <button
            key={w}
            onClick={() => setWeek(w)}
            className={`w-8 h-8 rounded text-xs font-mono transition-colors ${
              week === w
                ? "bg-field-600 text-white"
                : "bg-field-900 text-slate-500 hover:bg-field-800"
            }`}
          >
            {w}
          </button>
        ))}
      </div>

      {/* Rosters */}
      <div>
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
          Rosters — Week {week}
        </h2>
        {rosters.length === 0 ? (
          <div className="card text-slate-500 text-sm">
            No roster snapshots for week {week}. Run a sync first.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {rosters.map((r) => (
              <RosterPanel key={r.roster_id} roster={r} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
