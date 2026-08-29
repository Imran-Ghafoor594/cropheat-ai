"use client";

import { GROWTH_STAGES_BY_CROP, SUPPORTED_CROPS, type SupportedCrop } from "@/types/risk";
import { CROP_THEMES } from "@/lib/crop-theme";

interface ControlPanelProps {
  crop: SupportedCrop;
  growthStage: string;
  date: string;
  onCropChange: (crop: SupportedCrop) => void;
  onGrowthStageChange: (stage: string) => void;
  onDateChange: (date: string) => void;
  onAnalyze: () => void;
  loading: boolean;
}

export function ControlPanel({
  crop, growthStage, date, onCropChange, onGrowthStageChange, onDateChange, onAnalyze, loading,
}: ControlPanelProps) {
  const stages = GROWTH_STAGES_BY_CROP[crop];
  const theme = CROP_THEMES[crop];

  return (
    <div className="glass-panel rounded-2xl p-6 space-y-5 sticky top-6">
      <div>
        <label className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2 block">Location</label>
        <div className="text-sm text-ink font-medium">San Joaquin Valley, CA</div>
        <div className="text-xs text-ink-muted mt-0.5">FortyGuard coverage: US-only (confirmed)</div>
      </div>

      <div>
        <label className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2 block">Crop</label>
        <div className="grid grid-cols-2 gap-2">
          {SUPPORTED_CROPS.map((c) => {
            const t = CROP_THEMES[c];
            const active = crop === c;
            return (
              <button
                key={c}
                onClick={() => {
                  onCropChange(c);
                  onGrowthStageChange(GROWTH_STAGES_BY_CROP[c][0]);
                }}
                style={active ? { borderColor: t.accent, background: t.accentSoft, color: t.accent } : undefined}
                className={`rounded-lg border px-3 py-2.5 text-sm capitalize transition-all flex items-center gap-2 ${
                  active ? "" : "border-hairline text-ink-muted hover:border-ink-muted"
                }`}
              >
                <span>{t.emoji}</span>
                {c}
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <label className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2 block">Growth Stage</label>
        <select
          value={growthStage}
          onChange={(e) => onGrowthStageChange(e.target.value)}
          className="w-full bg-surface border border-hairline rounded-lg px-3 py-2 text-sm text-ink capitalize focus:outline-none"
          style={{ borderColor: undefined }}
        >
          {stages.map((s) => (
            <option key={s} value={s}>
              {s.replace("_", " ")}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="text-[11px] uppercase tracking-[0.15em] text-ink-muted mb-2 block">Date</label>
        <input
          type="date"
          value={date}
          min="2021-01-01"
          max={new Date().toISOString().slice(0, 10)}
          onChange={(e) => onDateChange(e.target.value)}
          className="w-full bg-surface border border-hairline rounded-lg px-3 py-2 text-sm text-ink font-mono focus:outline-none"
        />
      </div>

      <button
        onClick={onAnalyze}
        disabled={loading}
        style={{ background: `linear-gradient(135deg, ${theme.accent}, ${theme.accent}99)` }}
        className="w-full rounded-lg text-[#0A0D0B] font-semibold py-2.5 text-sm disabled:opacity-50 transition-all hover:scale-[1.02]"
      >
        {loading ? "Analyzing…" : "Analyze Heat Risk"}
      </button>

      <div className="flex gap-3 pt-2 border-t border-hairline">
        <a href="/simulate" className="text-xs text-ink-muted hover:text-sage transition-colors">
          What-If Simulator →
        </a>
        <a href="/history" className="text-xs text-ink-muted hover:text-sage transition-colors">
          History →
        </a>
      </div>
    </div>
  );
}
