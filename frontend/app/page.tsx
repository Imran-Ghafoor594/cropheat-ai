"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { CROP_THEMES } from "@/lib/crop-theme";

const CROPS = ["wheat", "maize", "rice", "cotton"] as const;

const STORY_STEPS = [
  { label: "Live Climate Data", detail: "FortyGuard hyperlocal heatmaps" },
  { label: "Heat Exposure", detail: "Exceedance + persistence duration" },
  { label: "Crop Vulnerability", detail: "Growth-stage sensitivity" },
  { label: "AI Risk", detail: "Transparent, weighted risk score" },
  { label: "Action", detail: "Advisory recommendation" },
];

const DATA_SOURCES = [
  { name: "FortyGuard", role: "Real-time heat intelligence, exceedance, persistence" },
  { name: "NASA POWER", role: "Historical meteorological baselines" },
  { name: "Peer-reviewed agronomy", role: "Crop heat-sensitivity thresholds, cited per crop" },
];

export default function LandingPage() {
  return (
    <main className="min-h-screen overflow-hidden">
      {/* Hero */}
      <section className="relative px-6 md:px-12 lg:px-20 pt-24 pb-32">
        <AmbientFieldGlow />

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="relative z-10 max-w-3xl"
        >
          <span className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.25em] text-sage font-mono mb-6">
            <span className="w-1.5 h-1.5 rounded-full bg-sage animate-pulse" />
            Powered by FortyGuard Temperature API
          </span>

          <h1 className="font-display text-5xl md:text-7xl font-semibold text-ink leading-[1.05] mb-6">
            CropHeat <span className="text-sage">AI</span>
          </h1>

          <p className="font-display text-xl md:text-2xl text-ink-muted mb-4 leading-snug">
            Hyperlocal climate intelligence for crop-level heat decisions.
          </p>

          <p className="text-ink-muted text-base max-w-xl mb-10 leading-relaxed">
            CropHeat AI transforms hyperlocal environmental intelligence into
            crop-specific heat-risk insights, explanations, and actionable
            agricultural recommendations — built on real FortyGuard data, not
            guesswork.
          </p>

          <div className="flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="group inline-flex items-center gap-2 rounded-full bg-sage text-base px-7 py-3.5 text-sm font-semibold text-[#0A0D0B] transition-transform hover:scale-[1.03]"
            >
              Analyze Crop Risk
              <span className="transition-transform group-hover:translate-x-1">→</span>
            </Link>
            <a
              href="#how-it-works"
              className="inline-flex items-center gap-2 rounded-full border border-hairline px-7 py-3.5 text-sm font-medium text-ink-muted hover:text-ink hover:border-ink-muted transition-colors"
            >
              Explore How It Works
            </a>
          </div>
        </motion.div>
      </section>

      {/* Product preview */}
      <section className="px-6 md:px-12 lg:px-20 py-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="glass-panel rounded-3xl p-6 md:p-8 max-w-4xl mx-auto"
        >
          <div className="flex items-center justify-between mb-6">
            <span className="text-[11px] uppercase tracking-[0.2em] text-ink-muted font-mono">
              Product Preview
            </span>
            <span className="inline-flex items-center gap-1.5 text-[10px] font-mono text-risk-moderate">
              <span className="w-1.5 h-1.5 rounded-full bg-risk-moderate" />
              DEMO DATA
            </span>
          </div>
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="w-32 h-32 shrink-0 relative">
              <svg viewBox="0 0 168 168" className="-rotate-90">
                <circle cx="84" cy="84" r="76" fill="none" stroke="#1C2320" strokeWidth="8" />
                <circle
                  cx="84" cy="84" r="76" fill="none" stroke="#FB923C" strokeWidth="8"
                  strokeLinecap="round" strokeDasharray={2 * Math.PI * 76}
                  strokeDashoffset={2 * Math.PI * 76 * (1 - 0.73)}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-mono text-2xl text-risk-high">73</span>
                <span className="text-[8px] uppercase tracking-wider text-ink-muted">HIGH</span>
              </div>
            </div>
            <div className="flex-1 space-y-3">
              <p className="text-sm text-ink">
                <span className="font-medium">Wheat · Flowering</span> — North Block, San Joaquin Valley
              </p>
              <p className="text-xs text-ink-muted leading-relaxed">
                ↑ Elevated risk driven by <strong className="text-ink-muted">persistence</strong> — 8.7 continuous
                hours above the 28°C flowering threshold, per FortyGuard's exceedance/persistence heatmap layers.
              </p>
              <div className="flex flex-wrap gap-2 pt-1">
                {["persistence", "growth stage", "exposure"].map((f) => (
                  <span key={f} className="text-[10px] px-2 py-0.5 rounded-full bg-risk-high/10 text-risk-high border border-risk-high/25">
                    {f}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      </section>

      {/* Story strip */}
      <section id="how-it-works" className="px-6 md:px-12 lg:px-20 py-20 border-t border-hairline">
        <p className="text-[11px] uppercase tracking-[0.2em] text-ink-muted mb-10 font-mono">
          The story, in 30 seconds
        </p>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          {STORY_STEPS.map((step, i) => (
            <motion.div
              key={step.label}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.5, delay: i * 0.08 }}
              className="relative"
            >
              <div className="flex items-center gap-2 mb-3">
                <span className="font-mono text-xs text-sage">{String(i + 1).padStart(2, "0")}</span>
                {i < STORY_STEPS.length - 1 && (
                  <div className="hidden md:block flex-1 h-px bg-gradient-to-r from-hairline to-transparent" />
                )}
              </div>
              <h3 className="font-display text-lg font-medium text-ink mb-1">{step.label}</h3>
              <p className="text-sm text-ink-muted">{step.detail}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Crop grid */}
      <section className="px-6 md:px-12 lg:px-20 py-20 border-t border-hairline">
        <p className="text-[11px] uppercase tracking-[0.2em] text-ink-muted mb-10 font-mono">
          Built for four crops, with sourced heat-stress science
        </p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {CROPS.map((crop, i) => {
            const theme = CROP_THEMES[crop];
            return (
              <motion.div
                key={crop}
                initial={{ opacity: 0, scale: 0.96 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 0.4, delay: i * 0.06 }}
                className="glass-panel rounded-2xl p-6 flex flex-col items-start gap-3"
                style={{ boxShadow: `0 0 40px -20px ${theme.glow}` }}
              >
                <span className="text-2xl">{theme.emoji}</span>
                <h3 className="font-display text-base font-medium text-ink capitalize">{crop}</h3>
                <p className="text-xs text-ink-muted leading-relaxed">
                  Growth-stage-aware thresholds from peer-reviewed agronomy research.
                </p>
              </motion.div>
            );
          })}
        </div>
      </section>

      {/* Data sources / transparency */}
      <section className="px-6 md:px-12 lg:px-20 py-20 border-t border-hairline">
        <p className="text-[11px] uppercase tracking-[0.2em] text-ink-muted mb-10 font-mono">
          Data sources — every metric is labeled, nothing is fabricated
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {DATA_SOURCES.map((source) => (
            <div key={source.name} className="glass-panel rounded-2xl p-6">
              <h3 className="font-display text-base font-medium text-sage mb-2">{source.name}</h3>
              <p className="text-sm text-ink-muted leading-relaxed">{source.role}</p>
            </div>
          ))}
        </div>
      </section>

      <footer className="px-6 md:px-12 lg:px-20 py-10 border-t border-hairline flex items-center justify-between text-xs text-ink-muted">
        <span>CropHeat AI — Hackathon build</span>
        <Link href="/dashboard" className="text-sage hover:underline">
          Open Dashboard →
        </Link>
      </footer>
    </main>
  );
}

/** Subtle ambient background glow, evoking a heat/field gradient without
 * relying on a stock photo or literal imagery. */
function AmbientFieldGlow() {
  return (
    <div className="pointer-events-none absolute inset-0 -z-10">
      <div
        className="absolute -top-40 -right-40 w-[600px] h-[600px] rounded-full opacity-30 blur-[120px]"
        style={{ background: "radial-gradient(circle, #FB923C, transparent 70%)" }}
      />
      <div
        className="absolute top-40 -left-20 w-[400px] h-[400px] rounded-full opacity-20 blur-[100px]"
        style={{ background: "radial-gradient(circle, #7FB069, transparent 70%)" }}
      />
    </div>
  );
}
