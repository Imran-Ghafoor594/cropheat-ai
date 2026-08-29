import type { DataSource } from "@/types/risk";

const STYLE: Record<DataSource, string> = {
  LIVE: "bg-sage/15 text-sage border-sage/30",
  CACHED: "bg-ink-muted/15 text-ink-muted border-ink-muted/30",
  DEMO_DATA: "bg-risk-moderate/15 text-risk-moderate border-risk-moderate/30",
  SIMULATED: "bg-blue-400/15 text-blue-300 border-blue-400/30",
};

const LABEL: Record<DataSource, string> = {
  LIVE: "LIVE · FortyGuard",
  CACHED: "CACHED · FortyGuard",
  DEMO_DATA: "DEMO DATA",
  SIMULATED: "SIMULATED SCENARIO",
};


export function DataSourceBadge({ source }: { source: DataSource }) {
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-[10px] font-mono tracking-wide ${STYLE[source]}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {LABEL[source]}
    </span>
  );
}
