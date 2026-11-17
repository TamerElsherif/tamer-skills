// process_flow: layered left→right (portrait: top→bottom) flowchart; nodes reveal on cues in node order,
// edges draw on as their target appears. Decision nodes are diamonds, start/end are pills.
import React from 'react';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, lin, alpha } from '../core/theme';
import { Bg, Header, fit } from '../core/ui';

type Node = { id: string; label: string; kind?: 'start' | 'step' | 'decision' | 'end' };
type Edge = { from: string; to: string; label?: string };

const layers = (nodes: Node[], edges: Edge[]) => {
  const idx = new Map(nodes.map((n, i) => [n.id, i]));
  const lay = nodes.map(() => 0);
  if (!edges.length) return nodes.map((_, i) => i);
  for (let it = 0; it < nodes.length; it++) {
    let changed = false;
    for (const e of edges) {
      const a = idx.get(e.from), b = idx.get(e.to);
      if (a === undefined || b === undefined || b <= a) continue; // back-edges (loops) don't add layers
      if (lay[b] < lay[a] + 1) { lay[b] = lay[a] + 1; changed = true; }
    }
    if (!changed) break;
  }
  return lay;
};

export const ProcessFlow: React.FC<{ title: string; nodes: Node[]; edges?: Edge[] }> = ({ title, nodes, edges = [] }) => {
  const { t, cue } = useScene();
  const { C, F, shadow } = useTheme();
  const L = useLayout();
  const lay = layers(nodes, edges);
  const nL = Math.max(...lay) + 1;
  const byLayer: number[][] = Array.from({ length: nL }, () => []);
  lay.forEach((l, i) => byLayer[l].push(i));
  const maxK = Math.max(...byLayer.map((x) => x.length));
  const horiz = L.landscape;
  // content box
  const top = L.portrait ? 420 : 330, bottom = L.H - (L.portrait ? 160 : 90);
  const left = L.pad, right = L.W - L.pad;
  const mainLen = horiz ? right - left : bottom - top;
  const crossLen = horiz ? bottom - top : right - left;
  const gapMain = horiz ? 90 : 70;
  const bw = horiz ? Math.min(360, (mainLen - (nL - 1) * gapMain) / nL) : Math.min(crossLen / maxK - 30, 760);
  const bh = horiz ? Math.min(190, crossLen / maxK - 40) : Math.min(150, (mainLen - (nL - 1) * gapMain) / nL);
  const pos = nodes.map((_, i) => {
    const l = lay[i], k = byLayer[l].indexOf(i), K = byLayer[l].length;
    const m = nL === 1 ? mainLen / 2 : (mainLen - (horiz ? bw : bh)) * (l / (nL - 1)) + (horiz ? bw : bh) / 2;
    const c = crossLen * ((k + 0.5) / K);
    let x = horiz ? left + m : left + c;
    const y = horiz ? top + c : top + m;
    if (L.rtl) x = L.W - x;
    return { x, y };
  });
  const at = (i: number) => cue(i);
  const anchor = (i: number, j: number) => {
    // point on box i's border towards box j
    const a = pos[i], b = pos[j];
    const dx = b.x - a.x, dy = b.y - a.y;
    const sx = (bw / 2 + 8) / Math.max(1e-3, Math.abs(dx)), sy = (bh / 2 + 8) / Math.max(1e-3, Math.abs(dy));
    const s = Math.min(sx, sy);
    return { x: a.x + dx * s, y: a.y + dy * s };
  };
  const idx = new Map(nodes.map((n, i) => [n.id, i]));
  return (
    <Bg>
      <Header title={title} />
      <svg width={L.W} height={L.H} style={{ position: 'absolute', left: 0, top: 0, overflow: 'visible' }}>
        <defs>
          <marker id="pf-ah" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10z" fill={C.muted} /></marker>
        </defs>
        {edges.map((e, k) => {
          const a = idx.get(e.from), b = idx.get(e.to);
          if (a === undefined || b === undefined) return null;
          const p0 = anchor(a, b), p1 = anchor(b, a);
          const len = Math.hypot(p1.x - p0.x, p1.y - p0.y);
          const p = lin(t, Math.max(at(a), at(b) - 0.35), 0.45);
          return (
            <g key={k} opacity={p > 0 ? 1 : 0}>
              <path d={`M${p0.x},${p0.y} L${p1.x},${p1.y}`} stroke={C.muted} strokeWidth={5} fill="none" strokeDasharray={len} strokeDashoffset={len * (1 - p)} markerEnd={p > 0.95 ? 'url(#pf-ah)' : undefined} strokeLinecap="round" />
            </g>
          );
        })}
      </svg>
      {edges.map((e, k) => {
        const a = idx.get(e.from), b = idx.get(e.to);
        if (!e.label || a === undefined || b === undefined) return null;
        const mx = (pos[a].x + pos[b].x) / 2, my = (pos[a].y + pos[b].y) / 2;
        return <div key={`l${k}`} style={{ position: 'absolute', left: mx - 110, top: my - 24, width: 220, textAlign: 'center', opacity: prog(t, at(b), 0.4), fontFamily: F.sans }}>
          <span style={{ display: 'inline-block', background: C.bg, color: C.accent, fontWeight: 700, fontSize: 24, padding: '4px 12px', borderRadius: 8, border: `2px solid ${alpha(C.accent, 0.3)}` }}>{e.label}</span>
        </div>;
      })}
      {nodes.map((n, i) => {
        const p = prog(t, at(i), 0.45);
        const kind = n.kind ?? (i === 0 && edges.length ? 'start' : 'step');
        const dec = kind === 'decision';
        const col = kind === 'start' ? C.accent : kind === 'end' ? C.safe : dec ? C.attention : C.primary;
        const w = dec ? bw * 1.0 : bw, h = dec ? bh * 1.15 : bh;
        return (
          <div key={n.id} style={{ position: 'absolute', left: pos[i].x - w / 2, top: pos[i].y - h / 2, width: w, height: h, opacity: p, transform: `scale(${0.85 + 0.15 * p})`, display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center' }}>
            {dec ? (
              <svg width={w} height={h} style={{ position: 'absolute', inset: 0, overflow: 'visible' }}>
                <polygon points={`${w / 2},2 ${w - 2},${h / 2} ${w / 2},${h - 2} 2,${h / 2}`} fill="#fff" stroke={col} strokeWidth={5} style={{ filter: `drop-shadow(0 10px 20px ${alpha(C.outline, 0.12)})` }} />
              </svg>
            ) : (
              <div style={{ position: 'absolute', inset: 0, background: kind === 'step' ? '#fff' : col, borderRadius: kind === 'step' ? 20 : h / 2, border: `4px solid ${col}`, boxShadow: shadow }} />
            )}
            <div style={{ position: 'relative', padding: dec ? `0 ${w * 0.18}px` : '0 22px', fontSize: fit(n.label, 30, dec ? w * 0.6 : w - 44, dec ? 2 : 3, 24), fontWeight: 700, lineHeight: 1.2, color: kind === 'step' || dec ? C.ink : '#fff' }}>{n.label}</div>
          </div>
        );
      })}
    </Bg>
  );
};
