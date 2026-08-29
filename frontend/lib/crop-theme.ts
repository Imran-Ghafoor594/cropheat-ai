// Crop-inspired accent theming. Risk severity colors (LOW->CRITICAL) NEVER
// change -- they stay semantically fixed so risk always reads the same way.
// This theme only affects ambient/decorative accents (backgrounds, buttons,
// hero art) so each crop's dashboard feels visually distinct, inspired by
// the crop's real-world appearance rather than a generic single brand color.

import type { SupportedCrop } from "@/types/risk";

export interface CropTheme {
  name: string;
  accent: string;       // primary accent (buttons, active states)
  accentSoft: string;   // low-opacity variant for backgrounds/glows
  gradient: string;      // tailwind gradient classes for hero/CTA elements
  glow: string;          // box-shadow color for ambient glow effects
  emoji: string;
}

export const CROP_THEMES: Record<SupportedCrop, CropTheme> = {
  wheat: {
    name: "Wheat",
    accent: "#D4A94C",
    accentSoft: "rgba(212, 169, 76, 0.12)",
    gradient: "from-[#D4A94C] to-[#8C6D2F]",
    glow: "rgba(212, 169, 76, 0.25)",
    emoji: "\u{1F33E}",
  },
  maize: {
    name: "Maize",
    accent: "#F0B429",
    accentSoft: "rgba(240, 180, 41, 0.12)",
    gradient: "from-[#F0B429] to-[#C2410C]",
    glow: "rgba(240, 180, 41, 0.25)",
    emoji: "\u{1F33D}",
  },
  rice: {
    name: "Rice",
    accent: "#7CB662",
    accentSoft: "rgba(124, 182, 98, 0.12)",
    gradient: "from-[#9AD180] to-[#4D7A3A]",
    glow: "rgba(124, 182, 98, 0.25)",
    emoji: "\u{1F33E}",
  },
  cotton: {
    name: "Cotton",
    accent: "#B9C2CC",
    accentSoft: "rgba(185, 194, 204, 0.12)",
    gradient: "from-[#E8E4DC] to-[#7A8896]",
    glow: "rgba(185, 194, 204, 0.20)",
    emoji: "\u{2601}\u{FE0F}",
  },
};
