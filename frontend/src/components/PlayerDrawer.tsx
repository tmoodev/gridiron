import { useEffect, useState } from "react";
import { api } from "../api";
import type { IntelItem, Player } from "../types";

interface Props {
  player: Player;
  leagueId: string;
  onClose: () => void;
}

function StatusDot({ status }: { status: string | null }) {
  if (!status || status === "Active") {
    return <span className="inline-block w-2 h-2 rounded-full bg-teal" />;
  }
  if (["Injured Reserve", "IR"].includes(status)) {
    return <span className="inline-block w-2 h-2 rounded-full bg-red-500" />;
  }
  if (["Questionable", "Doubtful"].includes(status)) {
    return <span className="inline-block w-2 h-2 rounded-full bg-yellow-400" />;
  }
  return <span className="inline-block w-2 h-2 rounded-full bg-slate-500" />;
}

function ValBlock({ label, value }: { label: string; value: number | null | undefined }) {
  return (
    <div className="bg-navy-200 rounded-lg p-3 text-center">
      <div className="text-xs text-slate-500 mb-1">{label}</div>
      <div className="font-mono text-lg font-medium text-teal">
        {value != null ? value : "—"}
      </div>
    </div>
  );
}

export default function PlayerDrawer({ player, leagueId: _leagueId, onClose }: Props) {
  const [intel, setIntel] = useState<IntelItem[]>([]);
  const [intelLoading, setIntelLoading] = useState(true);

  useEffect(() => {
    void api
      .playerIntel(player.player_id, 5)
      .then(setIntel)
      .catch(() => setIntel([]))
      .finally(() => setIntelLoading(false));
  }, [player.player_id]);

  const vals = player.valuations;

  return (
    <div className="fixed inset-0 z-50 flex justify-end" onClick={onClose}>
      <div
        className="w-[420px] h-full bg-navy-50 border-l border-border overflow-y-auto flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between p-5 border-b border-border">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <StatusDot status={player.status} />
              <span className="font-display font-semibold text-slate-100 text-lg">
                {player.player_name ?? player.player_id}
              </span>
            </div>
            <div className="flex items-center gap-2 text-sm text-slate-400 font-mono">
              <span className="text-teal font-medium">{player.position ?? "—"}</span>
              <span>·</span>
              <span>{player.team ?? "FA"}</span>
              {player.age && (
                <>
                  <span>·</span>
                  <span>age {player.age}</span>
                </>
              )}
              {player.years_exp != null && (
                <>
                  <span>·</span>
                  <span>{player.years_exp}yr exp</span>
                </>
              )}
            </div>
            {player.status && player.status !== "Active" && (
              <div className="mt-1.5 text-xs text-yellow-400 font-medium">
                {player.status}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="text-slate-500 hover:text-slate-200 transition-colors p-1"
          >
            ✕
          </button>
        </div>

        {/* Valuations */}
        {vals && (
          <div className="p-4 border-b border-border">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
              Gridiron Valuations
            </div>
            <div className="grid grid-cols-3 gap-2 mb-3">
              <ValBlock label="Dynasty" value={vals.dynasty} />
              <ValBlock label="Keeper" value={vals.keeper} />
              <ValBlock label="Redraft" value={vals.redraft} />
            </div>
            {(player.ktc_value_1qb != null || player.ktc_value_sf != null) && (
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-navy-200 rounded-lg p-3 text-center">
                  <div className="text-xs text-slate-500 mb-1">KTC 1QB</div>
                  <div className="font-mono text-sm text-slate-300">
                    {player.ktc_value_1qb ?? "—"}
                  </div>
                </div>
                <div className="bg-navy-200 rounded-lg p-3 text-center">
                  <div className="text-xs text-slate-500 mb-1">KTC SF</div>
                  <div className="font-mono text-sm text-slate-300">
                    {player.ktc_value_sf ?? "—"}
                  </div>
                </div>
              </div>
            )}
            {vals.reasoning && (
              <div className="mt-3 text-xs text-slate-500 italic leading-relaxed">
                {vals.reasoning}
              </div>
            )}
          </div>
        )}

        {/* IDP */}
        {vals?.idp && (
          <div className="p-4 border-b border-border">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-2">
              IDP Profile
            </div>
            <div className="grid grid-cols-3 gap-2">
              {(["weekly_floor", "weekly_ceiling", "idp_tier"] as const).map((k) => {
                const v = (vals.idp as Record<string, unknown>)?.[k];
                return (
                  <div key={k} className="bg-navy-200 rounded-lg p-3 text-center">
                    <div className="text-xs text-slate-500 mb-1">
                      {k.replace(/_/g, " ")}
                    </div>
                    <div className="font-mono text-sm text-teal">
                      {v != null ? String(v) : "—"}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Intel feed */}
        <div className="p-4 flex-1">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
            Intel Feed
          </div>
          {intelLoading ? (
            <div className="text-slate-600 text-sm">Loading...</div>
          ) : intel.length === 0 ? (
            <div className="text-slate-600 text-sm">No intel yet for this player.</div>
          ) : (
            <div className="space-y-3">
              {intel.map((item, i) => (
                <div
                  key={i}
                  className="bg-navy-200 rounded-lg p-3 text-xs leading-relaxed"
                >
                  <div className="text-slate-400 mb-1 font-mono">
                    {new Date(item.created_at).toLocaleDateString()} ·{" "}
                    <span
                      className={
                        item.intel.confidence === "HIGH"
                          ? "text-teal"
                          : item.intel.confidence === "MEDIUM"
                            ? "text-yellow-400"
                            : "text-slate-500"
                      }
                    >
                      {item.intel.confidence ?? "—"}
                    </span>
                  </div>
                  {item.intel.health && (
                    <div className="mb-1">
                      <span className="text-slate-500">Health: </span>
                      <span className="text-slate-300">{item.intel.health}</span>
                    </div>
                  )}
                  {item.intel.role && (
                    <div className="mb-1">
                      <span className="text-slate-500">Role: </span>
                      <span className="text-slate-300">{item.intel.role}</span>
                    </div>
                  )}
                  {item.intel.fantasy_outlook && (
                    <div>
                      <span className="text-slate-500">Outlook: </span>
                      <span className="text-slate-300">{item.intel.fantasy_outlook}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
