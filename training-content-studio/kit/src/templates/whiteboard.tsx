// whiteboard: white ground, ink line-art persons drawn top-down, line icons, handwritten notes, and
// marker annotations (arrow, circle, underline, box, cross, check) drawn on at their cue.
// Coordinates: x,y,w,h ≤ 1 are fractions of the canvas; larger values are 1920×1080 units (scaled).
// Omitted coordinates are auto-laid-out in reading order; annotations without coordinates target the
// previous content item (arrow: previous → next content item).
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, lin } from '../core/theme';
import { Person, Pose, Expr } from '../core/Person';
import { resolveIcon } from '../core/Icons';
import { fit } from '../core/ui';

type WbItem = { cue: number; kind: 'person' | 'icon' | 'note' | 'arrow' | 'circle' | 'underline' | 'box' | 'cross' | 'check'; cast?: string; pose?: Pose; expr?: Expr; icon?: string; text?: string; x?: number; y?: number; w?: number; h?: number; to?: { x?: number; y?: number }; color?: 'ink' | 'attention' | 'safe' };
type R = { x: number; y: number; w: number; h: number };

const CONTENT = new Set(['person', 'icon', 'note']);
// deterministic jitter so strokes look hand-drawn
const jit = (seed: number, k: number) => Math.sin(seed * 12.9898 + k * 78.233) * 43758.5453 % 1;

export const Whiteboard: React.FC<{ title?: string; items: WbItem[] }> = ({ title, items }) => {
  const { t, cue } = useScene();
  const { C, F } = useTheme();
  const L = useLayout();
  const { W, H } = L;
  const sx = (v: number) => (v <= 1 ? v * W : (v / 1920) * W);
  const sy = (v: number) => (v <= 1 ? v * H : (v / 1080) * H);
  const top = title ? (L.portrait ? 330 : 190) : (L.portrait ? 140 : 80);
  const content = items.filter((i) => CONTENT.has(i.kind));
  const nC = content.length;
  const cols = L.portrait ? (nC <= 2 ? 1 : 2) : Math.min(nC, nC === 4 ? 2 : 3) || 1;
  const rows = Math.ceil(nC / cols) || 1;
  const cellW = (W - L.pad * 2) / cols, cellH = (H - top - (L.portrait ? 200 : 70)) / rows;
  const rects: R[] = [];
  let ci = 0;
  const ink = (c?: string) => (c === 'attention' ? C.attention : c === 'safe' ? C.safe : C.primary);
  items.forEach((it) => {
    if (CONTENT.has(it.kind)) {
      const k = ci++;
      const col = k % cols, row = Math.floor(k / cols);
      const cxl = L.pad + cellW * (col + 0.5), cyl = top + cellH * (row + 0.5);
      const cx = L.rtl && it.x === undefined ? W - cxl : cxl;
      const defW = it.kind === 'person' ? Math.min(cellW, cellH * 0.6) : it.kind === 'icon' ? Math.min(cellW, cellH) * 0.55 : cellW * 0.9;
      const defH = it.kind === 'person' ? cellH * 0.92 : it.kind === 'icon' ? Math.min(cellW, cellH) * 0.55 : cellH * 0.5;
      const w = it.w !== undefined ? sx(it.w) : defW, h = it.h !== undefined ? sy(it.h) : defH;
      const x = it.x !== undefined ? (L.rtl ? W - sx(it.x) - w : sx(it.x)) : cx - w / 2;
      const y = it.y !== undefined ? sy(it.y) : cyl - h / 2;
      rects.push({ x, y, w, h });
    } else {
      rects.push({ x: 0, y: 0, w: 0, h: 0 });
    }
  });
  const prevContent = (i: number) => { for (let k = i - 1; k >= 0; k--) if (CONTENT.has(items[k].kind)) return rects[k]; return null; };
  const nextContent = (i: number) => { for (let k = i + 1; k < items.length; k++) if (CONTENT.has(items[k].kind)) return rects[k]; return null; };
  const handPath = (pts: [number, number][], seed: number) => pts.map((p, k) => `${k ? 'L' : 'M'}${p[0] + jit(seed, k) * 4},${p[1] + jit(seed + 1, k) * 4}`).join(' ');
  const strokes: React.ReactNode[] = [];
  const html: React.ReactNode[] = [];
  items.forEach((it, i) => {
    const at = cue(it.cue);
    const col = ink(it.color);
    const r = rects[i];
    if (it.kind === 'person') {
      const s = r.h / 560;
      strokes.push(<Person key={i} cast={it.cast ?? 'host'} x={r.x + r.w / 2} y={r.y + r.h} s={s} pose={it.pose} expr={it.expr} ink reveal={t < at ? 0 : prog(t, at, 1.3)} flip={L.rtl ? r.x + r.w / 2 < W / 2 : r.x + r.w / 2 > W / 2} />);
      return;
    }
    if (it.kind === 'icon') {
      const Cmp = resolveIcon(it.icon);
      const p = prog(t, at, 0.9);
      html.push(<div key={i} style={{ position: 'absolute', left: r.x, top: r.y, width: r.w, height: r.h, clipPath: `inset(0 ${L.rtl ? 0 : (1 - p) * 100}% 0 ${L.rtl ? (1 - p) * 100 : 0}%)`, opacity: t < at ? 0 : 1 }}><Cmp size={Math.min(r.w, r.h)} color={col} strokeWidth={1.6} /></div>);
      return;
    }
    if (it.kind === 'note') {
      const text = it.text ?? '';
      const chars = Array.from(text);
      const n = t < at ? 0 : Math.floor((t - at) * 26);
      const fs = fit(text, L.portrait ? 64 : 58, r.w, 3, 34);
      html.push(<div key={i} style={{ position: 'absolute', left: r.x, top: r.y, width: r.w, minHeight: r.h, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontFamily: F.hand, fontSize: fs, lineHeight: 1.15, fontWeight: 700, color: it.color === 'attention' ? C.attentionText : col, transform: `rotate(${(jit(i, 3) - 0.5) * 3}deg)` }}>
        <span style={{ position: 'relative' }}><span style={{ visibility: 'hidden' }}>{text}</span><span style={{ position: 'absolute', inset: 0 }}>{chars.slice(0, n).join('')}</span></span>
      </div>);
      return;
    }
    // annotations
    const tgt: R = it.x !== undefined ? { x: L.rtl ? W - sx(it.x) - sx(it.w ?? 0.15) : sx(it.x), y: sy(it.y ?? 0.5), w: sx(it.w ?? 0.15), h: sy(it.h ?? it.w ?? 0.1) } : (prevContent(i) ?? { x: W / 2 - 100, y: H / 2 - 50, w: 200, h: 100 });
    const p = lin(t, at, it.kind === 'arrow' ? 0.7 : 0.9);
    if (p <= 0) return;
    let d = '';
    let len = 2400;
    if (it.kind === 'arrow') {
      const a = it.x !== undefined ? { x: tgt.x, y: tgt.y } : (() => { const pr = prevContent(i); return pr ? { x: pr.x + pr.w / 2, y: pr.y + pr.h / 2 } : { x: W * 0.3, y: H * 0.5 }; })();
      const bR = it.to?.x !== undefined ? { x: L.rtl ? W - sx(it.to.x) : sx(it.to.x), y: sy(it.to.y ?? 0.5), w: 0, h: 0 } : nextContent(i);
      const b = bR ? { x: bR.x + bR.w / 2, y: bR.y + bR.h / 2 } : { x: a.x + (L.rtl ? -300 : 300), y: a.y };
      // shorten so it starts/ends outside the boxes
      const pr = it.x !== undefined ? null : prevContent(i);
      const dx = b.x - a.x, dy = b.y - a.y, dist = Math.hypot(dx, dy) || 1;
      const s0 = pr ? Math.min(0.45, (Math.max(pr.w, pr.h) * 0.5 + 20) / dist) : 0;
      const s1 = bR && bR.w ? Math.min(0.45, (Math.max(bR.w, bR.h) * 0.5 + 20) / dist) : 0;
      const A = { x: a.x + dx * s0, y: a.y + dy * s0 }, B = { x: b.x - dx * s1, y: b.y - dy * s1 };
      const mx = (A.x + B.x) / 2 - dy * 0.12, my = (A.y + B.y) / 2 + dx * 0.12;
      d = `M${A.x},${A.y} Q${mx},${my} ${B.x},${B.y}`;
      len = dist * 1.2;
      const ang = Math.atan2(B.y - my, B.x - mx);
      const head = `M${B.x - 34 * Math.cos(ang - 0.45)},${B.y - 34 * Math.sin(ang - 0.45)} L${B.x},${B.y} L${B.x - 34 * Math.cos(ang + 0.45)},${B.y - 34 * Math.sin(ang + 0.45)}`;
      strokes.push(<g key={i}><path d={d} stroke={col} strokeWidth={8} fill="none" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />{p > 0.9 && <path d={head} stroke={col} strokeWidth={8} fill="none" strokeLinecap="round" strokeLinejoin="round" />}</g>);
      return;
    }
    const pad = 22;
    if (it.kind === 'circle') {
      const cx = tgt.x + tgt.w / 2, cy = tgt.y + tgt.h / 2, rx = tgt.w / 2 + pad + 10, ry = tgt.h / 2 + pad;
      const pts: [number, number][] = Array.from({ length: 41 }, (_, k) => { const a = -Math.PI / 2 + (k / 40) * Math.PI * 2.1; return [cx + rx * Math.cos(a) * (1 + jit(i, k) * 0.03), cy + ry * Math.sin(a) * (1 + jit(i + 2, k) * 0.03)]; });
      d = handPath(pts, i); len = Math.PI * (rx + ry) * 1.15;
    } else if (it.kind === 'underline') {
      const y = tgt.y + tgt.h + 10;
      d = handPath([[tgt.x, y], [tgt.x + tgt.w * 0.5, y + 6], [tgt.x + tgt.w, y - 2]], i); len = tgt.w * 1.1;
    } else if (it.kind === 'box') {
      const x0 = tgt.x - pad, y0 = tgt.y - pad, x1 = tgt.x + tgt.w + pad, y1 = tgt.y + tgt.h + pad;
      d = handPath([[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0 + 4]], i); len = 2 * (x1 - x0 + y1 - y0) * 1.05;
    } else if (it.kind === 'cross') {
      const x0 = tgt.x, y0 = tgt.y, x1 = tgt.x + tgt.w, y1 = tgt.y + tgt.h;
      d = `${handPath([[x0, y0], [x1, y1]], i)} ${handPath([[x1, y0], [x0, y1]], i + 5)}`; len = Math.hypot(tgt.w, tgt.h) * 2.1;
    } else if (it.kind === 'check') {
      const s = Math.min(tgt.w, tgt.h) * 0.5, cx = tgt.x + tgt.w + 20, cy = tgt.y + 10;
      d = handPath([[cx, cy + s * 0.5], [cx + s * 0.35, cy + s * 0.9], [cx + s, cy]], i); len = s * 2.2;
    }
    strokes.push(<path key={i} d={d} stroke={col} strokeWidth={it.kind === 'cross' ? 12 : 9} fill="none" strokeLinecap="round" strokeLinejoin="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />);
  });
  const titleN = title ? Math.floor(Math.max(0, t - 0.2) * 24) : 0;
  return (
    <AbsoluteFill style={{ background: '#FFFFFF', overflow: 'hidden' }}>
      {title && (
        <div style={{ position: 'absolute', top: L.portrait ? 150 : 50, left: L.pad, right: L.pad, textAlign: 'center', fontFamily: F.hand, fontWeight: 700, fontSize: fit(title, L.portrait ? 80 : 76, W - L.pad * 2, 2, 40), color: C.primary, lineHeight: 1.1 }}>
          <span style={{ position: 'relative' }}><span style={{ visibility: 'hidden' }}>{title}</span><span style={{ position: 'absolute', inset: 0 }}>{Array.from(title).slice(0, titleN).join('')}</span></span>
        </div>
      )}
      <svg width={W} height={H} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>{strokes}</svg>
      {html}
    </AbsoluteFill>
  );
};
