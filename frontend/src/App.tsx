import { useEffect, useState } from "react";
import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import { api } from "./api";
import Dashboard from "./pages/Dashboard";
import DecisionLogPage from "./pages/DecisionLogPage";
import IntelFeedPage from "./pages/IntelFeedPage";
import PolicyPanelPage from "./pages/PolicyPanelPage";
import SystemHealthPage from "./pages/SystemHealthPage";
import type { League } from "./types";

const LEAGUE_LABELS: Record<string, string> = {
  "1331779473430810624": "Dynasty",
  "1183557197018804224": "Keeper",
};

const NAV_LINKS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/decisions", label: "Log" },
  { to: "/intel", label: "Intel" },
  { to: "/policy", label: "Policy" },
  { to: "/health", label: "Health" },
];

interface HeaderProps {
  leagues: League[];
  activeLeagueId: string | null;
  onLeagueChange: (id: string) => void;
  lastSync: string | null;
}

function Header({ leagues, activeLeagueId, onLeagueChange, lastSync }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-border bg-navy/95 backdrop-blur-sm">
      <div className="flex items-center gap-4 px-4 h-12">
        <span className="font-display font-bold text-teal tracking-tight text-base shrink-0">
          Gridiron
        </span>

        {leagues.length > 0 && (
          <div className="flex items-center gap-0.5 bg-navy-200 rounded-lg p-0.5">
            {leagues.map((l) => (
              <button
                key={l.league_id}
                onClick={() => onLeagueChange(l.league_id)}
                className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                  activeLeagueId === l.league_id
                    ? "bg-teal text-navy font-semibold"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {LEAGUE_LABELS[l.league_id] ?? l.league_name ?? l.league_id}
              </button>
            ))}
          </div>
        )}

        <nav className="flex items-center gap-0.5">
          {NAV_LINKS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? "text-teal bg-navy-300"
                    : "text-slate-500 hover:text-slate-200 hover:bg-navy-200"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-3 shrink-0">
          {lastSync && (
            <span className="text-xs text-slate-600 font-mono">sync {lastSync}</span>
          )}
          <span className="text-xs text-slate-500 font-mono">Travis · v0.3</span>
        </div>
      </div>
    </header>
  );
}

export default function App() {
  const [leagues, setLeagues] = useState<League[]>([]);
  const [activeLeagueId, setActiveLeagueId] = useState<string | null>(null);
  const [lastSync, setLastSync] = useState<string | null>(null);

  useEffect(() => {
    void api.leagues().then((ls) => {
      setLeagues(ls);
      if (ls.length > 0 && !activeLeagueId) {
        const dynasty = ls.find((l) => l.league_id === "1331779473430810624");
        setActiveLeagueId(dynasty?.league_id ?? ls[0].league_id);
      }
    });
    void api.health().then(() => setLastSync("just now"));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-navy">
        <Header
          leagues={leagues}
          activeLeagueId={activeLeagueId}
          onLeagueChange={setActiveLeagueId}
          lastSync={lastSync}
        />
        <Routes>
          <Route
            path="/"
            element={<Dashboard leagues={leagues} activeLeagueId={activeLeagueId} />}
          />
          <Route path="/decisions" element={<DecisionLogPage />} />
          <Route path="/intel" element={<IntelFeedPage />} />
          <Route path="/policy" element={<PolicyPanelPage />} />
          <Route path="/health" element={<SystemHealthPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
