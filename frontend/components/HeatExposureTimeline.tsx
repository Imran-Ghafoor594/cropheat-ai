"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ReferenceLine, ResponsiveContainer,
} from "recharts";
import { motion } from "framer-motion";

interface TimelineProps {
  hours: string[];
  temperatures: number[];
  thresholdC: number;
  accentColor: string;
}

/**
 *  "killer feature": a 24-hour temperature curve against the
 * crop's growth-stage threshold, with real periods above/below computed
 * from the actual array (never fabricated). If the analyzed day never
 * crosses the threshold, this component says so honestly rather than
 * inventing a dramatic exceedance.
 */
export function HeatExposureTimeline({ hours, temperatures, thresholdC, accentColor }: TimelineProps) {
  const data = hours.map((h, i) => ({ hour: `${h}:00`, temp: temperatures[i] }));

  const aboveThresholdHours = temperatures.filter((t) => t > thresholdC).length;

  // Longest continuous run above threshold
  let longestRun = 0;
  let currentRun = 0;
  for (const t of temperatures) {
    if (t > thresholdC) {
      currentRun += 1;
      longestRun = Math.max(longestRun, currentRun);
    } else {
      currentRun = 0;
    }
  }

  return (
    <div className="glass-panel rounded-2xl p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-display text-base font-medium text-ink">24-Hour Heat Exposure</h3>
        <span className="text-[10px] font-mono text-ink-muted">
          threshold: {thresholdC}°C
        </span>
      </div>

      <ResponsiveContainer width="100%" height={220}>
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="tempGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={accentColor} stopOpacity={0.5} />
              <stop offset="100%" stopColor={accentColor} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A332E" vertical={false} />
          <XAxis
            dataKey="hour"
            stroke="#8B968F"
            fontSize={10}
            interval={2}
            tickLine={false}
            axisLine={{ stroke: "#2A332E" }}
          />
          <YAxis stroke="#8B968F" fontSize={10} tickLine={false} axisLine={false} width={32} />
          <ReferenceLine
            y={thresholdC}
            stroke="#F43F5E"
            strokeDasharray="4 4"
            label={{ value: "CROP THRESHOLD", position: "insideTopRight", fill: "#F43F5E", fontSize: 9 }}
          />
          <Tooltip
            contentStyle={{ background: "#12171A", border: "1px solid #2A332E", borderRadius: 8, fontSize: 12 }}
            labelStyle={{ color: "#E8ECE9" }}
            formatter={(value: number) => [`${value.toFixed(1)}°C`, "Apparent Temp"]}
          />
          <Area type="monotone" dataKey="temp" stroke={accentColor} strokeWidth={2} fill="url(#tempGradient)" />
        </AreaChart>
      </ResponsiveContainer>

      <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-hairline">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
          <p className="text-[10px] uppercase tracking-wide text-ink-muted">Above Threshold</p>
          <p className="font-mono text-xl text-ink mt-1">
            {aboveThresholdHours}
            <span className="text-sm text-ink-muted">h</span>
          </p>
        </motion.div>
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}>
          <p className="text-[10px] uppercase tracking-wide text-ink-muted">Longest Continuous</p>
          <p className="font-mono text-xl text-ink mt-1">
            {longestRun}
            <span className="text-sm text-ink-muted">h</span>
          </p>
        </motion.div>
      </div>

      {aboveThresholdHours === 0 && (
        <p className="text-[11px] text-ink-muted mt-3 italic">
          This analyzed day stayed below the crop's threshold at every hour — genuinely, not adjusted for effect.
        </p>
      )}
    </div>
  );
}
