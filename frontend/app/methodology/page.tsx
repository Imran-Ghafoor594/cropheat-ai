import Link from "next/link";

const STEPS = [
  {
    n: "01", title: "FortyGuard Environmental Intelligence",
    body: "Real hyperlocal heatmap data: snapshot temperature (tcm), exceedance hours, and persistence hours, plus point-level environmental parameters (apparent temperature, wet-bulb, humidity).",
  },
  {
    n: "02", title: "Heat Exposure",
    body: "How many hours a field's tiles spent above the crop's growth-stage reference threshold, from FortyGuard's exceedance analytic.",
  },
  {
    n: "03", title: "Persistence",
    body: "The longest CONTINUOUS run of hours above threshold, from FortyGuard's persistence analytic — continuous exposure without a recovery window is weighted more heavily than the same total hours spread across multiple short episodes.",
  },
  {
    n: "04", title: "Crop Sensitivity",
    body: "A static, sourced rating (low/moderate/high/critical) per crop, drawn from peer-reviewed agronomy research — see citations below.",
  },
  {
    n: "05", title: "Growth Stage",
    body: "The crop's current phenological stage (e.g. flowering, silking). Every cited study identifies growth-stage TIMING as the dominant factor in whether a given temperature actually causes damage, so this carries the highest weight in the engine.",
  },
  {
    n: "06", title: "Risk Aggregation",
    body: "A transparent, weighted sum of the six components above (weights documented in config/risk_config.yaml as engineering defaults, not fitted ML coefficients — no labeled crop-damage dataset exists to fit against).",
  },
  {
    n: "07", title: "AI Advisory",
    body: "An LLM is given the ALREADY-COMPUTED risk score and component breakdown as structured input, and asked only to explain it in plain language and suggest actions. It never recalculates or overrides the score.",
  },
];

const CITATIONS = [
  { crop: "Wheat", ref: "Girousse et al., Field Crops Research 316 (2024) 109489" },
  { crop: "Maize", ref: "Djalovic et al., The Plant Genome (2024)" },
  { crop: "Rice", ref: "Jagadish et al., J. Exp. Bot. 58(7):1627 (2007)" },
  { crop: "Cotton", ref: "Oosterhuis & Snider, J. Cotton Research (2023)" },
];

export default function MethodologyPage() {
  return (
    <main className="min-h-screen px-6 py-10 md:px-12 lg:px-20 max-w-4xl mx-auto">
      <header className="mb-12 flex items-center justify-between">
        <div>
          <span className="text-xs uppercase tracking-[0.25em] text-sage font-mono">
            Data &amp; Methodology
          </span>
          <h1 className="font-display text-3xl font-semibold text-ink mt-1">
            How CropHeat AI calculates risk
          </h1>
        </div>
        <Link href="/dashboard" className="text-sm text-sage hover:underline whitespace-nowrap">
          ← Dashboard
        </Link>
      </header>

      <div className="space-y-8 mb-16">
        {STEPS.map((step) => (
          <div key={step.n} className="flex gap-6">
            <span className="font-mono text-sage text-sm pt-1 w-8 shrink-0">{step.n}</span>
            <div>
              <h3 className="font-display text-lg font-medium text-ink mb-1.5">{step.title}</h3>
              <p className="text-sm text-ink-muted leading-relaxed">{step.body}</p>
            </div>
          </div>
        ))}
      </div>

      <section className="glass-panel rounded-2xl p-8 mb-10">
        <h2 className="font-display text-lg font-medium text-ink mb-5">Honesty notes</h2>
        <ul className="space-y-3 text-sm text-ink-muted leading-relaxed list-disc list-inside">
          <li>
            This is an <strong className="text-ink">explainable hybrid risk engine</strong>, not a
            trained ML model. No labeled crop-heat-damage dataset exists that's accessible for
            this hackathon — see Section 4 of the original spec.
          </li>
          <li>
            The 0–24 / 25–49 / 50–74 / 75–100 risk bands are CropHeat engineering defaults for
            communicating relative severity, not a published agronomic standard.
          </li>
          <li>
            env_params is only fetched for the top-ranked fields by preliminary heatmap-derived
            risk, to conserve the hackathon's fixed FortyGuard credit budget — not because the
            data isn't wanted for every field.
          </li>
        </ul>
      </section>

      <section>
        <h2 className="font-display text-lg font-medium text-ink mb-4">
          Crop heat-stress citations
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {CITATIONS.map((c) => (
            <div key={c.crop} className="glass-panel rounded-xl p-4">
              <p className="text-xs text-sage font-mono mb-1">{c.crop}</p>
              <p className="text-xs text-ink-muted">{c.ref}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
