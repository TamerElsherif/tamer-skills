// Export every kit persona as a static SVG (idle/neutral + a few poses) for HTML lessons.
// usage (from kit/): node scripts/export_personas.mjs [out_dir=../assets/characters]
import path from 'node:path';
import fs from 'node:fs';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';

const here = path.dirname(fileURLToPath(import.meta.url));
const kit = path.join(here, '..');
const out = path.resolve(process.argv[2] ?? path.join(kit, '..', 'assets', 'characters'));
const tmp = path.join(kit, 'node_modules', '.cache', 'personas');
fs.mkdirSync(tmp, { recursive: true });
fs.writeFileSync(path.join(tmp, 'remotion-shim.js'), 'export const useCurrentFrame = () => 0;\n');
fs.writeFileSync(path.join(tmp, 'entry.tsx'), `
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { Person } from '${path.join(kit, 'src/core/Person').replace(/\\/g, '/')}';
import { CAST } from '${path.join(kit, 'src/core/cast').replace(/\\/g, '/')}';
import { SceneCtx } from '${path.join(kit, 'src/core/ctx').replace(/\\/g, '/')}';
const api: any = { t: 0, dur: 1, frame: 0, fps: 30, cue: () => 0, hasCue: () => false, amp: () => 0, speaking: () => false, row: { lines: [], cues: [] } };
export const ids = Object.keys(CAST);
export const svg = (cast: string, pose: string, expr: string) =>
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-200 -560 400 580" width="400" height="580">' +
  renderToStaticMarkup(<SceneCtx.Provider value={api}><Person cast={cast} x={0} y={0} s={1} pose={pose as any} expr={expr as any} /></SceneCtx.Provider>) + '</svg>';
`);
const bundle = path.join(tmp, 'bundle.cjs');
await build({ entryPoints: [path.join(tmp, 'entry.tsx')], bundle: true, platform: 'node', format: 'cjs', outfile: bundle, jsx: 'automatic',
  alias: { remotion: path.join(tmp, 'remotion-shim.js') }, nodePaths: [path.join(kit, 'node_modules')], logLevel: 'error' });
const m = createRequire(import.meta.url)(bundle);
const extras = [['wave', 'happy'], ['point', 'neutral'], ['think', 'think'], ['present', 'happy']];
for (const id of m.ids) {
  const d = path.join(out, id);
  fs.mkdirSync(d, { recursive: true });
  fs.writeFileSync(path.join(d, `${id}.svg`), m.svg(id, 'idle', 'neutral'));
  for (const [pose, expr] of extras) fs.writeFileSync(path.join(d, `${pose}.svg`), m.svg(id, pose, expr));
}
console.log(`exported ${m.ids.length} personas → ${out}`);
