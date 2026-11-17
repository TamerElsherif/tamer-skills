// Info templates: title, section, bullets, icon_grid, steps, timeline, do_dont, comparison, stat,
// definition, statement, table, checklist, quiz, outro, flashcard, decision. Each reads storyboard props
// exactly as schemas/storyboard.schema.json defines and reveals items on narration cues.
import React from 'react';
import { AbsoluteFill, interpolate } from 'remotion';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, pop, alpha, toneColor, toneSoft, toneText } from '../core/theme';
import { Icon } from '../core/Icons';
import { Header, Bg, fit, cardStyle, IconDisc, NumBadge, ClipVideo, useDirSign } from '../core/ui';
import { useT } from '../core/i18n';

type Item = { text: string; sub?: string; icon?: string; tone?: string };

// ---------------------------------------------------------------- title
export const Title: React.FC<{ kicker?: string; title: string; sub?: string; part?: string; icon?: string }> = ({ kicker, title, sub, part, icon = 'sparkles' }) => {
  const { t } = useScene();
  const { C, F, grad } = useTheme();
  const L = useLayout();
  const stack = !L.landscape;
  const disc = L.portrait ? 300 : L.square ? 220 : 340;
  const textW = stack ? L.W - L.pad * 2 : 1100;
  const cx = stack ? L.W / 2 : L.mx(1500);
  const cy = stack ? (L.portrait ? 560 : 300) : 540;
  return (
    <AbsoluteFill style={{ background: C.primary, fontFamily: F.sans, color: '#fff', overflow: 'hidden' }}>
      <svg width={L.W} height={L.H} style={{ position: 'absolute' }}>
        {Array.from({ length: 9 }).map((_, i) => (
          <circle key={i} cx={cx} cy={cy} r={disc / 2 + 40 + i * 70} fill="none" stroke={C.accent2} strokeOpacity={0.08 + 0.02 * (i % 3)} strokeWidth={2} strokeDasharray={`${4 + i * 3} ${10 + i * 2}`} transform={`rotate(${t * (6 + i * 2) * (i % 2 ? 1 : -1)} ${cx} ${cy})`} />
        ))}
      </svg>
      <div style={{ position: 'absolute', left: cx - disc / 2, top: cy - disc / 2, width: disc, height: disc, borderRadius: disc / 2, background: grad, display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${pop(t, 0.3, 0.7)})`, boxShadow: '0 30px 80px rgba(0,0,0,0.25)' }}>
        <Icon name={icon} size={disc * 0.5} color="#fff" stroke={1.6} />
      </div>
      <div style={{ position: 'absolute', insetInlineStart: L.pad + (stack ? 0 : 30), top: stack ? (L.portrait ? 860 : 500) : 0, bottom: stack ? undefined : 0, width: textW, display: 'flex', flexDirection: 'column', justifyContent: 'center', textAlign: stack ? 'center' : 'start' } as React.CSSProperties}>
        {kicker && <div style={{ fontSize: 30, fontWeight: 600, color: C.accent2, letterSpacing: 3, textTransform: 'uppercase', opacity: prog(t, 0.2, 0.5) }}>{kicker}</div>}
        <div style={{ width: 120 * prog(t, 0.35, 0.6), height: 8, background: grad, borderRadius: 4, margin: stack ? '26px auto 30px' : '26px 0 30px' }} />
        <div style={{ fontSize: fit(title, L.portrait ? 92 : 96, textW, 3, 48), fontWeight: 700, lineHeight: 1.1, opacity: prog(t, 0.5, 0.6), transform: `translateY(${(1 - prog(t, 0.5, 0.7)) * 30}px)` }}>{title}</div>
        {sub && <div style={{ fontSize: fit(sub, 38, textW, 3, 28), color: C.mist, marginTop: 30, lineHeight: 1.35, opacity: prog(t, 0.9, 0.6) }}>{sub}</div>}
        {part && <div style={{ alignSelf: stack ? 'center' : 'flex-start', marginTop: 34, fontSize: 26, fontWeight: 600, padding: '8px 20px', borderRadius: 8, background: 'rgba(255,255,255,0.12)', opacity: prog(t, 1.1, 0.5) }}>{part}</div>}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- section
export const Section: React.FC<{ n?: number | string; title: string; sub?: string; icon?: string }> = ({ n, title, sub, icon }) => {
  const { t } = useScene();
  const { C, F, grad } = useTheme();
  const L = useLayout();
  const ds = useDirSign();
  const w = L.landscape ? 1100 : L.W - L.pad * 2;
  return (
    <AbsoluteFill style={{ background: C.primary, fontFamily: F.sans, color: '#fff', justifyContent: 'center', padding: `0 ${L.pad + (L.landscape ? 60 : 0)}px` }}>
      <div style={{ position: 'absolute', insetInlineEnd: -80, top: L.portrait ? 160 : 140, width: 800, height: 800, borderRadius: 400, border: `2px solid ${alpha(C.accent2, 0.2)}`, transform: `scale(${0.9 + 0.1 * prog(t, 0, 1.2)})` } as React.CSSProperties} />
      {icon && <div style={{ position: 'absolute', insetInlineEnd: L.portrait ? L.W / 2 - 140 : 240, top: L.portrait ? 300 : L.H / 2 - 140, opacity: 0.9 * prog(t, 0.3, 0.6) } as React.CSSProperties}><Icon name={icon} size={280} color={C.accent2} stroke={1.3} /></div>}
      <div style={{ marginTop: L.portrait ? 380 : 0 }}>
        {n !== undefined && <div style={{ fontFamily: F.mono, fontSize: 44, color: C.attention2, fontWeight: 600, opacity: prog(t, 0.1, 0.4) }}>{typeof n === 'number' ? String(n).padStart(2, '0') : n}</div>}
        <div style={{ fontSize: fit(title, 86, w, 3, 44), fontWeight: 700, maxWidth: w, lineHeight: 1.1, marginTop: 10, opacity: prog(t, 0.25, 0.5), transform: `translateX(${(1 - prog(t, 0.25, 0.6)) * -40 * ds}px)` }}>{title}</div>
        <div style={{ width: 160 * prog(t, 0.45, 0.6), height: 8, background: grad, borderRadius: 4, margin: '30px 0' }} />
        {sub && <div style={{ fontSize: fit(sub, 36, w, 3, 28), color: C.mist, maxWidth: w, lineHeight: 1.4, opacity: prog(t, 0.6, 0.5) }}>{sub}</div>}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- bullets
export const BulletRows: React.FC<{ items: Item[]; dark?: boolean; maxW: number; base?: number; compact?: boolean; big?: boolean }> = ({ items, dark, maxW, base = 0, compact, big }) => {
  const { t, cue } = useScene();
  const { C, shadow } = useTheme();
  const ds = useDirSign();
  const n = items.length;
  const fs = big ? 42 : n > 5 || compact ? 32 : 36;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: n > 5 ? 22 : 30, maxWidth: maxW }}>
      {items.map((b, i) => {
        const at = cue(i + base);
        const p = prog(t, at, 0.5);
        const col = toneColor(C, b.tone);
        return (
          <div key={i} style={{ display: 'flex', gap: 26, alignItems: 'center', opacity: p, transform: `translateX(${(1 - p) * 40 * ds}px)` }}>
            <div style={{ flex: '0 0 auto', width: 84, height: 84, borderRadius: 20, background: dark ? 'rgba(255,255,255,0.1)' : '#fff', boxShadow: dark ? 'none' : shadow, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              {b.icon ? <Icon name={b.icon} size={44} color={dark ? C.accent2 : col} /> : <div style={{ fontWeight: 700, fontSize: 32, color: dark ? C.accent2 : toneText(C, b.tone) }}>{i + 1}</div>}
            </div>
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: fit(b.text, fs, maxW - 110, 2, 28), fontWeight: 600, lineHeight: 1.22 }}>{b.text}</div>
              {b.sub && <div style={{ fontSize: 26, color: dark ? C.mist : C.muted, marginTop: 6, lineHeight: 1.35 }}>{b.sub}</div>}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export const Bullets: React.FC<{ kicker?: string; title: string; items: Item[]; side_broll?: string; dark?: boolean }> = ({ kicker, title, items, side_broll, dark }) => {
  const { t } = useScene();
  const { shadow } = useTheme();
  const L = useLayout();
  const side = !!side_broll;
  const listW = side && L.landscape ? 1000 : L.W - L.pad * 2;
  const clip = side && (
    <div style={{ borderRadius: 30, overflow: 'hidden', boxShadow: shadow, opacity: prog(t, 0.2, 0.5), width: L.landscape ? 620 : L.W - L.pad * 2, height: L.landscape ? 720 : L.portrait ? 560 : 300, flex: '0 0 auto' }}>
      <ClipVideo shot={side_broll} style={{ transform: `scale(${1.05 + t * 0.004})` }} />
    </div>
  );
  return (
    <Bg dark={dark}>
      {side && !L.landscape && <div style={{ marginBottom: 40 }}>{clip}</div>}
      <Header kicker={kicker} title={title} dark={dark} maxW={listW} />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', paddingTop: 40, paddingBottom: L.portrait ? 120 : 30 }}>
        <BulletRows items={items} dark={dark} maxW={listW} compact={side && !L.landscape} big={L.portrait && !side} />
      </div>
      {side && L.landscape && <div style={{ position: 'absolute', insetInlineEnd: L.pad - 10, top: 0, bottom: 0, display: 'flex', alignItems: 'center' } as React.CSSProperties}>{clip}</div>}
    </Bg>
  );
};

// ---------------------------------------------------------------- icon grid
export const IconGrid: React.FC<{ kicker?: string; title: string; items: { icon: string; label: string; sub?: string; tone?: string }[]; cols?: number }> = ({ kicker, title, items, cols }) => {
  const { t, cue } = useScene();
  const { C, shadow } = useTheme();
  const L = useLayout();
  const n = items.length;
  const autoCols = L.landscape ? (n <= 4 ? n : 3) : L.portrait ? (n <= 3 ? 1 : 2) : n <= 2 ? n : n === 4 ? 2 : 3;
  const c = Math.min(cols ?? autoCols, L.landscape ? 6 : L.portrait ? 2 : 3);
  const rows = Math.ceil(n / c);
  const cellW = (L.W - L.pad * 2 - (c - 1) * 30) / c;
  const row1 = L.portrait && c === 1;
  return (
    <Bg>
      <Header kicker={kicker} title={title} />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', paddingTop: 30 }}>
        <div style={{ width: '100%', display: 'grid', gridTemplateColumns: `repeat(${c},1fr)`, gap: 30 }}>
          {items.map((it, i) => {
            const at = cue(i);
            const p = pop(t, at, 0.5);
            const col = toneColor(C, it.tone);
            const big = rows === 1 && !L.portrait;
            return (
              <div key={i} style={{ ...cardStyle(C, shadow, col), padding: big ? '44px 36px' : '30px 28px', display: 'flex', flexDirection: row1 ? 'row' : 'column', gap: row1 ? 28 : 0, alignItems: row1 ? 'center' : 'flex-start', minHeight: big ? 330 : 0, opacity: prog(t, at, 0.3), transform: `scale(${0.85 + 0.15 * p})` }}>
                <div style={{ marginBottom: row1 ? 0 : 22 }}><IconDisc name={it.icon} size={big ? 110 : 92} color={col} bg={toneSoft(C, it.tone)} /></div>
                <div>
                  <div style={{ fontSize: fit(it.label, big ? 36 : 32, row1 ? cellW - 160 : cellW - 60, 2, 28), fontWeight: 700, lineHeight: 1.2 }}>{it.label}</div>
                  {it.sub && <div style={{ fontSize: rows > 2 ? 24 : 26, color: C.muted, marginTop: 10, lineHeight: 1.35 }}>{it.sub}</div>}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Bg>
  );
};

// ---------------------------------------------------------------- steps
export const Steps: React.FC<{ kicker?: string; title: string; danger?: boolean; steps: { icon?: string; label: string; sub?: string }[] }> = ({ kicker, title, danger, steps }) => {
  const { t, cue } = useScene();
  const { C, shadow } = useTheme();
  const L = useLayout();
  const col = danger ? C.attention : C.accent;
  const vertical = !L.landscape || steps.length > 5;
  if (vertical) {
    const size = steps.length > 4 ? 96 : 116;
    return (
      <Bg>
        <Header kicker={kicker} title={title} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: steps.length > 4 ? 26 : 40, paddingTop: 30, position: 'relative' }}>
          {steps.map((s, i) => {
            const at = cue(i);
            const p = pop(t, at, 0.5);
            return (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 30, opacity: prog(t, at, 0.3), transform: `translateY(${(1 - p) * 24}px)` }}>
                <div style={{ position: 'relative', flex: '0 0 auto', width: size, height: size, borderRadius: size / 2, background: '#fff', boxShadow: shadow, border: `5px solid ${col}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {s.icon ? <Icon name={s.icon} size={size * 0.44} color={col} /> : <span style={{ fontSize: 40, fontWeight: 700, color: danger ? C.attentionText : col }}>{i + 1}</span>}
                  {s.icon && <div style={{ position: 'absolute', top: -8, insetInlineStart: -8 } as React.CSSProperties}><NumBadge n={i + 1} color={C.primary} size={42} /></div>}
                </div>
                <div style={{ minWidth: 0 }}>
                  <div style={{ fontSize: fit(s.label, 36, L.W - L.pad * 2 - size - 40, 2, 28), fontWeight: 700, lineHeight: 1.2 }}>{s.label}</div>
                  {s.sub && <div style={{ fontSize: 26, color: C.muted, marginTop: 6, lineHeight: 1.35 }}>{s.sub}</div>}
                </div>
              </div>
            );
          })}
        </div>
      </Bg>
    );
  }
  const colW = (L.W - L.pad * 2 - (steps.length - 1) * 70) / steps.length;
  return (
    <Bg>
      <Header kicker={kicker} title={title} />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', paddingBottom: 60 }}>
        <div style={{ width: '100%', display: 'flex', alignItems: 'flex-start' }}>
          {steps.map((s, i) => {
            const at = cue(i);
            const p = pop(t, at, 0.5);
            return (
              <React.Fragment key={i}>
                <div style={{ flex: 1, textAlign: 'center', opacity: prog(t, at, 0.3), transform: `translateY(${(1 - p) * 30}px)` }}>
                  <div style={{ margin: '0 auto', width: 170, height: 170, borderRadius: 85, background: '#fff', boxShadow: shadow, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', border: `5px solid ${col}` }}>
                    {s.icon ? <Icon name={s.icon} size={70} color={col} /> : <span style={{ fontSize: 56, fontWeight: 700, color: danger ? C.attentionText : col }}>{i + 1}</span>}
                    {s.icon && <div style={{ position: 'absolute', top: -10, insetInlineStart: -10 } as React.CSSProperties}><NumBadge n={i + 1} color={C.primary} /></div>}
                  </div>
                  <div style={{ fontSize: fit(s.label, 34, colW, 2, 26), fontWeight: 700, marginTop: 28, padding: '0 6px', lineHeight: 1.2 }}>{s.label}</div>
                  {s.sub && <div style={{ fontSize: 25, color: C.muted, marginTop: 10, padding: '0 10px', lineHeight: 1.4 }}>{s.sub}</div>}
                </div>
                {i < steps.length - 1 && (
                  <div style={{ flex: '0 0 70px', marginTop: 70, opacity: prog(t, cue(i + 1) - 0.2, 0.4), transform: L.rtl ? 'scaleX(-1)' : undefined }}>
                    <svg width={70} height={30}><path d="M4,15 L56,15 M44,4 L60,15 L44,26" stroke={C.mist} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" /></svg>
                  </div>
                )}
              </React.Fragment>
            );
          })}
        </div>
      </div>
    </Bg>
  );
};

// ---------------------------------------------------------------- timeline
export const TimelineT: React.FC<{ title: string; events: { when?: string; label: string; sub?: string }[] }> = ({ title, events }) => {
  const { t, cue } = useScene();
  const { C, F, shadow, grad } = useTheme();
  const L = useLayout();
  const n = events.length;
  if (!L.landscape || n > 6) {
    return (
      <Bg>
        <Header title={title} />
        <div style={{ flex: 1, position: 'relative', display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: n > 5 ? 22 : 34, paddingInlineStart: 70, marginTop: 30 } as React.CSSProperties}>
          <div style={{ position: 'absolute', insetInlineStart: 26, top: 40, bottom: 40, width: 6, borderRadius: 3, background: C.hair } as React.CSSProperties}>
            <div style={{ width: 6, height: `${100 * prog(t, 0.3, Math.max(1, cue(n - 1)))}%`, background: grad, borderRadius: 3 }} />
          </div>
          {events.map((e, i) => {
            const at = cue(i);
            return (
              <div key={i} style={{ position: 'relative', opacity: prog(t, at, 0.4), transform: `translateY(${(1 - prog(t, at, 0.5)) * 20}px)` }}>
                <div style={{ position: 'absolute', insetInlineStart: -58, top: 8, width: 30, height: 30, borderRadius: 15, background: '#fff', border: `6px solid ${C.accent}` } as React.CSSProperties} />
                {e.when && <div style={{ fontFamily: F.mono, fontSize: 26, fontWeight: 600, color: C.accent }}>{e.when}</div>}
                <div style={{ fontSize: 34, fontWeight: 700, lineHeight: 1.2 }}>{e.label}</div>
                {e.sub && <div style={{ fontSize: 25, color: C.muted, marginTop: 4, lineHeight: 1.35 }}>{e.sub}</div>}
              </div>
            );
          })}
        </div>
      </Bg>
    );
  }
  const colW = (L.W - L.pad * 2) / n;
  const axisY = 560;
  return (
    <Bg>
      <Header title={title} />
      <div style={{ position: 'absolute', left: L.pad, right: L.pad, top: axisY, height: 6, background: C.hair, borderRadius: 3, direction: L.rtl ? 'rtl' : 'ltr' }}>
        <div style={{ height: 6, width: `${100 * prog(t, 0.3, Math.max(1, cue(n - 1)))}%`, background: grad, borderRadius: 3 }} />
      </div>
      {events.map((e, i) => {
        const at = cue(i);
        const up = i % 2 === 0;
        const x = L.pad + colW * (i + 0.5);
        const xx = L.rtl ? L.W - x : x;
        return (
          <div key={i} style={{ position: 'absolute', left: xx - colW / 2, width: colW, top: 0, height: L.H, opacity: prog(t, at, 0.4) }}>
            <div style={{ position: 'absolute', left: colW / 2 - 18, top: axisY - 15, width: 36, height: 36, borderRadius: 18, background: '#fff', border: `7px solid ${C.accent}`, transform: `scale(${pop(t, at, 0.4)})` }} />
            <div style={{ position: 'absolute', left: colW / 2 - 2, top: up ? axisY - 60 : axisY + 30, width: 4, height: 30, background: C.mist }} />
            <div style={{ position: 'absolute', left: 10, right: 10, ...(up ? { bottom: L.H - axisY + 70 } : { top: axisY + 70 }), textAlign: 'center', ...cardStyle(C, shadow), padding: '20px 18px' }}>
              {e.when && <div style={{ fontFamily: F.mono, fontSize: 26, fontWeight: 600, color: C.accent }}>{e.when}</div>}
              <div style={{ fontSize: fit(e.label, 30, colW - 60, 3, 24), fontWeight: 700, lineHeight: 1.2, marginTop: 4 }}>{e.label}</div>
              {e.sub && <div style={{ fontSize: 24, color: C.muted, marginTop: 6, lineHeight: 1.3 }}>{e.sub}</div>}
            </div>
          </div>
        );
      })}
    </Bg>
  );
};

// ---------------------------------------------------------------- do / don't and comparison
const TwoCols: React.FC<{ title?: string; a: { head: string; items: string[]; color: string; icon: string }; b: { head: string; items: string[]; color: string; icon: string } }> = ({ title, a, b }) => {
  const { t, cue } = useScene();
  const { C, shadow } = useTheme();
  const L = useLayout();
  const stack = L.portrait;
  const total = a.items.length + b.items.length;
  const fs = stack ? (total > 8 ? 26 : 30) : total > 10 ? 26 : total <= 6 ? 36 : 30;
  const col = (c: typeof a, base: number) => (
    <div style={{ flex: stack ? '0 0 auto' : 1, ...cardStyle(C, shadow, c.color), padding: stack ? '28px 34px' : '36px 40px', minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16, fontSize: 38, fontWeight: 700, marginBottom: 22, color: c.color === C.attention ? C.attentionText : c.color }}>
        <IconDisc name={c.icon} size={60} color={c.color === C.attention ? C.outline : '#fff'} bg={c.color} />{c.head}
      </div>
      {c.items.map((s, i) => {
        const at = cue(base + i);
        return (
          <div key={i} style={{ fontSize: fs, lineHeight: 1.35, marginBottom: stack ? 14 : 20, opacity: prog(t, at, 0.4), transform: `translateY(${(1 - prog(t, at, 0.5)) * 16}px)`, display: 'flex', gap: 14 }}>
            <span style={{ color: c.color, fontWeight: 700 }}>•</span><span>{s}</span>
          </div>
        );
      })}
    </div>
  );
  return (
    <Bg>
      <Header title={title} />
      <div style={{ flex: 1, display: 'flex', flexDirection: stack ? 'column' : 'row', gap: stack ? 34 : 50, marginTop: 40, alignItems: stack ? 'stretch' : 'center', justifyContent: 'center', paddingBottom: stack ? 120 : 40 }}>
        {col(a, 0)}
        {col(b, a.items.length)}
      </div>
    </Bg>
  );
};

export const DoDont: React.FC<{ title: string; dont_head?: string; do_head?: string; dont: string[]; do: string[] }> = (p) => {
  const { C } = useTheme();
  const tr = useT();
  return <TwoCols title={p.title} a={{ head: p.dont_head ?? tr('dont'), items: p.dont, color: C.attention, icon: 'x' }} b={{ head: p.do_head ?? tr('do'), items: p.do, color: C.safe, icon: 'check' }} />;
};

export const Comparison: React.FC<{ title?: string; left: { head: string; items: string[] }; right: { head: string; items: string[] } }> = ({ title, left, right }) => {
  const { C } = useTheme();
  return <TwoCols title={title} a={{ ...left, color: C.primary, icon: 'layers' }} b={{ ...right, color: C.accent, icon: 'sparkles' }} />;
};

// ---------------------------------------------------------------- stat
export const Stat: React.FC<{ value: number; prefix?: string; suffix?: string; label: string; source?: string; icon?: string }> = ({ value, prefix = '', suffix = '', label, source, icon = 'trend' }) => {
  const { t, cue, hasCue } = useScene();
  const { C, F, grad } = useTheme();
  const L = useLayout();
  const at = hasCue(0) ? cue(0) : 0.4;
  const decimals = Number.isInteger(value) ? 0 : (String(value).split('.')[1]?.length ?? 1);
  const v = value * interpolate(t, [at, at + 1.6], [0, 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: (x) => 1 - Math.pow(1 - x, 3) });
  const txt = `${prefix}${v.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}${suffix}`;
  const finalTxt = `${prefix}${value.toLocaleString('en-US')}${suffix}`;
  return (
    <AbsoluteFill style={{ background: C.primary, color: '#fff', fontFamily: F.sans, alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: `0 ${L.pad}px` }}>
      <div style={{ opacity: prog(t, 0.1, 0.4) }}><Icon name={icon} size={96} color={C.accent2} /></div>
      <div style={{ fontSize: Math.min(230, (L.W - L.pad * 2) / (finalTxt.length * 0.62)), fontWeight: 800, lineHeight: 1.05, marginTop: 20, background: grad, WebkitBackgroundClip: 'text', color: 'transparent', direction: 'ltr' }}>{txt}</div>
      <div style={{ fontSize: fit(label, 46, L.W - L.pad * 2, 3, 30), fontWeight: 600, maxWidth: 1300, marginTop: 26, lineHeight: 1.25, opacity: prog(t, at + 0.6, 0.5) }}>{label}</div>
      {source && <div style={{ fontSize: 24, color: C.mist, marginTop: 26, opacity: prog(t, at + 1, 0.5) }}>{source}</div>}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- definition
export const Definition: React.FC<{ term: string; def: string; note?: string; icon?: string }> = ({ term, def, note, icon = 'book' }) => {
  const { t, cue, hasCue } = useScene();
  const { C, F, grad, shadow } = useTheme();
  const L = useLayout();
  const tr = useT();
  const stack = !L.landscape;
  const w = stack ? L.W - L.pad * 2 : 1500;
  const disc = stack ? 170 : 220;
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, color: C.ink, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: w, ...cardStyle(C, shadow), borderRadius: 30, padding: stack ? '56px 50px' : '70px 90px', display: 'flex', flexDirection: stack ? 'column' : 'row', gap: stack ? 34 : 60, alignItems: stack ? 'flex-start' : 'center', opacity: prog(t, 0.1, 0.4), transform: `translateY(${(1 - prog(t, 0.1, 0.6)) * 30}px)` }}>
        <div style={{ flex: `0 0 ${disc}px`, height: disc, width: disc, borderRadius: disc / 2, background: grad, display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name={icon} size={disc / 2} color="#fff" /></div>
        <div style={{ minWidth: 0 }}>
          <div style={{ fontSize: 28, fontWeight: 600, color: C.accent, letterSpacing: 2, textTransform: 'uppercase' }}>{tr('definition')}</div>
          <div style={{ fontSize: fit(term, 72, w - (stack ? 100 : disc + 240), 2, 40), fontWeight: 700, margin: '8px 0 20px', lineHeight: 1.1 }}>{term}</div>
          <div style={{ fontSize: fit(def, 38, w - (stack ? 100 : disc + 240), 5, 28), lineHeight: 1.45, opacity: prog(t, hasCue(0) ? cue(0) : 0.6, 0.6) }}>{def}</div>
          {note && <div style={{ fontSize: 28, color: C.muted, marginTop: 22, lineHeight: 1.4, opacity: prog(t, hasCue(1) ? cue(1) : 1.4, 0.6) }}>{note}</div>}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- statement
export const Statement: React.FC<{ text: string; accent?: string; sub?: string; icon?: string; light?: boolean }> = ({ text, accent, sub, icon, light }) => {
  const { t, cue, hasCue } = useScene();
  const { C, F } = useTheme();
  const L = useLayout();
  const idx = accent ? text.indexOf(accent) : -1;
  const parts = idx >= 0 ? [text.slice(0, idx), text.slice(idx + accent!.length)] : [text, ''];
  const w = L.W - L.pad * 2 - (L.landscape ? 160 : 0);
  return (
    <AbsoluteFill style={{ background: light ? C.bg : C.primary, color: light ? C.ink : '#fff', fontFamily: F.sans, alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: `0 ${L.pad}px` }}>
      {icon && <div style={{ transform: `scale(${pop(t, 0.1, 0.5)})`, marginBottom: 30 }}><Icon name={icon} size={110} color={light ? C.accent : C.accent2} stroke={1.8} /></div>}
      <div style={{ fontSize: fit(text, 84, w, L.portrait ? 6 : 3, 44), fontWeight: 700, lineHeight: 1.18, maxWidth: w, opacity: prog(t, 0.2, 0.5), transform: `translateY(${(1 - prog(t, 0.2, 0.7)) * 26}px)` }}>
        {parts[0]}{idx >= 0 && <span style={{ color: light ? C.attentionText : C.attention2 }}>{accent}</span>}{parts[1]}
      </div>
      {sub && <div style={{ fontSize: fit(sub, 38, w, 3, 28), color: light ? C.muted : C.mist, marginTop: 34, maxWidth: w, lineHeight: 1.4, opacity: prog(t, hasCue(0) ? cue(0) : 0.9, 0.5) }}>{sub}</div>}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- table
export const Table: React.FC<{ title?: string; columns: string[]; rows: string[][] }> = ({ title, columns, rows }) => {
  const { t, cue } = useScene();
  const { C, F, shadow } = useTheme();
  const L = useLayout();
  const cards = L.portrait && columns.length > 2;
  if (cards) {
    return (
      <Bg>
        <Header title={title} />
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 22, marginTop: 30 }}>
          {rows.map((r, i) => (
            <div key={i} style={{ ...cardStyle(C, shadow), padding: '22px 30px', opacity: prog(t, cue(i), 0.4), transform: `translateY(${(1 - prog(t, cue(i), 0.5)) * 18}px)` }}>
              <div style={{ fontSize: 32, fontWeight: 700, marginBottom: 8 }}>{r[0]}</div>
              {r.slice(1).map((c, j) => (
                <div key={j} style={{ fontSize: 26, lineHeight: 1.4, display: 'flex', gap: 10 }}><span style={{ color: C.accent, fontWeight: 600 }}>{columns[j + 1]}:</span><span>{c}</span></div>
              ))}
            </div>
          ))}
        </div>
      </Bg>
    );
  }
  const fs = rows.length > 6 || columns.length > 4 ? 26 : 30;
  return (
    <Bg>
      <Header title={title} />
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', marginTop: 30 }}>
        <div style={{ width: '100%', ...cardStyle(C, shadow), overflow: 'hidden', padding: 0 }}>
          <div style={{ display: 'grid', gridTemplateColumns: `repeat(${columns.length}, 1fr)`, background: C.primary, color: '#fff', fontWeight: 700, fontSize: fs }}>
            {columns.map((c, j) => <div key={j} style={{ padding: '20px 26px' }}>{c}</div>)}
          </div>
          {rows.map((r, i) => (
            <div key={i} style={{ display: 'grid', gridTemplateColumns: `repeat(${columns.length}, 1fr)`, fontSize: fs, background: i % 2 ? C.bg : '#fff', opacity: prog(t, cue(i), 0.4), borderTop: `1px solid ${C.hair}` }}>
              {r.map((c, j) => <div key={j} style={{ padding: '18px 26px', fontWeight: j === 0 ? 600 : 400, lineHeight: 1.35, fontFamily: /^[\d\s.,%$€£+-]+$/.test(c) ? F.mono : undefined }}>{c}</div>)}
            </div>
          ))}
        </div>
      </div>
    </Bg>
  );
};

// ---------------------------------------------------------------- checklist
export const Checklist: React.FC<{ kicker?: string; title: string; items: string[] }> = ({ kicker, title, items }) => {
  const { t, cue } = useScene();
  const { C } = useTheme();
  const L = useLayout();
  const tr = useT();
  const n = items.length;
  const w = L.W - L.pad * 2;
  return (
    <Bg dark>
      <Header kicker={kicker ?? tr('takeaways')} title={title} dark />
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: n > 5 ? 22 : 30, marginTop: 30 }}>
        {items.map((s, i) => {
          const at = cue(i);
          const p = pop(t, at, 0.45);
          return (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 28, opacity: prog(t, at - 0.1, 0.3) }}>
              <div style={{ width: 58, height: 58, borderRadius: 16, border: `4px solid ${C.accent2}`, display: 'flex', alignItems: 'center', justifyContent: 'center', background: p > 0.5 ? C.accent2 : 'transparent', flex: '0 0 auto' }}>
                <svg width={34} height={34} viewBox="0 0 34 34"><path d="M6,18 L14,26 L28,8" fill="none" stroke={C.primary} strokeWidth={5} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={40} strokeDashoffset={40 * (1 - p)} /></svg>
              </div>
              <div style={{ fontSize: fit(s, n > 5 ? 34 : 38, w - 90, 2, 28), fontWeight: 500, lineHeight: 1.25 }}>{s}</div>
            </div>
          );
        })}
      </div>
    </Bg>
  );
};

// ---------------------------------------------------------------- quiz
export const Quiz: React.FC<{ q?: string; options?: string[]; answer?: number; why?: string; quiz_item?: string }> = ({ q, options = [], answer = -1, why, quiz_item }) => {
  const { t, cue, hasCue, dur } = useScene();
  const { C, F, shadow } = useTheme();
  const L = useLayout();
  const tr = useT();
  const reveal = hasCue(0) ? cue(0) : dur * 0.65;
  const w = L.W - L.pad * 2;
  const on = t >= reveal;
  return (
    <Bg style={{ justifyContent: L.landscape ? undefined : 'center' }}>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, fontSize: 28, fontWeight: 700, color: C.accent, letterSpacing: 2, textTransform: 'uppercase' }}><Icon name="lightbulb" size={34} color={C.accent} /> {tr('quick_check')}</div>
      <div style={{ fontSize: fit(q ?? quiz_item ?? '', 52, w, 4, 32), fontWeight: 700, lineHeight: 1.25, margin: '20px 0 40px', opacity: prog(t, 0.2, 0.5) }}>{q ?? `[${quiz_item}]`}</div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: options.length > 4 ? 16 : 22 }}>
        {options.map((o, i) => {
          const right = i === answer;
          return (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 24, padding: '20px 28px', borderRadius: 18, background: on && right ? C.safeSoft : '#fff', border: `3px solid ${on && right ? C.safe : C.hair}`, opacity: prog(t, 0.6 + i * 0.25, 0.4) * (on && !right ? 0.45 : 1), boxShadow: shadow, fontSize: fit(o, 32, w - 140, 2, 26), fontWeight: 500 }}>
              <div style={{ width: 54, height: 54, borderRadius: 27, background: on && right ? C.safe : C.accentSoft, color: on && right ? '#fff' : C.accent, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto', fontFamily: F.latin }}>
                {on && right ? <Icon name="Check" size={30} color="#fff" stroke={3} /> : 'ABCDEF'[i]}
              </div>
              {o}
            </div>
          );
        })}
      </div>
      {why && <div style={{ fontSize: 28, color: C.muted, marginTop: 26, opacity: prog(t, reveal + 0.4, 0.5), lineHeight: 1.4 }}>{why}</div>}
    </Bg>
  );
};

// ---------------------------------------------------------------- outro
export const Outro: React.FC<{ title?: string; line: string; tips?: string[]; evidence_line?: string }> = ({ title, line, tips, evidence_line }) => {
  const { t } = useScene();
  const { C, F, grad, evidence } = useTheme();
  const L = useLayout();
  const ev = evidence_line ?? evidence;
  const w = L.W - L.pad * 2;
  return (
    <AbsoluteFill style={{ background: C.primary, color: '#fff', fontFamily: F.sans, alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: `0 ${L.pad}px` }}>
      <svg width={L.W} height={L.H} style={{ position: 'absolute', left: 0, top: 0 }}>
        {Array.from({ length: 6 }).map((_, i) => <circle key={i} cx={L.W / 2} cy={L.H / 2} r={200 + i * 110} fill="none" stroke={C.accent2} strokeOpacity={0.1} strokeWidth={2} strokeDasharray="6 14" transform={`rotate(${t * 4 * (i % 2 ? 1 : -1)} ${L.W / 2} ${L.H / 2})`} />)}
      </svg>
      {title && <div style={{ fontSize: 30, color: C.accent2, fontWeight: 600, letterSpacing: 3, textTransform: 'uppercase', opacity: prog(t, 0.1, 0.4) }}>{title}</div>}
      <div style={{ fontSize: fit(line, 76, w, 4, 40), fontWeight: 700, maxWidth: w, lineHeight: 1.15, margin: '26px 0', opacity: prog(t, 0.3, 0.5) }}>{line}</div>
      <div style={{ width: 160 * prog(t, 0.5, 0.6), height: 8, background: grad, borderRadius: 4 }} />
      {tips && <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center', gap: 20, marginTop: 50, maxWidth: w }}>{tips.map((s, i) => <div key={i} style={{ fontSize: 28, padding: '14px 26px', borderRadius: 12, background: 'rgba(255,255,255,0.1)', opacity: prog(t, 0.8 + i * 0.2, 0.4) }}>{s}</div>)}</div>}
      {ev && <div style={{ position: 'absolute', bottom: L.portrait ? 120 : 60, left: L.pad, right: L.pad, fontSize: 24, color: C.mist, opacity: 0.85 * prog(t, 1.2, 0.5) }}>{ev}</div>}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- flashcard
export const Flashcard: React.FC<{ front: string; back: string; icon?: string }> = ({ front, back, icon = 'lightbulb' }) => {
  const { t, cue, hasCue, dur } = useScene();
  const { C, F, grad, shadowLg } = useTheme();
  const L = useLayout();
  const at = hasCue(0) ? cue(0) : dur * 0.5;
  const flip = prog(t, at, 0.8);
  const ang = flip * 180;
  const w = L.landscape ? 1200 : L.W - L.pad * 2, h = L.portrait ? 1100 : L.square ? 760 : 700;
  const face = (side: 'front' | 'back'): React.CSSProperties => ({
    position: 'absolute', inset: 0, borderRadius: 36, backfaceVisibility: 'hidden', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', textAlign: 'center', padding: 70, boxShadow: shadowLg,
    transform: side === 'back' ? 'rotateY(180deg)' : undefined,
    background: side === 'front' ? '#fff' : C.primary, color: side === 'front' ? C.ink : '#fff',
  });
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, alignItems: 'center', justifyContent: 'center', perspective: 2400 }}>
      <div style={{ width: w, height: h, position: 'relative', transformStyle: 'preserve-3d', transform: `rotateY(${ang}deg) scale(${0.9 + 0.1 * prog(t, 0.1, 0.5)})`, opacity: prog(t, 0.05, 0.4) }}>
        <div style={face('front')}>
          <div style={{ width: 150, height: 150, borderRadius: 75, background: grad, display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: 40 }}><Icon name={icon} size={80} color="#fff" /></div>
          <div style={{ fontSize: fit(front, 64, w - 140, 4, 34), fontWeight: 700, lineHeight: 1.2 }}>{front}</div>
        </div>
        <div style={face('back')}>
          <div style={{ width: 110 * prog(t, at + 0.5, 0.5), height: 8, background: grad, borderRadius: 4, marginBottom: 40 }} />
          <div style={{ fontSize: fit(back, 48, w - 140, 6, 30), fontWeight: 600, lineHeight: 1.35 }}>{back}</div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- decision (branching choice screen)
export const Decision: React.FC<{ prompt: string; choices: { id: string; label: string; next: string; correct?: boolean }[]; video_choice?: string }> = ({ prompt, choices, video_choice }) => {
  const { t, cue, hasCue, dur } = useScene();
  const { C, F, shadow, grad } = useTheme();
  const L = useLayout();
  const tr = useT();
  const pickAt = hasCue(0) ? cue(0) : dur * 0.7;
  const picked = video_choice ?? choices.find((c) => c.correct)?.id ?? choices[0]?.id;
  const cols = L.landscape && choices.length > 2 ? 2 : 1;
  const w = L.W - L.pad * 2;
  return (
    <Bg dark>
      <div style={{ display: 'inline-flex', alignItems: 'center', gap: 14, fontSize: 28, fontWeight: 700, color: C.accent2, letterSpacing: 2, textTransform: 'uppercase' }}><Icon name="GitBranch" size={34} color={C.accent2} /> {tr('your_choice')}</div>
      <div style={{ fontSize: fit(prompt, 56, w, 3, 34), fontWeight: 700, lineHeight: 1.22, margin: '22px 0 46px', opacity: prog(t, 0.2, 0.5) }}>{prompt}</div>
      <div style={{ display: 'grid', gridTemplateColumns: `repeat(${cols}, 1fr)`, gap: 28 }}>
        {choices.map((c, i) => {
          const sel = c.id === picked && t >= pickAt;
          const dim = t >= pickAt && !sel;
          return (
            <div key={c.id} style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 24, padding: '30px 34px', borderRadius: 22, background: sel ? '#fff' : 'rgba(255,255,255,0.08)', color: sel ? C.ink : '#fff', border: `3px solid ${sel ? C.accent2 : 'rgba(255,255,255,0.18)'}`, boxShadow: sel ? shadow : 'none', opacity: prog(t, 0.6 + i * 0.3, 0.4) * (dim ? 0.45 : 1), transform: `scale(${sel ? 1 + 0.03 * pop(t, pickAt, 0.4) : 1})`, fontSize: fit(c.label, 34, w / cols - 160, 3, 26), fontWeight: 600, lineHeight: 1.3 }}>
              <div style={{ flex: '0 0 auto', width: 60, height: 60, borderRadius: 30, background: sel ? grad : 'rgba(255,255,255,0.14)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.latin, fontWeight: 700, color: '#fff' }}>{'ABCD'[i]}</div>
              {c.label}
              {sel && <div style={{ position: 'absolute', top: -18, insetInlineEnd: 24, background: C.accent2, color: C.primaryDeep, fontSize: 22, fontWeight: 700, padding: '4px 14px', borderRadius: 8 } as React.CSSProperties}>{tr('chosen')}</div>}
            </div>
          );
        })}
      </div>
    </Bg>
  );
};
