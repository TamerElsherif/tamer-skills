// screencast: a synthetic app UI (form / table / list / settings / dashboard / screenshot) driven by
// cue-timed actions: move, click, type, select, highlight, callout, toast, zoom. Element rects are
// computed (not measured) so the cursor always lands on its target in every aspect.
import React from 'react';
import { AbsoluteFill, Img, staticFile } from 'remotion';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, pop, lerp, alpha } from '../core/theme';
import { Icon } from '../core/Icons';
import { fit } from '../core/ui';
import { useTimeline } from '../core/timelineCtx';
import { useT } from '../core/i18n';

type Field = { id: string; label: string; value?: string; kind?: 'text' | 'select' | 'date' | 'amount' | 'file' | 'checkbox' | 'button' };
type Action = { cue: number; do: 'move' | 'click' | 'type' | 'select' | 'highlight' | 'callout' | 'toast' | 'zoom'; target?: string; value?: string; label?: string };
type Rect = { x: number; y: number; w: number; h: number };

const layoutFields = (kind: string, fields: Field[], W: number, H: number, wide: boolean): Record<string, Rect> => {
  const r: Record<string, Rect> = {};
  const pad = 48;
  if (kind === 'dashboard') {
    const cols = wide ? Math.min(3, fields.length) : 2;
    const rows = Math.ceil(fields.length / cols);
    const cw = (W - pad * 2 - (cols - 1) * 26) / cols, ch = Math.min(220, (H - pad * 2 - (rows - 1) * 26) / rows);
    fields.forEach((f, i) => { r[f.id] = { x: pad + (i % cols) * (cw + 26), y: pad + Math.floor(i / cols) * (ch + 26), w: cw, h: ch }; });
    return r;
  }
  if (kind === 'table' || kind === 'list' || kind === 'settings') {
    const top = kind === 'table' ? pad + 64 : pad;
    const rh = Math.min(96, (H - top - pad) / Math.max(1, fields.length));
    fields.forEach((f, i) => { r[f.id] = { x: pad, y: top + i * rh, w: W - pad * 2, h: rh - 10 }; });
    return r;
  }
  // form: label above input; 2 columns when wide and many fields; buttons span full width at the end
  const inputs = fields.filter((f) => f.kind !== 'button'), buttons = fields.filter((f) => f.kind === 'button');
  const cols = wide && inputs.length > 4 ? 2 : 1;
  const rows = Math.ceil(inputs.length / cols);
  const cw = Math.min(wide && cols === 1 ? 820 : 9999, (W - pad * 2 - (cols - 1) * 40) / cols);
  const rh = Math.min(132, (H - pad * 2 - (buttons.length ? 100 : 0)) / Math.max(1, rows));
  inputs.forEach((f, i) => {
    const c = Math.floor(i / rows), k = i % rows;
    r[f.id] = { x: pad + c * (cw + 40), y: pad + k * rh + 38, w: cw, h: Math.min(64, rh - 50) };
  });
  buttons.forEach((f, i) => { r[f.id] = { x: pad + i * 260, y: pad + rows * rh + 20, w: 240, h: 66 }; });
  return r;
};

export const Screencast: React.FC<{ app: { kind: string; title?: string; screenshot?: string; fields?: Field[] }; actions?: Action[]; sim?: { expect?: { target: string; value?: string }[] } }> = ({ app, actions: actions0 = [], sim }) => {
  // props.sim (interactive practice in HTML/SCORM) plays as a narrated demo: expected inputs become type/click actions
  const actions: Action[] = actions0.length ? actions0 : (sim?.expect ?? []).map((e, i) => ({ cue: i, do: (e.value ? 'type' : 'click') as Action['do'], target: e.target, value: e.value }));
  const { t, cue } = useScene();
  const { C, F, shadowLg, shadow } = useTheme();
  const L = useLayout();
  const tl = useTimeline();
  const tr = useT();
  const fields = app.fields ?? [];
  const winW = L.landscape ? 1560 : L.W - L.pad * 1.2;
  const winH = L.portrait ? 1380 : L.square ? 880 : 900;
  const barH = 64, sideW = L.landscape ? 250 : 0;
  const cW = winW - sideW, cH = winH - barH;
  const rects = layoutFields(app.kind, fields, cW, cH, L.landscape);
  const winX = (L.W - winW) / 2, winY = (L.H - winH) / 2 + (L.portrait ? 40 : 10);
  // canvas-space rect of a target ("field id" or "x,y" fractions of the content area)
  const rectOf = (target?: string): Rect | null => {
    if (!target) return null;
    const m = /^\s*([\d.]+)\s*,\s*([\d.]+)\s*$/.exec(target);
    if (m) return { x: winX + sideW + parseFloat(m[1]) * cW - 40, y: winY + barH + parseFloat(m[2]) * cH - 30, w: 80, h: 60 };
    const r = rects[target];
    if (!r) return null;
    const rx = L.rtl ? cW - r.x - r.w : r.x;
    return { x: winX + (L.rtl ? 0 : sideW) + rx, y: winY + barH + r.y, w: r.w, h: r.h };
  };
  const acts = actions.map((a) => ({ ...a, at: cue(a.cue) })).sort((a, b) => a.at - b.at);
  // field state
  const typed: Record<string, string> = {};
  const checked: Record<string, boolean> = {};
  const pressed: Record<string, number> = {};
  for (const a of acts) {
    if (!a.target || t < a.at) continue;
    const f = fields.find((x) => x.id === a.target);
    if (a.do === 'type') {
      const full = Array.from(a.value ?? f?.value ?? '');
      const n = Math.floor(Math.max(0, t - a.at - 0.35) * 18);
      typed[a.target] = full.slice(0, n).join('');
    } else if (a.do === 'select') typed[a.target] = a.value ?? f?.value ?? '';
    else if (a.do === 'click') {
      if (f?.kind === 'checkbox') checked[a.target] = !checked[a.target];
      pressed[a.target] = a.at;
    }
  }
  const typeTargets = new Set(acts.filter((a) => a.do === 'type').map((a) => a.target));
  const valueOf = (f: Field) => (typed[f.id] !== undefined ? typed[f.id] : typeTargets.has(f.id) ? '' : f.value ?? '');
  // cursor path
  const pts = acts.filter((a) => ['move', 'click', 'type', 'select'].includes(a.do) && rectOf(a.target)).map((a) => {
    const r = rectOf(a.target)!;
    return { at: a.at, x: r.x + Math.min(r.w * 0.5, 120), y: r.y + r.h * 0.6 };
  });
  let cx = winX + winW * 0.62, cy = winY + winH * 0.78;
  for (const p of pts) { const k = prog(t, p.at - 0.7, 0.65); cx = lerp(cx, p.x, k); cy = lerp(cy, p.y, k); }
  const clickA = acts.filter((a) => (a.do === 'click' || a.do === 'type' || a.do === 'select') && t >= a.at && t < a.at + 0.6).pop();
  // zoom camera
  let z = 1, zx = L.W / 2, zy = L.H / 2;
  for (const a of acts.filter((x) => x.do === 'zoom')) {
    const r = rectOf(a.target);
    const k = prog(t, a.at, 0.8);
    const tz = r ? Math.min(1.8, parseFloat(a.value ?? '') || 1.6) : 1;
    z = lerp(z, tz, k); zx = lerp(zx, r ? r.x + r.w / 2 : L.W / 2, k); zy = lerp(zy, r ? r.y + r.h / 2 : L.H / 2, k);
  }
  const tx = Math.min(0, Math.max(L.W - L.W * z, L.W / 2 - zx * z)), ty = Math.min(0, Math.max(L.H - L.H * z, L.H / 2 - zy * z));
  const fieldBox = (f: Field) => {
    const r = rects[f.id]; if (!r) return null;
    const v = valueOf(f);
    const rx = L.rtl ? cW - r.x - r.w : r.x;
    const isPressed = pressed[f.id] !== undefined && t - pressed[f.id] < 0.25;
    const base: React.CSSProperties = { position: 'absolute', left: rx, top: r.y, width: r.w, height: r.h };
    if (app.kind === 'dashboard') {
      return <div key={f.id} style={{ ...base, background: '#fff', borderRadius: 18, border: `2px solid ${C.hair}`, padding: '20px 26px', boxShadow: shadow }}>
        <div style={{ fontSize: 24, color: C.muted }}>{f.label}</div>
        <div style={{ fontSize: fit(v, 52, r.w - 50, 1, 28), fontWeight: 700, marginTop: 10, color: C.ink, direction: 'ltr', textAlign: L.rtl ? 'right' : 'left' }}>{v}</div>
        <svg width={r.w - 52} height={40} style={{ marginTop: 8 }}><path d={`M0,30 ${Array.from({ length: 8 }).map((_, i) => `L${((i + 1) * (r.w - 52)) / 8},${30 - ((i * 37 + f.id.length * 11) % 26)}`).join(' ')}`} fill="none" stroke={C.accent2} strokeWidth={4} /></svg>
      </div>;
    }
    if (app.kind === 'table' || app.kind === 'list' || app.kind === 'settings') {
      const isToggle = app.kind === 'settings' && (f.kind === 'checkbox' || !f.kind);
      const on = f.kind === 'checkbox' ? (checked[f.id] ? !/^(true|on|1|yes)$/i.test(f.value ?? '') : /^(true|on|1|yes)$/i.test(f.value ?? '')) : false;
      return <div key={f.id} style={{ ...base, display: 'flex', alignItems: 'center', gap: 20, padding: '0 24px', borderBottom: `1px solid ${C.hair}`, background: '#fff', fontSize: 27 }}>
        {app.kind === 'list' && <Icon name={f.kind === 'file' ? 'file' : f.kind === 'checkbox' ? (on ? 'check' : 'Circle') : 'ChevronRight'} size={30} color={C.accent} />}
        <div style={{ flex: 1, fontWeight: 600, minWidth: 0, color: C.ink }}>{f.label}</div>
        {isToggle ? (
          <div style={{ width: 76, height: 42, borderRadius: 21, background: on ? C.safe : C.mist, position: 'relative' }}><div style={{ position: 'absolute', top: 4, [on !== L.rtl ? 'right' : 'left']: 4, width: 34, height: 34, borderRadius: 17, background: '#fff' } as React.CSSProperties} /></div>
        ) : f.kind === 'button' ? (
          <div style={{ padding: '8px 22px', borderRadius: 10, background: C.accent, color: '#fff', fontWeight: 600, fontSize: 24, transform: `scale(${isPressed ? 0.94 : 1})` }}>{v || f.label}</div>
        ) : <div style={{ color: C.muted, direction: 'ltr', unicodeBidi: 'isolate' }}>{v}</div>}
      </div>;
    }
    // form
    if (f.kind === 'button') {
      return <div key={f.id} style={{ ...base, borderRadius: 12, background: C.accent, color: '#fff', fontWeight: 700, fontSize: 26, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${isPressed ? 0.94 : 1})` }}>{f.value || f.label}</div>;
    }
    if (f.kind === 'checkbox') {
      const on = !!checked[f.id] !== /^(true|on|1|yes)$/i.test(f.value ?? '');
      return <div key={f.id} style={{ ...base, display: 'flex', alignItems: 'center', gap: 16, fontSize: 26 }}>
        <div style={{ width: 40, height: 40, borderRadius: 8, border: `3px solid ${on ? C.accent : C.mist}`, background: on ? C.accent : '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{on && <Icon name="Check" size={28} color="#fff" stroke={3} />}</div>{f.label}
      </div>;
    }
    const caret = typed[f.id] !== undefined && Math.floor(t * 3) % 2 === 0 && typed[f.id].length < Array.from(acts.find((a) => a.target === f.id && a.do === 'type')?.value ?? f.value ?? '').length;
    return <div key={f.id} style={{ ...base }}>
      <div style={{ position: 'absolute', top: -36, fontSize: 24, color: C.muted, insetInlineStart: 0 } as React.CSSProperties}>{f.label}</div>
      <div style={{ width: '100%', height: '100%', border: `2px solid ${typed[f.id] !== undefined ? C.accent : C.hair}`, borderRadius: 10, background: '#fff', display: 'flex', alignItems: 'center', padding: '0 16px', fontSize: 26, gap: 10, color: C.ink }}>
        {f.kind === 'amount' && <span style={{ color: C.muted }}>$</span>}
        {f.kind === 'file' && <Icon name="paperclip" size={26} color={C.muted} />}
        <span style={{ flex: 1, direction: f.kind === 'amount' || f.kind === 'date' ? 'ltr' : undefined, whiteSpace: 'nowrap', overflow: 'hidden' }}>{v}{caret ? '|' : ''}</span>
        {(f.kind === 'select' || f.kind === 'date') && <Icon name={f.kind === 'date' ? 'calendar' : 'ChevronDown'} size={26} color={C.muted} />}
      </div>
    </div>;
  };
  const shot = app.screenshot ? tl.images?.[app.screenshot] ?? (/\.(png|jpe?g|webp)$/i.test(app.screenshot) ? { src: app.screenshot } : undefined) : undefined;
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, transformOrigin: '0 0', transform: `translate(${tx}px,${ty}px) scale(${z})` }}>
        <div style={{ position: 'absolute', left: winX, top: winY, width: winW, height: winH, background: '#fff', borderRadius: 18, boxShadow: shadowLg, overflow: 'hidden', opacity: prog(t, 0, 0.4) }}>
          <div style={{ height: barH, background: C.primary, color: '#fff', display: 'flex', alignItems: 'center', gap: 16, padding: '0 24px', fontSize: 26, fontWeight: 600 }}>
            <Icon name="LayoutGrid" size={28} color={C.accent2} />{app.title}
            <div style={{ marginInlineStart: 'auto', display: 'flex', alignItems: 'center', gap: 10, background: 'rgba(255,255,255,0.12)', borderRadius: 18, padding: '6px 16px', fontSize: 22, fontWeight: 400 }}><Icon name="search" size={20} color="#fff" />{tr('search')}</div>
          </div>
          {sideW > 0 && (
            <div style={{ position: 'absolute', top: barH, bottom: 0, insetInlineStart: 0, width: sideW, background: C.bg, borderInlineEnd: `1px solid ${C.hair}`, padding: 26, display: 'flex', flexDirection: 'column', gap: 20 } as React.CSSProperties}>
              {[0.7, 0.55, 0.8, 0.6, 0.5].map((f, i) => <div key={i} style={{ display: 'flex', gap: 12, alignItems: 'center' }}><div style={{ width: 26, height: 26, borderRadius: 6, background: i === 0 ? C.accent : C.mist }} /><div style={{ height: 16, width: `${f * 100}%`, borderRadius: 6, background: i === 0 ? C.accent : C.hair }} /></div>)}
            </div>
          )}
          <div style={{ position: 'absolute', top: barH, insetInlineStart: sideW, width: cW, height: cH } as React.CSSProperties}>
            {app.kind === 'screenshot' ? (
              shot ? <Img src={staticFile(shot.src)} style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top' }} /> : <div style={{ width: '100%', height: '100%', background: C.wall }} />
            ) : (
              <>
                {app.kind === 'table' && (
                  <div style={{ position: 'absolute', left: 48, right: 48, top: 40, height: 56, background: C.bg, borderRadius: 10, display: 'flex', alignItems: 'center', padding: '0 24px', fontSize: 22, fontWeight: 700, color: C.muted, letterSpacing: 1 }}>
                    <div style={{ flex: 1 }}>{fields[0] ? '' : ''}</div>
                  </div>
                )}
                {fields.map(fieldBox)}
              </>
            )}
          </div>
        </div>
        {/* highlights + callouts (canvas space, inside camera) */}
        {acts.filter((a) => (a.do === 'highlight' || a.do === 'callout') && t >= a.at).map((a, i) => {
          const r = rectOf(a.target); if (!r) return null;
          const p = pop(t, a.at, 0.4);
          const ring = <div key={`h${i}`} style={{ position: 'absolute', left: r.x - 10, top: r.y - 10, width: r.w + 20, height: r.h + 20, borderRadius: 14, boxShadow: `0 0 0 ${5 * p}px ${C.attention}`, background: alpha(C.attention, 0.06) }} />;
          if (a.do === 'highlight' || !a.label) return ring;
          const bw = Math.min(460, L.W - L.pad * 2);
          const right = L.rtl ? r.x - bw - 40 > 20 : r.x + r.w + 40 + bw < L.W - 20;
          const bx = right ? (L.rtl ? r.x - bw - 40 : r.x + r.w + 40) : Math.max(20, Math.min(L.W - bw - 20, r.x));
          const by = right ? r.y + r.h / 2 - 40 : r.y + r.h + 30;
          return <React.Fragment key={`c${i}`}>{ring}
            <div style={{ position: 'absolute', left: bx, top: by, width: bw, transform: `scale(${0.7 + 0.3 * p})`, opacity: Math.min(1, p * 2), background: C.attention, color: C.outline, fontWeight: 600, fontSize: fit(a.label, 28, bw - 40, 3, 24), padding: '14px 22px', borderRadius: 14, boxShadow: shadow, lineHeight: 1.3 }}>{a.label}</div>
          </React.Fragment>;
        })}
        {/* cursor */}
        {pts.length > 0 && (
          <div style={{ position: 'absolute', left: cx, top: cy, opacity: prog(t, Math.max(0, pts[0].at - 1.2), 0.4) }}>
            {clickA && <div style={{ position: 'absolute', left: -40, top: -40, width: 80, height: 80, borderRadius: 40, border: `5px solid ${C.accent}`, opacity: 1 - prog(t, clickA.at, 0.5), transform: `scale(${0.3 + prog(t, clickA.at, 0.5)})` }} />}
            <svg width={44} height={56} viewBox="0 0 22 28" style={{ position: 'absolute', left: -4, top: -2, filter: 'drop-shadow(0 4px 6px rgba(0,0,0,0.3))', transform: `scale(${clickA && t - clickA.at < 0.15 ? 0.85 : 1})` }}>
              <path d="M2,2 L2,22 L7,17 L11,26 L15,24 L11,15 L18,15 Z" fill="#fff" stroke="#1E2448" strokeWidth={1.8} strokeLinejoin="round" />
            </svg>
          </div>
        )}
      </div>
      {/* toasts (screen space) */}
      {acts.filter((a) => a.do === 'toast' && t >= a.at && t < a.at + 3.5).slice(-1).map((a, i) => {
        const p = prog(t, a.at, 0.5) * (1 - prog(t, a.at + 3, 0.4));
        return <div key={`t${i}`} style={{ position: 'absolute', top: L.portrait ? 140 : 60, insetInlineEnd: L.pad * 0.6, width: Math.min(560, L.W - L.pad * 1.2), opacity: p, transform: `translateY(${(1 - p) * -30}px)`, background: '#fff', borderRadius: 16, boxShadow: shadowLg, padding: '18px 22px', display: 'flex', gap: 16, alignItems: 'center' } as React.CSSProperties}>
          <div style={{ width: 56, height: 56, borderRadius: 14, background: C.safeSoft, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto' }}><Icon name="check" size={32} color={C.safe} /></div>
          <div><div style={{ fontWeight: 700, fontSize: 26, color: C.ink }}>{a.label ?? a.value}</div>{a.label && a.value && <div style={{ fontSize: 24, color: C.muted }}>{a.value}</div>}</div>
        </div>;
      })}
    </AbsoluteFill>
  );
};
