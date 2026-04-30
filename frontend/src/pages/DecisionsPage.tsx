import { useEffect, useState } from "react";
import { api } from "../api";
import type { Decision } from "../types";

const TYPE_STYLES: Record<string, string> = {
  lineup:         "bg-blue-900/40 text-blue-300 border-blue-800",
  waiver:         "bg-purple-900/40 text-purple-300 border-purple-800",
  trade_response: "bg-orange-900/40 text-orange-300 border-orange-800",
  trade_proposal: "bg-yellow-900/40 text-yellow-300 border-yellow-800",
  research:       "bg-slate-800 text-slate-400 border-slate-700",
};

const STATUS_STYLES: Record<string, string> = {
  pending:  "bg-yellow-900/30 text-yellow-300",
  approved: "bg-field-900/50 text-field-400",
  rejected: "bg-red-900/30 text-red-400",
  expired:  "bg-slate-800 text-slate-500",
};

function DecisionCard({ d, onAction }: { d: Decision; onAction: () => void }) {
  const [expanded, setExpanded] = useState(false);
  const [loading, setLoading] = useState<"approve" | "reject" | null>(null);

  const handle = async (action: "approve" | "reject") => {
    setLoading(action);
    try {
      if (action === "approve") await api.approve(d.decision_id, d.league_id);
      else await api.reject(d.decision_id, d.league_id);
      onAction();
    } finally {
      setLoading(null);
    }
  };

  const typeStyle = TYPE_STYLES[d.type] ?? "bg-slate-800 text-slate-400 border-slate-700";
  const statusStyle = STATUS_STYLES[d.status] ?? "bg-slate-800 text-slate-400";
  const leagueName = d.league_id === "1183557197018804224" ? "Season 9" : "Degen X";

  return (
    <div className="card border border-field-800 space-y-3">
      {/* Header row */}
      <div className="flex items-start gap-3">
        <span className={`badge border ${typeStyle} shrink-0 mt-0.5`}>
          {d.type.replace(/_/g, " ")}
        </span>
        <div className="flex-1 min-w-0">
          <div className="text-sm font-medium text-slate-100">{d.summary}</div>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-slate-500">{leagueName}</span>
            <span className="text-slate-700">·</span>
            <span className="text-xs text-slate-500">
              {new Date(d.created_at).toLocaleDateString("en-US", {
                month: "short", day: "numeric", hour: "2-digit", minute: "2-digit",
              })}
            </span>
          </div>
        </div>
        <span className={`badge ${statusStyle} shrink-0`}>{d.status}</span>
      </div>

      {/* Expand reasoning */}
      {d.reasoning && (
        <div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="text-xs text-field-500 hover:text-field-400 transition-colors"
          >
            {expanded ? "Hide reasoning ▲" : "Show reasoning ▼"}
          </button>
          {expanded && (
            <div className="mt-2 p-3 bg-field-950 rounded-lg text-xs text-slate-400 leading-relaxed">
              {d.reasoning}
            </div>
          )}
        </div>
      )}

      {/* Proposed action */}
      {expanded && d.proposed_action && (
        <pre className="bg-field-950 rounded-lg p-3 text-xs text-slate-400 font-mono overflow-x-auto whitespace-pre-wrap">
          {JSON.stringify(d.proposed_action, null, 2)}
        </pre>
      )}

      {/* Actions */}
      {d.status === "pending" && (
        <div className="flex items-center gap-2 pt-1">
          <button
            onClick={() => handle("approve")}
            disabled={loading !== null}
            className="btn-primary disabled:opacity-50"
          >
            {loading === "approve" ? "Approving…" : "Approve"}
          </button>
          <button
            onClick={() => handle("reject")}
            disabled={loading !== null}
            className="btn-danger disabled:opacity-50"
          >
            {loading === "reject" ? "Rejecting…" : "Reject"}
          </button>
          <span className="text-xs text-slate-600 ml-auto">
            Expires {new Date(d.expires_at).toLocaleDateString("en-US", {
              month: "short", day: "numeric",
            })}
          </span>
        </div>
      )}
    </div>
  );
}

type StatusFilter = "pending" | "approved" | "rejected";

export default function DecisionsPage() {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [filter, setFilter] = useState<StatusFilter>("pending");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    try {
      const data = await api.decisions(undefined, filter);
      setDecisions(data);
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [filter]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-bold text-slate-100">Decisions</h1>
        <div className="flex items-center gap-1 bg-field-900 border border-field-800 rounded-lg p-1">
          {(["pending", "approved", "rejected"] as StatusFilter[]).map((s) => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3 py-1 rounded text-xs font-medium capitalize transition-colors ${
                filter === s
                  ? "bg-field-700 text-field-300"
                  : "text-slate-500 hover:text-slate-300"
              }`}
            >
              {s}
            </button>
          ))}
        </div>
      </div>

      {error && <div className="card border-red-900 text-red-400 text-sm">{error}</div>}

      {loading ? (
        <div className="text-slate-500 text-center py-12">Loading decisions…</div>
      ) : decisions.length === 0 ? (
        <div className="card text-slate-500 text-sm">
          No {filter} decisions.
        </div>
      ) : (
        <div className="space-y-3">
          {decisions.map((d) => (
            <DecisionCard key={d.decision_id} d={d} onAction={load} />
          ))}
        </div>
      )}
    </div>
  );
}
