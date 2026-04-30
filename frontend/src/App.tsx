import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import LeaguePage from "./pages/LeaguePage";
import DecisionsPage from "./pages/DecisionsPage";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/decisions", label: "Decisions" },
];

function NavBar() {
  return (
    <header className="border-b border-field-800 bg-field-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center gap-8">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">🏈</span>
          <span className="font-bold text-field-400 tracking-tight text-lg">Gridiron</span>
        </div>
        <nav className="flex items-center gap-1">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-field-800 text-field-400"
                    : "text-slate-400 hover:text-slate-100 hover:bg-field-800/50"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="ml-auto">
          <span className="text-xs text-slate-500 font-mono">Travy2Chains</span>
        </div>
      </div>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen">
        <NavBar />
        <main className="max-w-6xl mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/leagues/:id" element={<LeaguePage />} />
            <Route path="/decisions" element={<DecisionsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
