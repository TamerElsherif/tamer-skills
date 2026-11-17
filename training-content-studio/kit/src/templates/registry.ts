// Template dispatcher: storyboard `scenes[].template` → component. One entry per enums.templates.
import React from 'react';
import * as I from './info';
import { ProcessFlow } from './flow';
import { Broll, BrollPanel, ImageT } from './media';
import { EmailMock, ChatMock, BrowserMock, MfaPrompt, Popup, CodeMock } from './mocks';
import { Screencast } from './screencast';
import { Cartoon, Comic } from './cartoon';
import { Whiteboard } from './whiteboard';
import { Mindmap } from './mindmap';

export const TEMPLATES: Record<string, React.FC<any>> = {
  title: I.Title,
  section: I.Section,
  bullets: I.Bullets,
  icon_grid: I.IconGrid,
  steps: I.Steps,
  process_flow: ProcessFlow,
  timeline: I.TimelineT,
  do_dont: I.DoDont,
  comparison: I.Comparison,
  stat: I.Stat,
  definition: I.Definition,
  statement: I.Statement,
  table: I.Table,
  checklist: I.Checklist,
  quiz: I.Quiz,
  outro: I.Outro,
  broll: Broll,
  broll_panel: BrollPanel,
  image: ImageT,
  email_mock: EmailMock,
  chat_mock: ChatMock,
  browser_mock: BrowserMock,
  mfa_prompt: MfaPrompt,
  popup: Popup,
  code_mock: CodeMock,
  screencast: Screencast,
  cartoon: Cartoon,
  whiteboard: Whiteboard,
  comic: Comic,
  mindmap: Mindmap,
  decision: I.Decision,
  flashcard: I.Flashcard,
};
