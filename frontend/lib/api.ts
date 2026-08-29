import type { RiskRequest, RiskResponse } from "@/types/risk";
import demoResponse from "./demo-response.json";
import demoExceedance from "./demo-heatmap-exceedance.json";
import demoPersistence from "./demo-heatmap-persistence.json";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

/**
 * Calls the real CropHeat backend (/api/risk). If the backend is unreachable
 * (e.g. previewing the frontend standalone without `uvicorn backend.main:app`
 * running), falls back to `demo-response.json` -- which is NOT fabricated
 * data. It's the actual output of RiskService.compute_region_risk() run
 * against FortyGuard's real bundled sample data (San Jose, July 2024,
 * wheat/flowering), captured verbatim. The UI always labels this via
 * `data_source: "DEMO_DATA"` on each field, per Section 28's requirement
 * that demo data is never presented as live.
 */
export async function fetchRisk(req: RiskRequest): Promise<RiskResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/risk`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      // BUGFIX: FortyGuard's heatmap endpoints are async (submit, then poll
      // until status="completed"). compute_region_risk() makes THREE
      // sequential heatmap calls (tcm, exceedance, persistence) plus up to
      // 3 env_params calls for the top-ranked fields -- easily over 15s
      // total. The old 15s timeout was aborting the fetch on the frontend
      // side WHILE the backend call kept running and completed successfully
      // (confirmed: FortyGuard credits were actually deducted server-side
      // even though the UI showed DEMO_DATA, because the frontend had
      // already given up and rendered its local fallback by then).
      signal: AbortSignal.timeout(90000),
    });
    if (!res.ok) throw new Error(`Backend responded ${res.status}`);
    return (await res.json()) as RiskResponse;
  } catch (err) {
    console.warn(
      "[CropHeat] Backend unreachable or timed out, falling back to bundled DEMO_DATA response:",
      err
    );
    return demoResponse as RiskResponse;
  }
}

export interface EnvironmentResponse {
  date: string;
  tcm: { source: string; data: any };
  exceedance: { source: string; data: any };
  persistence: { source: string; data: any };
  budget: any;
}

/**
 * Fetches the region's raw heatmap layers (for the map view). Falls back to
 * the real bundled multi-day sample (San Jose, 2024-07-12 to 2024-07-18) --
 * same honesty guarantee as fetchRisk: this is genuine FortyGuard output,
 * not synthesized, labeled DEMO_DATA in the UI.
 */
export async function fetchEnvironment(req: RiskRequest): Promise<EnvironmentResponse> {
  try {
    const res = await fetch(`${API_BASE}/api/environment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(req),
      // Same async-polling reasoning as fetchRisk above.
      signal: AbortSignal.timeout(90000),
    });
    if (!res.ok) throw new Error(`Backend responded ${res.status}`);
    return (await res.json()) as EnvironmentResponse;
  } catch (err) {
    console.warn("[CropHeat] Backend unreachable or timed out, falling back to bundled DEMO_DATA heatmap:", err);
    return {
      date: req.date,
      tcm: { source: "DEMO_DATA", data: demoExceedance },
      exceedance: { source: "DEMO_DATA", data: demoExceedance },
      persistence: { source: "DEMO_DATA", data: demoPersistence },
      budget: null,
    };
  }
}
