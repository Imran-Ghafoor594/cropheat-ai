"use client";

import type { RiskComponent } from "@/types/risk";

const COMPONENT_LABELS: Record<string, string> = {
  temperature: "Temperature",
  exposure: "Heat Exposure",
  persistence: "Persistence",
  humidity_wetbulb: "Humidity / Wet-Bulb",
  crop_sensitivity: "Crop Sensitivity",
  growth_stage: "Growth Stage",
};

/**
 *  "Why?" explainability panel: each component's WEIGHTED
 * contribution as a horizontal bar (not the raw 0-100 score, which would
 * misrepresent low-weight components as more important than they are to
 * the final score) plus its plain-language explanation and data source.
 */
export function ExplainabilityBars({ components }: { components: RiskComponent[] }) {
  const maxContribution = Math.max(...components.map((c) => c.weighted_contribution), 1);
  const sorted = [...components].sort((a, b) => b.weighted_contribution - a.weighted_contribution);

  return (
    <div className="space-y-4">
      {sorted.map((c) => {
        const pct = (c.weighted_contribution / maxContribution) * 100;
        return (
          <div key={c.name}>
            <div className="flex items-baseline justify-between mb-1">
              <span className="text-sm font-medium text-ink">
                {COMPONENT_LABELS[c.name] ?? c.name}
              </span>
              <span className="font-mono text-xs text-ink-muted">
                {c.weighted_contribution.toFixed(1)}
              </span>
            </div>
            <div className="h-2 rounded-full bg-hairline overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-risk-low via-risk-moderate to-risk-high transition-[width] duration-500"
                style={{ width: `${pct}%` }}
              />
            </div>
            <p className="text-xs text-ink-muted mt-1.5 leading-relaxed">{c.explanation}</p>
            <p className="text-[10px] text-ink-muted/70 mt-0.5 font-mono">{c.source}</p>
          </div>
        );
      })}
    </div>
  );
}
