"use client";

import { motion } from "framer-motion";
import type { FieldRiskResult } from "@/types/risk";

const LEVEL_COLOR: Record<string, string> = {
  LOW: "#4ADE80", MODERATE: "#FBBF24", HIGH: "#FB923C", CRITICAL: "#F43F5E",
};

/** ranked list of fields by risk, with an explicit note when
 * env_params (humidity/wet-bulb) was only sampled for the top-N fields --
 * framed as a credit-conservation feature, not a limitation, per spec. */
export function TopRiskFields({ fields }: { fields: FieldRiskResult[] }) {
  const ranked = [...fields].sort((a, b) => b.risk_score - a.risk_score);
  const unsampledCount = fields.filter((f) =>
    f.components.some((c) => c.name === "humidity_wetbulb" && c.source.includes("not sampled"))
  ).length;

  return (
    <div className="glass-panel rounded-2xl p-6">
      <h3 className="font-display text-base font-medium text-ink mb-4">Top Risk Areas</h3>
      <div className="space-y-3">
        {ranked.map((field, i) => (
          <motion.div
            key={`${field.latitude}-${field.longitude}`}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.06 }}
            className="flex items-center gap-4 py-2"
          >
            <span className="font-mono text-sm text-ink-muted w-5">{i + 1}</span>
            <div className="flex-1 min-w-0">
              <p className="text-sm text-ink truncate">
                {field.label ?? `${field.latitude.toFixed(3)}, ${field.longitude.toFixed(3)}`}
              </p>
              <p className="text-[11px] text-ink-muted">
                {field.primary_factors[0]?.replace("_", " ") ?? "—"}
              </p>
            </div>
            <div className="text-right">
              <span className="font-mono text-lg" style={{ color: LEVEL_COLOR[field.risk_level] }}>
                {Math.round(field.risk_score)}
              </span>
              <p className="text-[9px] uppercase tracking-wide" style={{ color: LEVEL_COLOR[field.risk_level] }}>
                {field.risk_level}
              </p>
            </div>
          </motion.div>
        ))}
      </div>
      {unsampledCount > 0 && (
        <p className="text-[11px] text-ink-muted mt-4 pt-4 border-t border-hairline leading-relaxed">
          Environmental diagnostics (humidity/wet-bulb) sampled for the top-ranked
          fields only, to conserve FortyGuard API credits — {unsampledCount} field
          {unsampledCount !== 1 ? "s" : ""} use heatmap-derived risk alone.
        </p>
      )}
    </div>
  );
}
