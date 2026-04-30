import { useEffect, useState } from "react";
import { api } from "../api";
import type { PolicyConfig } from "../types";

const ACTION_LABELS: Record<string, string> = {
  lineup_set: "Set Lineup",
  waiver_claim_low_faab: "Waiver Claim (Low FAAB)",
  waiver_claim_high_faab: "Waiver Claim (High FAAB)",
  player_drop_low_value: "Drop Player (Low Value)",
  player_drop_high_value: "Drop Player (High Value)",
  trade_respond: "Respond to Trade",
  trade_send: "Send Trade Offer",
};

const THRESHOLD_LABELS: Record<string, string> = {
  faab_high_pct: "FAAB High Threshold (%)",
  drop_value_high: "High Value Drop Threshold",
};

const MODE_OPTIONS = [
  { value: "propose", label: "Propose (require approval)" },
  { value: "auto_email", label: "Auto + email notification" },
  { value: "auto_silent", label: "Auto (silent)" },
];

export default function PolicyPanelPage() {
  const [config, setConfig] = useState<PolicyConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [draft, setDraft] = useState<PolicyConfig | null>(null);

  useEffect(() => {
    setLoading(true);
    void api
      .policy()
      .then((c) => {
        setConfig(c);
        setDraft(structuredClone(c));
      })
      .catch(() => setConfig(null))
      .finally(() => setLoading(false));
  }, []);

  const save = async () => {
    if (!draft) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.updatePolicy(draft);
      setConfig(structuredClone(draft));
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  const setMode = (key: string, value: string) => {
    setDraft((prev) => {
      if (!prev) return prev;
      return { ...prev, policy: { ...prev.policy, [key]: value } };
    });
  };

  const setThreshold = (key: string, value: number) => {
    setDraft((prev) => {
      if (!prev) return prev;
      return { ...prev, thresholds: { ...prev.thresholds, [key]: value } };
    });
  };

  const isDirty = JSON.stringify(draft) !== JSON.stringify(config);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-600 text-sm">
        Loading policy...
      </div>
    );
  }

  if (!draft) {
    return (
      <div className="max-w-2xl mx-auto px-4 py-6">
        <div className="card border-red-900 text-red-400 text-sm">
          Failed to load policy config.
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="font-display font-semibold text-slate-100 text-lg">Policy Panel</h1>
        <button
          onClick={() => void save()}
          disabled={saving || !isDirty}
          className="btn-primary disabled:opacity-50"
        >
          {saving ? "Saving..." : saved ? "Saved ✓" : "Save Changes"}
        </button>
      </div>

      {/* Action modes */}
      <div className="card space-y-4">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
          Action Modes
        </div>
        {Object.entries(ACTION_LABELS).map(([key, label]) => (
          <div key={key} className="flex items-center justify-between gap-4">
            <div className="text-sm text-slate-300">{label}</div>
            <div className="flex items-center gap-1 bg-navy-200 rounded-lg p-0.5">
              {MODE_OPTIONS.map((opt) => (
                <button
                  key={opt.value}
                  onClick={() => setMode(key, opt.value)}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                    draft.policy[key] === opt.value
                      ? "bg-teal text-navy font-semibold"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {opt.value === "propose" ? "Propose" : opt.value === "auto_email" ? "Auto+Email" : "Silent"}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Thresholds */}
      <div className="card space-y-4">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
          Thresholds
        </div>
        {Object.entries(THRESHOLD_LABELS).map(([key, label]) => (
          <div key={key} className="flex items-center justify-between gap-4">
            <div>
              <div className="text-sm text-slate-300">{label}</div>
              <div className="text-xs text-slate-600 font-mono mt-0.5">
                {key === "faab_high_pct"
                  ? "Bids above this % of remaining FAAB are 'high'"
                  : "Players above this value are 'high value' for drops"}
              </div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="range"
                min={key === "faab_high_pct" ? 5 : 1}
                max={key === "faab_high_pct" ? 50 : 20}
                value={draft.thresholds[key] ?? 0}
                onChange={(e) => setThreshold(key, Number(e.target.value))}
                className="w-24 accent-teal"
              />
              <span className="text-sm font-mono text-teal w-8 text-right">
                {draft.thresholds[key]}
                {key === "faab_high_pct" ? "%" : ""}
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="text-xs text-slate-600 font-mono leading-relaxed">
        Policy config is stored in DynamoDB (FF#CONFIG#POLICY) and takes effect on the next agent run.
        Changes here override config/policy.yaml defaults.
      </div>
    </div>
  );
}
