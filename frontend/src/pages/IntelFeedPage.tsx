import { useEffect, useState } from "react";
import { api } from "../api";
import type { IntelItem } from "../types";

function IntelCard({ item }: { item: IntelItem }) {
  const confCls =
    item.intel.confidence === "HIGH"
      ? "text-teal"
      : item.intel.confidence === "MEDIUM"
        ? "text-yellow-400"
        : "text-slate-500";

  return (
    <div className="card space-y-2">
      <div className="flex items-center gap-2">
        <span className="font-medium text-slate-200 text-sm">
          {item.player_name ?? item.player_id}
        </span>
        {item.intel.confidence && (
          <span className={`text-xs font-mono ${confCls}`}>{item.intel.confidence}</span>
        )}
        <span className="text-xs text-slate-600 font-mono ml-auto">
          {new Date(item.created_at).toLocaleString()}
        </span>
      </div>

      {item.intel.health && (
        <div className="text-xs">
          <span className="text-slate-500">Health: </span>
          <span className="text-slate-300">{item.intel.health}</span>
        </div>
      )}
      {item.intel.role && (
        <div className="text-xs">
          <span className="text-slate-500">Role: </span>
          <span className="text-slate-300">{item.intel.role}</span>
        </div>
      )}
      {item.intel.fantasy_outlook && (
        <div className="text-xs">
          <span className="text-slate-500">Outlook: </span>
          <span className="text-slate-300">{item.intel.fantasy_outlook}</span>
        </div>
      )}
      {item.intel.raw && !item.intel.health && !item.intel.role && !item.intel.fantasy_outlook && (
        <div className="text-xs text-slate-400 leading-relaxed">{item.intel.raw}</div>
      )}

      <div className="text-[10px] text-slate-600 font-mono">player_id: {item.player_id}</div>
    </div>
  );
}

export default function IntelFeedPage() {
  const [items, setItems] = useState<IntelItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [confFilter, setConfFilter] = useState<string>("all");

  // Load intel for all players — use a broad search
  // The API exposes per-player intel; we fetch the recent global feed via a known approach:
  // GET /players/{playerId}/intel doesn't have a global endpoint yet, so we use the decision log
  // to seed player IDs. For now, display a message if nothing is available.
  useEffect(() => {
    setLoading(false);
  }, []);

  const loadPlayerIntel = async (playerId: string) => {
    try {
      const intel = await api.playerIntel(playerId, 20);
      setItems((prev) => {
        const existing = new Set(prev.map((i) => `${i.player_id}:${i.created_at}`));
        const newItems = intel.filter((i) => !existing.has(`${i.player_id}:${i.created_at}`));
        return [...prev, ...newItems].sort(
          (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      });
    } catch {
      // ignore
    }
  };

  const filtered = items.filter((item) => {
    const name = (item.player_name ?? item.player_id).toLowerCase();
    if (search && !name.includes(search.toLowerCase())) return false;
    if (confFilter !== "all" && item.intel.confidence !== confFilter) return false;
    return true;
  });

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="font-display font-semibold text-slate-100 text-lg">Intel Feed</h1>
      </div>

      <div className="flex flex-wrap gap-3">
        <input
          type="text"
          placeholder="Filter by player..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="bg-navy-200 border border-border rounded-lg px-3 py-1.5 text-sm text-slate-300 placeholder-slate-600 focus:outline-none focus:border-teal/50 font-mono"
        />
        <div className="flex gap-1">
          {["all", "HIGH", "MEDIUM", "LOW"].map((c) => (
            <button
              key={c}
              onClick={() => setConfFilter(c)}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                confFilter === c
                  ? "bg-teal text-navy"
                  : "text-slate-500 hover:text-slate-200 bg-navy-200"
              }`}
            >
              {c}
            </button>
          ))}
        </div>

        <div className="flex gap-2 ml-auto">
          <input
            type="text"
            placeholder="Player ID to load..."
            className="bg-navy-200 border border-border rounded-lg px-3 py-1.5 text-xs text-slate-300 placeholder-slate-600 focus:outline-none focus:border-teal/50 font-mono w-40"
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                const val = (e.target as HTMLInputElement).value.trim();
                if (val) void loadPlayerIntel(val);
                (e.target as HTMLInputElement).value = "";
              }
            }}
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center text-slate-600 text-sm py-12">Loading...</div>
      ) : filtered.length === 0 ? (
        <div className="text-center text-slate-600 text-sm py-12">
          <div className="mb-2">No intel loaded yet.</div>
          <div className="text-xs text-slate-700">
            Enter a player ID above and press Enter to load their intel, or click a player in the Dashboard roster.
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((item, i) => (
            <IntelCard key={`${item.player_id}:${item.created_at}:${i}`} item={item} />
          ))}
        </div>
      )}
    </div>
  );
}
