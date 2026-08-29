"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import type { FieldRiskResult } from "@/types/risk";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

interface Advisory {
  summary: string;
  recommendations: string[];
  source: "AI_GENERATED" | "RULE_BASED_FALLBACK";
}

/** Fetches /api/advisory for a field's already-computed risk. The LLM (or
 * rule-based fallback, see backend/services/advisory_service.py) explains
 * the given risk_score/level -- it never recomputes or overrides it. */
export function AdvisoryPanel({ field, crop, growthStage }: {
  field: FieldRiskResult; crop: string; growthStage: string;
}) {
  const [advisory, setAdvisory] = useState<Advisory | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`${API_BASE}/api/advisory`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        crop, growth_stage: growthStage,
        risk_score: field.risk_score, risk_level: field.risk_level,
        primary_factors: field.primary_factors,
        component_explanations: Object.fromEntries(field.components.map((c) => [c.name, c.explanation])),
      }),
      signal: AbortSignal.timeout(10000),
    })
      .then((r) => (r.ok ? r.json() : null))
      .then((data) => !cancelled && setAdvisory(data))
      .catch(() => !cancelled && setAdvisory(null))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [field, crop, growthStage]);

  if (loading) {
    return <p className="text-xs text-ink-muted animate-pulse">Generating advisory…</p>;
  }
  if (!advisory) {
    return <p className="text-xs text-ink-muted">Advisory unavailable — backend unreachable.</p>;
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-3">
      <p className="text-sm text-ink leading-relaxed">{advisory.summary}</p>
      <ul className="space-y-1.5">
        {advisory.recommendations.map((rec, i) => (
          <li key={i} className="flex gap-2 text-xs text-ink-muted">
            <span className="text-sage mt-0.5">→</span>
            <span>{rec}</span>
          </li>
        ))}
      </ul>
      <span className="inline-block text-[9px] font-mono text-ink-muted/60 uppercase tracking-wide">
        {advisory.source === "AI_GENERATED" ? "AI-generated" : "Rule-based (no LLM key configured)"}
      </span>
    </motion.div>
  );
}
