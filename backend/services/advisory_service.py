"""AdvisoryService .

The LLM is given the ALREADY-COMPUTED risk_score, risk_level, and
component breakdown as structured input, and asked only to explain it in
plain language and suggest actions. It never independently invents
agricultural facts or overrides the risk engine's number -- the prompt
explicitly forbids changing the score, and the response is treated as
advisory text only, never re-parsed back into risk_score.

Requires ANTHROPIC_API_KEY. If unset (or the call fails), falls back to a
deterministic, rule-based advisory built directly from primary_factors --
so the dashboard's "AI Advisory" panel always has something honest to show,
labeled accordingly, rather than crashing or fabricating LLM-sounding text.

NOTE: This module has not been exercised against a live Anthropic API call
in development (no key was available in the build environment). The prompt
and parsing logic are correct by inspection but should be smoke-tested with
a real key before relying on it for a live demo.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

logger = logging.getLogger("cropheat.advisory_service")

SYSTEM_PROMPT = """You are an agricultural heat-risk advisory assistant for CropHeat AI.

You will be given a JSON object describing an ALREADY-COMPUTED heat-stress risk
assessment for one crop field: its risk_score (0-100), risk_level, and the
top contributing factors with their explanations.

Your job:
1. Explain in 2-3 plain-language sentences WHY the risk is at this level,
   using the given factors -- do not invent new causes not present in the input.
2. Give 2-4 concise, actionable recommendations appropriate for the crop,
   growth stage, and risk level.

Rules:
- NEVER state or imply a different risk_score or risk_level than the one given.
- NEVER claim scientific certainty beyond what a risk score justifies -- use
  language like "elevated risk" and "consider", not "will fail" or guarantees.
- NEVER invent crop-specific facts not grounded in the given factors.
- Output ONLY valid JSON, no markdown fences, matching this exact shape:
  {"summary": "...", "recommendations": ["...", "..."]}
"""


class AdvisoryService:
    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-6"):
        self._api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self._model = model
        self._client = None
        if self._api_key:
            try:
                import anthropic  # local import so the package is optional at runtime

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                logger.warning("anthropic package not installed; advisory will use rule-based fallback.")

    def generate(self, *, crop: str, growth_stage: str, risk_score: float, risk_level: str,
                 primary_factors: list[str], component_explanations: dict[str, str]) -> dict[str, Any]:
        structured_input = {
            "crop": crop,
            "growth_stage": growth_stage,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "primary_factors": primary_factors,
            "factor_explanations": {f: component_explanations.get(f, "") for f in primary_factors},
        }

        if self._client is None:
            return self._rule_based_fallback(structured_input)

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=500,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": json.dumps(structured_input)}],
            )
            text = "".join(block.text for block in response.content if hasattr(block, "text"))
            parsed = json.loads(text.strip())
            parsed["source"] = "AI_GENERATED"
            return parsed
        except Exception as exc:  # noqa: BLE001 -- any failure should degrade gracefully, not crash the dashboard
            logger.error("Advisory LLM call failed, falling back to rule-based advisory: %s", exc)
            return self._rule_based_fallback(structured_input)

    @staticmethod
    def _rule_based_fallback(structured_input: dict[str, Any]) -> dict[str, Any]:
        level = structured_input["risk_level"]
        factors = structured_input["primary_factors"]
        factor_text = ", ".join(f.replace("_", " ") for f in factors) if factors else "no dominant factor"

        summary = (
            f"Risk is classified {level} for {structured_input['crop']} at the "
            f"{structured_input['growth_stage'].replace('_', ' ')} stage, driven primarily by {factor_text}."
        )

        recommendations_by_level = {
            "CRITICAL": [
                "Consider emergency irrigation or evaporative cooling if available for this field.",
                "Delay any non-essential field operations during peak heat hours.",
                "Monitor for visible heat-stress symptoms (wilting, leaf curl) over the next 24-48 hours.",
            ],
            "HIGH": [
                "Increase irrigation frequency if soil moisture allows.",
                "Avoid additional stressors (fertilizer application, mechanical work) during this window.",
                "Re-check risk after the next FortyGuard update for this field.",
            ],
            "MODERATE": [
                "Monitor conditions; no immediate action required for most fields at this level.",
                "Verify irrigation schedule aligns with the current heat exposure trend.",
            ],
            "LOW": [
                "No action needed. Continue standard field management.",
            ],
        }

        return {
            "summary": summary,
            "recommendations": recommendations_by_level.get(level, recommendations_by_level["MODERATE"]),
            "source": "RULE_BASED_FALLBACK",
        }
