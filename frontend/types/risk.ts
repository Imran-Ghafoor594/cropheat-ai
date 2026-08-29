// Mirrors backend/models/schemas.py — keep these in sync manually until an
// OpenAPI-generated client is wired in (Stage 11).

export type DataSource = "LIVE" | "CACHED" | "DEMO_DATA" | "SIMULATED";
export type RiskLevel = "LOW" | "MODERATE" | "HIGH" | "CRITICAL";

export interface RiskComponent {
  name: string;
  score_0_100: number;
  weight: number;
  weighted_contribution: number;
  source: string;
  explanation: string;
}

export interface FieldRiskResult {
  label: string | null;
  latitude: number;
  longitude: number;
  risk_score: number;
  risk_level: RiskLevel;
  components: RiskComponent[];
  primary_factors: string[];
  data_source: DataSource;
}

export interface BudgetSnapshot {
  plan: string | null;
  credits_total: number | null;
  credits_remaining: number | null;
  remaining_fraction: number | null;
}

export interface RiskResponse {
  crop: string;
  growth_stage: string;
  date: string;
  region_data_source: DataSource;
  fields: FieldRiskResult[];
  budget_snapshot: BudgetSnapshot | null;
  // BUGFIX: bundled directly into /api/risk's response so the dashboard no
  // longer needs a separate /api/environment call, which used to trigger a
  // SECOND live FortyGuard heatmap generation for the same data -- doubling
  // both credit cost and wait time.
  heatmap_exceedance?: any;
}

export interface FieldLocationInput {
  latitude: number;
  longitude: number;
  label?: string;
}

export interface RiskRequest {
  region_polygon_aoi: GeoJSON.Polygon;
  fields: FieldLocationInput[];
  date: string;
  crop: string;
  growth_stage: string;
  demo_mode: boolean;
}

export const SUPPORTED_CROPS = ["wheat", "maize", "rice", "cotton"] as const;
export type SupportedCrop = (typeof SUPPORTED_CROPS)[number];

export const GROWTH_STAGES_BY_CROP: Record<SupportedCrop, string[]> = {
  wheat: ["vegetative", "flowering", "grain_filling"],
  maize: ["vegetative", "tasseling", "silking", "grain_filling"],
  rice: ["vegetative", "flowering", "grain_filling"],
  cotton: ["vegetative", "flowering", "boll_development"],
};
