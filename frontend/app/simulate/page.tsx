"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import { RiskRing } from "@/components/RiskRing";
import { DataSourceBadge } from "@/components/DataSourceBadge";
import { ExplainabilityBars } from "@/components/ExplainabilityBars";
import type { RiskResponse } from "@/types/risk";
import demoResponse from "@/lib/demo-response.json";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";


export default function SimulatePage() {
  const baseRisk = demoResponse as RiskResponse; // starting point: last real/demo analysis
  const [tempDelta, setTempDelta] = useState(0);
  const [simulated, setSimulated] = useState<RiskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const field = baseRisk.fields[0];

  async function runSimulation(delta: number) {
    setTempDelta(delta);
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ base_risk: baseRisk, temperature_delta_c: delta }),
        signal: AbortSignal.timeout(8000),
      });
      if (res.ok) {
        setSimulated(await res.json());
      }
    } catch {
      // Backend unreachable -- simulation simply doesn't update; base card still shows.
    } finally {
      setLoading(false);
    }
  }

  const displayedField = simulated?.fields[0] ?? field;

  return (
    <main className="min-h-screen px-6 py-10 md:px-12 lg:px-20">
      <header className="mb-10 flex items-center justify-between">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-sage font-mono">
            What-If Simulation
          </span>
          <h1 className="font-display text-3xl font-semibold text-ink mt-1">
            Scenario Explorer
          </h1>
          <p className="text-ink-muted text-sm mt-1 max-w-lg">
            Adjust temperature and see the risk recompute instantly — pure local
            math, zero additional FortyGuard credits spent.
          </p>
        </div>
        <Link href="/dashboard" className="text-sm text-sage hover:underline">
          ← Dashboard
        </Link>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_380px] gap-8">
        <div className="glass-panel rounded-2xl p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h2 className="font-display text-lg font-medium text-ink">{field.label}</h2>
              <p className="text-xs text-ink-muted font-mono">
                {field.latitude.toFixed(4)}, {field.longitude.toFixed(4)}
              </p>
            </div>
            <DataSourceBadge source={displayedField.data_source} />
          </div>

          <div className="mb-10">
            <div className="flex items-center justify-between mb-3">
              <label className="text-sm text-ink-muted">Temperature adjustment</label>
              <span className="font-mono text-lg text-ink">
                {tempDelta > 0 ? "+" : ""}
                {tempDelta}°C
              </span>
            </div>
            <input
              type="range"
              min={-5}
              max={10}
              step={0.5}
              value={tempDelta}
              onChange={(e) => runSimulation(parseFloat(e.target.value))}
              className="w-full accent-risk-high"
            />
            <div className="flex justify-between text-[10px] text-ink-muted font-mono mt-1">
              <span>-5°C</span>
              <span>0</span>
              <span>+10°C</span>
            </div>
          </div>

          <div className="flex items-center gap-10">
            <motion.div
              key={displayedField.risk_score}
              initial={{ scale: 0.92, opacity: 0.6 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <RiskRing score={displayedField.risk_score} level={displayedField.risk_level} />
            </motion.div>
            <div className="flex-1">
              <p className="text-sm text-ink-muted leading-relaxed">
                {tempDelta === 0
                  ? "Baseline scenario — no adjustment applied."
                  : `Simulated: temperature shifted ${tempDelta > 0 ? "up" : "down"} by ${Math.abs(tempDelta)}°C from the base analysis.`}
              </p>
              {loading && <p className="text-xs text-ink-muted mt-2 animate-pulse">Recomputing…</p>}
            </div>
          </div>
        </div>

        <div className="glass-panel rounded-2xl p-6">
          <h3 className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-4">
            Risk Drivers
          </h3>
          <ExplainabilityBars components={displayedField.components} />
        </div>
      </div>
    </main>
  );
}
