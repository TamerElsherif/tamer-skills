// Media templates: broll (full-bleed stock clip + chips), broll_panel (clip + frosted points panel),
// image (generated/provided still with slow Ken-Burns, caption, chips). Missing assets → placeholders.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, alpha, toneColor, toneSoft, toneText } from '../core/theme';
import { Icon } from '../core/Icons';
import { Chips, ClipVideo, Media, fit } from '../core/ui';

export const Broll: React.FC<{ shot: string; chips?: string[]; dim?: number }> = ({ shot, chips, dim = 0 }) => {
  const { t } = useScene();
  const { C } = useTheme();
  return (
    <AbsoluteFill style={{ background: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${1.04 + t * 0.006})` }}><ClipVideo shot={shot} /></AbsoluteFill>
      {dim > 0 && <AbsoluteFill style={{ background: alpha(C.primaryDeep, dim) }} />}
      <Chips items={chips} />
    </AbsoluteFill>
  );
};

export const BrollPanel: React.FC<{ shot: string; kicker?: string; title: string; items: { text: string; sub?: string; icon?: string; tone?: string }[]; side?: 'left' | 'right' }> = ({ shot, kicker, title, items, side = 'right' }) => {
  const { t, cue } = useScene();
  const { C, F, grad, shadow } = useTheme();
  const L = useLayout();
  const p = prog(t, 0.3, 0.7);
  const s = L.rtl ? (side === 'right' ? 'left' : 'right') : side;
  const panel: React.CSSProperties = L.landscape
    ? { top: 90, bottom: 90, [s]: 90, width: 820 }
    : { left: L.pad * 0.6, right: L.pad * 0.6, bottom: L.portrait ? 130 : 60, maxHeight: L.portrait ? 1100 : 640 };
  const pw = L.landscape ? 820 : L.W - L.pad * 1.2;
  const n = items.length;
  return (
    <AbsoluteFill style={{ background: '#000', overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${1.04 + t * 0.006})` }}><ClipVideo shot={shot} /></AbsoluteFill>
      <AbsoluteFill style={{ background: alpha(C.primaryDeep, 0.12) }} />
      <div style={{ position: 'absolute', ...panel, background: 'rgba(255,255,255,0.95)', borderRadius: 30, padding: L.landscape ? '56px 56px' : '44px 46px', fontFamily: F.sans, color: C.ink, boxShadow: shadow, opacity: p, transform: L.landscape ? `translateX(${(1 - p) * (s === 'right' ? 60 : -60)}px)` : `translateY(${(1 - p) * 60}px)`, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {kicker && <div style={{ fontSize: 24, fontWeight: 600, color: C.accent, letterSpacing: 2, textTransform: 'uppercase' }}>{kicker}</div>}
        <div style={{ fontSize: fit(title, 50, pw - 110, 2, 32), fontWeight: 700, lineHeight: 1.15, marginTop: 6 }}>{title}</div>
        <div style={{ width: 100 * prog(t, 0.5, 0.6), height: 7, background: grad, borderRadius: 4, margin: '22px 0 32px' }} />
        {items.map((b, i) => {
          const q = prog(t, cue(i), 0.5);
          const col = toneColor(C, b.tone);
          return (
            <div key={i} style={{ display: 'flex', gap: 22, alignItems: 'flex-start', marginBottom: n > 4 ? 20 : 28, opacity: q, transform: `translateY(${(1 - q) * 18}px)` }}>
              <div style={{ flex: '0 0 auto', width: 66, height: 66, borderRadius: 18, background: toneSoft(C, b.tone), display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                {b.icon ? <Icon name={b.icon} size={36} color={col} /> : <span style={{ fontSize: 28, fontWeight: 700, color: toneText(C, b.tone) }}>{i + 1}</span>}
              </div>
              <div>
                <div style={{ fontSize: fit(b.text, 31, pw - 200, 2, 26), fontWeight: 600, lineHeight: 1.25 }}>{b.text}</div>
                {b.sub && <div style={{ fontSize: 24, color: C.muted, marginTop: 6, lineHeight: 1.35 }}>{b.sub}</div>}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const ImageT: React.FC<{ image: string; caption?: string; chips?: string[] }> = ({ image, caption, chips }) => {
  const { t, dur } = useScene();
  const { C, F } = useTheme();
  const L = useLayout();
  const z = 1.02 + 0.06 * (t / Math.max(1, dur));
  return (
    <AbsoluteFill style={{ background: C.primaryDeep, overflow: 'hidden' }}>
      <AbsoluteFill style={{ transform: `scale(${z})` }}><Media id={image} /></AbsoluteFill>
      {caption && (
        <div style={{ position: 'absolute', left: L.pad * 0.6, right: L.pad * 0.6, bottom: chips?.length ? (L.portrait ? 260 : 170) : (L.portrait ? 150 : 70), display: 'flex', justifyContent: 'center', opacity: prog(t, 0.5, 0.5) }}>
          <div style={{ background: alpha(C.primaryDeep, 0.82), color: '#fff', fontFamily: F.sans, fontSize: fit(caption, 34, L.W - L.pad * 2, 3, 26), fontWeight: 600, lineHeight: 1.35, padding: '18px 30px', borderRadius: 16, textAlign: 'center', maxWidth: L.W - L.pad * 1.2 }}>{caption}</div>
        </div>
      )}
      <Chips items={chips} />
    </AbsoluteFill>
  );
};
