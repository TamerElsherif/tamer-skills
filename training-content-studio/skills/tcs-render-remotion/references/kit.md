# Render kit (`kit/`)

Standalone Remotion 4 project shared by tcs-render-remotion and tcs-render-openmontage. Only deps: remotion,
@remotion/cli|bundler|renderer|google-fonts, react, lucide-react (pinned to the versions OpenMontage's
remotion-composer ships, so the same source bundles in both places).

```
kit/
  setup.sh                 npm install (idempotent)
  scripts/stills.mjs       many stills with one bundle + one browser (used by stills.py)
  src/index.ts             registerRoot(Root) — composition "tcs-lesson", size/length from props.tl
  src/Root.tsx             Root + makeFixedRoot(tl, id) for bundled timelines (OpenMontage entry)
  src/core/
    types.ts               Timeline contract (written by prepare.py)
    Lesson.tsx             scenes → dispatcher, narration audio, music ducking, sfx, progress bar, logo slot
    ctx.tsx                useScene() {t, dur, cue(i), hasCue, amp(who), speaking} · useLayout() {W,H,portrait,square,rtl,pad}
    theme.tsx              presets, fonts, motion helpers (prog, pop, lin, lerp), contrast helpers
    ui.tsx                 Header, Bg, cards, chips, ClipVideo (loop/slow), Media, Placeholder, fit() text sizing
    Icons.tsx              lucide icons: kit aliases, PascalCase or kebab-case names
    Person.tsx cast.ts     flat personas: poses, expressions, blinking, amplitude lip-flap, ink mode, reveal wipe
    Sets.tsx Stage.tsx     13 sets (no signage text) · stageFit(): cover + people re-spacing per aspect, camera
    i18n.ts                the few fixed UI strings (EN/AR)
  src/templates/           info, flow, media, mocks, screencast, cartoon(+comic), whiteboard, mindmap; registry.ts
  tests/                   en-phishing-16x9, ar-passwords-9x16, gallery (all 32 templates, placeholder voice)
```

## Theme
`theme.preset`: neutral (default) | whiteboard | midnight | executive | high_contrast — mirrors
`assets/theme_presets.yaml`. `theme.colors` may override any palette key or yaml key (`surface`, `accent_2`,
`attention_text`, `line`, `ink_strong`) or alias (`navy`, `blue`, `cyan`, `orange`). Fonts: Latin Poppins, Arabic
IBM Plex Sans Arabic (Cairo / Noto Kufi Arabic allowed), mono IBM Plex Mono, hand Caveat. `theme.logo` optional, empty by default.

Contrast: attention orange is never text on light grounds (use `attentionText`) and chips on orange use dark ink
(`onFill`, `NumBadge` handle it). No one-sided thick accent borders: cards use a soft full border + shadow.

## RTL
`direction: rtl` (or `ar-*`) sets `dir=rtl`; flex/grid layouts mirror naturally; stage x positions, facing, comic panel
order, mindmap angles, broll_panel side, step arrows and slide-in motion are mirrored explicitly. URLs, code, email
addresses and numbers stay LTR (isolated).

## Adding a template
1. Add the name to `schemas/enums.json` + props to `storyboard.schema.json` (orchestrator owns schemas).
2. Write the component in `src/templates/*.tsx` using `useScene`/`useLayout`/`useTheme`; text only from props; ≥ 24 px.
3. Register it in `src/templates/registry.ts`; add a scene to `tests/gallery.storyboard.json`; check stills in 16:9 and 9:16.
