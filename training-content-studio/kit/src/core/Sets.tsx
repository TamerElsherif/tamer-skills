// Flat cartoon environments (1920×1080 stage units; adapted from the uSecure engine). No signage text. Thin outlines so characters (thick outlines) read first.
import React from 'react';
import { useCurrentFrame } from 'remotion';

// Fixed cool environment palette (sets read the same under every theme preset; never cream/terracotta).
const C = {
  navyInk: '#1E2448', navy: '#363E77', navyDeep: '#232957', ink: '#363E77', ink2: '#6781AC', mist: '#BFCEDD', hair: '#D8E1EC',
  blue: '#006AB3', blueSoft: '#DCEDF8', cyan: '#6FC7DA', cyanSoft: '#E3F5F9', orange: '#FF6700', orange2: '#FF8A00', orangeSoft: '#FFEADB',
  red: '#E0453A', bg: '#F4F7FB', wall: '#E8EEF5', wall2: '#DCE4EE', floor: '#C9D3E0', wood: '#B8C4D6',
};

const OL = C.navyInk;
const o = { stroke: OL, strokeWidth: 4, strokeLinejoin: 'round' as const };

export const Window: React.FC<{ x: number; y: number; w: number; h: number; night?: boolean }> = ({ x, y, w, h, night }) => {
  const sky = night ? '#2B3566' : '#CFE8F5';
  const bld = night ? '#3E4A80' : '#A9C3DA';
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} fill={sky} {...o} />
      {[0.08, 0.25, 0.44, 0.62, 0.8].map((p, i) => (
        <rect key={i} x={x + w * p} y={y + h * (0.35 + (i % 3) * 0.12)} width={w * 0.14} height={h} fill={bld} />
      ))}
      {night && [0.12, 0.3, 0.5, 0.68, 0.84].map((p, i) => <rect key={i} x={x + w * p} y={y + h * 0.6} width={10} height={14} fill="#F3C969" />)}
      <rect x={x} y={y} width={w} height={h} fill="none" {...o} strokeWidth={10} stroke="#fff" />
      <rect x={x} y={y} width={w} height={h} fill="none" {...o} />
      <path d={`M${x + w / 2},${y} L${x + w / 2},${y + h} M${x},${y + h / 2} L${x + w},${y + h / 2}`} stroke="#fff" strokeWidth={8} />
    </g>
  );
};

export const Plant: React.FC<{ x: number; y: number; s?: number }> = ({ x, y, s = 1 }) => (
  <g transform={`translate(${x},${y}) scale(${s})`}>
    {[-40, -15, 10, 35].map((a, i) => (
      <path key={i} d={`M0,-60 Q${a * 1.2},-150 ${a * 2},-190 Q${a * 0.4},-130 0,-60Z`} fill={i % 2 ? '#3E9C7A' : '#57B892'} {...o} strokeWidth={3} />
    ))}
    <path d="M-45,-70 L45,-70 L35,0 L-35,0Z" fill="#E7EDF4" {...o} />
  </g>
);

export const Clock: React.FC<{ x: number; y: number }> = ({ x, y }) => {
  const f = useCurrentFrame();
  const a = f * 0.6;
  return (
    <g transform={`translate(${x},${y})`}>
      <circle r={44} fill="#fff" {...o} />
      <path d={`M0,0 L${Math.sin((a * Math.PI) / 180) * 30},${-Math.cos((a * Math.PI) / 180) * 30}`} stroke={OL} strokeWidth={4} strokeLinecap="round" />
      <path d="M0,0 L0,-22" stroke={OL} strokeWidth={6} strokeLinecap="round" transform="rotate(120)" />
    </g>
  );
};

export const Frame: React.FC<{ x: number; y: number; w: number; h: number }> = ({ x, y, w, h }) => (
  <g>
    <rect x={x} y={y} width={w} height={h} fill="#fff" {...o} />
    <path d={`M${x + 12},${y + h - 12} L${x + w * 0.4},${y + h * 0.45} L${x + w * 0.6},${y + h * 0.7} L${x + w * 0.75},${y + h * 0.55} L${x + w - 12},${y + h - 12}Z`} fill={C.cyan} />
    <circle cx={x + w * 0.75} cy={y + h * 0.3} r={10} fill={C.orange2} />
  </g>
);

const Floor: React.FC<{ y?: number; color?: string }> = ({ y = 820, color = C.floor }) => (
  <g>
    <rect x={0} y={y} width={1920} height={1080 - y} fill={color} />
    <path d={`M0,${y} L1920,${y}`} {...o} />
  </g>
);

export type SetKind = 'office' | 'openOffice' | 'home' | 'server' | 'meeting' | 'reception' | 'airport' | 'cafe' | 'den' | 'street' | 'plain' | 'boardroom' | 'whiteboard';

export const SetBg: React.FC<{ kind: SetKind; night?: boolean }> = ({ kind, night }) => {
  const f = useCurrentFrame();
  switch (kind) {
    case 'office':
      return (
        <g>
          <rect width={1920} height={1080} fill={C.wall} />
          <rect x={0} y={0} width={1920} height={60} fill={C.wall2} />
          <Window x={1180} y={150} w={560} h={380} night={night} />
          <Frame x={260} y={200} w={200} h={140} />
          <Clock x={620} y={230} />
          <Floor />
          <Plant x={1820} y={860} s={1.2} />
          <g>
            <rect x={80} y={420} width={160} height={400} fill="#DCE4EE" {...o} />
            {[470, 600, 730].map((yy) => <g key={yy}><rect x={96} y={yy} width={128} height={100} fill="#E8EEF5" {...o} strokeWidth={3} /><rect x={140} y={yy + 40} width={40} height={10} rx={4} fill={C.ink2} /></g>)}
          </g>
        </g>
      );
    case 'openOffice':
      return (
        <g>
          <rect width={1920} height={1080} fill={C.wall} />
          <Window x={140} y={130} w={520} h={340} night={night} />
          <Window x={760} y={130} w={520} h={340} night={night} />
          <Window x={1380} y={130} w={400} h={340} night={night} />
          <Floor y={760} />
          {[300, 960, 1600].map((x) => (
            <g key={x}>
              <rect x={x - 180} y={640} width={360} height={30} fill={C.wood} {...o} />
              <rect x={x - 60} y={540} width={120} height={90} rx={8} fill={C.navyDeep} {...o} />
              <rect x={x - 50} y={550} width={100} height={70} rx={4} fill={C.cyanSoft} />
            </g>
          ))}
        </g>
      );
    case 'home':
      return (
        <g>
          <rect width={1920} height={1080} fill="#E4ECF2" />
          <Window x={1240} y={170} w={440} h={380} night={night} />
          <path d="M1210,150 Q1260,380 1230,600 L1210,600Z M1710,150 Q1660,380 1690,600 L1710,600Z" fill="#FFFFFF" {...o} strokeWidth={3} />
          <Frame x={420} y={220} w={180} h={130} />
          <Frame x={640} y={260} w={120} h={160} />
          <Floor y={800} color="#C8D2DE" />
          <g>
            <rect x={200} y={560} width={900} height={200} rx={40} fill="#6781AC" {...o} />
            <rect x={240} y={480} width={820} height={140} rx={40} fill="#7F97BE" {...o} />
            <rect x={170} y={560} width={90} height={230} rx={30} fill="#56627F" {...o} />
            <rect x={1040} y={560} width={90} height={230} rx={30} fill="#56627F" {...o} />
          </g>
          <g>
            <path d="M1560,800 L1560,620" stroke={OL} strokeWidth={6} />
            <path d="M1500,620 L1620,620 L1590,540 L1530,540Z" fill={C.orangeSoft} {...o} />
          </g>
        </g>
      );
    case 'server':
      return (
        <g>
          <rect width={1920} height={1080} fill="#2B3566" />
          <Floor y={860} color="#232957" />
          {[120, 460, 800, 1140, 1480].map((x, i) => (
            <g key={x}>
              <rect x={x} y={140} width={300} height={720} fill="#3A4478" {...o} stroke="#1B2046" />
              {Array.from({ length: 10 }).map((_, k) => (
                <g key={k}>
                  <rect x={x + 20} y={170 + k * 68} width={260} height={52} rx={6} fill="#4A5590" />
                  <circle cx={x + 250} cy={196 + k * 68} r={6} fill={(f + k * 7 + i * 13) % 40 < 20 ? C.cyan : '#1F9D6B'} />
                  <circle cx={x + 228} cy={196 + k * 68} r={6} fill={(f + k * 11 + i * 5) % 60 < 8 ? C.orange2 : '#39447A'} />
                  <rect x={x + 36} y={188 + k * 68} width={120} height={8} rx={4} fill="#5E6AA6" />
                </g>
              ))}
            </g>
          ))}
        </g>
      );
    case 'meeting':
      return (
        <g>
          <rect width={1920} height={1080} fill={C.wall} />
          <Floor y={840} />
          <rect x={560} y={140} width={800} height={500} rx={10} fill="#fff" {...o} strokeWidth={6} />
          <rect x={540} y={630} width={840} height={16} fill={C.mist} {...o} />
          <Window x={1500} y={180} w={330} h={420} night={night} />
          <Plant x={170} y={880} s={1.3} />
        </g>
      );
    case 'boardroom':
      return (
        <g>
          <rect width={1920} height={1080} fill="#DCE4EE" />
          <Window x={120} y={120} w={1680} h={460} night={night} />
          <Floor y={760} color="#B8C4D6" />
          <path d="M260,780 L1660,780 L1760,900 L160,900Z" fill="#56627F" {...o} />
          <path d="M160,900 L1760,900 L1760,930 L160,930Z" fill="#3D4466" {...o} />
        </g>
      );
    case 'reception':
      return (
        <g>
          <rect width={1920} height={1080} fill={C.wall} />
          <Floor y={830} />
          <rect x={1160} y={200} width={420} height={630} fill="#B8C4D6" {...o} />
          <rect x={1180} y={220} width={185} height={610} fill="#CFE0EE" {...o} />
          <rect x={1375} y={220} width={185} height={610} fill="#CFE0EE" {...o} />
          <rect x={1600} y={460} width={70} height={110} rx={10} fill={C.navyDeep} {...o} />
          <circle cx={1635} cy={495} r={14} fill={(f % 60) < 30 ? C.red : '#5E2A2A'} />
          <rect x={1612} y={525} width={46} height={30} rx={4} fill="#4A5590" />
          <rect x={1250} y={156} width={240} height={30} rx={6} fill={C.ink2} opacity={0.5} />
          <rect x={160} y={560} width={620} height={270} fill={C.navy} {...o} />
          <rect x={140} y={540} width={660} height={40} fill={C.mist} {...o} />
          <Plant x={930} y={860} s={1.2} />
        </g>
      );
    case 'airport':
      return (
        <g>
          <rect width={1920} height={1080} fill="#DCE8F2" />
          <rect x={0} y={120} width={1920} height={520} fill="#BFDDF0" {...o} />
          {[0, 1, 2, 3].map((i) => <path key={i} d={`M${i * 480},120 L${i * 480},640`} stroke="#fff" strokeWidth={14} />)}
          <g transform={`translate(${((f * 3) % 2600) - 400},300)`}>
            <path d="M0,0 L260,0 Q300,0 300,20 Q300,40 260,40 L0,40 Q-20,20 0,0Z" fill="#fff" {...o} />
            <path d="M120,20 L60,90 L100,90 L180,20Z M20,5 L0,-40 L30,-40 L60,5Z" fill={C.blue} {...o} />
          </g>
          <rect x={1300} y={680} width={520} height={200} rx={8} fill={C.navyDeep} {...o} />
          {[0, 1, 2, 3].map((i) => (
            <rect key={i} x={1330} y={706 + i * 44} width={[300, 380, 260, 340][i]} height={22} rx={4} fill={i === 2 ? C.orange2 : '#F3C969'} opacity={0.85} />
          ))}
          <Floor y={880} color="#C3CFDD" />
          {[140, 420, 700].map((x) => (
            <g key={x}>
              <rect x={x} y={780} width={220} height={60} rx={12} fill={C.ink2} {...o} />
              <rect x={x + 10} y={720} width={200} height={70} rx={12} fill={C.ink} {...o} />
            </g>
          ))}
        </g>
      );
    case 'cafe':
      return (
        <g>
          <rect width={1920} height={1080} fill="#E8E4F0" />
          <rect x={0} y={0} width={1920} height={120} fill={C.navy} />
          {Array.from({ length: 12 }).map((_, i) => <path key={i} d={`M${i * 170},120 L${i * 170 + 85},180 L${i * 170 + 170},120Z`} fill={i % 2 ? C.cyan : '#fff'} {...o} strokeWidth={3} />)}
          <Window x={120} y={240} w={700} h={420} night={night} />
          <rect x={1100} y={260} width={620} height={300} rx={12} fill={C.navyDeep} {...o} />
          {[0, 1, 2, 3].map((i) => <rect key={i} x={1160} y={310 + i * 54} width={[380, 300, 420, 260][i]} height={22} rx={6} fill={i === 0 ? '#fff' : C.cyan} opacity={0.8} />)}
          <Floor y={820} color="#C9C3D8" />
        </g>
      );
    case 'den':
      return (
        <g>
          <rect width={1920} height={1080} fill="#1E2448" />
          <Floor y={840} color="#171B38" />
          {[[300, 220], [760, 160], [1220, 220]].map(([x, y], i) => (
            <g key={i}>
              <rect x={x} y={y} width={400} height={260} rx={10} fill="#0F1330" {...o} stroke="#4A5590" />
              {Array.from({ length: 7 }).map((_, k) => (
                <rect key={k} x={x + 24} y={y + 30 + k * 30} width={((k * 97 + i * 53 + f * 3) % 300) + 40} height={10} rx={5} fill={k % 3 === 0 ? C.orange : '#4A5590'} opacity={0.9} />
              ))}
            </g>
          ))}
          <rect x={260} y={660} width={1400} height={30} fill="#3A3F5C" {...o} stroke="#4A5590" />
        </g>
      );
    case 'street':
      return (
        <g>
          <rect width={1920} height={1080} fill="#CFE8F5" />
          <rect x={260} y={160} width={900} height={700} fill="#DCE4EE" {...o} />
          {Array.from({ length: 4 }).map((_, r) => Array.from({ length: 5 }).map((__, c) => (
            <rect key={`${r}${c}`} x={310 + c * 170} y={220 + r * 140} width={120} height={90} fill="#A9C3DA" {...o} strokeWidth={3} />
          )))}
          <rect x={620} y={740} width={180} height={120} fill={C.navy} {...o} />
          <rect x={1280} y={420} width={500} height={440} fill="#E8EEF5" {...o} />
          <Floor y={860} color="#9FAFC4" />
        </g>
      );
    case 'whiteboard':
      return <rect width={1920} height={1080} fill="#FFFFFF" />;
    case 'plain':
    default:
      return (
        <g>
          <rect width={1920} height={1080} fill={C.bg} />
          <circle cx={1650} cy={200} r={320} fill={C.blueSoft} />
          <circle cx={240} cy={930} r={260} fill={C.cyanSoft} />
          <Floor y={900} color={C.hair} />
        </g>
      );
  }
};

/** Desk seen from the front, with a monitor turned toward camera. Returns SVG; screen rect exported for HTML overlays. */
export const Desk: React.FC<{ x?: number; y?: number; w?: number; monitor?: 'left' | 'right' | 'none'; laptop?: boolean; mug?: boolean; papers?: boolean }> = ({ x = 960, y = 760, w = 900, monitor = 'right', laptop, mug = true, papers }) => (
  <g>
    <rect x={x - w / 2} y={y} width={w} height={34} fill={C.wood} {...o} />
    <rect x={x - w / 2 + 30} y={y + 34} width={w - 60} height={1080 - y} fill="#A3B1C6" {...o} />
    {monitor !== 'none' && (() => {
      const mx = monitor === 'right' ? x + w / 2 - 330 : x - w / 2 + 30;
      return (
        <g>
          <rect x={mx + 130} y={y - 60} width={40} height={60} fill="#56627F" {...o} />
          <rect x={mx + 80} y={y - 12} width={140} height={14} rx={6} fill="#56627F" {...o} />
          <rect x={mx} y={y - 290} width={300} height={230} rx={12} fill={C.navyDeep} {...o} />
        </g>
      );
    })()}
    {laptop && (
      <g>
        <path d={`M${x - 150},${y} L${x + 150},${y} L${x + 120},${y - 14} L${x - 120},${y - 14}Z`} fill="#8C9AB3" {...o} />
        <path d={`M${x - 120},${y - 14} L${x - 140},${y - 190} L${x + 140},${y - 190} L${x + 120},${y - 14}Z`} fill="#56627F" {...o} />
      </g>
    )}
    {mug && (
      <g transform={`translate(${monitor === 'right' ? x - w / 2 + 90 : x + w / 2 - 120},${y - 58})`}>
        <path d="M0,0 L50,0 L46,58 L4,58Z" fill="#fff" {...o} />
        <path d="M50,14 q18,0 14,20 q-3,10 -16,10" fill="none" {...o} />
      </g>
    )}
    {papers && (
      <g transform={`translate(${x - 60},${y - 30})`}>
        {[0, 1, 2, 3, 4].map((i) => <rect key={i} x={-i * 3} y={-i * 7} width={130} height={30} fill="#fff" {...o} strokeWidth={3} />)}
      </g>
    )}
  </g>
);

/** Screen rectangle of the Desk monitor (for HTML overlays). */
export const deskScreen = (x = 960, y = 760, w = 900, side: 'left' | 'right' = 'right') => {
  const mx = side === 'right' ? x + w / 2 - 330 : x - w / 2 + 30;
  return { x: mx + 12, y: y - 278, w: 276, h: 206 };
};
export const laptopScreen = (x = 960, y = 760) => ({ x: x - 128, y: y - 180, w: 256, h: 158 });
