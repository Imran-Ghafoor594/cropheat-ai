"use client";

import { motion } from "framer-motion";
import type { FieldRiskResult } from "@/types/risk";
import { RiskRing } from "./RiskRing";
import { DataSourceBadge } from "./DataSourceBadge";

export function HeroRiskCard({
  field, crop, growthStage,
}: { field: FieldRiskResult; crop: string; growthStage: string }) {
  const topDriver = field.primary_factors[0]?.replace("_", " ") ?? "unknown";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-3xl p-8 md:p-10 flex flex-col md:flex-row items-center gap-8"
    >
      <RiskRing score={field.risk_score} level={field.risk_level} size={200} />

      <div className="flex-1 text-center md:text-left">
        <div className="flex items-center justify-center md:justify-start gap-3 mb-2">
          <span className="text-[11px] uppercase tracking-[0.2em] text-ink-muted font-mono">
            Crop Heat Risk
          </span>
          <DataSourceBadge source={field.data_source} />
        </div>

        <h2 className="font-display text-2xl md:text-3xl font-semibold text-ink mb-1 capitalize">
          {crop} · {growthStage.replace("_", " ")}
        </h2>
        <p className="text-sm text-ink-muted mb-4">
          {field.label ?? `${field.latitude.toFixed(4)}, ${field.longitude.toFixed(4)}`}
        </p>

        <div className="inline-flex items-center gap-2 rounded-full bg-risk-high/10 border border-risk-high/25 px-3 py-1.5 text-xs text-risk-high">
          ↑ Elevated risk driven by {topDriver}
        </div>

        <p className="text-[11px] text-ink-muted mt-4 max-w-md">
          Explainable Crop Heat-Risk Engine — a transparent, weighted decision-support
          index, not a black-box prediction. See the breakdown below for exactly why.
        </p>
      </div>
    </motion.div>
  );
}
