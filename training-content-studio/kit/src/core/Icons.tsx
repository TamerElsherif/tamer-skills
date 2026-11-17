// Icons: lucide-react (ISC). Accepts kit aliases (below), any lucide name in PascalCase
// ("ShieldCheck") or kebab-case ("shield-check"). Unknown names fall back to a neutral dot icon.
import React from 'react';
import * as L from 'lucide-react';

const ALIASES: Record<string, string> = {
  mail: 'Mail', lock: 'Lock', unlock: 'LockOpen', key: 'KeyRound', shield: 'ShieldCheck', phone: 'Phone', alert: 'TriangleAlert',
  warning: 'TriangleAlert', user: 'User', users: 'Users', server: 'Server', cloud: 'Cloud', wifi: 'Wifi', usb: 'Usb', printer: 'Printer',
  money: 'Banknote', card: 'CreditCard', link: 'Link', qr: 'QrCode', camera: 'Camera', mic: 'Mic', bot: 'Bot', file: 'FileText',
  folder: 'Folder', eye: 'Eye', eyeOff: 'EyeOff', clock: 'Clock', globe: 'Globe', laptop: 'Laptop', check: 'CircleCheck', x: 'CircleX',
  flag: 'Flag', megaphone: 'Megaphone', refresh: 'RefreshCw', database: 'Database', plane: 'Plane', bag: 'Briefcase', badge: 'IdCard',
  building: 'Building2', chat: 'MessageSquare', smartphone: 'Smartphone', trash: 'Trash2', search: 'Search', fingerprint: 'Fingerprint',
  bug: 'Bug', zap: 'Zap', target: 'Target', trend: 'TrendingUp', gift: 'Gift', hand: 'Hand', heart: 'Heart', userX: 'UserX',
  userCheck: 'UserCheck', settings: 'Settings', download: 'Download', upload: 'Upload', share: 'Share2', layers: 'Layers', drive: 'HardDrive',
  archive: 'Archive', calendar: 'Calendar', lightbulb: 'Lightbulb', idea: 'Lightbulb', book: 'BookOpen', scale: 'Scale', gavel: 'Gavel', siren: 'Siren',
  sparkles: 'Sparkles', video: 'Video', headset: 'Headset', map: 'Map', home: 'House', door: 'DoorOpen', shieldAlert: 'ShieldAlert',
  monitor: 'Monitor', click: 'MousePointerClick', handCoins: 'HandCoins', invoice: 'ReceiptText', verified: 'BadgeCheck', face: 'ScanFace',
  voice: 'AudioLines', brain: 'Brain', checklist: 'ListChecks', undo: 'RotateCcw', activity: 'Activity', network: 'Network', keyOld: 'Key',
  userSearch: 'UserRoundSearch', wallet: 'Wallet', fileLock: 'FileLock', graduation: 'GraduationCap', award: 'Award', chart: 'BarChart3',
  pie: 'PieChart', clipboard: 'ClipboardList', code: 'Code', terminal: 'Terminal', tool: 'Wrench', wrench: 'Wrench', package: 'Package',
  truck: 'Truck', cart: 'ShoppingCart', store: 'Store', health: 'HeartPulse', leaf: 'Leaf', handshake: 'Handshake', info: 'Info',
  help: 'CircleHelp', question: 'CircleHelp', star: 'Star', thumbsUp: 'ThumbsUp', thumbsDown: 'ThumbsDown', timer: 'Timer', rocket: 'Rocket',
  puzzle: 'Puzzle', compass: 'Compass', fire: 'Flame', ban: 'Ban', bell: 'Bell', send: 'Send', inbox: 'Inbox', paperclip: 'Paperclip',
  pencil: 'Pencil', image: 'Image', cpu: 'Cpu', factory: 'Factory', hardhat: 'HardHat', bank: 'Landmark', coins: 'Coins', growth: 'TrendingUp',
  flow: 'Workflow', branch: 'GitBranch', pin: 'MapPin', language: 'Languages', smile: 'Smile', frown: 'Frown', presentation: 'Presentation',
  calculator: 'Calculator', school: 'School', trophy: 'Trophy', save: 'Save', login: 'LogIn', logout: 'LogOut', filter: 'Filter',
  magic: 'Wand2', chats: 'MessagesSquare', signature: 'Signature', fileCheck: 'FileCheck', fileX: 'FileX', shieldX: 'ShieldX', meeting: 'Presentation',
  question2: 'MessageCircleQuestion', team: 'Users', person: 'User', email: 'Mail', password: 'KeyRound', danger: 'OctagonAlert', stop: 'OctagonX',
};

const toPascal = (s: string) => s.replace(/(^|[-_ ])(\w)/g, (_, __, c: string) => c.toUpperCase());

export const resolveIcon = (name?: string): React.FC<any> => {
  const lib = L as unknown as Record<string, React.FC<any>>;
  if (!name) return lib.Circle;
  const n = ALIASES[name] ?? (lib[name] ? name : toPascal(name));
  return lib[n] ?? lib[toPascal(name)] ?? lib.CircleDot ?? lib.Circle;
};

export const Icon: React.FC<{ name?: string; size?: number; color?: string; stroke?: number; style?: React.CSSProperties }> = ({ name, size = 48, color = 'currentColor', stroke = 2, style }) => {
  const Cmp = resolveIcon(name);
  return <Cmp size={size} color={color} strokeWidth={stroke} style={style} />;
};
