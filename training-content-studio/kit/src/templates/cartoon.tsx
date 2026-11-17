// cartoon: set + people + cue-timed beats (pose / expression / move / camera) + speech bubbles,
// optional UI overlay (any other template) on a screen panel. comic: panel grid of mini stages.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { useScene, useLayout, LayoutProvider, makeLayout } from '../core/ctx';
import { useTheme, prog, pop, lerp, alpha } from '../core/theme';
import { Person, heldFor, Pose, Expr } from '../core/Person';
import { SetBg, Desk, SetKind } from '../core/Sets';
import { Layer, stageFit, useCam, CamKey, StageXf, SW } from '../core/Stage';
import { fit } from '../core/ui';
import { TEMPLATES } from './registry';

export type PersonSpec = { cast: string; x?: number; y?: number; s?: number; pose?: Pose; expr?: Expr; flip?: boolean; lowerHidden?: boolean; holding?: string };
type Beat = { cue: number; cast?: string; pose?: Pose; expr?: Expr; move_to?: { x?: number; y?: number }; camera?: { zoom?: number; x?: number; y?: number }; sfx?: string };
type BubbleSpec = { cue?: number; out_cue?: number; who: string; text: string; think?: boolean; tone?: 'plain' | 'warn' | 'villain' };

const FIG_H = 520; // feet → top of head, figure units

/** Fill default x/y/s so storyboards can omit coordinates. */
export type Placed = PersonSpec & { x: number; y: number; s: number };
export const placePeople = (people: PersonSpec[], desk?: boolean): Placed[] =>
  people.map((p, i) => ({
    ...p,
    x: p.x ?? (SW * (i + 1)) / (people.length + 1),
    y: p.y ?? (desk || p.lowerHidden ? 1060 : 1000),
    s: p.s ?? (people.length > 3 ? 1.15 : 1.35),
  }));

/** Draws one Person through a stage fit (reflow + RTL mirroring + auto facing). */
export const StagePerson: React.FC<{ p: PersonSpec & { x: number; y: number; s: number }; xf: StageXf; walk?: boolean; ink?: boolean; reveal?: number }> = ({ p, xf, walk, ink, reveal }) => {
  const L = useLayout();
  const x = xf.mapX(p.x);
  const autoFlip = p.flip ?? (p.x > SW / 2 + 40);
  const flip = L.rtl ? !autoFlip : autoFlip;
  return <Person cast={p.cast} x={x} y={p.y} s={xf.mapS(p.s)} pose={p.pose} expr={p.expr} flip={flip} lowerHidden={p.lowerHidden} holding={heldFor(p.holding)} walk={walk} ink={ink} reveal={reveal} />;
};

/** Speech / thought bubble in canvas px with a tail pointing at (tipX, tipY). */
export const Bubble: React.FC<{ x: number; y: number; w: number; text: string; tipX?: number; think?: boolean; tone?: string; vis: number; scale: number; fs?: number; maxH?: number }> = ({ x, y, w, text, tipX, think, tone = 'plain', vis, scale, fs = 30 }) => {
  const { C, F } = useTheme();
  const { rtl } = useLayout();
  const bg = tone === 'warn' ? C.attentionSoft : tone === 'villain' ? '#2B2F45' : '#fff';
  const fg = tone === 'villain' ? '#fff' : C.ink;
  const tail = tipX !== undefined ? Math.max(40, Math.min(w - 70, tipX - x - 25)) : undefined;
  return (
    <div style={{ position: 'absolute', left: x, top: y, width: w, opacity: vis, transform: `scale(${scale})`, transformOrigin: `${tail ?? w / 2}px 100%`, fontFamily: F.sans }}>
      <div style={{ background: bg, color: fg, border: `5px solid ${C.outline}`, borderRadius: think ? 60 : 28, padding: '16px 24px', fontWeight: 500, fontSize: fs, lineHeight: 1.3, textAlign: 'center', direction: rtl ? 'rtl' : 'ltr' }}>{text}</div>
      {tail !== undefined && !think && (
        <svg width={60} height={46} style={{ position: 'absolute', bottom: -40, left: tail, overflow: 'visible' }}>
          <path d="M4,0 L22,40 L44,0" fill={bg} stroke={C.outline} strokeWidth={5} strokeLinejoin="round" />
          <path d="M8,0 L40,0" stroke={bg} strokeWidth={8} />
        </svg>
      )}
      {tail !== undefined && think && (
        <>
          <div style={{ position: 'absolute', bottom: -30, left: tail + 10, width: 26, height: 26, borderRadius: 13, background: bg, border: `4px solid ${C.outline}` }} />
          <div style={{ position: 'absolute', bottom: -58, left: tail + 22, width: 16, height: 16, borderRadius: 8, background: bg, border: `4px solid ${C.outline}` }} />
        </>
      )}
    </div>
  );
};

/** Render another template inside a box using its own virtual canvas, scaled to fit. */
export const NestedTemplate: React.FC<{ template: string; props: any; w: number; h: number; vw: number; vh: number }> = ({ template, props, w, h, vw, vh }) => {
  const L = useLayout();
  const Comp = TEMPLATES[template];
  if (!Comp) return null;
  const s = Math.min(w / vw, h / vh);
  return (
    <div style={{ width: vw * s, height: vh * s, overflow: 'hidden', position: 'relative', borderRadius: 18 }}>
      <div style={{ width: vw, height: vh, transform: `scale(${s})`, transformOrigin: '0 0', position: 'absolute' }}>
        <LayoutProvider value={makeLayout({ width: vw, height: vh, direction: L.rtl ? 'rtl' : 'ltr', language: L.lang })}>
          <Comp {...props} />
        </LayoutProvider>
      </div>
    </div>
  );
};

export const Cartoon: React.FC<{ set: SetKind; night?: boolean; people: PersonSpec[]; desk?: boolean; beats?: Beat[]; bubbles?: BubbleSpec[]; overlay?: { template: string; props: any; cue?: number; out_cue?: number } }> = ({ set, night, people, desk, beats = [], bubbles = [], overlay }) => {
  const { t, cue, dur } = useScene();
  const { C, shadowLg } = useTheme();
  const L = useLayout();
  const placed = placePeople(people, desk);
  // overlay panel takes the end side (landscape) or the top (portrait/square); people squeeze aside
  const ovAt = overlay ? (overlay.cue !== undefined ? cue(overlay.cue) : 0.3) : 0;
  const ovOut = overlay?.out_cue !== undefined ? cue(overlay.out_cue) : dur + 1;
  const ovVis = overlay ? Math.min(prog(t, ovAt, 0.5), 1 - prog(t, ovOut, 0.4)) : 0;
  const squeeze = overlay && L.landscape ? lerp(1, 0.48, ovVis) : 1;
  // beats → per-person state at t
  const state = placed.map((p) => ({ ...p, walk: false }));
  const camKeys: CamKey[] = [{ at: 0, zoom: 1, x: SW / 2, y: 540 }];
  for (const b of [...beats].sort((a, c) => a.cue - c.cue)) {
    const at = cue(b.cue);
    if (b.camera) camKeys.push({ at, zoom: b.camera.zoom ?? 1, x: b.camera.x ?? SW / 2, y: b.camera.y ?? 540 });
    if (!b.cast) continue;
    const i = state.findIndex((s) => s.cast === b.cast);
    if (i < 0 || t < at) continue;
    const s = state[i];
    if (b.pose) s.pose = b.pose;
    if (b.expr) s.expr = b.expr;
    if (b.move_to) {
      const k = prog(t, at, 1.1);
      const nx = b.move_to.x ?? s.x, ny = b.move_to.y ?? s.y;
      if (k < 1 && (nx !== s.x || ny !== s.y)) s.walk = true;
      s.x = lerp(s.x, nx, k); s.y = lerp(s.y, ny, k);
    }
  }
  const cam = useCam(camKeys);
  const xs = [...placed.map((p) => p.x), ...beats.filter((b) => b.move_to?.x !== undefined).map((b) => b.move_to!.x!)];
  const span: [number, number] | undefined = L.landscape ? undefined : [Math.min(...xs), Math.max(...xs)];
  const base = stageFit(L.W, L.H, L.rtl, { ...cam, z: cam.z * (1 + t * 0.003) }, span && span[1] - span[0] < 200 ? [span[0] - 100, span[1] + 100] : span);
  const xf: StageXf = squeeze === 1 ? base : { ...base, mapX: (x: number) => { const m = base.mapX(x); const anchor = L.rtl ? SW * 0.94 : SW * 0.06; return anchor + (m - anchor) * squeeze; } };
  const sorted = [...state].sort((a, b) => a.y - b.y);
  // bubbles
  const active = bubbles.map((b, i) => {
    const at = b.cue !== undefined ? cue(b.cue) : 0.4 + i * 1.5;
    const same = bubbles.slice(i + 1).find((x) => x.who === b.who);
    const out = b.out_cue !== undefined ? cue(b.out_cue) : same?.cue !== undefined ? cue(same.cue) - 0.1 : dur + 1;
    return { ...b, at, out };
  }).filter((b) => t >= b.at - 0.05 && t < b.out + 0.3);
  const bw = L.portrait ? Math.min(820, L.W - 120) : L.square ? 640 : 560;
  return (
    <AbsoluteFill style={{ overflow: 'hidden', background: C.wall, direction: 'ltr' }}>
      <div style={{ position: 'absolute', left: 0, top: 0, width: SW, height: 1080, transformOrigin: '0 0', transform: `translate(${xf.tx}px,${xf.ty}px) scale(${xf.S})` }}>
        <Layer>
          <SetBg kind={set} night={night} />
          {sorted.map((p, i) => <StagePerson key={p.cast + i} p={p} xf={xf} walk={p.walk} />)}
          {desk && <Desk x={xf.mapX(SW / 2)} monitor={L.rtl ? 'left' : 'right'} />}
        </Layer>
      </div>
      {overlay && ovVis > 0 && (() => {
        const land = L.landscape;
        const pw = land ? L.W * 0.5 : L.W - 80, ph = land ? L.H - 160 : L.portrait ? 860 : 560;
        const vw = land ? 1080 : 1080, vh = land ? 1080 : L.portrait ? 960 : 640;
        return (
          <div style={{ position: 'absolute', top: land ? 80 : 70, insetInlineEnd: land ? 70 : 40, opacity: ovVis, transform: `translateY(${(1 - ovVis) * 40}px)`, boxShadow: shadowLg, borderRadius: 22, border: `10px solid ${C.outline}`, background: C.outline } as React.CSSProperties}>
            <NestedTemplate template={overlay.template} props={overlay.props} w={pw} h={ph} vw={vw} vh={vh} />
          </div>
        );
      })()}
      {active.map((b, i) => {
        const sp = state.find((s) => s.cast === b.who);
        const vis = Math.min(prog(t, b.at, 0.25), 1 - prog(t, b.out, 0.25));
        const sc = 0.6 + 0.4 * pop(t, b.at, 0.4);
        const fs = fit(b.text, L.portrait ? 36 : 30, bw - 60, 3, 26);
        const lines = Math.ceil(b.text.length / ((bw - 60) / (fs * 0.54)));
        const bh = lines * fs * 1.3 + 42;
        if (!sp) {
          // narrator / off-screen voice → caption box at the top
          return <Bubble key={i} x={(L.W - bw) / 2} y={L.portrait ? 160 : 50} w={bw} text={b.text} think={b.think} tone={b.tone} vis={vis} scale={sc} fs={fs} />;
        }
        const [hx, hy] = xf.toCanvas(xf.mapX(sp.x), sp.y - FIG_H * xf.mapS(sp.s));
        if (!L.landscape) {  // tall/square canvases: stack bubbles in the free space above the heads
          const k = active.slice(0, i).filter((x) => state.some((s) => s.cast === x.who)).length;
          return <Bubble key={i} x={(L.W - bw) / 2} y={(L.portrait ? 170 : 40) + k * (bh + 70)} w={bw} text={b.text} tipX={hx} think={b.think} tone={b.tone} vis={vis} scale={sc} fs={fs} />;
        }
        let bx = Math.max(30, Math.min(L.W - bw - 30, hx - bw / 2));
        if (overlay && ovVis > 0.5 && L.landscape) bx = L.rtl ? Math.max(bx, L.W * 0.5 + 30) : Math.min(bx, L.W * 0.5 - bw - 60);
        const by = Math.max(L.portrait ? 120 : 30, hy - bh - 60);
        return <Bubble key={i} x={bx} y={by} w={bw} text={b.text} tipX={hx} think={b.think} tone={b.tone} vis={vis} scale={sc} fs={fs} />;
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- comic
type Panel = { cue?: number; set: SetKind; people: PersonSpec[]; caption?: string; bubbles?: { who: string; text: string; think?: boolean }[]; sfx_word?: string };

const panelRects = (layout: string, n: number, W: number, H: number, portrait: boolean, top: number, pad: number, gap = 26) => {
  const x0 = pad, y0 = top, w = W - pad * 2, h = H - top - pad;
  const grid = (cols: number, rows: number) => Array.from({ length: cols * rows }, (_, i) => ({ x: x0 + (i % cols) * ((w + gap) / cols), y: y0 + Math.floor(i / cols) * ((h + gap) / rows), w: (w + gap) / cols - gap, h: (h + gap) / rows - gap }));
  const lay = layout || (n === 1 ? '1' : n === 2 ? '2' : n === 3 ? (portrait ? '3-row' : '3') : '2x2');
  switch (lay) {
    case '1': return grid(1, 1);
    case '2': return portrait ? grid(1, 2) : grid(2, 1);
    case '3': return portrait ? grid(1, 3) : grid(3, 1);
    case '3-row': return grid(1, 3);
    case '2x2': return grid(2, 2);
    case '1+2': {
      if (portrait) { const a = { x: x0, y: y0, w, h: h * 0.55 - gap / 2 }; const b = grid(2, 1).map((r) => ({ ...r, y: y0 + h * 0.55 + gap / 2, h: h * 0.45 - gap / 2 })); return [a, ...b]; }
      const a = { x: x0, y: y0, w: w * 0.55 - gap / 2, h };
      return [a, { x: x0 + w * 0.55 + gap / 2, y: y0, w: w * 0.45 - gap / 2, h: h / 2 - gap / 2 }, { x: x0 + w * 0.55 + gap / 2, y: y0 + h / 2 + gap / 2, w: w * 0.45 - gap / 2, h: h / 2 - gap / 2 }];
    }
    default: return grid(2, 2);
  }
};

export const Comic: React.FC<{ layout?: string; panels: Panel[] }> = ({ layout, panels }) => {
  const { t, cue } = useScene();
  const { C, F } = useTheme();
  const L = useLayout();
  const rects = panelRects(layout ?? '', panels.length, L.W, L.H, L.portrait, L.portrait ? 110 : 50, L.portrait ? 50 : 60);
  return (
    <AbsoluteFill style={{ background: C.primaryDeep, fontFamily: F.sans }}>
      {panels.map((pn, i) => {
        const r = rects[i]; if (!r) return null;
        const at = pn.cue !== undefined ? cue(pn.cue) : cue(i);
        const p = pop(t, at, 0.5);
        const placed = placePeople(pn.people);
        const pxs = placed.map((q) => q.x);
        const xf = stageFit(r.w, r.h, L.rtl, { z: 1.0 + 0.04 * prog(t, at, 6), x: SW / 2, y: 560 }, pxs.length > 1 ? [Math.min(...pxs), Math.max(...pxs)] : [pxs[0] - 200, pxs[0] + 200]);
        const bubbleW = Math.min(r.w - 40, L.portrait ? 640 : 520);
        // wide panels: bubbles stack top-centre; tall panels: same, smaller
        return (
          <div key={i} style={{ position: 'absolute', left: L.rtl ? L.W - r.x - r.w : r.x, top: r.y, width: r.w, height: r.h, overflow: 'hidden', borderRadius: 10, border: `7px solid ${C.outline}`, background: '#fff', opacity: prog(t, at, 0.25), transform: `scale(${0.92 + 0.08 * p})`, boxShadow: '0 16px 40px rgba(0,0,0,0.35)' }}>
            <div style={{ position: 'absolute', left: 0, top: 0, width: SW, height: 1080, transformOrigin: '0 0', transform: `translate(${xf.tx}px,${xf.ty}px) scale(${xf.S})`, direction: 'ltr' }}>
              <Layer>
                <SetBg kind={pn.set} />
                {placed.map((pp, k) => <StagePerson key={k} p={pp as any} xf={xf} />)}
              </Layer>
            </div>
            {pn.caption && <div style={{ position: 'absolute', top: 0, insetInlineStart: 0, maxWidth: r.w * 0.8, background: C.accent2Soft, color: C.ink, fontSize: fit(pn.caption, 28, r.w * 0.8 - 40, 2, 24), fontWeight: 600, padding: '10px 18px', borderBottom: `5px solid ${C.outline}`, borderInlineEnd: `5px solid ${C.outline}`, lineHeight: 1.3 } as React.CSSProperties}>{pn.caption}</div>}
            <div style={{ position: 'absolute', left: 20, right: 20, top: pn.caption ? 78 : 22, display: 'flex', flexDirection: 'column', gap: 52, alignItems: 'center' }}>
              {(pn.bubbles ?? []).map((b, k) => {
                const sp = placed.find((x) => x.cast === b.who);
                const bAt = at + 0.4 + k * 0.9;
                const [hx] = sp ? xf.toCanvas(xf.mapX(sp.x), 0) : [undefined];
                const vis = prog(t, bAt, 0.25);
                const fs = fit(b.text, 28, bubbleW - 50, 3, 24);
                const left = (r.w - 40 - bubbleW) / 2;
                const tip = hx !== undefined ? hx - 20 : undefined;
                return <div key={k} style={{ position: 'relative', width: bubbleW, height: fs * 1.3 * Math.ceil(b.text.length / ((bubbleW - 50) / (fs * 0.54))) + 40 }}>
                  <Bubble x={0} y={0} w={bubbleW} text={b.text} tipX={tip !== undefined ? tip - left : undefined} think={b.think} vis={vis} scale={0.7 + 0.3 * pop(t, bAt, 0.4)} fs={fs} />
                </div>;
              })}
            </div>
            {pn.sfx_word && <div style={{ position: 'absolute', insetInlineEnd: 24, bottom: 24, fontSize: Math.min(110, r.w / 5), fontWeight: 800, color: C.attention, WebkitTextStroke: `4px ${C.outline}`, transform: `rotate(-8deg) scale(${pop(t, at + 0.3, 0.4)})`, letterSpacing: 2 } as React.CSSProperties}>{pn.sfx_word}</div>}
          </div>
        );
      })}
    </AbsoluteFill>
  );
};
