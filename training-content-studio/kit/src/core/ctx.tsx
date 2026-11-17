// Scene API (time, cues, lip-sync amplitude) and Layout API (canvas size, aspect, RTL).
import React, { createContext, useContext } from 'react';
import { SceneRow, Timeline } from './types';

export type SceneApi = {
  t: number; // scene-local seconds
  dur: number;
  frame: number;
  fps: number;
  /** time of the i-th '^' cue. If the narration has fewer cues, falls back to an even spread (never blocks). */
  cue: (i: number) => number;
  hasCue: (i: number) => boolean;
  amp: (who: string) => number; // 0..1 mouth amplitude
  speaking: (who: string) => boolean;
  row: SceneRow;
};

export const SceneCtx = createContext<SceneApi | null>(null);
export const useScene = (): SceneApi => {
  const c = useContext(SceneCtx);
  if (!c) throw new Error('useScene outside a scene');
  return c;
};

export const makeApi = (row: SceneRow, frame: number, fps: number): SceneApi => {
  const t = frame / fps;
  const dur = row.frames / fps;
  const first = row.lines[0]?.at ?? 0.4;
  const lastEnd = row.lines.length ? row.lines[row.lines.length - 1].at + row.lines[row.lines.length - 1].dur : dur * 0.7;
  const fallback = (i: number) => {
    // after the last real cue (or the first line) spread further reveals across the narration
    const n = row.cues.length;
    const base = n ? row.cues[n - 1] : first;
    const span = Math.max(0.6, Math.min(lastEnd, dur - 0.6) - base);
    const k = i - n + 1;
    return Math.min(dur - 0.5, base + (n ? 0 : -span / 6) + (span * k) / 6);
  };
  const ampOf = (who: string) => {
    for (const l of row.lines) {
      if (l.who !== who) continue;
      const k = Math.floor((t - l.at) * fps);
      if (k >= 0 && k < l.amp.length) return Number(l.amp[k]) / 9;
    }
    return 0;
  };
  return {
    t, dur, frame, fps,
    cue: (i: number) => (i >= 0 && i < row.cues.length ? row.cues[i] : fallback(Math.max(0, i))),
    hasCue: (i: number) => i >= 0 && i < row.cues.length,
    amp: ampOf,
    speaking: (who: string) => row.lines.some((l) => l.who === who && t >= l.at && t < l.at + l.dur),
    row,
  };
};

export type LayoutApi = {
  W: number; H: number;
  portrait: boolean; square: boolean; landscape: boolean;
  rtl: boolean; lang: string;
  pad: number; // outer safe padding in px
  /** mirror an x coordinate for RTL (in a space of width w) */
  mx: (x: number, w?: number) => number;
};
export const LayoutCtx = createContext<LayoutApi | null>(null);
export const useLayout = (): LayoutApi => {
  const c = useContext(LayoutCtx);
  if (!c) throw new Error('useLayout outside LayoutCtx');
  return c;
};
export const makeLayout = (tl: Pick<Timeline, 'width' | 'height' | 'direction' | 'language'>): LayoutApi => {
  const W = tl.width, H = tl.height;
  const portrait = H > W * 1.1, square = !portrait && W < H * 1.2;
  const rtl = tl.direction === 'rtl';
  return {
    W, H, portrait, square, landscape: !portrait && !square, rtl, lang: tl.language,
    pad: portrait ? 72 : square ? 80 : 120,
    mx: (x: number, w = W) => (rtl ? w - x : x),
  };
};
export const LayoutProvider: React.FC<{ value: LayoutApi; children: React.ReactNode }> = ({ value, children }) => (
  <LayoutCtx.Provider value={value}>{children}</LayoutCtx.Provider>
);
