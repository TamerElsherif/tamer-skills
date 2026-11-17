// Stage: 1920×1080 "stage units" SVG world, fitted to ANY canvas (16:9, 9:16, 1:1) by covering
// the canvas and re-flowing people toward the centre (x compression + scale) instead of cropping them.
// Camera keys zoom around a stage-unit focus. RTL mirrors x positions and facing.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { useLayout, useScene } from './ctx';
import { lerp, prog } from './theme';

export const SW = 1920, SH = 1080;
export type CamKey = { at: number; zoom?: number; x?: number; y?: number; len?: number };
export type StageXf = {
  S: number; tx: number; ty: number; // canvas = stage * S + t
  kx: number; ks: number; // people x-compression and scale factor for this aspect
  mapX: (x: number) => number; // storyboard x (stage units, LTR) → placed x
  mapS: (s: number) => number;
  toCanvas: (x: number, y: number) => [number, number];
  view: { x0: number; x1: number }; // visible stage-unit x range at zoom 1
};

/** Fit for a W×H box (canvas or comic panel). */
export const stageFit = (W: number, H: number, rtl: boolean, cam = { z: 1, x: SW / 2, y: SH / 2 }, span?: [number, number]): StageXf => {
  const b = Math.max(W / SW, H / SH);
  const vw = W / b;
  const ks = vw >= 1600 ? 1 : vw >= 1000 ? 0.85 : Math.max(0.55, 0.62 * (vw / 607));
  // fit the people's actual x-span (if given) into the visible width, centred
  const [x0, x1] = span ?? [180, SW - 180];
  const margin = 210 * ks;
  const kx = Math.min(1, (vw - 2 * margin) / Math.max(1, x1 - x0));
  const mid = (x0 + x1) / 2;
  const mapX = (x: number) => { const xx = rtl ? SW - x : x; const m = rtl ? SW - mid : mid; return SW / 2 + (xx - m) * kx; };
  const S = b * cam.z;
  const fx = SW / 2 + (cam.x - SW / 2) * kx * (rtl ? -1 : 1);
  let tx = W / 2 - fx * S, ty = H / 2 - cam.y * S;
  tx = Math.min(0, Math.max(W - SW * S, tx));
  ty = Math.min(0, Math.max(H - SH * S, ty));
  return {
    S, tx, ty, kx, ks, mapX, mapS: (s: number) => s * ks,
    toCanvas: (x: number, y: number) => [x * S + tx, y * S + ty],
    view: { x0: SW / 2 - vw / 2, x1: SW / 2 + vw / 2 },
  };
};

export const useCam = (keys: CamKey[] = []) => {
  const { t } = useScene();
  let z = 1, x = SW / 2, y = SH / 2;
  if (keys.length) {
    z = keys[0].zoom ?? 1; x = keys[0].x ?? x; y = keys[0].y ?? y;
    for (let i = 1; i < keys.length; i++) {
      const k = keys[i];
      const p = prog(t, k.at, k.len ?? 0.9);
      z = lerp(z, k.zoom ?? z, p); x = lerp(x, k.x ?? x, p); y = lerp(y, k.y ?? y, p);
    }
  }
  return { z, x, y };
};

/** Full-canvas stage. Children are SVG in stage units (wrap in <Layer>) or <At> HTML boxes in stage units. */
export const Stage: React.FC<{ xf: StageXf; children: React.ReactNode; bg?: string; overlay?: React.ReactNode }> = ({ xf, children, bg, overlay }) => (
  <AbsoluteFill style={{ overflow: 'hidden', background: bg, direction: 'ltr' }}>
    <div style={{ position: 'absolute', left: 0, top: 0, width: SW, height: SH, transformOrigin: '0 0', transform: `translate(${xf.tx}px,${xf.ty}px) scale(${xf.S})` }}>
      {children}
    </div>
    {overlay}
  </AbsoluteFill>
);

export const Layer: React.FC<{ children: React.ReactNode; style?: React.CSSProperties }> = ({ children, style }) => (
  <svg viewBox={`0 0 ${SW} ${SH}`} width={SW} height={SH} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible', ...style }}>
    {children}
  </svg>
);

export const At: React.FC<{ x: number; y: number; w?: number; h?: number; children: React.ReactNode; style?: React.CSSProperties }> = ({ x, y, w, h, children, style }) => (
  <div style={{ position: 'absolute', left: x, top: y, width: w, height: h, ...style }}>{children}</div>
);

/** Hook: stage fit for the whole canvas with a camera. */
export const useStage = (cam: CamKey[] = [], drift = true): StageXf => {
  const { W, H, rtl } = useLayout();
  const { t } = useScene();
  const c = useCam(cam);
  return stageFit(W, H, rtl, { ...c, z: c.z * (drift ? 1 + t * 0.003 : 1) });
};
