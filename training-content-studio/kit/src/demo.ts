// Tiny built-in timeline so `npm run studio` opens without a prepared run.
import { Timeline } from './core/types';

export const DEMO: Timeline = {
  lesson_id: 'demo', title: 'Demo', fps: 30, width: 1920, height: 1080, total: 150, language: 'en-US', direction: 'ltr',
  theme: { preset: 'neutral' },
  scenes: [
    { id: 'title', template: 'title', from: 0, frames: 150, cues: [], lines: [],
      props: { kicker: 'Training Content Studio', title: 'Render kit ready', sub: 'Prepare a storyboard to render a lesson', icon: 'sparkles' } },
  ],
};
