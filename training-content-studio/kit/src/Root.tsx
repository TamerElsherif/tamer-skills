// Generic Root: one composition ("tcs-lesson") whose size/length come from the timeline props.
// Render with:  npx remotion render src/index.ts tcs-lesson out.mp4 --props=<run_dir>/timeline.json --public-dir=<run_dir>/public
import React from 'react';
import { Composition, CalculateMetadataFunction } from 'remotion';
import { Lesson } from './core/Lesson';
import { Timeline } from './core/types';
import { DEMO } from './demo';

type Props = { tl: Timeline };
const meta: CalculateMetadataFunction<Props> = ({ props }) => ({
  durationInFrames: Math.max(1, props.tl.total),
  fps: props.tl.fps || 30,
  width: props.tl.width,
  height: props.tl.height,
});

const LessonComp: React.FC<Props> = ({ tl }) => <Lesson tl={tl} />;

/** Composition ids may only contain [a-zA-Z0-9-]. */
export const compId = (s: string) => s.replace(/[^a-zA-Z0-9-]+/g, '-').replace(/^-+|-+$/g, '') || 'lesson';

export const Root: React.FC = () => (
  <Composition id="tcs-lesson" component={LessonComp} defaultProps={{ tl: DEMO }} calculateMetadata={meta}
    durationInFrames={DEMO.total} fps={30} width={1920} height={1080} />
);

/** Root for a fixed, bundled timeline (used by the OpenMontage atelier entry). */
export const makeFixedRoot = (tl: Timeline, id?: string): React.FC => () => (
  <Composition id={compId(id ?? tl.comp_id ?? tl.lesson_id)} component={LessonComp} defaultProps={{ tl }}
    durationInFrames={Math.max(1, tl.total)} fps={tl.fps || 30} width={tl.width} height={tl.height} />
);
