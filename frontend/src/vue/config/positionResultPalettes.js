/** Soft card palettes for published result winner cards — keyed by position title. */

const PALETTE_ROTATION = [
  {
    bg: "#EFF6FF",
    border: "#BFDBFE",
    accent: "#1E3A6E",
    badge: "#1E3A6E",
    photoRing: "#93C5FD",
  },
  {
    bg: "#F0FDF4",
    border: "#BBF7D0",
    accent: "#15803D",
    badge: "#15803D",
    photoRing: "#86EFAC",
  },
  {
    bg: "#EEF2FF",
    border: "#C7D2FE",
    accent: "#4F46E5",
    badge: "#4F46E5",
    photoRing: "#A5B4FC",
  },
  {
    bg: "#FFFBEB",
    border: "#FDE68A",
    accent: "#B45309",
    badge: "#B45309",
    photoRing: "#FCD34D",
  },
  {
    bg: "#ECFEFF",
    border: "#A5F3FC",
    accent: "#0F766E",
    badge: "#0F766E",
    photoRing: "#67E8F9",
  },
  {
    bg: "#F5F3FF",
    border: "#DDD6FE",
    accent: "#7C3AED",
    badge: "#7C3AED",
    photoRing: "#C4B5FD",
  },
  {
    bg: "#FFF1F2",
    border: "#FECDD3",
    accent: "#BE123C",
    badge: "#BE123C",
    photoRing: "#FDA4AF",
  },
];

const TITLE_PALETTES = {
  President: PALETTE_ROTATION[0],
  "Vice President": PALETTE_ROTATION[1],
  "General Secretary": PALETTE_ROTATION[2],
  "Financial Secretary": PALETTE_ROTATION[3],
  "Women's Commissioner": PALETTE_ROTATION[4],
  Organiser: PALETTE_ROTATION[5],
  "Organising Secretary": PALETTE_ROTATION[5],
  "Sports Secretary": PALETTE_ROTATION[6],
  "Entertainment Secretary": PALETTE_ROTATION[1],
};

export function getPositionResultPalette(positionTitle = "", displayOrder = 0) {
  if (positionTitle && TITLE_PALETTES[positionTitle]) {
    return TITLE_PALETTES[positionTitle];
  }
  const index = Number.isFinite(displayOrder) ? displayOrder : 0;
  return PALETTE_ROTATION[((index % PALETTE_ROTATION.length) + PALETTE_ROTATION.length) % PALETTE_ROTATION.length];
}
