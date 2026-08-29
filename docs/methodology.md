# CropHeat AI — Methodology & Staged Plan

## Why no supervised ML 
No labeled crop-heat-damage dataset exists that is accessible for this hackathon.
Rather than fabricate labels (e.g. "temperature > 40C = heat stress" treated as
ground truth), CropHeat uses a transparent, weighted hybrid risk engine
(backend/risk_engine/) where every component is either:
  (a) real FortyGuard data (temperature, exceedance hours, persistence hours,
      humidity/wet-bulb), or
  (b) a static, peer-reviewed threshold from data/crop_profiles/*.json.

If a legitimate labeled dataset becomes available, XGBoost with SHAP would be
the natural next step (Section 10) -- but that is not represented as already
built, because it isn't.

## Staged implementation plan 
1. Repository audit -- DONE (see conversation history / git log)
2. GET /api/environment -- DONE (backend/api/routes/environmental.py)
3. GET /api/risk -- DONE (backend/api/routes/risk.py)
4. Frontend dashboard -- DONE (frontend/app/dashboard/)
5. Crop profiles -- DONE (data/crop_profiles/*.json)
6. FortyGuard heatmap (map view) -- PENDING
7. Historical view (/history) -- PENDING
8. Explainability -- PARTIALLY DONE (component breakdown + bars exist in the
   dashboard; a dedicated /explain deep-dive view is pending)
9. AI advisory (LLM explains, never overrides, the computed score) -- PENDING
10. What-if simulation (/simulate, pure local math, zero API calls) -- PENDING
11. Testing & deployment -- PARTIALLY DONE (backend risk-engine tests exist
    and pass against real bundled sample data; frontend has no test suite yet;
    no deployment config yet)

## Real schema discrepancies found (vs. quickstart repo docstrings)
1. `create_heatmap`'s docstring claims `tcm` tiles are in Fahrenheit; the
   bundled real sample (data/heatmaps/heatmap_parcel_diridon_san_jose_2024-07-15_tcm.json)
   has average_temperature values (~20-21) consistent with Celsius for a July
   San Jose reading. Not yet re-verified against a live call.
2. `environmental_parameters`'s actual response is nested
   ({"locations": [{"parameters": {param: [24 hourly values]}}]}), not a flat
   dict of scalars as a first read of the client signature might suggest.
3. Real heatmap responses nest tile features under `map_data.features`
   (GeoJSON FeatureCollection), not at the top level.

## Credit budget (Section per user instruction: "use API less, 2M credit total")
See backend/utils/budget_guard.py and backend/services/fortyguard_service.py
docstrings for the full design. Summary: one shared heatmap call per region
(not per field), env_params only for the top-3 fields by preliminary
heatmap-derived risk, aggressive SQLite caching, and a hard budget-floor
stop that falls back to DEMO MODE.
# CropHeat AI — Methodology

This document explains exactly how CropHeat AI turns FortyGuard's raw environmental data into a crop-specific heat-risk score — what is real data, what is a sourced scientific reference, and what is an engineering default. Nothing described below is a black-box prediction.

---

## 1. Why not machine learning?

A trained ML model needs labeled outcomes — real historical records of "this field, this crop, this weather → this much crop damage." No such labeled dataset exists that is accessible for this hackathon. Building one would mean either:

- fabricating labels (e.g. treating "temperature > 40°C" as ground-truth damage, with no evidence that's the actual threshold for a given crop), or
- training on made-up data and presenting the result as validated — which is scientifically dishonest.

CropHeat AI instead uses an **explainable hybrid risk engine**: a transparent, documented weighted sum of real environmental signals and sourced agronomic thresholds. Every number in the final score can be traced back to either live FortyGuard data or a cited peer-reviewed source — never an invented constant.

---

## 2. The six risk components

| Component | Weight | Source | What it measures |
|---|---|---|---|
| Temperature | 15% | FortyGuard `tcm` heatmap | How far the field's peak temperature is above the crop's growth-stage threshold |
| Heat Exposure | 15% | FortyGuard `exceedance` heatmap | Total hours the field spent above threshold in the analyzed window |
| Persistence | 20% | FortyGuard `persistence` heatmap | The *longest continuous* run of hours above threshold — no-recovery-window exposure is weighted higher than the same hours spread across multiple short episodes |
| Humidity / Wet-Bulb | 15% | FortyGuard `env_params` | Apparent temperature, wet-bulb temperature, relative humidity — evaporative cooling is impaired at high humidity, making the same air temperature more physiologically damaging |
| Crop Sensitivity | 15% | `data/crop_profiles/*.json` (static, sourced) | How heat-tolerant this crop generally is |
| Growth Stage | 20% | `data/crop_profiles/*.json` (static, sourced) | The crop's current phenological stage — every cited study below identifies growth-stage *timing* as the dominant factor in whether a given temperature actually causes damage, which is why this carries the highest weight |

**Formula:**
```
risk_score = Σ (component_score_0-100 × component_weight)
```
Each component is independently normalized to 0–100 before weighting, then the weighted sum is clipped to the 0–100 range and mapped to a risk level:

| Score | Level |
|---|---|
| 0–24 | LOW |
| 25–49 | MODERATE |
| 50–74 | HIGH |
| 75–100 | CRITICAL |

**These bands are CropHeat engineering defaults for communicating relative severity to a non-technical user — not a published agronomic standard.** They exist to make the score interpretable, not to claim scientific precision at the boundary between, say, 74 and 75.

---

## 3. What's real data vs. what's a static reference

**Live from FortyGuard, every analysis:**
- Peak/spatial temperature (`tcm`)
- Exceedance hours (`exceedance`)
- Persistence hours (`persistence`)
- Apparent temperature, wet-bulb temperature, relative humidity (`env_params` — sampled only for the top-ranked fields per region, to conserve API credits; see Section 5)

**Static per crop/growth-stage, sourced from peer-reviewed literature:**
- Heat-sensitivity rating (low / moderate / high / critical)
- Reference temperature threshold (°C)

---

## 4. Crop heat-stress thresholds — full citation list

Every threshold below is a number reported in a real, cited study — not an invented round number.

### Wheat (*Triticum aestivum*)
| Stage | Sensitivity | Threshold | Source |
|---|---|---|---|
| Vegetative | Low | — (no threshold cited; heat mainly accelerates development rate rather than damaging tissue) | — |
| Flowering | Critical | 28°C | Girousse et al., *Field Crops Research* 316 (2024) 109489; Saini & Aspinall 1982 |
| Grain filling | High | 32°C | Girousse et al. 2024; Semenov & Stratonovitch, *J. Exp. Bot.* 66(12):3599 (2015) |

### Maize (*Zea mays*)
| Stage | Sensitivity | Threshold | Source |
|---|---|---|---|
| Vegetative | Low | 38°C | Crafts-Brandner & Salvucci 2002, cited in Djalovic et al. 2024 |
| Tasseling | Critical | 35°C | Djalovic et al., *The Plant Genome* (2024); Begcy et al. 2019 |
| Silking | Critical | 35°C | "Heat-stress-induced ROS in maize silks," *iScience* (2024) |
| Grain filling | Moderate | 35°C | Shao et al. 2021, cited in Djalovic et al. 2024 |

### Rice (*Oryza sativa*)
| Stage | Sensitivity | Threshold | Source |
|---|---|---|---|
| Vegetative | Low | — (comparatively heat-tolerant; not a focus of the cited literature) | — |
| Flowering | Critical | 35°C | Jagadish et al., *J. Exp. Bot.* 58(7):1627 (2007); Satake & Yoshida 1978 |
| Grain filling | Moderate | — | Prasad et al., *Field Crops Research* 95:398–411 (2006) |

*Note: some genotypes show sterility onset closer to 33°C (Bheemanahalli et al. 2016) — CropHeat uses the more frequently replicated 35°C as the default and documents the lower variant as genotype-dependent uncertainty rather than hiding it.*

### Cotton (*Gossypium hirsutum*)
| Stage | Sensitivity | Threshold | Source |
|---|---|---|---|
| Vegetative | Low | 35°C | Bibi et al. 2008/2010, cited in *Stress Physiology in Cotton* Ch.1 |
| Flowering | Critical | 30°C | Oosterhuis & Snider, *J. Cotton Research* (2023); Brown & Zeiher (Univ. Arizona AZ1448) |
| Boll development | Critical | 32°C | Brown & Zeiher, Univ. Arizona AZ1448 |

*Note: cotton has the widest cited range (28–32°C) of the four crops because fruit retention decline is gradual rather than a sharp step function. 30°C is used as the flowering-stage default (mid-point of the cited onset range).*

---

## 5. Credit-conscious architecture

FortyGuard's hackathon allotment is a **fixed, one-time credit budget** — not unlimited. CropHeat's data-fetching strategy is designed around that constraint:

1. **One heatmap call per region, not per field.** A single `exceedance`/`persistence`/`tcm` call covers an entire growing region; every field in that region reads from the same cached tile set via a nearest-tile lookup — zero additional API cost per field.
2. **`env_params` (humidity/wet-bulb) is sampled only for the top-ranked fields** by preliminary heatmap-derived risk, not every field — explicitly labeled in the UI ("sampled for highest-risk fields to conserve API credits") rather than silently omitted.
3. **SQLite caching**, keyed by (region, date, analytic_type, threshold) — an identical request is never re-fetched from FortyGuard.
4. **A live credit-budget guard** checks remaining balance before every batch of calls and automatically falls back to clearly-labeled DEMO MODE if the budget runs low, rather than silently failing.

---

## 6. AI advisory — explanation, not calculation

The advisory layer receives the **already-computed** risk score, level, and top contributing factors as structured input. It is explicitly prompted to explain that result in plain language and suggest actions — never to recalculate or override the number. If no LLM API key is configured, or the call fails, a deterministic rule-based advisory (keyed off risk level) is shown instead, clearly labeled as rule-based rather than presented as AI-generated when it isn't.

---

## 7. Honesty commitments

- Every data point in the UI is labeled `LIVE`, `CACHED`, `DEMO DATA`, or `SIMULATED` — never presented as something it isn't.
- The what-if simulator relabels its output `SIMULATED SCENARIO` and never mixes simulated values into a live result.
- Where a crop's growth stage has no sourced threshold (e.g. wheat/rice "vegetative"), the temperature component says so explicitly rather than inventing a number — see `risk_engine/temperature.py`.
- The risk-level bands (LOW/MODERATE/HIGH/CRITICAL) are documented as engineering defaults, not scientific consensus.