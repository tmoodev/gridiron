import { useEffect, useState } from "react";
import { api } from "../api";

interface JobStatus {
  job_id: string;
  job_name: string;
  status: "success" | "failed" | "running" | "skipped";
  started_at: string;
  finished_at?: string | null;
  error?: string | null;
}

interface HealthData {
  status: string;
  version: string;
}

const JOB_NAMES = [
  "sync_leagues",
  "sync_rosters",
  "sync_players",
  "run_research",
  "run_valuation",
  "run_lineup_waiver",
  "sync_strategy_docs",
];

const STATUS_COLORS: Record<string, string> = {
  success: "text-teal",
  failed: "text-red-400",
  running: "text-yellow-400",
  skipped: "text-slate-500",
};

const STATUS_DOTS: Record<string, string> = {
  success: "bg-teal",
  failed: "bg-red-500",
  running: "bg-yellow-400 animate-pulse",
  skipped: "bg-slate-600",
};

function JobRow({ job }: { job: JobStatus }) {
  const dotCls = STATUS_DOTS[job.status] ?? "bg-slate-600";
  const textCls = STATUS_COLORS[job.status] ?? "text-slate-400";
  const duration =
    job.started_at && job.finished_at
      ? Math.round(
          (new Date(job.finished_at).getTime() - new Date(job.started_at).getTime()) / 1000
        )
      : null;

  return (
    <div className="flex items-center gap-3 py-2.5 border-b border-border last:border-0">
      <span className={`w-2 h-2 rounded-full shrink-0 ${dotCls}`} />
      <span className="font-mono text-sm text-slate-300 flex-1">{job.job_name}</span>
      <span className={`text-xs font-mono ${textCls}`}>{job.status}</span>
      {duration != null && (
        <span className="text-xs text-slate-600 font-mono">{duration}s</span>
      )}
      <span className="text-xs text-slate-600 font-mono">
        {new Date(job.started_at).toLocaleString()}
      </span>
    </div>
  );
}

export default function SystemHealthPage() {
  const [health, setHealth] = useState<HealthData | null>(null);
  const [jobs, setJobs] = useState<JobStatus[]>([]);
  const [triggering, setTriggering] = useState<string | null>(null);
  const [triggerResult, setTriggerResult] = useState<Record<string, string>>({});

  useEffect(() => {
    void api.health().then(setHealth).catch(() => setHealth(null));
    // Jobs endpoint doesn't exist yet — placeholder
    setJobs([]);
  }, []);

  const triggerJob = async (jobName: string) => {
    setTriggering(jobName);
    setTriggerResult((prev) => ({ ...prev, [jobName]: "triggering..." }));
    try {
      const result = await api.triggerJob(jobName);
      setTriggerResult((prev) => ({ ...prev, [jobName]: result.status ?? "triggered" }));
    } catch (e) {
      setTriggerResult((prev) => ({ ...prev, [jobName]: `error: ${String(e)}` }));
    } finally {
      setTriggering(null);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
      <h1 className="font-display font-semibold text-slate-100 text-lg">System Health</h1>

      {/* API Status */}
      <div className="card space-y-3">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
          API Status
        </div>
        {health ? (
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-teal" />
            <span className="text-sm text-slate-300">Backend online</span>
            <span className="text-xs text-slate-600 font-mono ml-auto">v{health.version}</span>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <span className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-sm text-red-400">Backend unreachable</span>
          </div>
        )}
      </div>

      {/* Job Triggers */}
      <div className="card space-y-3">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest">
          Job Triggers
        </div>
        <div className="space-y-2">
          {JOB_NAMES.map((jobName) => (
            <div key={jobName} className="flex items-center gap-3">
              <span className="font-mono text-sm text-slate-300 flex-1">{jobName}</span>
              {triggerResult[jobName] && (
                <span className="text-xs font-mono text-slate-500">{triggerResult[jobName]}</span>
              )}
              <button
                onClick={() => void triggerJob(jobName)}
                disabled={triggering === jobName}
                className="btn-ghost py-1 px-3 text-xs disabled:opacity-50"
              >
                {triggering === jobName ? "Running..." : "Run now"}
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Recent job runs */}
      <div className="card">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-widest mb-3">
          Recent Runs
        </div>
        {jobs.length === 0 ? (
          <div className="text-slate-600 text-sm">
            No job history available. Job run history will appear here once the scheduler has run.
          </div>
        ) : (
          jobs.map((job) => <JobRow key={job.job_id} job={job} />)
        )}
      </div>

      <div className="text-xs text-slate-600 font-mono">
        Gridiron v{health?.version ?? "—"} · datatrav-mdc-prod · 107.23.69.25
      </div>
    </div>
  );
}
