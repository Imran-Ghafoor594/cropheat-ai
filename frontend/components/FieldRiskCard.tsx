"use client";

import { motion } from "framer-motion";
import type { FieldRiskResult } from "@/types/risk";
import { RiskRing } from "./RiskRing";
import { DataSourceBadge } from "./DataSourceBadge";
import { ExplainabilityBars } from "./ExplainabilityBars";
import { AdvisoryPanel } from "./AdvisoryPanel";

export function FieldRiskCard({
  field, crop, growthStage, index = 0,
}: { field: FieldRiskResult; crop: string; growthStage: string; index?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.08, ease: "easeOut" }}
      className="glass-panel rounded-2xl p-6 hover:border-ink-muted/40 transition-colors"
    >
      <div className="flex items-start justify-between mb-5">
        <div>
          <h3 className="font-display text-lg font-semibold text-ink">
            {field.label ?? `${field.latitude.toFixed(4)}, ${field.longitude.toFixed(4)}`}
          </h3>
          <p className="text-xs text-ink-muted font-mono mt-0.5">
            {field.latitude.toFixed(4)}, {field.longitude.toFixed(4)}
          </p>
        </div>
        <DataSourceBadge source={field.data_source} />
      </div>

      <div className="flex flex-col items-center mb-6">
        <RiskRing score={field.risk_score} level={field.risk_level} />
      </div>

      <div className="mb-5">
        <h4 className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2">Why?</h4>
        <ExplainabilityBars components={field.components} />
      </div>

      <div className="mb-5 pt-4 border-t border-hairline">
        <h4 className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2">
          Primary Drivers
        </h4>
        <div className="flex flex-wrap gap-2">
          {field.primary_factors.map((factor) => (
            <span
              key={factor}
              className="text-xs px-2.5 py-1 rounded-full bg-risk-high/10 text-risk-high border border-risk-high/25"
            >
              {factor.replace("_", " ")}
            </span>
          ))}
        </div>
      </div>

      <div className="pt-4 border-t border-hairline">
        <h4 className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2">
          AI Advisory
        </h4>
        <AdvisoryPanel field={field} crop={crop} growthStage={growthStage} />
      </div>
    </motion.div>
  );
}

