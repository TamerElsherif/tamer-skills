// Theme: presets + storyboard overrides, fonts (Latin/Arabic/mono/hand), motion helpers.
import React, { createContext, useContext } from 'react';
import { Easing, interpolate } from 'remotion';
import { loadFont as loadPoppins } from '@remotion/google-fonts/Poppins';
import { loadFont as loadInter } from '@remotion/google-fonts/Inter';
import { loadFont as loadCairo } from '@remotion/google-fonts/Cairo';
import { loadFont as loadPlexArabic } from '@remotion/google-fonts/IBMPlexSansArabic';
import { loadFont as loadKufi } from '@remotion/google-fonts/NotoKufiArabic';
import { loadFont as loadMono } from '@remotion/google-fonts/IBMPlexMono';
import { loadFont as loadCaveat } from '@remotion/google-fonts/Caveat';
import { ThemeSpec } from './types';

export type Palette = {
  bg: string; card: string; primary: string; primaryDeep: string; ink: string; muted: string;
  hair: string; mist: string; accent: string; accent2: string; attention: string; attention2: string; attentionText: string;
  safe: string; danger: string; outline: string; wall: string; wall2: string; floor: string; wood: string;
  // derived
  accentSoft: string; accent2Soft: string; attentionSoft: string; safeSoft: string; dangerSoft: string;
};

// Mirrors assets/theme_presets.yaml (agent E) mapped onto kit roles. `primary` = dark panel colour,
// `ink` = text on light surfaces, `attentionText` = the only orange allowed as TEXT on light grounds (AA).
const PRESETS: Record<string, Partial<Palette>> = {
  neutral: {
    bg: '#F4F7FB', card: '#FFFFFF', primary: '#363E77', primaryDeep: '#232957', ink: '#363E77', muted: '#5A6385',
    hair: '#D5DCE8', mist: '#BFCEDD', accent: '#006AB3', accent2: '#6FC7DA', attention: '#FF6700', attention2: '#FF8A00', attentionText: '#B34700',
    safe: '#1E7F4F', danger: '#C9372C', outline: '#1E2350', wall: '#E8EEF5', wall2: '#DCE4EE', floor: '#C9D3E0', wood: '#B8C4D6',
  },
  whiteboard: {
    bg: '#FFFFFF', card: '#FFFFFF', primary: '#1F2A5A', primaryDeep: '#161E44', ink: '#1F2A5A', muted: '#5A6385', hair: '#D5DCE8',
    accent: '#006AB3', accent2: '#6FC7DA', attention: '#FF6700', attentionText: '#B34700', safe: '#1E7F4F', outline: '#1F2A5A',
  },
  midnight: {
    bg: '#E9EDF6', card: '#FFFFFF', primary: '#0F1530', primaryDeep: '#0A0F24', ink: '#1A2246', muted: '#4F587A', hair: '#D0D7E6', mist: '#B9C2DD',
    accent: '#1F6FB8', accent2: '#6FC7DA', attention: '#FF8A3D', attention2: '#FF8A3D', attentionText: '#A84300', safe: '#1E7F4F', outline: '#0F1530',
  },
  executive: {
    bg: '#FFFFFF', card: '#F2F4F8', primary: '#1E2350', primaryDeep: '#151A3D', ink: '#1E2350', muted: '#4F587A', hair: '#D5DCE8',
    accent: '#006AB3', accent2: '#6FC7DA', attention: '#FF6700', attentionText: '#A84300', safe: '#1E7F4F', outline: '#1E2350',
  },
  high_contrast: {
    bg: '#FFFFFF', card: '#FFFFFF', primary: '#000000', primaryDeep: '#000000', ink: '#000000', muted: '#2B2B2B', hair: '#8A8A8A', mist: '#D0D0D0',
    accent: '#0047AB', accent2: '#5AB4FF', attention: '#C2410C', attention2: '#E8590C', attentionText: '#A33608', safe: '#0B6B3A', danger: '#B3261E', outline: '#000000',
  },
};
// colour keys a storyboard may override (theme.colors): any Palette key, assets/theme_presets.yaml keys, or friendly aliases
const ALIAS: Record<string, keyof Palette> = {
  navy: 'primary', blue: 'accent', cyan: 'accent2', orange: 'attention', background: 'bg', text: 'ink', green: 'safe', red: 'danger',
  surface: 'card', accent_2: 'accent2', attention_text: 'attentionText', line: 'hair', ink_strong: 'outline',
};

const hex = (h: string) => [1, 3, 5].map((i) => parseInt(h.slice(i, i + 2), 16));
export const mix = (a: string, b: string, p: number) => {
  const A = hex(a), B = hex(b);
  return '#' + A.map((v, i) => Math.round(v + (B[i] - v) * p).toString(16).padStart(2, '0')).join('');
};
export const alpha = (h: string, a: number) => { const [r, g, b] = hex(h); return `rgba(${r},${g},${b},${a})`; };

export const makePalette = (spec?: ThemeSpec): Palette => {
  const base = { ...PRESETS.neutral, ...(PRESETS[spec?.preset ?? 'neutral'] ?? {}) } as Palette;
  for (const [k, v] of Object.entries(spec?.colors ?? {})) {
    const key = (ALIAS[k] ?? k) as keyof Palette;
    (base as any)[key] = v;
  }
  base.accentSoft = mix(base.accent, '#FFFFFF', 0.86);
  base.accent2Soft = mix(base.accent2, '#FFFFFF', 0.82);
  base.attentionSoft = mix(base.attention, '#FFFFFF', 0.86);
  base.safeSoft = mix(base.safe, '#FFFFFF', 0.85);
  base.dangerSoft = mix(base.danger, '#FFFFFF', 0.86);
  return base;
};

// ---- fonts ---------------------------------------------------------------
const LOADERS: Record<string, () => { fontFamily: string }> = {
  Poppins: () => loadPoppins('normal', { weights: ['400', '500', '600', '700', '800'], subsets: ['latin'] }),
  Inter: () => loadInter('normal', { weights: ['400', '500', '600', '700', '800'], subsets: ['latin'] }),
  Cairo: () => loadCairo('normal', { weights: ['400', '500', '600', '700', '800'], subsets: ['arabic', 'latin'] }),
  'IBM Plex Sans Arabic': () => loadPlexArabic('normal', { weights: ['400', '500', '600', '700'], subsets: ['arabic', 'latin'] }),
  'Noto Kufi Arabic': () => loadKufi('normal', { weights: ['400', '500', '600', '700', '800'], subsets: ['arabic', 'latin'] }),
  'IBM Plex Mono': () => loadMono('normal', { weights: ['400', '600'], subsets: ['latin'] }),
  Caveat: () => loadCaveat('normal', { weights: ['500', '700'], subsets: ['latin'] }),
};
const loaded: Record<string, string> = {};
const font = (name: string, fallback: string) => {
  const key = LOADERS[name] ? name : fallback;
  if (!loaded[key]) loaded[key] = LOADERS[key]().fontFamily;
  return loaded[key];
};

export type Fonts = { sans: string; mono: string; hand: string; latin: string; arabic: string };
export const makeFonts = (spec: ThemeSpec | undefined, rtl: boolean): Fonts => {
  const latin = font(spec?.fonts?.latin ?? 'Poppins', 'Poppins');
  const arabic = font(spec?.fonts?.arabic ?? 'IBM Plex Sans Arabic', 'Cairo');
  const mono = font(spec?.fonts?.mono ?? 'IBM Plex Mono', 'IBM Plex Mono');
  // handwriting: Caveat has no Arabic glyphs → Arabic falls back to the Arabic face
  const hand = font(spec?.fonts?.hand ?? 'Caveat', 'Caveat');
  const sans = rtl ? `'${arabic}', '${latin}', sans-serif` : `'${latin}', '${arabic}', sans-serif`;
  return { sans, mono: `'${mono}', monospace`, hand: rtl ? `'${arabic}', cursive` : `'${hand}', '${arabic}', cursive`, latin, arabic };
};

export type Theme = { C: Palette; F: Fonts; grad: string; gradV: string; logo?: string | null; evidence?: string; shadow: string; shadowLg: string };
export const ThemeCtx = createContext<Theme | null>(null);
export const useTheme = (): Theme => {
  const t = useContext(ThemeCtx);
  if (!t) throw new Error('useTheme outside ThemeCtx');
  return t;
};
export const makeTheme = (spec: ThemeSpec | undefined, rtl: boolean): Theme => {
  const C = makePalette(spec);
  return {
    C, F: makeFonts(spec, rtl),
    grad: `linear-gradient(90deg, ${C.accent} 0%, ${C.accent2} 100%)`,
    gradV: `linear-gradient(180deg, ${C.primary} 0%, ${C.primaryDeep} 100%)`,
    logo: spec?.logo ?? null,
    evidence: spec?.evidence_line,
    shadow: `0 18px 50px ${alpha(C.outline, 0.14)}, 0 3px 10px ${alpha(C.outline, 0.08)}`,
    shadowLg: `0 24px 60px ${alpha(C.outline, 0.2)}, 0 4px 12px ${alpha(C.outline, 0.1)}`,
  };
};
export const ThemeProvider: React.FC<{ theme: Theme; children: React.ReactNode }> = ({ theme, children }) => (
  <ThemeCtx.Provider value={theme}>{children}</ThemeCtx.Provider>
);

// ---- motion helpers -------------------------------------------------------
const outCubic = Easing.bezier(0.22, 1, 0.36, 1);
const outBack = Easing.bezier(0.34, 1.56, 0.64, 1);
const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
/** 0→1 over `len` s starting at `start` s (eased out). */
export const prog = (t: number, start: number, len = 0.6) => interpolate(t, [start, start + len], [0, 1], { ...clamp, easing: outCubic });
/** 0→1 with a gentle overshoot. */
export const pop = (t: number, start: number, len = 0.5) => interpolate(t, [start, start + len], [0, 1], { ...clamp, easing: outBack });
export const lin = (t: number, start: number, len: number) => interpolate(t, [start, start + len], [0, 1], clamp);
export const lerp = (a: number, b: number, p: number) => a + (b - a) * p;
export const window01 = (t: number, a: number, b: number, f = 0.35) => Math.min(prog(t, a, f), 1 - prog(t, b, f));

export type Tone = 'info' | 'warn' | 'safe' | undefined;
export const toneColor = (C: Palette, tone?: string) =>
  tone === 'warn' || tone === 'bad' ? C.attention : tone === 'safe' ? C.safe : tone === 'danger' ? C.danger : C.accent;
/** colour for TEXT in a tone on light grounds (orange text uses attentionText for AA contrast) */
export const toneText = (C: Palette, tone?: string) => (tone === 'warn' || tone === 'bad' ? C.attentionText : toneColor(C, tone));
/** readable foreground on a filled chip of the given colour (dark ink on orange, white otherwise) */
export const onFill = (C: Palette, fill: string) => (fill === C.attention || fill === C.attention2 ? C.outline : '#FFFFFF');
export const toneSoft = (C: Palette, tone?: string) =>
  tone === 'warn' || tone === 'bad' ? C.attentionSoft : tone === 'safe' ? C.safeSoft : tone === 'danger' ? C.dangerSoft : C.accentSoft;
