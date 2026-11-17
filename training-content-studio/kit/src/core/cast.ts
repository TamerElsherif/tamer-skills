// Persona looks (neutral, fictional, diverse, flat vector). Clothing stays in cool tones;
// the attention colour (orange) is reserved for `vex`, the security pack's attacker.
export type Look = {
  skin: string;
  hair: string;
  hairStyle: 'short' | 'long' | 'bun' | 'ponytail' | 'curly' | 'side' | 'buzz' | 'slick' | 'bald' | 'hijab';
  shirt: string;
  jacket?: string;
  tie?: string;
  pants: string;
  shoes: string;
  skirt?: boolean;
  glasses?: boolean;
  beard?: boolean;
  mustache?: boolean;
  goatee?: boolean;
  lanyard?: string;
  shortSleeves?: boolean;
  blush?: boolean;
  headset?: boolean;
};

// Aligned with assets/characters/personas.yaml (+ domains/security-awareness/personas.yaml for vex / voice_clone).
export const CAST: Record<string, Look> = {
  // host "Lina" — navy blazer over light-cyan top
  host: { skin: '#A86B4C', hair: '#3B2A22', hairStyle: 'long', shirt: '#6FC7DA', jacket: '#363E77', pants: '#3A3F55', shoes: '#2A2E45' },
  // learner "Nour" — blue hijab, grey cardigan, white top, badge
  learner: { skin: '#D9A982', hair: '#006AB3', hairStyle: 'hijab', shirt: '#FFFFFF', jacket: '#9AA3B5', pants: '#26305C', shoes: '#F4F7FB', lanyard: '#6FC7DA' },
  // manager "Karim" — white shirt (rolled sleeves), navy waistcoat, grey beard
  manager: { skin: '#6B4532', hair: '#4A4A4A', hairStyle: 'short', shirt: '#FFFFFF', tie: '#363E77', pants: '#5A6385', shoes: '#2A2E45', beard: true, shortSleeves: true },
  // mentor "Omar" — blue polo, khaki trousers, glasses, beard, lanyard
  mentor: { skin: '#B98563', hair: '#1F1A17', hairStyle: 'short', shirt: '#006AB3', pants: '#C9B48A', shoes: '#2A2E45', glasses: true, beard: true, lanyard: '#6FC7DA' },
  // customer "Dana" — green blazer, silver bob
  customer: { skin: '#F0CFB4', hair: '#C8CCD4', hairStyle: 'side', shirt: '#F7F7F2', jacket: '#1E7F4F', pants: '#2E3446', shoes: '#2A2E45', blush: true },
  // rookie "Sam" — light-blue shirt, curly black hair, badge
  rookie: { skin: '#C68B5E', hair: '#141414', hairStyle: 'curly', shirt: '#A9D4F5', pants: '#4A4F5E', shoes: '#F4F7FB', lanyard: '#006AB3' },
  // colleague "Maya" — short natural curls, teal sweater
  colleague: { skin: '#5C3A28', hair: '#1B1412', hairStyle: 'curly', shirt: '#2A9D8F', pants: '#6B7280', shoes: '#2A2E45' },
  // exec "Hana" — dark navy suit, grey-streaked low bun
  exec: { skin: '#C9906B', hair: '#7A7A80', hairStyle: 'bun', shirt: '#FFFFFF', jacket: '#232957', pants: '#232957', shoes: '#1E2448' },
  // support "Dina" — black ponytail, headset, light-blue polo
  support: { skin: '#C68F6A', hair: '#141414', hairStyle: 'ponytail', shirt: '#8EC5E8', pants: '#3D4466', shoes: '#2A2E45', headset: true },
  // vex — attacker (security pack): the ONLY persona in attention orange (jacket), thin moustache
  vex: { skin: '#D8B08C', hair: '#1B1B1B', hairStyle: 'slick', shirt: '#3A3F55', jacket: '#FF6700', pants: '#2E3446', shoes: '#15172A', mustache: true },
};
/** personas rendered as another look with an effect (security pack: voice_clone = exec + glitch) */
export const ALIASES: Record<string, { as: string; glitch?: boolean }> = { voice_clone: { as: 'exec', glitch: true } };

const EXTRAS: Look[] = [
  { skin: '#8D5B3E', hair: '#111111', hairStyle: 'buzz', shirt: '#9FB4CC', pants: '#56627F', shoes: '#2A2E45' },
  { skin: '#F1C7A5', hair: '#6B4A2E', hairStyle: 'ponytail', shirt: '#D8E1EC', pants: '#363E77', shoes: '#2A2E45' },
  { skin: '#C98E62', hair: '#2B2522', hairStyle: 'curly', shirt: '#B8C4D6', jacket: '#4A5578', pants: '#363E77', shoes: '#2A2E45', glasses: true },
];

/** Look for any persona id; unknown ids (domain-pack personas) get a stable neutral extra. */
export const lookFor = (id: string): Look => {
  if (ALIASES[id]) return CAST[ALIASES[id].as];
  if (CAST[id]) return CAST[id];
  const h = [...id].reduce((a, c) => a + c.charCodeAt(0), 0);
  return EXTRAS[h % EXTRAS.length];
};
export const PERSONAS = Object.keys(CAST);
