// South Indian chart layout: signs are FIXED to grid cells (never move).
// Mirrors app/astro/constants.py SI_GRID exactly -- 4x4 grid, center 2x2
// left blank (traditionally used for the chart title).
export const SIGN_GRID_POSITION: Record<number, [number, number]> = {
  1: [0, 1], 2: [0, 2], 3: [0, 3],
  4: [1, 3], 5: [2, 3], 6: [3, 3],
  7: [3, 2], 8: [3, 1], 9: [3, 0],
  10: [2, 0], 11: [1, 0], 12: [0, 0],
};

export const SIGN_NAMES = [
  "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
  "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
];

export const SIGN_LORDS = [
  "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
  "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
];

export const PLACEABLE_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"];

export const PLANET_COLOR: Record<string, string> = {
  Sun: "#c2410c",
  Moon: "#475569",
  Mars: "#dc2626",
  Mercury: "#15803d",
  Jupiter: "#a16207",
  Venus: "#be185d",
  Saturn: "#64748b",
  Rahu: "#6d28d9",
  Ketu: "#78350f",
  Lagna: "#4f46e5",
};

// Rasi drishti (sign/house aspect) offsets, mirrors app/derived/factors.py
// planet_aspects() exactly -- every planet aspects the 7th house from
// itself (universal); Mars/Jupiter/Saturn get extra SPECIAL aspects.
// Kept as a static frontend constant (not a network round-trip) so aspect
// lines render live while dragging, before the user even clicks Analyze.
// If planet_aspects() in the backend ever changes, update here too.
export const UNIVERSAL_ASPECT_OFFSET = 7;
export const SPECIAL_ASPECT_OFFSETS: Record<string, number[]> = {
  Mars: [4, 8],
  Jupiter: [5, 9],
  Saturn: [3, 10],
};

export function houseForSign(lagnaSign: number, sign: number): number {
  return (((sign - lagnaSign) % 12) + 12) % 12 + 1;
}

export function signForHouseOffset(fromSign: number, offset: number): number {
  return (((fromSign - 1 + offset - 1) % 12) + 12) % 12 + 1;
}

export function ketuSignFor(rahuSign: number): number {
  return (((rahuSign - 1 + 6) % 12) + 12) % 12 + 1;
}

// Percentage-space center of a sign's grid cell, for SVG overlays
// (aspect lines, transit badges) drawn on top of the fixed South Indian
// layout. Shared so every overlay agrees on the same coordinate system.
export function cellCenter(sign: number): { x: number; y: number } {
  const [row, col] = SIGN_GRID_POSITION[sign];
  return { x: ((col + 0.5) / 4) * 100, y: ((row + 0.5) / 4) * 100 };
}

// Aspect-line display modes (Chart Lab v2 spec section 13). Default is
// 'selected' -- only show the currently focused planet's aspects, to
// avoid an all-planets spaghetti diagram.
export type AspectMode = "off" | "selected" | "all";

// Fixed Vimsottari 9-planet cycle, mirrors app/astro/constants.py
// DASHA_ORDER exactly -- used for the manual MD/AD/PD dropdowns when no
// birth date is available to compute a real chain (Chart Lab v2 Sprint 2).
export const DASHA_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"];
