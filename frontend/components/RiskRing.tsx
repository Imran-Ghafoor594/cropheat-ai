"use client";

import type { RiskLevel } from "@/types/risk";

const LEVEL_COLOR: Record<RiskLevel, string> = {
  LOW: "#4ADE80",
  MODERATE: "#FBBF24",
  HIGH: "#FB923C",
  CRITICAL: "#F43F5E",
};

interface RiskRingProps {
  score: number; // 0-100
  level: RiskLevel;
  size?: number;
}

/**
 * The dashboard's signature element: risk_score rendered as a gradient arc
 * sweeping 0-100 degrees-of-severity around a ring, rather than a generic
 * linear progress bar. The arc's own color transitions along the same
 * LOW->CRITICAL gradient used everywhere else in the app, so the ring reads
 * as "how far into the heat spectrum" at a glance, not just a percentage.
 */
export function RiskRing({ score, level, size = 168 }: RiskRingProps) {
  const strokeWidth = 10;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.max(0, Math.min(100, score));
  const offset = circumference * (1 - clamped / 100);
  const color = LEVEL_COLOR[level];
  const gradientId = "risk-ring-gradient";

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <defs>
          <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#4ADE80" />
            <stop offset="40%" stopColor="#FBBF24" />
            <stop offset="70%" stopColor="#FB923C" />
            <stop offset="100%" stopColor="#F43F5E" />
          </linearGradient>
        </defs>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1C2320"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={`url(#${gradientId})`}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-[stroke-dashoffset] duration-700 ease-out"
        />
      </svg>
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-4xl font-medium text-ink" style={{ color }}>
          {Math.round(clamped)}
        </span>
        <span className="text-[10px] tracking-[0.2em] text-ink-muted uppercase mt-1">
          {level}
        </span>
      </div>
    </div>
  );
}
