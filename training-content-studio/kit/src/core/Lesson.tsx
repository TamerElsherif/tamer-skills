// The lesson composition: sequences every scene from the timeline through the template dispatcher,
// plays narration lines, music (ducked under speech) and sfx, and draws a thin progress bar.
import React, { useMemo } from 'react';
import { AbsoluteFill, Audio, Img, Sequence, staticFile, useCurrentFrame, interpolate } from 'remotion';
import { SceneCtx, makeApi, LayoutProvider, makeLayout } from './ctx';
import { ThemeProvider, makeTheme } from './theme';
import { TimelineCtx } from './timelineCtx';
import { SceneRow, Timeline } from './types';
import { TEMPLATES } from '../templates/registry';

const Missing: React.FC<{ id: string; template: string }> = ({ id, template }) => (
  <AbsoluteFill style={{ background: '#E0453A', color: '#fff', fontSize: 48, alignItems: 'center', justifyContent: 'center', fontFamily: 'sans-serif', textAlign: 'center' }}>
    unknown template “{template}” in scene {id}
  </AbsoluteFill>
);

class Boundary extends React.Component<{ id: string; children: React.ReactNode }, { err?: string }> {
  state: { err?: string } = {};
  static getDerivedStateFromError(e: Error) { return { err: String(e?.message ?? e) }; }
  render() {
    if (this.state.err) {
      return (
        <AbsoluteFill style={{ background: '#2B2F45', color: '#fff', fontSize: 34, padding: 80, fontFamily: 'monospace' }}>
          scene {this.props.id} failed: {this.state.err}
        </AbsoluteFill>
      );
    }
    return this.props.children;
  }
}

const SceneHost: React.FC<{ row: SceneRow; fps: number; fadeIn: boolean; fadeOut: boolean; slide: boolean; rtl: boolean }> = ({ row, fps, fadeIn, fadeOut, slide, rtl }) => {
  const f = useCurrentFrame();
  const api = makeApi(row, f, fps);
  const Comp = TEMPLATES[row.template];
  const fin = fadeIn ? 7 : 0.001, fout = fadeOut ? 7 : 0.001;
  const op = interpolate(f, [0, fin, row.frames - fout, row.frames], [fadeIn ? 0 : 1, 1, 1, fadeOut ? 0 : 1], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const sx = slide ? interpolate(f, [0, 10], [rtl ? -80 : 80, 0], { extrapolateRight: 'clamp' }) : 0;
  return (
    <SceneCtx.Provider value={api}>
      <AbsoluteFill style={{ opacity: op, transform: sx ? `translateX(${sx}px)` : undefined }}>
        <Boundary id={row.id}>{Comp ? <Comp {...row.props} /> : <Missing id={row.id} template={row.template} />}</Boundary>
      </AbsoluteFill>
      {row.lines.map((l, i) => l.src ? (
        <Sequence key={i} from={Math.round(l.at * fps)} layout="none">
          <Audio src={staticFile(l.src)} />
        </Sequence>
      ) : null)}
    </SceneCtx.Provider>
  );
};

export const Lesson: React.FC<{ tl: Timeline }> = ({ tl }) => {
  const frame = useCurrentFrame();
  const fps = tl.fps || 30;
  const layout = useMemo(() => makeLayout(tl), [tl]);
  const theme = useMemo(() => makeTheme(tl.theme, tl.direction === 'rtl'), [tl]);
  const speech = useMemo(() => {
    const iv: [number, number][] = [];
    for (const s of tl.scenes) for (const l of s.lines) iv.push([s.from + l.at * fps, s.from + (l.at + l.dur) * fps]);
    return iv;
  }, [tl, fps]);
  const musicVol = (f: number) => {
    let d = 1e9;
    for (const [a, b] of speech) {
      if (f >= a && f <= b) { d = 0; break; }
      d = Math.min(d, f < a ? a - f : f - b);
    }
    const duck = interpolate(d, [0, 12], [0.32, 1], { extrapolateRight: 'clamp' });
    const fadeIn = interpolate(f, [0, 20], [0, 1], { extrapolateRight: 'clamp' });
    const fadeOut = interpolate(f, [tl.total - 60, tl.total], [1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
    return (tl.music?.vol ?? 0.12) * duck * fadeIn * fadeOut;
  };
  const { C, F, grad } = theme;
  return (
    <TimelineCtx.Provider value={tl}>
      <ThemeProvider theme={theme}>
        <LayoutProvider value={layout}>
          <AbsoluteFill dir={tl.direction} style={{ background: C.bg, fontFamily: F.sans, color: C.ink, direction: tl.direction }}>
            {tl.scenes.map((row, i) => {
              const tr = row.transition ?? 'fade';
              const next = tl.scenes[i + 1]?.transition ?? 'fade';
              return (
                <Sequence key={row.id + i} from={row.from} durationInFrames={row.frames}>
                  <SceneHost row={row} fps={fps} fadeIn={i > 0 && tr === 'fade'} fadeOut={i < tl.scenes.length - 1 && next === 'fade'} slide={tr === 'slide'} rtl={layout.rtl} />
                </Sequence>
              );
            })}
            {tl.music?.src && <Audio src={staticFile(tl.music.src)} loop volume={musicVol} />}
            {(tl.sfx ?? []).map((s, i) => (
              <Sequence key={`sfx${i}`} from={Math.round(s.at * fps)} layout="none">
                <Audio src={staticFile(s.src)} volume={s.vol ?? 0.35} />
              </Sequence>
            ))}
            {theme.logo && (
              <Img src={staticFile(theme.logo)} style={{ position: 'absolute', top: 36, insetInlineEnd: 40, height: 56, objectFit: 'contain', opacity: 0.9 } as React.CSSProperties} />
            )}
            {tl.progress_bar !== false && (
              <div style={{ position: 'absolute', left: 0, right: 0, bottom: 0, height: 6, background: 'rgba(191,206,221,0.35)', direction: 'ltr' }}>
                <div style={{ height: 6, width: `${(frame / Math.max(1, tl.total)) * 100}%`, background: grad, marginLeft: layout.rtl ? 'auto' : 0 }} />
              </div>
            )}
          </AbsoluteFill>
        </LayoutProvider>
      </ThemeProvider>
    </TimelineCtx.Provider>
  );
};
