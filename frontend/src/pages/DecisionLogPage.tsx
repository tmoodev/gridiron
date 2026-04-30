import { useEffect, useState } from "react";
import { api } from "../api";
import type { Decision } from "../types";

const TYPE_COLORS: Record<string, string> = {
  lineup: "bg-blue-900/40 text-blue-300",
  waiver: "bg-purple-900/40 text-purple-300",
  trade_response: "bg-orange-900/40 text-orange-300",
  trade_proposal: "bg-yellow-900/40 text-yellow-300",
  trade: "bg-yellow-900/40 text-yellow-300",
  research: "bg-slate-800 text-slate-400",
  drop: "bg-red-900/40 text-red-300",
};

const STATUS_COLORS: Record<string, string> = {
  pending: "text-yellow-400",
  approved: "text-teal",
  rejected: "text-red-400",
  executed: "text-blue-400",
  expired: "text-slate-500",
};

function DecisionRow({ d }: { d: Decision }) {
  const [expanded, setExpanded] = useState(false);
  const typeCls = TYPE_COLORS[d.type] ?? "bg-slate-800 text-slate-400";
  const statusCls = STATUS_COLORS[d.status] ?? "text-slate-400";

  return (
    <div className="border-b border-border last:border-0">
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-3 px-4 py-3 hover:bg-navy-200 transition-colors text-left"
      >
        <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium shrink-0 ${typeCls}`}>
          {d.type.replace(/_/g, " ")}
        </span>
        <span className="flex-1 min-w-0 text-sm text-slate-300 truncate">{d.summary}</span>
        <span className={`text-xs font-mono shrink-0 ${statusCls}`}>{d.status}</span>
        <span className="text-xs text-slate-600 font-mono shrink-0">
          {new Date(d.created_at).toLocaleDateString()}
        </span>
        <span className="text-slate-600 text-xs ml-1">{expanded ? "▲" : "▼"}</span>
      </button>

      {expanded && (
        <div className="px-4 pb-3 space-y-2">
          {d.reasoning && (
            <div className="bg-navy-200 rounded p-3">
              <div className="text-xs text-slate-500 mb-1">Reasoning</div>
              <div className="text-xs text-slate-300 leading-relaxed whitespace-pre-wrap">{d.reasoning}</div>
            </div>
          )}
          {d.strategy_docs_loaded && d.strategy_docs_loaded.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {d.strategy_docs_loaded.map((doc) => (
                <span key={doc} className="text-[10px] font-mono bg-teal/10 text-teal px-1.5 py-0.5 rounded">
                  {doc}
                  {d.strategy_doc_versions?.[doc] ? ` v${d.strategy_doc_versions[doc]}` : ""}
                </span>
              ))}
            </div>
          )}
          <div className="text-[10px] text-slate-600 font-mono">
            ID: {d.decision_id} · League: {d.league_id}
          </div>
        </div>
      )}
    </div>
  );
}

const STATUS_FILTERS = ["all", "pending", "approved", "rejected", "executed", "expired"];
const TYPE_FILTERS = ["all", "lineup", "waiver", "trade", "trade_response", "trade_proposal", "research", "drop"];

export default function DecisionLogPage() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    void api
      .decisions(undefined, statusFilter === "all" ? "all" : statusFilter)
      .then(setDecisions)
      .catch(() => setDecisions([]))
      .finally(() => setLoading(false));
  }, [statusFilter]);

  const filtered = decisions.filter((d) => {
    if (typeFilter !== "all" && d.type !== typeFilter) return false;
    if (search && !d.summary.toLowerCase().includes(search.toLowerCase())) return false;
    return true;
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-6">
      <h1 className="font-display font-semibold text-slate-100 text-lg mb-4">Decision Log</h1>

      <div className="flex flex-wrap gap-3 mb-4">
        <input
          type="text"
          placeholder="Search..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-navy-200 border border-border rounded-lg px-3 py-1.5 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-teal/50 font-mono"
        />

        <div className="flex items-center gap-1">
          {STATUS_FILTERS.map((s) => (
            <button
              key={s}
              onClick={() => setStatusFilter(s)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                statusFilter === s
                  ? "bg-teal text-navy"
                  : "text-slate-500 hover:text-slate-200 bg-navy-200"
              }`}
            >
              {s}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-1">
          {TYPE_FILTERS.map((t) => (
            <button
              key={t}
              onClick={() => setTypeFilter(t)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                typeFilter === t
                  ? "bg-teal text-navy"
                  : "text-slate-500 hover:text-slate-200 bg-navy-200"
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      <div className="card p-0 overflow-hidden">
        {loading ? (
          <div className="p-8 text-center text-slate-600 text-sm">Loading decisions...</div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-slate-600 text-sm">No decisions found.</div>
        ) : (
          filtered.map((d) => <DecisionRow key={d.decision_id} d={d} />)
        )}
      </div>

      {!loading && (
        <div className="mt-2 text-xs text-slate-600 font-mono">
          {filtered.length} of {decisions.length} decisions
        </div>
      )}
    </div>
  );
}
