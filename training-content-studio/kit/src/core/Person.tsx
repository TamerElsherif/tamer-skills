// Flat cartoon person (adapted from the uSecure engine) — front view, thick navy outlines, pose-able arms, blinking eyes,
// amplitude-driven talking mouth. Coordinates: origin at the feet centre, figure ≈ 540 units tall.
import React from 'react';
import { useCurrentFrame } from 'remotion';
import { useScene } from './ctx';
import { lookFor, Look, ALIASES } from './cast';

// Outline colour is fixed navy-ink so characters read the same in every theme.
const C = { navyInk: '#1E2448', navyDeep: '#232957', cyan: '#6FC7DA', mist: '#BFCEDD', orange: '#FF6700', blue: '#006AB3' };

export type Expr = 'neutral' | 'happy' | 'worried' | 'shocked' | 'sly' | 'angry' | 'sad' | 'think';
export type Pose =
  | 'idle' | 'wave' | 'point' | 'pointUp' | 'shrug' | 'phone' | 'think' | 'cheer' | 'facepalm'
  | 'type' | 'present' | 'stop' | 'hold' | 'armsOut' | 'handsHips' | 'rub' | 'cross';

const OL = C.navyInk;
const OW = 7; // outline width

// Arm angles in degrees: [upper, fore] absolute from "straight down", positive = outward.
const POSES: Record<Pose, { r: [number, number]; l: [number, number] }> = {
  idle: { r: [10, 5], l: [10, 5] },
  wave: { r: [120, 165], l: [10, 5] },
  point: { r: [80, 95], l: [10, 5] },
  pointUp: { r: [60, 170], l: [10, 5] },
  shrug: { r: [55, 120], l: [55, 120] },
  phone: { r: [120, -107], l: [10, 5] },
  think: { r: [100, -93], l: [25, -80] },
  cheer: { r: [150, 170], l: [150, 170] },
  facepalm: { r: [140, -74], l: [10, 5] },
  type: { r: [20, -55], l: [20, -55] },
  present: { r: [70, 110], l: [10, 5] },
  stop: { r: [70, 150], l: [10, 5] },
  hold: { r: [15, -75], l: [15, -75] },
  armsOut: { r: [100, 100], l: [100, 100] },
  handsHips: { r: [40, -40], l: [40, -40] },
  rub: { r: [20, -70], l: [20, -70] },
  cross: { r: [25, -85], l: [25, -95] },
};

const rad = (d: number) => (d * Math.PI) / 180;
const limb = (sx: number, sy: number, side: 1 | -1, a1: number, a2: number, L1 = 92, L2 = 86) => {
  const ex = sx + side * L1 * Math.sin(rad(a1));
  const ey = sy + L1 * Math.cos(rad(a1));
  const hx = ex + side * L2 * Math.sin(rad(a2));
  const hy = ey + L2 * Math.cos(rad(a2));
  return { ex, ey, hx, hy };
};

const Stroke: React.FC<{ d: string; color: string; w: number }> = ({ d, color, w }) => (
  <>
    <path d={d} stroke={OL} strokeWidth={w + OW * 2} strokeLinecap="round" strokeLinejoin="round" fill="none" />
    <path d={d} stroke={color} strokeWidth={w} strokeLinecap="round" strokeLinejoin="round" fill="none" />
  </>
);

const Arm: React.FC<{ look: Look; side: 1 | -1; a: [number, number]; wob: number; holding?: React.ReactNode }> = ({ look, side, a, wob, holding }) => {
  const sx = side * 66, sy = -350;
  const { ex, ey, hx, hy } = limb(sx, sy, side, a[0] + wob, a[1] + wob * 1.4);
  const sleeve = look.jacket ?? look.shirt;
  const short = look.shortSleeves && !look.jacket;
  const cap = { strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const, fill: 'none' };
  return (
    <g>
      <path d={`M${sx},${sy} L${ex},${ey}`} stroke={OL} strokeWidth={34 + OW * 2} {...cap} />
      <path d={`M${ex},${ey} L${hx},${hy}`} stroke={OL} strokeWidth={(short ? 24 : 30) + OW * 2} {...cap} />
      <path d={`M${ex},${ey} L${hx},${hy}`} stroke={short ? look.skin : sleeve} strokeWidth={short ? 24 : 30} {...cap} />
      <path d={`M${sx},${sy} L${ex},${ey}`} stroke={sleeve} strokeWidth={34} {...cap} />
      <circle cx={hx} cy={hy} r={19} fill={look.skin} stroke={OL} strokeWidth={OW - 1} />
      {holding && <g transform={`translate(${hx},${hy})`}>{holding}</g>}
    </g>
  );
};

const Hair: React.FC<{ look: Look; layer: 'back' | 'front' }> = ({ look, layer }) => {
  const c = look.hair;
  const s = { fill: c, stroke: OL, strokeWidth: OW - 1, strokeLinejoin: 'round' as const };
  switch (look.hairStyle) {
    case 'long':
      return layer === 'back' ? <path d="M-66,-440 Q-74,-360 -62,-322 L62,-322 Q74,-360 66,-440 Q60,-505 0,-506 Q-60,-505 -66,-440Z" {...s} /> :
        <path d="M-60,-452 Q-58,-500 0,-502 Q58,-500 62,-452 Q30,-478 -6,-470 Q-34,-462 -60,-452Z" {...s} />;
    case 'bun':
      return layer === 'back' ? <circle cx={0} cy={-510} r={30} {...s} /> :
        <path d="M-60,-446 Q-56,-500 0,-500 Q56,-500 60,-446 Q40,-470 0,-472 Q-40,-470 -60,-446Z" {...s} />;
    case 'ponytail':
      return layer === 'back' ? <path d="M40,-470 Q100,-470 92,-380 Q86,-340 70,-330 Q78,-380 52,-430Z" {...s} /> :
        <path d="M-60,-444 Q-58,-502 2,-502 Q60,-500 60,-446 Q30,-474 -8,-468 Q-40,-462 -60,-444Z" {...s} />;
    case 'curly':
      return layer === 'back' ? (
        <g>{[[-58, -470], [-40, -500], [-10, -512], [22, -508], [50, -488], [62, -455], [-66, -438], [66, -425], [-64, -405], [64, -395]].map(([x, y], i) => <circle key={i} cx={x} cy={y} r={26} {...s} />)}</g>
      ) : <path d="M-54,-458 Q-30,-486 0,-470 Q30,-490 56,-458 Q30,-472 0,-462 Q-30,-474 -54,-458Z" fill={c} />;
    case 'side':
      return layer === 'back' ? null : <path d="M-60,-438 Q-64,-500 -4,-506 Q58,-504 62,-446 Q54,-474 20,-480 Q-20,-484 -44,-462 Q-54,-452 -60,-438Z" {...s} />;
    case 'buzz':
      return layer === 'back' ? null : <path d="M-58,-446 Q-54,-500 0,-500 Q54,-500 58,-446 Q40,-468 0,-470 Q-40,-468 -58,-446Z" {...s} />;
    case 'slick':
      return layer === 'back' ? null : <path d="M-60,-440 Q-66,-506 6,-508 Q70,-500 62,-440 Q56,-470 30,-478 Q64,-486 20,-492 Q-30,-492 -52,-466 Q-58,-456 -60,-440Z" {...s} />;
    case 'bald':
      return layer === 'back' ? null : (
        <g>
          <path d="M-60,-420 Q-66,-446 -56,-462 L-50,-420Z" {...s} />
          <path d="M60,-420 Q66,-446 56,-462 L50,-420Z" {...s} />
        </g>
      );
    case 'hijab':
      return layer === 'back' ? (
        <path d="M-80,-440 Q-82,-520 0,-522 Q82,-520 80,-440 Q84,-380 92,-346 Q40,-330 0,-330 Q-40,-330 -92,-346 Q-84,-380 -80,-440Z" {...s} />
      ) : (
        <path fillRule="evenodd" d="M-76,-436 Q-76,-514 0,-516 Q76,-514 76,-436 Q76,-372 40,-352 L-40,-352 Q-76,-372 -76,-436Z M-50,-436 Q-50,-486 0,-488 Q50,-486 50,-436 Q50,-378 0,-366 Q-50,-378 -50,-436Z" {...s} />
      );
    case 'short':
    default:
      return layer === 'back' ? null : <path d="M-60,-440 Q-62,-504 0,-506 Q62,-504 60,-440 Q52,-470 26,-474 Q0,-488 -26,-476 Q-50,-470 -60,-440Z" {...s} />;
  }
};

const Face: React.FC<{ look: Look; expr: Expr; amp: number; blink: number; gaze: number }> = ({ look, expr, amp, blink, gaze }) => {
  const eyeY = -432, ex = 22;
  const big = expr === 'shocked' ? 1.25 : 1;
  const lid = expr === 'sly' ? 0.45 : expr === 'sad' ? 0.3 : 0;
  const open = Math.max(0.08, 1 - blink);
  const pr = expr === 'shocked' ? 4.5 : 6.5;
  const browY = expr === 'shocked' ? -466 : expr === 'happy' ? -462 : -458;
  const brow = (side: 1 | -1) => {
    // positive tilt = inner end lower (angry); negative = inner end higher (worried)
    const tilt = { neutral: 0, happy: -2, worried: -14, shocked: -4, sly: side === 1 ? -10 : 12, angry: 16, sad: -12, think: side === 1 ? -12 : 4 }[expr];
    const x0 = side * 10, x1 = side * 36;
    return <path d={`M${x0},${browY + tilt * 0.5} L${x1},${browY - tilt * 0.5}`} stroke={OL} strokeWidth={6.5} strokeLinecap="round" />;
  };
  // mouth
  const mo = Math.min(1, amp * 1.3);
  const my = -392;
  let mouth: React.ReactNode;
  if (mo > 0.12 || expr === 'shocked') {
    const ry = expr === 'shocked' ? Math.max(12, 16 * mo) : 4 + 15 * mo;
    const rx = expr === 'shocked' ? 12 : 17 - 3 * mo;
    mouth = (
      <g>
        <ellipse cx={0} cy={my} rx={rx} ry={ry} fill="#5A1F2B" stroke={OL} strokeWidth={4} />
        <ellipse cx={0} cy={my + ry * 0.45} rx={rx * 0.6} ry={ry * 0.35} fill="#E0707A" />
      </g>
    );
  } else {
    const d = {
      neutral: `M-14,${my} Q0,${my + 4} 14,${my}`,
      happy: `M-20,${my - 4} Q0,${my + 16} 20,${my - 4}`,
      worried: `M-16,${my + 4} Q-8,${my - 3} 0,${my + 2} Q8,${my + 6} 16,${my}`,
      sly: `M-16,${my + 2} Q4,${my + 8} 20,${my - 8}`,
      angry: `M-16,${my + 5} Q0,${my - 5} 16,${my + 5}`,
      sad: `M-16,${my + 7} Q0,${my - 6} 16,${my + 7}`,
      think: `M-10,${my + 2} L12,${my - 1}`,
      shocked: '',
    }[expr];
    mouth = <path d={d} stroke={OL} strokeWidth={5.5} strokeLinecap="round" fill={expr === 'happy' ? '#fff' : 'none'} />;
  }
  const eye = (side: 1 | -1) => (
    <g transform={`translate(${side * ex},${eyeY}) scale(${big},${big * open})`}>
      <ellipse cx={0} cy={0} rx={12} ry={14} fill="#fff" stroke={OL} strokeWidth={3.5} />
      <circle cx={gaze * 4} cy={1} r={pr} fill={OL} />
      <circle cx={gaze * 4 + 2} cy={-2} r={1.8} fill="#fff" />
      {lid > 0 && <path d={`M-13,-14 L13,-14 L13,${-14 + 28 * lid} Q0,${-12 + 28 * lid} -13,${-14 + 28 * lid}Z`} fill={look.skin} stroke={OL} strokeWidth={3} />}
    </g>
  );
  return (
    <g>
      {eye(-1)}
      {eye(1)}
      {look.glasses && (
        <g fill="none" stroke={OL} strokeWidth={4.5}>
          <circle cx={-ex} cy={eyeY} r={20} />
          <circle cx={ex} cy={eyeY} r={20} />
          <path d={`M${-ex + 20},${eyeY} L${ex - 20},${eyeY}`} />
        </g>
      )}
      {brow(-1)}
      {brow(1)}
      <path d="M-2,-420 Q6,-408 -4,-404" stroke={OL} strokeWidth={4} fill="none" strokeLinecap="round" />
      {look.beard && <path d="M-50,-420 Q-48,-360 0,-352 Q48,-360 50,-420 Q40,-386 0,-380 Q-40,-386 -50,-420Z" fill={look.hair} stroke={OL} strokeWidth={4} />}
      {look.goatee && <path d="M-12,-378 Q0,-352 12,-378 Q0,-372 -12,-378Z" fill={look.hair} stroke={OL} strokeWidth={4} />}
      {(look.mustache || look.beard) && <path d="M-26,-400 Q-12,-412 0,-404 Q12,-412 26,-400 Q14,-398 0,-399 Q-14,-398 -26,-400Z" fill={look.hair} stroke={OL} strokeWidth={4} />}
      {mouth}
      {(expr === 'worried' || expr === 'shocked') && <path d="M58,-470 q6,10 0,16 q-6,-6 0,-16Z" fill="#9FD3F0" stroke={OL} strokeWidth={2.5} />}
      {look.blush && <><ellipse cx={-38} cy={-404} rx={9} ry={5} fill="#F2A7A0" opacity={0.6} /><ellipse cx={38} cy={-404} rx={9} ry={5} fill="#F2A7A0" opacity={0.6} /></>}
    </g>
  );
};

export type PersonProps = {
  cast: string;
  x: number;
  y: number;
  s?: number;
  pose?: Pose;
  expr?: Expr;
  who?: string; // speaker id for mouth sync (defaults to cast)
  gaze?: number; // -1 left … 1 right
  flip?: boolean;
  walk?: boolean; // swing legs
  bob?: number; // extra vertical bob amplitude
  lean?: number; // degrees
  holding?: React.ReactNode; // drawn at the right hand
  holdingL?: React.ReactNode;
  lowerHidden?: boolean; // skip legs (behind a desk)
  opacity?: number;
  ink?: boolean; // whiteboard line-art: white fills, navy marker outlines
  reveal?: number; // 0..1 top-to-bottom "being drawn" wipe (whiteboard); omit for fully visible
};

export const Person: React.FC<PersonProps> = ({ cast, x, y, s = 1, pose = 'idle', expr = 'neutral', who, gaze = 0, flip, walk, bob = 0, lean = 0, holding, holdingL, lowerHidden, opacity = 1, ink, reveal }) => {
  const frame = useCurrentFrame();
  const sc = useScene();
  const base = lookFor(cast);
  const look: Look = ink
    ? { ...base, skin: '#FFFFFF', hair: base.hairStyle === 'bald' ? '#FFFFFF' : '#E9EEF5', shirt: '#FFFFFF', jacket: base.jacket ? '#F4F7FB' : undefined, tie: base.tie ? '#FFFFFF' : undefined, pants: '#FFFFFF', shoes: '#DDE3EC', lanyard: base.lanyard ? '#FFFFFF' : undefined, blush: false }
    : base;
  const clipId = `rv-${cast}-${Math.round(x)}-${Math.round(y)}`;
  const id = who ?? cast;
  const amp = sc.amp(id);
  const talking = sc.speaking(id);
  // deterministic blink: every ~3.3s with per-character offset
  const seed = [...cast].reduce((a, ch) => a + ch.charCodeAt(0), 0);
  const cyc = (frame + seed * 7) % 100;
  const blink = cyc < 3 ? 1 - Math.abs(cyc - 1.5) / 1.5 : 0;
  const breathe = Math.sin((frame + seed) / 22) * 2.2;
  const wob = talking ? Math.sin(frame / 5 + seed) * 4 : Math.sin((frame + seed) / 30) * 1.5;
  const headTilt = talking ? Math.sin(frame / 9 + seed) * 3 : 0;
  const walkPh = walk ? Math.sin(frame / 4) : 0;
  const by = walk ? -Math.abs(Math.cos(frame / 4)) * 8 : Math.sin((frame + seed) / 18) * bob;
  const P = POSES[pose];
  const body = look.jacket ?? look.shirt;
  return (
    <g clipPath={reveal !== undefined && reveal < 1 ? `url(#${clipId})` : undefined}>
    {reveal !== undefined && reveal < 1 && (
      <defs><clipPath id={clipId}><rect x={x - 400 * s} y={y - 600 * s} width={800 * s} height={640 * s * Math.max(0, reveal)} /></clipPath></defs>
    )}
    {ALIASES[cast]?.glitch && frame % 9 < 3 && (
      <g opacity={0.55}>
        {[0, 1, 2].map((k) => <rect key={k} x={x - 120 * s + ((frame * 37 + k * 53) % 40) - 20} y={y - (120 + ((frame * 13 + k * 97) % 380)) * s} width={240 * s} height={(6 + k * 4) * s} fill={k % 2 ? '#6FC7DA' : '#FF6700'} />)}
      </g>
    )}
    <g transform={`translate(${x + (ALIASES[cast]?.glitch && frame % 9 < 2 ? (frame % 2 ? 6 : -6) : 0)},${y + by}) scale(${flip ? -s : s},${s}) rotate(${lean})`} opacity={opacity}>
      {/* legs */}
      {!lowerHidden && (
        <g>
          <g transform={`rotate(${walkPh * 16},-26,-200)`}>
            <Stroke d="M-28,-200 L-30,-30" color={look.pants} w={44} />
            <ellipse cx={-36} cy={-16} rx={34} ry={17} fill={look.shoes} stroke={OL} strokeWidth={OW - 1} />
          </g>
          <g transform={`rotate(${-walkPh * 16},26,-200)`}>
            <Stroke d="M28,-200 L30,-30" color={look.pants} w={44} />
            <ellipse cx={36} cy={-16} rx={34} ry={17} fill={look.shoes} stroke={OL} strokeWidth={OW - 1} />
          </g>
        </g>
      )}
      <g transform={`translate(0,${breathe * 0.5})`}>
        <Hair look={look} layer="back" />
        {/* back arm drawn first when crossing */}
        <Arm look={look} side={-1} a={P.l} wob={-wob} holding={holdingL} />
        {/* torso */}
        <path d={look.skirt ? 'M-66,-362 Q-80,-250 -74,-196 L74,-196 Q80,-250 66,-362 Q0,-380 -66,-362Z' : 'M-66,-362 Q-76,-260 -64,-192 L64,-192 Q76,-260 66,-362 Q0,-380 -66,-362Z'}
          fill={body} stroke={OL} strokeWidth={OW} strokeLinejoin="round" />
        {look.jacket && (
          <g>
            <path d="M-22,-366 L0,-300 L22,-366 Z" fill={look.shirt} stroke={OL} strokeWidth={4} />
            <path d="M-22,-366 L-8,-318 L-30,-300Z M22,-366 L8,-318 L30,-300Z" fill={look.jacket} stroke={OL} strokeWidth={4} strokeLinejoin="round" />
            <path d="M0,-300 L0,-196" stroke={OL} strokeWidth={3} />
          </g>
        )}
        {!look.jacket && <path d="M-24,-368 L0,-346 L24,-368" fill="none" stroke={OL} strokeWidth={4} strokeLinejoin="round" />}
        {look.tie && <path d="M0,-352 L-10,-340 L-4,-262 L0,-250 L4,-262 L10,-340Z" fill={look.tie} stroke={OL} strokeWidth={3.5} strokeLinejoin="round" />}
        {look.lanyard && (
          <g>
            <path d="M-26,-364 L-6,-290 M26,-364 L6,-290" stroke={look.lanyard} strokeWidth={6} />
            <rect x={-18} y={-292} width={36} height={46} rx={6} fill="#fff" stroke={OL} strokeWidth={4} />
            <rect x={-10} y={-282} width={20} height={14} rx={3} fill={look.lanyard} />
          </g>
        )}
        <path d="M-64,-200 L64,-200" stroke={OL} strokeWidth={0} />
        {/* neck + head */}
        <g transform={`rotate(${headTilt},0,-360)`}>
          <rect x={-17} y={-384} width={34} height={30} fill={look.skin} stroke={OL} strokeWidth={OW - 2} />
          <ellipse cx={-58} cy={-424} rx={11} ry={15} fill={look.skin} stroke={OL} strokeWidth={OW - 2} />
          <ellipse cx={58} cy={-424} rx={11} ry={15} fill={look.skin} stroke={OL} strokeWidth={OW - 2} />
          <ellipse cx={0} cy={-432} rx={58} ry={66} fill={look.skin} stroke={OL} strokeWidth={OW} />
          <Hair look={look} layer="front" />
          <Face look={look} expr={expr} amp={amp} blink={blink} gaze={flip ? -gaze : gaze} />
          {look.headset && (
            <g fill="none" stroke={OL} strokeWidth={6} strokeLinecap="round">
              <path d="M-62,-430 Q-66,-512 0,-514 Q66,-512 62,-430" />
              <rect x={-74} y={-448} width={18} height={36} rx={8} fill="#56627F" />
              <rect x={56} y={-448} width={18} height={36} rx={8} fill="#56627F" />
              <path d="M66,-414 Q60,-384 24,-388" strokeWidth={5} />
            </g>
          )}
        </g>
        <Arm look={look} side={1} a={P.r} wob={wob} holding={holding} />
      </g>
    </g>
    </g>
  );
};

// ---- Small hand-held props (drawn at hand origin) ----
export const HeldPhone: React.FC<{ glow?: boolean }> = ({ glow }) => (
  <g transform="translate(-14,-40) rotate(8)">
    <rect x={0} y={0} width={30} height={54} rx={6} fill={C.navyDeep} stroke={OL} strokeWidth={4} />
    <rect x={4} y={6} width={22} height={38} rx={3} fill={glow ? C.cyan : '#8FB6D9'} />
  </g>
);
export const HeldPaper: React.FC<{ label?: string }> = ({ label }) => (
  <g transform="translate(-10,-70) rotate(-6)">
    <rect x={0} y={0} width={70} height={90} rx={4} fill="#fff" stroke={OL} strokeWidth={4} />
    {[16, 30, 44, 58].map((y) => <path key={y} d={`M10,${y} L60,${y}`} stroke={C.mist} strokeWidth={4} />)}
    {label && <text x={35} y={80} fontSize={11} textAnchor="middle" fill={C.orange} fontWeight={700} fontFamily="sans-serif">{label}</text>}
  </g>
);
export const HeldCup: React.FC = () => (
  <g transform="translate(-16,-36)">
    <path d="M0,0 L32,0 L28,40 L4,40Z" fill="#fff" stroke={OL} strokeWidth={4} />
    <path d="M32,10 q12,0 10,12 q-2,8 -12,8" fill="none" stroke={OL} strokeWidth={4} />
  </g>
);
export const HeldCard: React.FC<{ color?: string }> = ({ color = C.blue }) => (
  <g transform="translate(-20,-34) rotate(-12)">
    <rect x={0} y={0} width={60} height={38} rx={5} fill={color} stroke={OL} strokeWidth={4} />
    <rect x={8} y={10} width={12} height={9} rx={2} fill="#F3C969" />
  </g>
);
export const HeldUsb: React.FC = () => (
  <g transform="translate(-8,-40) rotate(10)">
    <rect x={0} y={10} width={20} height={34} rx={4} fill={C.orange} stroke={OL} strokeWidth={4} />
    <rect x={3} y={0} width={14} height={12} fill="#D5DCE6" stroke={OL} strokeWidth={3} />
  </g>
);
export const HeldLaptop: React.FC = () => (
  <g transform="translate(-60,-50)">
    <rect x={0} y={0} width={120} height={78} rx={6} fill="#56627F" stroke={OL} strokeWidth={4} />
    <rect x={8} y={8} width={104} height={60} rx={3} fill={C.cyan} />
  </g>
);

/** storyboard `holding` enum → prop drawn at the right hand */
export const heldFor = (name?: string): React.ReactNode => {
  switch (name) {
    case 'phone': return <HeldPhone glow />;
    case 'paper': return <HeldPaper />;
    case 'cup': return <HeldCup />;
    case 'card': return <HeldCard />;
    case 'usb': return <HeldUsb />;
    case 'laptop': return <HeldLaptop />;
    default: return undefined;
  }
};
