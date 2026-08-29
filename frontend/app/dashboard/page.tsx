"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ControlPanel } from "@/components/ControlPanel";
import { FieldRiskCard } from "@/components/FieldRiskCard";
import { HeroRiskCard } from "@/components/HeroRiskCard";
import { TopRiskFields } from "@/components/TopRiskFields";
import { HeatExposureTimeline } from "@/components/HeatExposureTimeline";
import { DataSourceBadge } from "@/components/DataSourceBadge";
import { fetchRisk } from "@/lib/api";
import { CROP_THEMES } from "@/lib/crop-theme";
import type { RiskResponse, SupportedCrop } from "@/types/risk";
import timelineData from "@/lib/demo-timeline.json";

const CropHeatMap = dynamic(() => import("@/components/CropHeatMap").then((m) => m.CropHeatMap), {
  ssr: false,
  loading: () => <div className="w-full h-[420px] rounded-2xl bg-surface animate-pulse" />,
});


const REGION_AOI = {
  type: "Polygon" as const,
  coordinates: [
    [
      [-121.9213, 37.3135],
      [-121.8848, 37.3135],
      [-121.8848, 37.3425],
      [-121.9213, 37.3425],
      [-121.9213, 37.3135],
    ],
  ],
};

const SAMPLE_FIELDS = [
  { latitude: 37.3257, longitude: -121.9057, label: "North Block" },
  { latitude: 37.33, longitude: -121.9, label: "South Block" },
  { latitude: 37.328, longitude: -121.903, label: "East Ridge" },
];


const LOADING_STAGES = [
  "Analyzing FortyGuard heatmap…",
  "Calculating heat exposure…",
  "Evaluating crop vulnerability…",
  "Generating advisory…",
];

export default function DashboardPage() {
  const [crop, setCrop] = useState<SupportedCrop>("wheat");
  const [growthStage, setGrowthStage] = useState("flowering");
  const [date, setDate] = useState("2024-07-15");
  const [loading, setLoading] = useState(false);
  const [loadingStage, setLoadingStage] = useState(0);
  const [result, setResult] = useState<RiskResponse | null>(null);

  const theme = CROP_THEMES[crop];

  useEffect(() => {
    if (!loading) return;
    setLoadingStage(0);
    const interval = setInterval(() => {
      setLoadingStage((s) => Math.min(s + 1, LOADING_STAGES.length - 1));
    }, 500);
    return () => clearInterval(interval);
  }, [loading]);

  async function handleAnalyze() {
    setLoading(true);
    try {
      const req = {
        region_polygon_aoi: REGION_AOI,
        fields: SAMPLE_FIELDS,
        date,
        crop,
        growth_stage: growthStage,
        demo_mode: false,
      };

      const riskRes = await fetchRisk(req);
      setResult(riskRes);
    } finally {
      setLoading(false);
    }
  }

  const topField = result ? [...result.fields].sort((a, b) => b.risk_score - a.risk_score)[0] : null;

  return (
    <main className="min-h-screen px-6 py-10 md:px-12 lg:px-20 relative">
      <div
        className="pointer-events-none fixed top-0 right-0 w-[500px] h-[500px] rounded-full opacity-[0.08] blur-[140px] -z-10 transition-colors duration-700"
        style={{ background: theme.accent }}
      />

      <header className="mb-10 flex items-start justify-between">
        <div>
          <Link href="/" className="text-xs uppercase tracking-[0.25em] text-sage font-mono hover:underline">
            CropHeat AI
          </Link>
          <h1 className="font-display text-3xl md:text-4xl font-semibold text-ink mt-1">
            Live Crop Heat Intelligence
          </h1>
          <p className="text-ink-muted text-sm max-w-xl mt-1">
            Hyperlocal FortyGuard climate data, translated into crop-specific heat-stress
            risk and action.
          </p>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/methodology" className="text-xs text-ink-muted hover:text-sage transition-colors hidden md:block">
            Methodology
          </Link>
          <span className="text-4xl hidden md:block">{theme.emoji}</span>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6">
        <aside>
          <ControlPanel
            crop={crop} growthStage={growthStage} date={date}
            onCropChange={setCrop} onGrowthStageChange={setGrowthStage} onDateChange={setDate}
            onAnalyze={handleAnalyze} loading={loading}
          />
        </aside>

        <section>
          <AnimatePresence mode="wait">
            {!result && !loading && (
              <motion.div
                key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="glass-panel rounded-2xl p-16 text-center"
              >
                <span className="text-5xl mb-4 block">{theme.emoji}</span>
                <p className="text-ink-muted text-sm max-w-sm mx-auto">
                  Select a crop and growth stage, then run an analysis to see
                  per-field heat-stress risk, explanations, and AI advisory.
                </p>
              </motion.div>
            )}

            {loading && (
              <motion.div
                key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="glass-panel rounded-2xl p-16 text-center"
              >
                <div className="inline-flex gap-1 mb-4">
                  {[0, 1, 2].map((i) => (
                    <motion.span
                      key={i} className="w-2 h-2 rounded-full" style={{ background: theme.accent }}
                      animate={{ opacity: [0.3, 1, 0.3] }}
                      transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
                    />
                  ))}
                </div>
                <motion.p
                  key={loadingStage}
                  initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }}
                  className="text-ink-muted text-sm"
                >
                  {LOADING_STAGES[loadingStage]}
                </motion.p>
              </motion.div>
            )}

            {result && !loading && topField && (
              <motion.div key="result" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
                <div className="flex items-center justify-between glass-panel rounded-2xl px-5 py-3">
                  <div className="flex items-center gap-3 text-sm text-ink-muted">
                    <span className="capitalize text-ink font-medium">{result.crop}</span>
                    <span>·</span>
                    <span className="capitalize">{result.growth_stage.replace("_", " ")}</span>
                    <span>·</span>
                    <span className="font-mono">{result.date}</span>
                  </div>
                  <DataSourceBadge source={result.region_data_source} />
                </div>

                <HeroRiskCard field={topField} crop={result.crop} growthStage={result.growth_stage} />

                {result.heatmap_exceedance && (
                  <div>
                    <h2 className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-3">
                      Crop Heat Risk Map — Exceedance
                    </h2>
                    <CropHeatMap
                      heatmapData={result.heatmap_exceedance}
                      analyticLabel="Exceedance hours"
                      center={[SAMPLE_FIELDS[0].latitude, SAMPLE_FIELDS[0].longitude]}
                    />
                  </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <HeatExposureTimeline
                    hours={timelineData.hours}
                    temperatures={timelineData.apparent_temperature_c}
                    thresholdC={timelineData.threshold_c}
                    accentColor={theme.accent}
                  />
                  <TopRiskFields fields={result.fields} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  {result.fields.map((field, i) => (
                    <FieldRiskCard
                      key={`${field.latitude}-${field.longitude}`}
                      field={field} crop={result.crop} growthStage={result.growth_stage} index={i}
                    />
                  ))}
                </div>

                {result.budget_snapshot?.remaining_fraction != null && (
                  <div className="glass-panel rounded-2xl px-5 py-3 text-xs text-ink-muted font-mono">
                    FortyGuard credit budget remaining:{" "}
                    {(result.budget_snapshot.remaining_fraction * 100).toFixed(1)}%
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </section>
      </div>
    </main>
  );
}
