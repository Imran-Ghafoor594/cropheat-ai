"use client";

import Link from "next/link";
import historyStats from "@/lib/demo-history-stats.json";
import { DataSourceBadge } from "@/components/DataSourceBadge";

export default function HistoryPage() {
  const { exceedance, persistence } = historyStats;

  return (
    <main className="min-h-screen px-6 py-10 md:px-12 lg:px-20">
      <header className="mb-10 flex items-center justify-between">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-sage font-mono">
            Historical View
          </span>
          <h1 className="font-display text-3xl font-semibold text-ink mt-1">
            {historyStats.window_start} → {historyStats.window_end}
          </h1>
          <p className="text-ink-muted text-sm mt-1">{historyStats.region_label}</p>
        </div>
        <Link href="/dashboard" className="text-sm text-sage hover:underline">
          ← Dashboard
        </Link>
      </header>

      <div className="mb-6">
        <DataSourceBadge source="DEMO_DATA" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
        <StatCard
          title="Heat Exposure (Exceedance)"
          unit={exceedance.units}
          min={exceedance.min}
          mean={exceedance.mean}
          max={exceedance.max}
          nCells={exceedance.n_cells}
          color="#FB923C"
        />
        <StatCard
          title="Heat Persistence"
          unit={persistence.units}
          min={persistence.min}
          mean={persistence.mean}
          max={persistence.max}
          nCells={persistence.n_cells}
          color="#F43F5E"
        />
      </div>

      <div className="glass-panel rounded-2xl p-6">
        <h3 className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-3">
          A note on honesty
        </h3>
        <p className="text-sm text-ink-muted leading-relaxed">{historyStats.note}</p>
      </div>
    </main>
  );
}

function StatCard({
  title, unit, min, mean, max, nCells, color,
}: { title: string; unit: string; min: number; mean: number; max: number; nCells: number; color: string }) {
  const pct = ((mean - min) / (max - min)) * 100;
  return (
    <div className="glass-panel rounded-2xl p-6">
      <h3 className="font-display text-base font-medium text-ink mb-1">{title}</h3>
      <p className="text-xs text-ink-muted font-mono mb-5">
        {nCells} tiles analyzed · unit: {unit}
      </p>

      <div className="flex items-end gap-8 mb-6">
        <div>
          <p className="text-[10px] text-ink-muted uppercase tracking-wide">Min</p>
          <p className="font-mono text-lg text-ink">{min.toFixed(1)}</p>
        </div>
        <div>
          <p className="text-[10px] text-ink-muted uppercase tracking-wide">Mean</p>
          <p className="font-mono text-2xl" style={{ color }}>
            {mean.toFixed(1)}
          </p>
        </div>
        <div>
          <p className="text-[10px] text-ink-muted uppercase tracking-wide">Max</p>
          <p className="font-mono text-lg text-ink">{max.toFixed(1)}</p>
        </div>
      </div>

      <div className="h-2 rounded-full bg-hairline overflow-hidden">
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}
