// Render many QA stills with ONE bundle + ONE browser (fast).
// usage: node scripts/stills.mjs <props.json> <public_dir> <out_dir> <scale> <frame> [<frame> ...]
import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import { bundle } from '@remotion/bundler';
import { renderStill, selectComposition, openBrowser } from '@remotion/renderer';

const here = path.dirname(fileURLToPath(import.meta.url));
const [propsPath, publicDir, outDir, scaleS, ...frames] = process.argv.slice(2);
const inputProps = JSON.parse(fs.readFileSync(propsPath, 'utf8'));
fs.mkdirSync(outDir, { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(here, '..', 'src', 'index.ts'), publicDir, onProgress: () => {} });
const browser = await openBrowser('chrome', { chromiumOptions: process.platform === 'darwin' ? { gl: 'angle' } : {} });
const composition = await selectComposition({ serveUrl, id: 'tcs-lesson', inputProps, puppeteerInstance: browser });
for (const f of frames) {
  const frame = Math.min(composition.durationInFrames - 1, Math.max(0, parseInt(f, 10)));
  const output = path.join(outDir, `f${String(frame).padStart(6, '0')}.png`);
  await renderStill({ serveUrl, composition, inputProps, frame, output, scale: parseFloat(scaleS), puppeteerInstance: browser, chromiumOptions: process.platform === 'darwin' ? { gl: 'angle' } : {} });
  console.log(output);
}
await browser.close({ silent: true });
