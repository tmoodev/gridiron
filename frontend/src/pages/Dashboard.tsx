import { useCallback, useEffect, useState } from "react";
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api";
import PlayerDrawer from "../components/PlayerDrawer";
import type {
  AnalyticsConstruction,
  AnalyticsPerformance,
  AnalyticsThisWeek,
  EnrichedRoster,
  EnrichedRosterPlayer,
  League,
  Player,
  Proposal,
  Recommendation,
} from "../types";

// ─── Position badge ──────────────────────────────────────────────────────────

const POS_COLORS: Record<string, string> = {
  QB: "bg-red-900/50 text-red-300",
  RB: "bg-blue-900/50 text-blue-300",
  WR: "bg-purple-900/50 text-purple-300",
  TE: "bg-yellow-900/50 text-yellow-300",
  K: "bg-slate-800 text-slate-400",
  DL: "bg-orange-900/50 text-orange-300",
  LB: "bg-green-900/50 text-green-300",
  DB: "bg-teal/10 text-teal",
  DEF: "bg-slate-800 text-slate-400",
};

function PosBadge({ pos }: { pos: string | null }) {
  const cls = POS_COLORS[pos ?? ""] ?? "bg-slate-800 text-slate-400";
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium font-mono ${cls}`}>
      {pos ?? "—"}
    </span>
  );
}

function StatusBadge({ status }: { status: string | null }) {
  if (!status || status === "Active") return null;
  if (["Injured Reserve", "IR"].includes(status)) {
    return <span className="text-[10px] text-red-400 font-mono">{status}</span>;
  }
  if (["Questionable", "Doubtful"].includes(status)) {
    return <span className="text-[10px] text-yellow-400 font-mono">{status}</span>;
  }
  return <span className="text-[10px] text-slate-500 font-mono">{status}</span>;
}

function TrendArrow({ trend }: { trend: number | null | undefined }) {
  if (trend == null) return <span className="text-slate-600">—</span>;
  if (trend > 0) return <span className="text-teal text-xs">↑</span>;
  if (trend < 0) return <span className="text-red-400 text-xs">↓</span>;
  return <span className="text-slate-500 text-xs">→</span>;
}

// ─── Roster column ────────────────────────────────────────────────────────────

const SLOT_ORDER = ["QB", "RB", "WR", "TE", "FLEX", "SUPER_FLEX", "K", "DL", "LB", "DB", "IDP_FLEX", "BN", "IR", "TAXI"];

function RosterRow({
  ep,
  onClick,
}: {
  ep: EnrichedRosterPlayer;
  onClick: (p: Player) => void;
}) {
  const p = ep.player;
  if (!p) return null;
  const val = p.valuations?.dynasty ?? p.valuations?.keeper ?? null;
  return (
    <button
      onClick={() => onClick(p)}
      className="w-full flex items-center gap-2 px-3 py-1.5 hover:bg-navy-300 transition-colors text-left group"
    >
      <PosBadge pos={p.position} />
      <span className="flex-1 min-w-0 text-sm text-slate-200 truncate group-hover:text-teal transition-colors">
        {p.player_name ?? p.player_id}
      </span>
      <span className="text-xs text-slate-500 font-mono shrink-0">{p.team ?? "FA"}</span>
      <StatusBadge status={p.status} />
      <span className="text-xs font-mono text-teal shrink-0 w-8 text-right">
        {val != null ? val : "—"}
      </span>
      <TrendArrow trend={p.ktc_trend_1qb} />
    </button>
  );
}

function RosterColumn({
  leagueId,
  onPlayerClick,
}: {
  leagueId: string;
  onPlayerClick: (p: Player) => void;
}) {
  const [roster, setRoster] = useState<EnrichedRoster | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void api
      .myRoster(leagueId)
      .then(setRoster)
      .catch(() => setRoster(null))
      .finally(() => setLoading(false));
  }, [leagueId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-32 text-slate-600 text-sm">
        Loading roster...
      </div>
    );
  }

  if (!roster) {
    return (
      <div className="px-3 py-2 text-slate-600 text-sm">No roster data.</div>
    );
  }

  const starters = roster.players.filter((ep) => ep.is_starter);
  const bench = roster.players.filter((ep) => !ep.is_starter);

  const sortedStarters = [...starters].sort(
    (a, b) => SLOT_ORDER.indexOf(a.slot) - SLOT_ORDER.indexOf(b.slot)
  );
  const sortedBench = [...bench].sort(
    (a, b) => SLOT_ORDER.indexOf(a.slot) - SLOT_ORDER.indexOf(b.slot)
  );

  const totalVal = roster.total_dynasty_value ?? roster.total_keeper_value ?? null;

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-border">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
          Starters
        </div>
      </div>
      <div>
        {sortedStarters.map((ep) => (
          <RosterRow key={ep.player_id} ep={ep} onClick={onPlayerClick} />
        ))}
      </div>

      <div className="px-3 py-2 border-t border-b border-border mt-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest opacity-60">
          Bench
        </div>
      </div>
      <div className="opacity-70">
        {sortedBench.map((ep) => (
          <RosterRow key={ep.player_id} ep={ep} onClick={onPlayerClick} />
        ))}
      </div>

      {totalVal != null && (
        <div className="mt-auto px-3 py-2 border-t border-border">
          <div className="flex justify-between text-xs font-mono">
            <span className="text-slate-500">Total value</span>
            <span className="text-teal font-medium">{totalVal.toLocaleString()}</span>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Analytics column ─────────────────────────────────────────────────────────

function PerformanceTab({ leagueId }: { leagueId: string }) {
  const [data, setData] = useState<AnalyticsPerformance | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void api
      .analyticsPerformance(leagueId)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [leagueId]);

  if (loading) return <div className="text-slate-600 text-sm p-4">Loading...</div>;
  if (!data) return <div className="text-slate-600 text-sm p-4">No performance data.</div>;

  const { record, points_for, points_against, league_avg_points, playoff_odds, scoring_history, sos_remaining } = data;

  return (
    <div className="p-4 space-y-4">
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-navy-200 rounded-lg p-3 text-center">
          <div className="text-xs text-slate-500 mb-1">Record</div>
          <div className="font-mono text-lg text-slate-100">
            {record.wins}-{record.losses}{record.ties ? `-${record.ties}` : ""}
          </div>
        </div>
        <div className="bg-navy-200 rounded-lg p-3 text-center">
          <div className="text-xs text-slate-500 mb-1">PF</div>
          <div className="font-mono text-lg text-teal">{points_for.toFixed(1)}</div>
        </div>
        <div className="bg-navy-200 rounded-lg p-3 text-center">
          <div className="text-xs text-slate-500 mb-1">PA</div>
          <div className="font-mono text-lg text-slate-300">{points_against.toFixed(1)}</div>
        </div>
      </div>

      {(playoff_odds != null || sos_remaining != null) && (
        <div className="grid grid-cols-2 gap-3">
          {playoff_odds != null && (
            <div className="bg-navy-200 rounded-lg p-3 text-center">
              <div className="text-xs text-slate-500 mb-1">Playoff Odds</div>
              <div className="font-mono text-lg text-teal">{(playoff_odds * 100).toFixed(0)}%</div>
            </div>
          )}
          {sos_remaining != null && (
            <div className="bg-navy-200 rounded-lg p-3 text-center">
              <div className="text-xs text-slate-500 mb-1">SOS Remaining</div>
              <div className="font-mono text-lg text-slate-300">{sos_remaining.toFixed(2)}</div>
            </div>
          )}
        </div>
      )}

      {scoring_history.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2">Scoring vs League Avg</div>
          <ResponsiveContainer width="100%" height={140}>
            <LineChart data={scoring_history}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1a2332" />
              <XAxis
                dataKey="week"
                tick={{ fontSize: 10, fill: "#64748b" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 10, fill: "#64748b" }}
                axisLine={false}
                tickLine={false}
                width={35}
              />
              <Tooltip
                contentStyle={{ background: "#0d1117", border: "1px solid #1a2332", borderRadius: 6, fontSize: 11 }}
                labelStyle={{ color: "#94a3b8" }}
              />
              <Line
                type="monotone"
                dataKey="points"
                stroke="#2dd4bf"
                strokeWidth={2}
                dot={false}
                name="My pts"
              />
              <Line
                type="monotone"
                dataKey="opp_points"
                stroke="#475569"
                strokeWidth={1.5}
                strokeDasharray="4 2"
                dot={false}
                name="Opp pts"
              />
            </LineChart>
          </ResponsiveContainer>
          <div className="text-xs text-slate-600 font-mono mt-1">
            League avg: {league_avg_points.toFixed(1)} pts/wk
          </div>
        </div>
      )}
    </div>
  );
}

function ConstructionTab({ leagueId }: { leagueId: string }) {
  const [data, setData] = useState<AnalyticsConstruction | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void api
      .analyticsConstruction(leagueId)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [leagueId]);

  if (loading) return <div className="text-slate-600 text-sm p-4">Loading...</div>;
  if (!data) return <div className="text-slate-600 text-sm p-4">No construction data.</div>;

  const { positional_values, starter_depth_split, trade_need, pick_inventory } = data;

  const posEntries = Object.entries(positional_values).sort(([, a], [, b]) => b - a);
  const maxVal = posEntries[0]?.[1] ?? 1;

  return (
    <div className="p-4 space-y-4">
      {posEntries.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2">Positional Value Distribution</div>
          <div className="space-y-1.5">
            {posEntries.map(([pos, val]) => (
              <div key={pos} className="flex items-center gap-2">
                <PosBadge pos={pos} />
                <div className="flex-1 h-2 bg-navy-300 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-teal rounded-full"
                    style={{ width: `${(val / maxVal) * 100}%` }}
                  />
                </div>
                <span className="text-xs font-mono text-slate-400 w-12 text-right">
                  {val.toLocaleString()}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {starter_depth_split && (
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-navy-200 rounded-lg p-3 text-center">
            <div className="text-xs text-slate-500 mb-1">Starter Value</div>
            <div className="font-mono text-lg text-teal">
              {(starter_depth_split.starter_pct * 100).toFixed(0)}%
            </div>
          </div>
          <div className="bg-navy-200 rounded-lg p-3 text-center">
            <div className="text-xs text-slate-500 mb-1">Depth Value</div>
            <div className="font-mono text-lg text-slate-300">
              {(starter_depth_split.depth_pct * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      )}

      {trade_need && (
        <div className="bg-navy-200 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-1">Trade Need</div>
          <div className="text-xs text-slate-300 leading-relaxed">{trade_need}</div>
        </div>
      )}

      {pick_inventory.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-2">Pick Inventory</div>
          <div className="flex flex-wrap gap-1.5">
            {pick_inventory.map((pick, i) => (
              <span
                key={i}
                className="inline-flex items-center px-2 py-0.5 rounded bg-navy-300 text-xs font-mono text-slate-300"
              >
                {pick.year} R{pick.round}
                {pick.slot !== "mid" ? ` (${pick.slot})` : ""}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ThisWeekTab({ leagueId }: { leagueId: string }) {
  const [data, setData] = useState<AnalyticsThisWeek | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    void api
      .analyticsThisWeek(leagueId)
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [leagueId]);

  if (loading) return <div className="text-slate-600 text-sm p-4">Loading...</div>;
  if (!data) return <div className="text-slate-600 text-sm p-4">No weekly data.</div>;

  const { matchup, win_probability, weather_flags, start_sit } = data;

  return (
    <div className="p-4 space-y-4">
      {matchup && (
        <div className="bg-navy-200 rounded-lg p-3">
          <div className="text-xs text-slate-500 mb-2">Matchup vs {matchup.opponent_team}</div>
          <div className="flex items-center justify-between">
            <div className="text-center">
              <div className="font-mono text-xl text-teal">{matchup.my_projected.toFixed(1)}</div>
              <div className="text-xs text-slate-500">My proj</div>
            </div>
            <div className="text-slate-600 text-lg">vs</div>
            <div className="text-center">
              <div className="font-mono text-xl text-slate-300">{matchup.opp_projected.toFixed(1)}</div>
              <div className="text-xs text-slate-500">Opp proj</div>
            </div>
          </div>
          {win_probability != null && (
            <div className="mt-2">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>Win probability</span>
                <span className="text-teal font-mono">{(win_probability * 100).toFixed(0)}%</span>
              </div>
              <div className="h-1.5 bg-navy-300 rounded-full overflow-hidden">
                <div
                  className="h-full bg-teal rounded-full"
                  style={{ width: `${win_probability * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {weather_flags.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-1.5">Weather Flags</div>
          <div className="space-y-1">
            {weather_flags.map((wf, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span className="text-yellow-400">⚠</span>
                <span className="text-slate-300">{wf.player}</span>
                <span className="text-slate-500">— {wf.flag}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {start_sit.length > 0 && (
        <div>
          <div className="text-xs text-slate-500 mb-1.5">Start / Sit</div>
          <div className="space-y-1.5">
            {start_sit.map((ss) => (
              <div key={ss.player_id} className="bg-navy-200 rounded p-2">
                <div className="flex items-center gap-2 mb-0.5">
                  <span
                    className={`text-[10px] font-mono font-medium ${
                      ss.recommendation === "START" ? "text-teal" : "text-red-400"
                    }`}
                  >
                    {ss.recommendation}
                  </span>
                  <span className="text-xs text-slate-200">{ss.player}</span>
                </div>
                <div className="text-xs text-slate-500">{ss.reason}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!matchup && weather_flags.length === 0 && start_sit.length === 0 && (
        <div className="text-slate-600 text-sm">No weekly data available yet.</div>
      )}
    </div>
  );
}

type AnalyticsTab = "performance" | "construction" | "this-week";

function AnalyticsColumn({ leagueId }: { leagueId: string }) {
  const [tab, setTab] = useState<AnalyticsTab>("performance");

  const tabs: { id: AnalyticsTab; label: string }[] = [
    { id: "performance", label: "Performance" },
    { id: "construction", label: "Construction" },
    { id: "this-week", label: "This Week" },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="flex border-b border-border px-4 gap-4">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`text-xs font-medium py-2.5 border-b-2 transition-colors ${
              tab === t.id
                ? "text-teal border-teal"
                : "text-slate-500 border-transparent hover:text-slate-300"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto">
        {tab === "performance" && <PerformanceTab leagueId={leagueId} />}
        {tab === "construction" && <ConstructionTab leagueId={leagueId} />}
        {tab === "this-week" && <ThisWeekTab leagueId={leagueId} />}
      </div>
    </div>
  );
}

// ─── Recommendations sidebar ──────────────────────────────────────────────────

const TYPE_COLORS: Record<string, string> = {
  lineup: "bg-blue-900/40 text-blue-300",
  waiver: "bg-purple-900/40 text-purple-300",
  trade_response: "bg-orange-900/40 text-orange-300",
  trade_proposal: "bg-yellow-900/40 text-yellow-300",
  trade: "bg-yellow-900/40 text-yellow-300",
  research: "bg-slate-800 text-slate-400",
  drop: "bg-red-900/40 text-red-300",
};

function ProposalCard({
  proposal,
  onAction,
}: {
  proposal: Proposal;
  onAction: () => void;
}) {
  const [loading, setLoading] = useState(false);

  const handle = async (action: "approve" | "reject") => {
    setLoading(true);
    try {
      if (action === "approve") {
        await api.approveProposal(proposal.decision_id, proposal.league_id);
      } else {
        await api.rejectProposal(proposal.decision_id, proposal.league_id);
      }
      onAction();
    } finally {
      setLoading(false);
    }
  };

  const typeCls = TYPE_COLORS[proposal.type] ?? "bg-slate-800 text-slate-400";

  return (
    <div className="bg-navy-200 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-2">
        <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium ${typeCls}`}>
          {proposal.type.replace(/_/g, " ")}
        </span>
        <span className="text-[10px] text-slate-600 font-mono ml-auto">
          {new Date(proposal.created_at).toLocaleDateString()}
        </span>
      </div>
      <div className="text-xs text-slate-300 leading-relaxed">{proposal.summary}</div>
      <div className="flex gap-2">
        <button
          onClick={() => void handle("approve")}
          disabled={loading}
          className="btn-primary py-1 px-3 text-xs disabled:opacity-50 flex-1"
        >
          Approve
        </button>
        <button
          onClick={() => void handle("reject")}
          disabled={loading}
          className="btn-danger py-1 px-3 text-xs disabled:opacity-50 flex-1"
        >
          Reject
        </button>
      </div>
    </div>
  );
}

function RecommendationsSidebar({ leagueId }: { leagueId: string }) {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [recs, setRecs] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [promoting, setPromoting] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    void Promise.all([
      api.proposals(leagueId),
      api.recommendations(leagueId),
    ])
      .then(([p, r]) => {
        setProposals(p);
        setRecs(r);
      })
      .catch(() => {
        setProposals([]);
        setRecs([]);
      })
      .finally(() => setLoading(false));
  }, [leagueId]);

  useEffect(() => {
    load();
  }, [load]);

  const promote = async (id: string) => {
    setPromoting(id);
    try {
      await api.promoteRecommendation(id);
      load();
    } finally {
      setPromoting(null);
    }
  };

  const PRIORITY_COLORS = {
    high: "text-red-400",
    medium: "text-yellow-400",
    low: "text-slate-500",
  };

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Approval queue */}
      <div className="p-3 border-b border-border">
        <div className="flex items-center gap-2 mb-2">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
            Approval Queue
          </div>
          {proposals.length > 0 && (
            <span className="bg-teal/20 text-teal text-[10px] font-mono px-1.5 py-0.5 rounded">
              {proposals.length}
            </span>
          )}
        </div>
        {loading ? (
          <div className="text-slate-600 text-xs">Loading...</div>
        ) : proposals.length === 0 ? (
          <div className="text-slate-600 text-xs">No pending proposals.</div>
        ) : (
          <div className="space-y-2">
            {proposals.map((p) => (
              <ProposalCard key={p.decision_id} proposal={p} onAction={load} />
            ))}
          </div>
        )}
      </div>

      {/* Passive recommendations */}
      <div className="p-3 flex-1">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
          Recommendations
        </div>
        {loading ? (
          <div className="text-slate-600 text-xs">Loading...</div>
        ) : recs.length === 0 ? (
          <div className="text-slate-600 text-xs">No recommendations.</div>
        ) : (
          <div className="space-y-2">
            {recs.map((r) => (
              <div key={r.id} className="bg-navy-200 rounded-lg p-3 space-y-1.5">
                <div className="flex items-center gap-2">
                  <span className={`text-[10px] font-mono font-medium ${PRIORITY_COLORS[r.priority]}`}>
                    {r.priority.toUpperCase()}
                  </span>
                  <span className="text-[10px] text-slate-600 font-mono ml-auto">
                    {new Date(r.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="text-xs text-slate-300 leading-relaxed">{r.summary}</div>
                <button
                  onClick={() => void promote(r.id)}
                  disabled={promoting === r.id}
                  className="text-[10px] text-teal hover:text-teal-bright font-mono transition-colors disabled:opacity-50"
                >
                  {promoting === r.id ? "Promoting..." : "→ Promote to proposal"}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Root Dashboard ───────────────────────────────────────────────────────────

interface Props {
  leagues: League[];
  activeLeagueId: string | null;
}

export default function Dashboard({ leagues: _leagues, activeLeagueId }: Props) {
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);

  if (!activeLeagueId) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-600 text-sm">
        No league selected.
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-dashboard h-[calc(100vh-48px)] overflow-hidden divide-x divide-border">
        {/* Left — Roster */}
        <div className="overflow-y-auto">
          <RosterColumn leagueId={activeLeagueId} onPlayerClick={setSelectedPlayer} />
        </div>

        {/* Middle — Analytics */}
        <div className="overflow-hidden flex flex-col">
          <AnalyticsColumn leagueId={activeLeagueId} />
        </div>

        {/* Right — Recommendations */}
        <div className="overflow-hidden flex flex-col">
          <RecommendationsSidebar leagueId={activeLeagueId} />
        </div>
      </div>

      {selectedPlayer && (
        <PlayerDrawer
          player={selectedPlayer}
          leagueId={activeLeagueId}
          onClose={() => setSelectedPlayer(null)}
        />
      )}
    </>
  );
}
