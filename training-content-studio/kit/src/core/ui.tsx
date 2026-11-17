// Shared building blocks for templates: headers, cards, chips, media, typewriter, text fitting.
import React from 'react';
import { AbsoluteFill, Img, Loop, OffthreadVideo, staticFile } from 'remotion';
import { useScene, useLayout } from './ctx';
import { useTheme, prog, pop, alpha } from './theme';
import { Icon } from './Icons';
import { useTimeline } from './timelineCtx';

/** Font size that keeps `text` inside `lines` lines of a `boxW`-px box. Never below `min` (24 px rule). */
export const fit = (text: string | undefined, base: number, boxW: number, lines = 2, min = 26) => {
  const n = (text ?? '').length || 1;
  let fs = base;
  while (fs > min) {
    const cpl = boxW / (fs * 0.54);
    if (Math.ceil(n / cpl) <= lines) break;
    fs -= 2;
  }
  return Math.max(min, fs);
};

export const Appear: React.FC<{ at: number; children: React.ReactNode; dy?: number; dx?: number; scale?: boolean; style?: React.CSSProperties; out?: number; len?: number }> = ({ at, children, dy = 24, dx = 0, scale, style, out, len = 0.55 }) => {
  const { t } = useScene();
  const { rtl } = useLayout();
  const p = scale ? pop(t, at, 0.5) : prog(t, at, len);
  const q = out !== undefined ? 1 - prog(t, out, 0.35) : 1;
  const ddx = rtl ? -dx : dx;
  return (
    <div style={{ opacity: Math.min(1, prog(t, at, 0.3)) * q, transform: `translate(${(1 - p) * ddx}px,${(1 - p) * dy}px) scale(${scale ? 0.6 + 0.4 * p : 1})`, ...style }}>
      {children}
    </div>
  );
};

/** Typewriter reveal of a string from `at` at `cps` chars/sec. */
export const Type: React.FC<{ text: string; at: number; cps?: number; caret?: boolean }> = ({ text, at, cps = 24, caret }) => {
  const { t } = useScene();
  const chars = Array.from(text);
  const n = Math.max(0, Math.floor((t - at) * cps));
  const done = n >= chars.length;
  return <span>{chars.slice(0, n).join('')}{caret && !done && t >= at ? <span style={{ opacity: Math.floor(t * 3) % 2 ? 1 : 0.2 }}>|</span> : null}</span>;
};

/** Kicker + title + gradient rule, used by most info templates. */
export const Header: React.FC<{ kicker?: string; title?: string; dark?: boolean; maxW?: number; center?: boolean; size?: number; at?: number }> = ({ kicker, title, dark, maxW, center, size, at = 0.1 }) => {
  const { t } = useScene();
  const { C, F, grad } = useTheme();
  const { W, pad, portrait } = useLayout();
  const w = maxW ?? W - pad * 2;
  const base = size ?? (portrait ? 64 : 62);
  if (!kicker && !title) return null;
  return (
    <div style={{ textAlign: center ? 'center' : 'start', fontFamily: F.sans }}>
      {kicker && <div style={{ fontSize: 26, fontWeight: 600, color: dark ? C.accent2 : C.accent, letterSpacing: 2, textTransform: 'uppercase', opacity: prog(t, at, 0.4) }}>{kicker}</div>}
      {title && <div style={{ fontSize: fit(title, base, w, 2, 34), fontWeight: 700, lineHeight: 1.15, maxWidth: w, margin: center ? '8px auto 0' : '8px 0 0', opacity: prog(t, at + 0.05, 0.5), color: dark ? '#fff' : C.ink }}>{title}</div>}
      <div style={{ width: 110 * prog(t, at + 0.2, 0.6), height: 7, background: grad, borderRadius: 4, margin: center ? '24px auto 0' : '24px 0 0' }} />
    </div>
  );
};

/** Full-frame scene background. */
export const Bg: React.FC<{ dark?: boolean; children: React.ReactNode; style?: React.CSSProperties; pad?: boolean }> = ({ dark, children, style, pad = true }) => {
  const { C, F } = useTheme();
  const L = useLayout();
  return (
    <AbsoluteFill style={{ background: dark ? C.primary : C.bg, color: dark ? '#fff' : C.ink, fontFamily: F.sans, padding: pad ? (L.portrait ? `${L.pad + 70}px ${L.pad}px ${L.pad + 40}px` : `${L.pad - 10}px ${L.pad}px`) : 0, display: 'flex', flexDirection: 'column', ...style }}>
      {children}
    </AbsoluteFill>
  );
};

/** White card with a soft shadow and a subtle full border — never a one-sided thick accent border. */
export const cardStyle = (C: ReturnType<typeof useTheme>['C'], shadow: string, tint?: string): React.CSSProperties => ({
  background: C.card, borderRadius: 24, boxShadow: shadow, border: `2px solid ${tint ? alpha(tint, 0.22) : C.hair}`,
});

export const IconDisc: React.FC<{ name?: string; size?: number; color: string; bg: string; radius?: number; stroke?: number }> = ({ name, size = 84, color, bg, radius, stroke = 2 }) => (
  <div style={{ flex: '0 0 auto', width: size, height: size, borderRadius: radius ?? size / 2, background: bg, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
    <Icon name={name} size={size * 0.52} color={color} stroke={stroke} />
  </div>
);

export const NumBadge: React.FC<{ n: number | string; color: string; size?: number; fg?: string }> = ({ n, color, size = 48, fg }) => {
  const { F, C } = useTheme();
  fg = fg ?? (color === C.attention || color === C.attention2 ? C.outline : '#fff');
  return <div style={{ flex: '0 0 auto', width: size, height: size, borderRadius: size / 2, background: color, color: fg, fontFamily: F.sans, fontWeight: 700, fontSize: size * 0.5, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>{n}</div>;
};

/** Topic chips (lower start corner) — used over b-roll. Max 2. */
export const Chips: React.FC<{ items?: string[]; at?: number; pos?: 'bottom' | 'top' }> = ({ items, at = 0.3, pos = 'bottom' }) => {
  const { t, dur } = useScene();
  const { C, F, shadow } = useTheme();
  const L = useLayout();
  if (!items?.length) return null;
  const vis = Math.min(prog(t, at, 0.4), 1 - prog(t, dur - 0.5, 0.35));
  return (
    <div style={{ position: 'absolute', insetInlineStart: L.pad * 0.75, [pos]: L.portrait ? 150 : 80, display: 'flex', flexWrap: 'wrap', gap: 14, maxWidth: L.W - L.pad * 1.5, opacity: vis, fontFamily: F.sans, transform: `translateY(${(1 - prog(t, at, 0.5)) * 20}px)` } as React.CSSProperties}>
      {items.slice(0, 2).map((s, i) => (
        <div key={i} style={{ background: i === 0 ? C.accent : '#fff', color: i === 0 ? '#fff' : C.accent, border: i ? `2px solid ${C.accent}` : 'none', fontWeight: 600, fontSize: 28, padding: '12px 26px', borderRadius: 10, boxShadow: shadow, opacity: prog(t, at + i * 0.25, 0.4) }}>{s}</div>
      ))}
    </div>
  );
};

/** Neutral placeholder for a missing asset (never blocks a render). */
export const Placeholder: React.FC<{ label?: string; icon?: string; style?: React.CSSProperties }> = ({ label, icon = 'image', style }) => {
  const { C, F, grad } = useTheme();
  return (
    <div style={{ width: '100%', height: '100%', background: `${grad}`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 16, color: '#fff', fontFamily: F.sans, ...style }}>
      <div style={{ position: 'absolute', inset: 0, background: `radial-gradient(circle at 30% 30%, ${alpha('#ffffff', 0.25)}, transparent 60%)` }} />
      <Icon name={icon} size={120} color="#fff" stroke={1.4} />
      {label && <div style={{ fontSize: 24, opacity: 0.85, background: alpha(C.primaryDeep, 0.35), padding: '6px 16px', borderRadius: 8, direction: 'ltr' }}>{label}</div>}
    </div>
  );
};

/** Stock clip that never runs out: slows to ≥0.6× and loops if the scene outlasts it. */
export const ClipVideo: React.FC<{ shot?: string; style?: React.CSSProperties; rate?: number }> = ({ shot, style, rate }) => {
  const { dur, fps } = useScene();
  const tl = useTimeline();
  const b = shot ? tl.broll?.[shot] : undefined;
  if (!b || b.placeholder || !b.src) return <Placeholder icon="video" label={shot ? `b-roll: ${shot}` : undefined} />;
  const st: React.CSSProperties = { width: '100%', height: '100%', objectFit: 'cover', ...style };
  const avail = Math.max(1, b.len || 10);
  const r = rate ?? Math.max(0.6, Math.min(1, avail / Math.max(dur, 0.1)));
  const loopFrames = Math.max(30, Math.floor((avail / r) * fps) - 2);
  return (
    <Loop durationInFrames={loopFrames} layout="none">
      <OffthreadVideo src={staticFile(b.src)} muted playbackRate={r} style={st} />
    </Loop>
  );
};

/** Generated / provided image by id (generated_images[].id) or public-relative path. */
export const Media: React.FC<{ id?: string; fit?: 'cover' | 'contain'; style?: React.CSSProperties; label?: string }> = ({ id, fit: f = 'cover', style, label }) => {
  const tl = useTimeline();
  const im = id ? tl.images?.[id] : undefined;
  if (!im || im.placeholder || !im.src) return <Placeholder icon="image" label={label ?? (id ? `image: ${id}` : undefined)} />;
  return <Img src={staticFile(im.src)} style={{ width: '100%', height: '100%', objectFit: f, ...style }} />;
};

/** Small helper: horizontal direction sign for RTL-aware motion. */
export const useDirSign = () => (useLayout().rtl ? -1 : 1);
