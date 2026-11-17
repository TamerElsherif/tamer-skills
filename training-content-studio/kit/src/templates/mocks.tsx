// UI mock-up templates: email_mock, chat_mock, browser_mock, mfa_prompt, popup, code_mock.
// Callouts never rely on pixel arrows: the target gets a highlight ring + numbered badge and the
// matching numbered note appears beside (landscape) or below (portrait/square) the mock on its cue.
import React from 'react';
import { AbsoluteFill } from 'remotion';
import { useScene, useLayout } from '../core/ctx';
import { useTheme, prog, pop, alpha, toneColor, lerp, onFill } from '../core/theme';
import { Icon } from '../core/Icons';
import { Appear, Type, fit, NumBadge, cardStyle } from '../core/ui';
import { useT } from '../core/i18n';

type Callout = { cue: number; label: string; tone?: string; target?: string };

const useHl = (callouts: Callout[] = []) => {
  const { t, cue } = useScene();
  const { C } = useTheme();
  const on = (target: string) => {
    const i = callouts.findIndex((c) => c.target === target);
    if (i < 0) return null;
    const c = callouts[i];
    const at = cue(c.cue);
    if (t < at) return null;
    return { n: i + 1, col: toneColor(C, c.tone ?? 'warn'), p: pop(t, at, 0.4) };
  };
  const ring = (target: string, radius = 8): React.CSSProperties => {
    const h = on(target);
    return h ? { boxShadow: `0 0 0 ${4 * h.p}px ${h.col}`, background: alpha(h.col, 0.1), borderRadius: radius, position: 'relative' } : { position: 'relative' };
  };
  const badge = (target: string) => {
    const h = on(target);
    return h ? <span style={{ position: 'absolute', top: -20, insetInlineEnd: -20, transform: `scale(${h.p})`, zIndex: 3 } as React.CSSProperties}><NumBadge n={h.n} color={h.col} size={40} /></span> : null;
  };
  return { ring, badge };
};

const CalloutList: React.FC<{ callouts: Callout[]; w: number }> = ({ callouts, w }) => {
  const { t, cue } = useScene();
  const { C, F, shadow } = useTheme();
  return (
    <div style={{ width: w, display: 'flex', flexDirection: 'column', gap: 20, fontFamily: F.sans }}>
      {callouts.map((c, i) => {
        const at = cue(c.cue);
        const col = toneColor(C, c.tone ?? 'warn');
        return (
          <Appear key={i} at={at} dx={40} dy={0}>
            <div style={{ display: 'flex', gap: 18, alignItems: 'center', ...cardStyle(C, shadow, col), borderRadius: 18, padding: '18px 22px', opacity: t >= at ? 1 : 0 }}>
              <NumBadge n={i + 1} color={col} size={46} />
              <div style={{ fontSize: fit(c.label, 30, w - 110, 3, 24), fontWeight: 600, lineHeight: 1.3, color: C.ink }}>{c.label}</div>
            </div>
          </Appear>
        );
      })}
    </div>
  );
};

/** Lays out a mock + its callouts for the current aspect. */
const MockStage: React.FC<{ mock: (w: number) => React.ReactNode; callouts?: Callout[]; mockW: number; caption?: string; title?: string }> = ({ mock, callouts = [], mockW, caption, title }) => {
  const { t } = useScene();
  const { C, F } = useTheme();
  const L = useLayout();
  const has = callouts.length > 0;
  const avail = L.W - L.pad * 2;
  const head = title ? <div style={{ position: 'absolute', top: L.portrait ? 140 : 60, left: L.pad, right: L.pad, fontSize: fit(title, 50, avail, 2, 30), fontWeight: 700, color: C.ink, opacity: prog(t, 0.1, 0.4) }}>{title}</div> : null;
  const padTop = title ? (L.portrait ? 160 : 120) : 0;
  if (L.landscape) {
    const mw = has ? Math.min(mockW, avail - 600) : Math.min(mockW, avail);
    return (
      <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, alignItems: 'center', justifyContent: 'center', flexDirection: 'row', gap: 60, padding: `${padTop}px ${L.pad}px 0` }}>
        {head}
        <div style={{ opacity: prog(t, 0.05, 0.5), transform: `translateY(${(1 - prog(t, 0.05, 0.6)) * 30}px)` }}>{mock(mw)}</div>
        {has && <CalloutList callouts={callouts} w={Math.min(560, avail - mw - 60)} />}
        {caption && <div style={{ position: 'absolute', bottom: 60, left: L.pad, right: L.pad, textAlign: 'center', fontSize: 32, fontWeight: 600, color: C.ink, opacity: prog(t, 0.8, 0.5) }}>{caption}</div>}
      </AbsoluteFill>
    );
  }
  const mw = Math.min(mockW, avail);
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: L.portrait ? 50 : 30, padding: `${(L.portrait ? 120 : 40) + padTop}px ${L.pad}px ${L.portrait ? 120 : 40}px` }}>
      {head}
      <div style={{ opacity: prog(t, 0.05, 0.5), transform: `translateY(${(1 - prog(t, 0.05, 0.6)) * 30}px)` }}>{mock(mw)}</div>
      {has && <CalloutList callouts={callouts} w={avail} />}
      {caption && <div style={{ textAlign: 'center', fontSize: 32, fontWeight: 600, color: C.ink, opacity: prog(t, 0.8, 0.5) }}>{caption}</div>}
    </AbsoluteFill>
  );
};

const WinDots: React.FC = () => {
  const { C } = useTheme();
  return <div style={{ display: 'flex', gap: 10, direction: 'ltr' }}>{[C.danger, C.attention2, C.safe].map((c) => <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c, opacity: 0.9 }} />)}</div>;
};

// ---------------------------------------------------------------- email
export const EmailMock: React.FC<{ email: { from: string; from_addr?: string; to?: string; subject: string; body: string[]; attachment?: string; button?: string; signature?: string[]; external?: boolean }; callouts?: Callout[] }> = ({ email, callouts = [] }) => {
  const { C, F, shadowLg } = useTheme();
  const L = useLayout();
  const tr = useT();
  const { ring, badge } = useHl(callouts);
  const initials = email.from.split(/\s+/).map((s) => Array.from(s.replace(/[^\p{L}\p{N}]/gu, ''))[0]).filter(Boolean).slice(0, 2).join('');
  const bodyFs = L.portrait ? 28 : 26;
  return (
    <MockStage mockW={1100} callouts={callouts} mock={(w) => (
      <div style={{ width: w, background: '#fff', borderRadius: 18, boxShadow: shadowLg, overflow: 'visible', fontFamily: F.sans, color: C.ink }}>
        <div style={{ height: 58, background: C.primary, display: 'flex', alignItems: 'center', padding: '0 22px', gap: 16, borderRadius: '18px 18px 0 0' }}>
          <WinDots /><div style={{ color: '#fff', fontSize: 24, fontWeight: 600, opacity: 0.9 }}>{tr('inbox')}</div>
        </div>
        {email.external && <div style={{ background: C.attentionSoft, color: C.ink, fontSize: 24, padding: '10px 28px', borderBottom: `1px solid ${C.hair}`, display: 'flex', gap: 10, alignItems: 'center' }}><Icon name="alert" size={26} color={C.attention} />{tr('external')}</div>}
        <div style={{ padding: '26px 34px 10px' }}>
          <div style={{ display: 'inline-block', padding: '2px 8px', ...ring('subject') }}>
            <span style={{ fontSize: fit(email.subject, 34, w - 90, 2, 26), fontWeight: 700 }}>{email.subject}</span>{badge('subject')}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginTop: 16 }}>
            <div style={{ flex: '0 0 auto', width: 58, height: 58, borderRadius: 29, background: C.accent, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, fontWeight: 700 }}>{initials}</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8 }}>
                <span style={{ fontSize: 26, fontWeight: 600, padding: '2px 6px', ...ring('from') }}>{email.from}{badge('from')}</span>
                {email.from_addr && <span style={{ fontFamily: F.mono, fontSize: 24, color: C.muted, padding: '2px 6px', direction: 'ltr', unicodeBidi: 'isolate', ...ring('addr') }}>&lt;{email.from_addr}&gt;{badge('addr')}</span>}
              </div>
              <div style={{ fontSize: 24, color: C.muted, paddingInlineStart: 6 } as React.CSSProperties}>{tr('to')}: <span style={{ direction: 'ltr', unicodeBidi: 'isolate' }}>{email.to ?? 'you@northwind.example'}</span></div>
            </div>
          </div>
        </div>
        <div style={{ padding: '14px 40px 30px', fontSize: bodyFs, lineHeight: 1.5 }}>
          {email.body.map((p, i) => (
            <div key={i} style={{ margin: '0 0 12px', padding: '2px 6px', display: 'table', ...ring(`b${i}`) }}>{p}{badge(`b${i}`)}</div>
          ))}
          {email.button && (
            <div style={{ margin: '8px 0 18px' }}>
              <span style={{ display: 'inline-block', position: 'relative', background: C.accent, color: '#fff', padding: '14px 30px', borderRadius: 10, fontWeight: 600, fontSize: 26, ...(ring('button', 10).boxShadow ? { boxShadow: ring('button', 10).boxShadow } : {}) }}>{email.button}{badge('button')}</span>
            </div>
          )}
          {email.attachment && (
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: 12, border: `2px solid ${C.hair}`, background: C.bg, borderRadius: 12, padding: '10px 18px', fontSize: 24, ...ring('attachment', 12) }}>
              <Icon name="file" size={30} color={C.muted} /> <span style={{ fontFamily: F.mono, direction: 'ltr' }}>{email.attachment}</span>{badge('attachment')}
            </div>
          )}
          {email.signature && <div style={{ marginTop: 18, fontSize: 24, color: C.muted, lineHeight: 1.4, padding: '2px 6px', display: 'table', ...ring('signature') }}>{email.signature.map((s, i) => <div key={i}>{s}</div>)}{badge('signature')}</div>}
        </div>
      </div>
    )} />
  );
};

// ---------------------------------------------------------------- chat
export const ChatMock: React.FC<{ device?: 'phone' | 'desktop'; title?: string; messages: { me?: boolean; text: string; warn?: boolean; cue?: number }[]; callouts?: Callout[] }> = ({ device = 'phone', title, messages, callouts = [] }) => {
  const { cue, hasCue } = useScene();
  const { C, F, shadowLg } = useTheme();
  const L = useLayout();
  const tr = useT();
  // messages without explicit cue appear on successive cues not used by callouts, else every 1.2 s
  const used = new Set(callouts.map((c) => c.cue));
  let k = 0;
  const times = messages.map((m, i) => {
    if (m.cue !== undefined) return cue(m.cue);
    while (used.has(k)) k++;
    const at = hasCue(k) ? cue(k) : 0.6 + i * 1.2;
    k++;
    return at;
  });
  const bubbles = (fs: number) => messages.map((m, i) => (
    <Appear key={i} at={times[i]} dy={16} style={{ display: 'flex', justifyContent: m.me ? 'flex-end' : 'flex-start', marginBottom: 14 }}>
      <div style={{ maxWidth: '82%', background: m.me ? C.accent : m.warn ? C.attentionSoft : '#fff', color: m.me ? '#fff' : C.ink, border: m.warn ? `2px solid ${C.attention}` : `1px solid ${C.hair}`, borderRadius: 22, padding: '14px 20px', fontSize: fs, lineHeight: 1.4 }}>{m.text}</div>
    </Appear>
  ));
  if (device === 'desktop') {
    return (
      <MockStage mockW={1050} callouts={callouts} mock={(w) => (
        <div style={{ width: w, height: L.portrait ? 1000 : 700, background: '#fff', borderRadius: 18, boxShadow: shadowLg, overflow: 'hidden', fontFamily: F.sans, display: 'flex', flexDirection: 'column' }}>
          <div style={{ height: 66, background: C.primary, color: '#fff', fontWeight: 600, fontSize: 26, display: 'flex', alignItems: 'center', padding: '0 24px', gap: 14 }}><Icon name="chat" size={30} color="#fff" />{title}</div>
          <div style={{ flex: 1, padding: 26, background: C.bg, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>{bubbles(26)}</div>
          <div style={{ height: 70, borderTop: `1px solid ${C.hair}`, display: 'flex', alignItems: 'center', padding: '0 24px', color: C.mist, fontSize: 24 }}>{tr('type_message')}</div>
        </div>
      )} />
    );
  }
  const pw = L.portrait ? 640 : L.square ? 420 : 470;
  return (
    <MockStage mockW={pw} callouts={callouts} mock={(w) => (
      <div style={{ width: w, height: w * (L.square ? 1.75 : 1.95), background: C.outline, borderRadius: w * 0.12, padding: w * 0.035, boxShadow: shadowLg }}>
        <div style={{ width: '100%', height: '100%', background: C.bg, borderRadius: w * 0.09, overflow: 'hidden', fontFamily: F.sans, display: 'flex', flexDirection: 'column' }}>
          <div style={{ height: 96, display: 'flex', alignItems: 'flex-end', justifyContent: 'center', paddingBottom: 14, fontSize: 26, fontWeight: 600, color: C.ink, borderBottom: `1px solid ${C.hair}`, background: '#fff' }}>{title}</div>
          <div style={{ flex: 1, padding: 20, display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>{bubbles(w > 500 ? 28 : 24)}</div>
        </div>
      </div>
    )} />
  );
};

// ---------------------------------------------------------------- browser
export const BrowserMock: React.FC<{ url: string; bad?: boolean; page?: 'login' | 'blank' | 'article' | 'checkout' | 'error'; brand?: string; heading?: string; lines?: string[]; callouts?: Callout[] }> = ({ url, bad, page = 'login', brand, heading, lines = [], callouts = [] }) => {
  const { t } = useScene();
  const { C, F, shadowLg, shadow } = useTheme();
  const L = useLayout();
  const tr = useT();
  const { ring, badge } = useHl(callouts);
  const h = L.portrait ? 1050 : L.square ? 640 : 720;
  const field = (label: string, val: string, at: number) => (
    <div style={{ marginBottom: 16 }}>
      <div style={{ fontSize: 22, color: C.muted, marginBottom: 6 }}>{label}</div>
      <div style={{ height: 54, border: `2px solid ${C.hair}`, borderRadius: 8, padding: '0 14px', display: 'flex', alignItems: 'center', fontSize: 24, direction: 'ltr' }}><Type text={val} at={at} /></div>
    </div>
  );
  return (
    <MockStage mockW={1150} callouts={callouts} mock={(w) => (
      <div style={{ width: w, height: h, background: '#fff', borderRadius: 16, boxShadow: shadowLg, overflow: 'hidden', fontFamily: F.sans, color: C.ink, display: 'flex', flexDirection: 'column' }}>
        <div style={{ height: 76, background: C.wall, display: 'flex', alignItems: 'center', gap: 14, padding: '0 20px', direction: 'ltr' }}>
          <WinDots />
          <div style={{ flex: 1, marginLeft: 10, height: 48, background: '#fff', borderRadius: 24, display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px', fontFamily: F.mono, fontSize: fit(url, 26, w - 220, 1, 22), color: bad ? C.danger : C.ink, whiteSpace: 'nowrap', overflow: 'visible', ...ring('url', 24) }}>
            <Icon name={bad ? 'alert' : 'lock'} size={22} color={bad ? C.danger : C.muted} />{url}{badge('url')}
          </div>
        </div>
        <div style={{ flex: 1, position: 'relative', background: page === 'login' || page === 'checkout' ? C.bg : '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 40 }}>
          {page === 'login' && (
            <div style={{ width: Math.min(520, w - 80), background: '#fff', borderRadius: 16, padding: 40, boxShadow: shadow, ...ring('form', 16) }}>
              {badge('form')}
              <div style={{ fontSize: 34, fontWeight: 700, color: C.accent, marginBottom: 24, ...ring('heading') }}>{brand ?? heading}{badge('heading')}</div>
              {field(tr('email'), 'alex@northwind.example', 0.8)}
              {field(tr('password'), '••••••••••', 2.0)}
              <div style={{ height: 58, background: C.accent, color: '#fff', borderRadius: 10, display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 600, fontSize: 26, marginTop: 10 }}>{tr('sign_in')}</div>
            </div>
          )}
          {page === 'checkout' && (
            <div style={{ width: Math.min(620, w - 80), background: '#fff', borderRadius: 16, padding: 40, boxShadow: shadow, ...ring('form', 16) }}>
              {badge('form')}
              <div style={{ fontSize: 34, fontWeight: 700, marginBottom: 22, ...ring('heading') }}>{heading ?? brand}{badge('heading')}</div>
              {field('Card', '•••• •••• •••• 4242', 0.8)}
              <div style={{ display: 'flex', gap: 16 }}><div style={{ flex: 1 }}>{field('MM/YY', '••/••', 1.6)}</div><div style={{ flex: 1 }}>{field('CVC', '•••', 2.0)}</div></div>
              {lines.map((l, i) => <div key={i} style={{ fontSize: 24, color: C.muted, lineHeight: 1.4, ...ring(i === 0 ? 'body' : `x${i}`) }}>{l}{i === 0 && badge('body')}</div>)}
            </div>
          )}
          {(page === 'article' || page === 'blank') && (
            <div style={{ position: 'absolute', inset: 40, display: 'flex', flexDirection: 'column', gap: 18 }}>
              {brand && <div style={{ fontSize: 28, fontWeight: 800, color: C.accent }}>{brand}</div>}
              {heading && <div style={{ fontSize: fit(heading, 46, w - 100, 2, 30), fontWeight: 700, lineHeight: 1.2, alignSelf: 'flex-start', ...ring('heading') }}>{heading}{badge('heading')}</div>}
              <div style={{ alignSelf: 'stretch', ...ring('body', 12), padding: 6 }}>
                {badge('body')}
                {lines.map((l, i) => <div key={i} style={{ fontSize: 27, lineHeight: 1.5, marginBottom: 12, opacity: prog(t, 0.5 + i * 0.2, 0.4) }}>{l}</div>)}
                {page === 'article' && !lines.length && [0.9, 0.75, 0.95, 0.6].map((f, i) => <div key={i} style={{ height: 22, width: `${f * 100}%`, background: C.hair, borderRadius: 6, marginBottom: 16 }} />)}
              </div>
            </div>
          )}
          {page === 'error' && (
            <div style={{ textAlign: 'center', ...ring('body', 16), padding: 30 }}>
              {badge('body')}
              <Icon name="alert" size={120} color={C.danger} />
              {heading && <div style={{ fontSize: fit(heading, 44, w - 140, 2, 30), fontWeight: 700, marginTop: 20, ...ring('heading') }}>{heading}{badge('heading')}</div>}
              {lines.map((l, i) => <div key={i} style={{ fontSize: 26, color: C.muted, marginTop: 10 }}>{l}</div>)}
            </div>
          )}
        </div>
      </div>
    )} />
  );
};

// ---------------------------------------------------------------- MFA prompt (fatigue counter)
export const MfaPrompt: React.FC<{ app?: string; place?: string; count_to?: number; caption?: string }> = ({ app = 'Northwind Sign-in', place = 'Unknown location', count_to = 1, caption }) => {
  const { t, cue, hasCue, dur } = useScene();
  const { C, F, shadowLg } = useTheme();
  const L = useLayout();
  const tr = useT();
  const a = hasCue(0) ? cue(0) : 0.6;
  const b = hasCue(1) ? cue(1) : Math.max(a + 1, dur * 0.75);
  const n = count_to > 1 ? Math.max(1, Math.min(count_to, 1 + Math.floor(((t - a) / Math.max(0.5, b - a)) * (count_to - 1)))) : 1;
  const shake = count_to > 2 && t > a ? Math.sin(t * 40) * 4 * (1 - prog(t, a + ((n - 1) * (b - a)) / Math.max(1, count_to - 1), 0.3)) : 0;
  const pw = L.portrait ? 640 : 460;
  return (
    <MockStage mockW={pw} caption={caption} mock={(w) => (
      <div style={{ width: w, height: w * 1.95, background: C.outline, borderRadius: w * 0.12, padding: w * 0.035, boxShadow: shadowLg }}>
        <div style={{ width: '100%', height: '100%', background: `linear-gradient(180deg, ${C.primary}, ${C.primaryDeep})`, borderRadius: w * 0.09, overflow: 'hidden', fontFamily: F.sans, display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
          <div style={{ position: 'absolute', top: 60, color: '#fff', fontSize: w * 0.16, fontWeight: 300, fontFamily: F.latin, opacity: 0.9 }}>09:41</div>
          {t >= a && Array.from({ length: Math.min(n, 3) }).map((_, i) => (
            <div key={i} style={{ position: 'absolute', width: w * 0.82, transform: `translate(${shake}px, ${(Math.min(n, 3) - 1 - i) * -18}px) scale(${1 - (Math.min(n, 3) - 1 - i) * 0.05})`, opacity: i === Math.min(n, 3) - 1 ? 1 : 0.7 }}>
              <Appear at={a} scale>
                <div style={{ background: '#fff', borderRadius: 26, padding: 30, color: C.ink, textAlign: 'center', position: 'relative', boxShadow: '0 20px 50px rgba(0,0,0,0.3)' }}>
                  {n > 1 && i === Math.min(n, 3) - 1 && <div style={{ position: 'absolute', top: -20, insetInlineEnd: -20, width: 60, height: 60, borderRadius: 30, background: C.danger, color: '#fff', fontWeight: 700, fontSize: 28, display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: F.latin } as React.CSSProperties}>{n}</div>}
                  <Icon name="key" size={52} color={C.accent} />
                  <div style={{ fontSize: 30, fontWeight: 700, margin: '12px 0 8px' }}>{tr('approve_q')}</div>
                  <div style={{ fontSize: 24, color: C.muted }}>{app}</div>
                  <div style={{ fontSize: 24, color: C.muted, marginBottom: 22 }}>{place}</div>
                  <div style={{ display: 'flex', gap: 14 }}>
                    <div style={{ flex: 1, padding: '14px 0', borderRadius: 14, border: `2px solid ${C.hair}`, fontWeight: 600, fontSize: 26 }}>{tr('deny')}</div>
                    <div style={{ flex: 1, padding: '14px 0', borderRadius: 14, background: C.accent, color: '#fff', fontWeight: 600, fontSize: 26 }}>{tr('approve')}</div>
                  </div>
                </div>
              </Appear>
            </div>
          ))}
        </div>
      </div>
    )} />
  );
};

// ---------------------------------------------------------------- popup
export const Popup: React.FC<{ title: string; body: string; cta?: string; tone?: 'warn' | 'bad' | 'info'; icon?: string }> = ({ title, body, cta, tone = 'warn', icon = 'alert' }) => {
  const { t, cue, hasCue } = useScene();
  const { C, F, shadowLg } = useTheme();
  const L = useLayout();
  const col = tone === 'bad' ? C.danger : tone === 'warn' ? C.attention : C.accent;
  const fg = onFill(C, col);
  const at = hasCue(0) ? cue(0) : 0.5;
  const ww = L.W - L.pad * (L.landscape ? 2.4 : 1.2), wh = L.portrait ? 1300 : L.H - 200;
  const pw = Math.min(L.portrait ? L.W - L.pad * 2 : 760, ww - 60);
  const pulse = cta ? 1 + 0.04 * Math.sin(t * 6) * prog(t, at + 1, 0.4) : 1;
  return (
    <AbsoluteFill style={{ background: C.bg, fontFamily: F.sans, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: ww, height: wh, background: '#fff', borderRadius: 18, boxShadow: shadowLg, overflow: 'hidden', position: 'relative', opacity: prog(t, 0, 0.4) }}>
        <div style={{ height: 64, background: C.wall, display: 'flex', alignItems: 'center', padding: '0 22px' }}><WinDots /></div>
        <div style={{ padding: 40, display: 'flex', flexDirection: 'column', gap: 18, filter: `blur(${3 * prog(t, at, 0.4)}px)` }}>
          {[0.5, 0.9, 0.8, 0.95, 0.6, 0.85, 0.7].map((f, i) => <div key={i} style={{ height: i === 0 ? 40 : 22, width: `${f * 100}%`, background: i === 0 ? C.mist : C.hair, borderRadius: 6 }} />)}
        </div>
        <div style={{ position: 'absolute', inset: 0, background: alpha(C.primaryDeep, 0.35 * prog(t, at, 0.4)) }} />
        <div style={{ position: 'absolute', left: 0, right: 0, top: 0, bottom: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Appear at={at} scale>
            <div style={{ width: pw, background: '#fff', borderRadius: 18, overflow: 'hidden', boxShadow: shadowLg, color: C.ink }}>
              <div style={{ background: col, color: fg, padding: '18px 26px', fontWeight: 700, fontSize: fit(title, 32, pw - 120, 2, 26), display: 'flex', alignItems: 'center', gap: 14 }}><Icon name={icon} size={36} color={fg} />{title}</div>
              <div style={{ padding: '26px 30px', fontSize: fit(body, 28, pw - 60, 5, 24), lineHeight: 1.45 }}>{body}</div>
              {cta && <div style={{ padding: '0 30px 28px' }}><span style={{ display: 'inline-block', background: col, color: fg, borderRadius: 12, padding: '14px 30px', fontWeight: 700, fontSize: 26, transform: `scale(${pulse})` }}>{cta}</span></div>}
            </div>
          </Appear>
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- code
export const CodeMock: React.FC<{ title?: string; filename?: string; lines: string[]; highlight?: { cue: number; line: number; tone?: string; label?: string }[] }> = ({ title, filename, lines, highlight = [] }) => {
  const { t, cue } = useScene();
  const { C, F, shadowLg } = useTheme();
  const L = useLayout();
  const hlFor = (n: number) => highlight.map((h, i) => ({ ...h, i })).filter((h) => h.line === n && t >= cue(h.cue)).pop();
  const labelled = highlight.filter((h) => h.label).map((h) => ({ cue: h.cue, label: h.label!, tone: h.tone }));
  const fs = lines.length > 16 ? 22 : lines.length > 11 ? 24 : 27;
  return (
    <>
        <MockStage mockW={1150} callouts={labelled} title={title} mock={(w) => (
          <div style={{ width: w, background: '#1B2036', borderRadius: 16, boxShadow: shadowLg, overflow: 'hidden', direction: 'ltr', textAlign: 'left' }}>
            <div style={{ height: 58, background: '#141829', display: 'flex', alignItems: 'center', gap: 16, padding: '0 20px' }}>
              <WinDots /><span style={{ fontFamily: F.mono, color: '#AEB9CC', fontSize: 22 }}>{filename}</span>
            </div>
            <div style={{ padding: '20px 0' }}>
              {lines.map((ln, i) => {
                const h = hlFor(i + 1);
                const col = h ? toneColor(C, h.tone ?? 'warn') : undefined;
                return (
                  <div key={i} style={{ display: 'flex', fontFamily: F.mono, fontSize: fs, lineHeight: 1.6, background: col ? alpha(col, lerp(0, 0.22, prog(t, cue(h!.cue), 0.3))) : undefined, boxShadow: col ? `inset 0 0 0 2px ${alpha(col, 0.7)}` : undefined, opacity: prog(t, 0.2 + i * 0.05, 0.3) }}>
                    <span style={{ width: 64, flex: '0 0 auto', textAlign: 'right', paddingRight: 18, color: '#5D6B8A' }}>{i + 1}</span>
                    <span style={{ color: '#E6ECF5', whiteSpace: 'pre' }}>{ln}</span>
                    {h?.label && <span style={{ marginLeft: 'auto', marginRight: 16 }}><NumBadge n={labelled.findIndex((x) => x.label === h.label) + 1} color={col!} size={34} /></span>}
                  </div>
                );
              })}
            </div>
          </div>
        )} />
    </>
  );
};
const MockStageInner: React.FC<{ title: boolean; children: React.ReactNode }> = ({ title, children }) => {
  const L = useLayout();
  return <AbsoluteFill style={{ top: title ? (L.portrait ? 120 : 90) : 0 }}>{children}</AbsoluteFill>;
};
