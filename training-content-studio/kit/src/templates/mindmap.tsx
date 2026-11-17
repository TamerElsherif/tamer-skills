// mindmap: radial tree (root centre, branches on an aspect-fitted ellipse, sub-nodes fanned outward),
// nodes revealed at their cue with draw-on branches; `focus` keys move a camera onto a node.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, pop, lerp, lin, toneColor, alpha } from '../core/theme';
import { Icon } from '../core/Icons';
import { fit } from '../core/ui';

type MNode = { id: string; label: string; parent: string; cue: number; icon?: string; tone?: string };

export const Mindmap: React.FC<{ root: string; nodes: MNode[]; focus?: { cue: number; node: string }[] }> = ({ root, nodes, focus = [] }) => {
  const { t, cue } = useScene();
  const { C, F, shadow, grad } = useTheme();
  const L = useLayout();
  const { W, H } = L;
  const cx = W / 2, cy = H / 2 + (L.portrait ? 40 : 20);
  const ids = new Set(nodes.map((n) => n.id));
  const isRoot = (p: string) => !ids.has(p); // parent "root" (or the root label) → level 1
  const lvl1 = nodes.filter((n) => isRoot(n.parent));
  const kids = (id: string) => nodes.filter((n) => n.parent === id);
  const rx = L.portrait ? W * 0.3 : L.square ? W * 0.3 : W * 0.27;
  const ry = L.portrait ? H * 0.26 : H * 0.3;
  const pos: Record<string, { x: number; y: number; ang: number; lvl: number; col: string }> = {};
  const palette = [C.accent, C.attention, C.safe, C.primary, C.accent2, C.danger];
  lvl1.forEach((n, i) => {
    const ang = -Math.PI / 2 + (i / lvl1.length) * Math.PI * 2 + (lvl1.length % 2 ? 0 : Math.PI / lvl1.length) * 0;
    const a = L.rtl ? Math.PI - ang : ang;
    pos[n.id] = { x: cx + rx * Math.cos(a), y: cy + ry * Math.sin(a), ang: a, lvl: 1, col: n.tone ? toneColor(C, n.tone) : palette[i % palette.length] };
  });
  const place = (id: string, depth: number) => {
    const ks = kids(id);
    const P = pos[id];
    ks.forEach((k, j) => {
      const spread = Math.min(1.1, 0.5 * ks.length) ;
      const a = P.ang + (ks.length > 1 ? (j / (ks.length - 1) - 0.5) * spread : 0);
      const R = L.portrait ? 250 : 260;
      pos[k.id] = { x: P.x + R * Math.cos(a) * (L.portrait ? 0.8 : 1.15), y: P.y + R * Math.sin(a) * (L.portrait ? 1.1 : 0.75), ang: a, lvl: depth, col: k.tone ? toneColor(C, k.tone) : P.col };
      place(k.id, depth + 1);
    });
  };
  lvl1.forEach((n) => place(n.id, 2));
  for (const k of Object.keys(pos)) {  // keep every node inside the frame
    const hw = (pos[k].lvl === 1 ? 190 : 160);
    pos[k].x = Math.min(W - L.pad * 0.5 - hw, Math.max(L.pad * 0.5 + hw, pos[k].x));
    pos[k].y = Math.min(H - (L.portrait ? 160 : 70), Math.max(L.portrait ? 160 : 70, pos[k].y));
  }
  // camera
  let z = 1, fx = cx, fy = cy;
  for (const f of [...focus].sort((a, b) => a.cue - b.cue)) {
    const p = prog(t, cue(f.cue), 1.0);
    const grp = [f.node, ...nodes.filter((n) => n.parent === f.node).map((n) => n.id)].map((id) => pos[id]).filter(Boolean);
    const P = grp.length ? { x: grp.reduce((a, q) => a + q.x, 0) / grp.length, y: grp.reduce((a, q) => a + q.y, 0) / grp.length } : null;
    const tz = P ? 1.3 : 1;
    z = lerp(z, tz, p); fx = lerp(fx, P ? P.x : cx, p); fy = lerp(fy, P ? P.y : cy, p);
  }
  const tx = Math.min(0, Math.max(W - W * z, W / 2 - fx * z)), ty = Math.min(0, Math.max(H - H * z, H / 2 - fy * z));
  const parentPos = (n: MNode) => (isRoot(n.parent) ? { x: cx, y: cy } : pos[n.parent]);
  const nodeW = (lvl: number) => (lvl === 1 ? (L.portrait ? 380 : 360) : L.portrait ? 300 : 300);
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, transformOrigin: '0 0', transform: `translate(${tx}px,${ty}px) scale(${z})` }}>
        <svg width={W} height={H} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
          {nodes.map((n) => {
            const P = pos[n.id], Q = parentPos(n); if (!P || !Q) return null;
            const at = cue(n.cue);
            const p = lin(t, at - 0.15, 0.55);
            const mx = (P.x + Q.x) / 2 + (P.y - Q.y) * 0.12, my = (P.y + Q.y) / 2 - (P.x - Q.x) * 0.12;
            const len = Math.hypot(P.x - Q.x, P.y - Q.y) * 1.15;
            return <path key={n.id} d={`M${Q.x},${Q.y} Q${mx},${my} ${P.x},${P.y}`} stroke={alpha(P.col, P.lvl === 1 ? 0.85 : 0.55)} strokeWidth={P.lvl === 1 ? 12 : 6} fill="none" strokeLinecap="round" strokeDasharray={len} strokeDashoffset={len * (1 - p)} />;
          })}
        </svg>
        <div style={{ position: 'absolute', left: cx - (L.portrait ? 230 : 240), top: cy - 90, width: L.portrait ? 460 : 480, minHeight: 180, borderRadius: 90, background: grad, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: '20px 40px', boxShadow: shadow, transform: `scale(${pop(t, 0.1, 0.6)})`, fontSize: fit(root, 46, 380, 3, 30), fontWeight: 700, lineHeight: 1.15 }}>{root}</div>
        {nodes.map((n) => {
          const P = pos[n.id]; if (!P) return null;
          const at = cue(n.cue);
          const p = pop(t, at, 0.5);
          const w = nodeW(P.lvl);
          const l1 = P.lvl === 1;
          return (
            <div key={n.id} style={{ position: 'absolute', left: P.x - w / 2, top: P.y - (l1 ? 50 : 40), width: w, display: 'flex', justifyContent: 'center', opacity: prog(t, at, 0.3), transform: `scale(${0.6 + 0.4 * p})` }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14, padding: l1 ? '18px 26px' : '12px 20px', borderRadius: 22, background: l1 ? P.col : '#fff', color: l1 ? (P.col === C.attention ? C.outline : '#fff') : C.ink, border: l1 ? 'none' : `3px solid ${alpha(P.col, 0.5)}`, boxShadow: shadow, fontSize: fit(n.label, l1 ? 34 : 28, w - (n.icon ? 110 : 50), 2, 24), fontWeight: l1 ? 700 : 600, lineHeight: 1.2 }}>
                {n.icon && <Icon name={n.icon} size={l1 ? 40 : 32} color={l1 ? (P.col === C.attention ? C.outline : '#fff') : P.col} />}
                <span>{n.label}</span>
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
