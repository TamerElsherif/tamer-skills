// Timeline contract produced by skills/tcs-render-remotion/scripts/prepare.py.
// One Timeline = one lesson render. All times in seconds unless named *frames/from.

export type LineRow = {
  who: string;
  at: number; // scene-local start (s)
  dur: number; // seconds
  src: string; // public-relative audio path ('' = silent placeholder)
  amp: string; // per-frame mouth amplitude 0..9, one char per frame
  text: string;
};

export type SceneRow = {
  id: string;
  template: string;
  props: Record<string, any>;
  from: number; // frame offset in the lesson
  frames: number;
  cues: number[]; // scene-local seconds, one per '^' marker
  lines: LineRow[];
  transition?: 'fade' | 'cut' | 'slide';
};

export type ThemeSpec = {
  preset?: string;
  colors?: Record<string, string>;
  fonts?: { latin?: string; arabic?: string; mono?: string; hand?: string };
  logo?: string | null; // public-relative path or null
  evidence_line?: string;
};

export type Timeline = {
  lesson_id: string;
  course_id?: string;
  title?: string;
  comp_id?: string;
  fps: number;
  width: number;
  height: number;
  total: number; // frames
  language: string; // en-US | en-GB | ar-EG | ar-MSA
  direction: 'ltr' | 'rtl';
  theme?: ThemeSpec;
  scenes: SceneRow[];
  music?: { src: string; vol: number } | null;
  sfx?: { at: number; src: string; vol?: number }[];
  broll?: Record<string, { src: string; len: number; placeholder?: boolean }>;
  images?: Record<string, { src: string; placeholder?: boolean }>;
  progress_bar?: boolean;
};
