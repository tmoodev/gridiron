import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import type { Decision, League } from "../types";

function StatusBadge({ status }: { status: string | null }) {
  const map: Record<string, string> = {
    pre_draft: "bg-yellow-900/50 text-yellow-300 border border-yellow-700",
    drafting: "bg-blue-900/50 text-blue-300 border border-blue-700",
    in_season: "bg-field-800 text-field-400 border border-field-700",
    complete: "bg-slate-800 text-slate-400 border border-slate-600",
  };
  const cls = map[status ?? ""] ?? "bg-slate-800 text-slate-400";
  return (
    <span className={`badge ${cls}`}>{status?.replace("_", " ") ?? "unknown"}</span>
  );
}

function FormatBadge({ format }: { format: string | null }) {
  const label: Record<string, string> = {
    keeper_idp: "Keeper · IDP · Half-PPR",
    dynasty: "Dynasty · SUPER_FLEX · TE+ · Full PPR",
  };
  return (
    <span className="text-xs text-slate-500 font-mono">
      {label[format ?? ""] ?? format ?? "—"}
    </span>
  );
}

function LeagueCard({ league }: { league: League }) {
  const faabPct =
    league.faab_budget && league.faab_remaining != null
      ? Math.round((league.faab_remaining / league.faab_budget) * 100)
      : null;

  return (
    <Link to={`/leagues/${league.league_id}`} className="card block hover:border-field-700 transition-colors group">
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <div className="font-semibold text-slate-100 group-hover:text-field-400 transition-colors">
            {league.league_name ?? "—"}
          </div>
          <div className="mt-1">
            <FormatBadge format={league.format} />
          </div>
        </div>
        <StatusBadge status={league.status} />
      </div>

      <div className="grid grid-cols-3 gap-3 mt-4">
        <div className="bg-field-950 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">Teams</div>
          <div className="text-lg font-bold text-slate-100">{league.total_rosters ?? "—"}</div>
        </div>
        <div className="bg-field-950 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">Season</div>
          <div className="text-lg font-bold text-slate-100">{league.season ?? "—"}</div>
        </div>
        <div className="bg-field-950 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">FAAB</div>
          {faabPct !== null ? (
            <>
              <div className="text-lg font-bold text-slate-100">
                ${league.faab_remaining}
                <span className="text-xs text-slate-500 font-normal ml-1">/ ${league.faab_budget}</span>
              </div>
              <div className="mt-1.5 h-1 bg-field-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-field-500 rounded-full"
                  style={{ width: `${faabPct}%` }}
                />
              </div>
            </>
          ) : (
            <div className="text-lg font-bold text-slate-100">—</div>
          )}
        </div>
      </div>

      <div className="mt-3 text-xs text-slate-600 font-mono truncate">{league.league_id}</div>
    </Link>
  );
}

function DecisionRow({ d, onAction }: { d: Decision; onAction: () => void }) {
  const [loading, setLoading] = useState(false);

  const handle = async (action: "approve" | "reject") => {
    setLoading(true);
    try {
      if (action === "approve") await api.approve(d.decision_id, d.league_id);
      else await api.reject(d.decision_id, d.league_id);
      onAction();
    } finally {
      setLoading(false);
    }
  };

  const typeColor: Record<string, string> = {
    lineup: "bg-blue-900/40 text-blue-300",
    waiver: "bg-purple-900/40 text-purple-300",
    trade_response: "bg-orange-900/40 text-orange-300",
    trade_proposal: "bg-yellow-900/40 text-yellow-300",
    research: "bg-slate-800 text-slate-400",
  };

  return (
    <div className="flex items-center gap-3 py-3 border-b border-field-800 last:border-0">
      <span className={`badge ${typeColor[d.type] ?? "bg-slate-800 text-slate-400"} shrink-0`}>
        {d.type.replace("_", " ")}
      </span>
      <span className="text-sm text-slate-300 flex-1 min-w-0 truncate">{d.summary}</span>
      <div className="flex items-center gap-2 shrink-0">
        <button
          onClick={() => handle("approve")}
          disabled={loading}
          className="btn-primary py-1 px-3 disabled:opacity-50"
        >
          Approve
        </button>
        <button
          onClick={() => handle("reject")}
          disabled={loading}
          className="btn-danger py-1 px-3 disabled:opacity-50"
        >
          Reject
        </button>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const [l, d] = await Promise.all([api.leagues(), api.decisions()]);
      setLeagues(l);
      setDecisions(d);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-500">
        Loading...
      </div>
    );
  }

  if (error) {
    return (
      <div className="card border-red-900 text-red-400 text-sm">{error}</div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Leagues */}
      <section>
        <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
          Leagues
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {leagues.map((l) => <LeagueCard key={l.league_id} league={l} />)}
        </div>
      </section>

      {/* Pending decisions */}
      <section>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
            Pending Decisions
            {decisions.length > 0 && (
              <span className="ml-2 badge bg-field-800 text-field-400">{decisions.length}</span>
            )}
          </h2>
          <Link to="/decisions" className="text-xs text-field-500 hover:text-field-400">
            View all →
          </Link>
        </div>
        <div className="card">
          {decisions.length === 0 ? (
            <div className="text-slate-500 text-sm py-2">No pending decisions.</div>
          ) : (
            decisions.slice(0, 5).map((d) => (
              <DecisionRow key={d.decision_id} d={d} onAction={load} />
            ))
          )}
        </div>
      </section>
    </div>
  );
}
