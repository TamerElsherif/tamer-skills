# EXAMPLES — valid storyboard fragments per format

## explainer — example.ar-EG.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M1L1",
 "title": "إزاي تكشف إيميل التصيّد",
 "language": "ar-EG",
 "direction": "rtl",
 "subtitle_languages": [
  "en-US"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "explainer"
 ],
 "wpm": 130,
 "objective_ids": [
  "O1"
 ],
 "theme": {
  "preset": "neutral",
  "fonts": {
   "arabic": "IBM Plex Sans Arabic"
  },
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "ar-EG",
   "instructions": "Speak natural Egyptian Arabic (Cairene colloquial), warm and friendly like a respected colleague explaining to the team. Clear, relaxed pace; pronounce English technical terms the way Egyptian professionals say them."
  }
 },
 "music": {
  "bed": "explainer",
  "volume": 0.12
 },
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "kicker": "أساسيات الأمن",
    "title": "إزاي تكشف إيميل التصيّد",
    "sub": "خمس علامات في دقيقتين",
    "icon": "mail"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "أهلاً بيك. في الدقايق الجاية هنتعلم إزاي نكشف إيميل التصيّد قبل ما يكلفنا كتير."
    }
   ],
   "claims": [
    {
     "text": "Phishing emails try to trick people into clicking, paying or sharing data.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "s02_email",
   "template": "email_mock",
   "props": {
    "email": {
     "from": "مكتب الدعم الفني - نورثويند",
     "from_addr": "it-desk@northwlnd.example",
     "to": "you@northwind.example",
     "subject": "عاجل: صندوق بريدك هيتقفل النهارده",
     "external": true,
     "body": [
      "عزيزي المستخدم،",
      "صندوق بريدك تخطّى الحد وهيتقفل خلال ساعتين.",
      "اضغط تحت عشان تحافظ على حسابك."
     ],
     "button": "حافظ على بريدي"
    },
    "callouts": [
     {
      "cue": 0,
      "target": "addr",
      "label": "دومين شبه الأصلي",
      "tone": "warn"
     },
     {
      "cue": 1,
      "target": "b1",
      "label": "ضغط ومهلة قصيرة",
      "tone": "warn"
     },
     {
      "cue": 2,
      "target": "button",
      "label": "شوف الرابط قبل ما تدوس",
      "tone": "warn"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ أول حاجة، الدومين: northwlnd بحرف L بدل I. ^ تاني حاجة، الضغط: هيتقفل خلال ساعتين. ^ وأخيراً الزرار: قف عليه بالماوس الأول وشوف رايح فين."
    }
   ],
   "claims": [
    {
     "text": "Look-alike domains, urgency and disguised links are phishing red flags.",
     "source_ids": [
      "S01#c4"
     ]
    }
   ],
   "notes": "URL and email addresses stay LTR inside RTL layout (bidi isolates)."
  },
  {
   "id": "s03_recap",
   "template": "checklist",
   "props": {
    "title": "الخلاصة",
    "items": [
     "راجع دومين المرسِل",
     "ماتصدّقش الاستعجال",
     "قف على الرابط قبل ما تدوس",
     "بلّغ، ماتردّش"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "الخلاصة: ^ راجع الدومين، ^ ماتصدّقش الاستعجال، ^ قف على الرابط قبل ما تدوس، ^ وبلّغ بدل ما ترد."
    }
   ],
   "claims": [
    {
     "text": "Recap of red flags and reporting.",
     "source_ids": [
      "S01#c4",
      "S02#p2"
     ]
    }
   ]
  }
 ]
}
```

## explainer — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M1L1",
 "title": "Spot a Phishing Email",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "explainer"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  }
 },
 "music": {
  "bed": "explainer",
  "volume": 0.12
 },
 "broll_shots": [
  {
   "id": "hook",
   "query": "person reading email on laptop in office",
   "provider": "pexels",
   "min_s": 12
  },
  {
   "id": "inbox",
   "query": "hands typing on laptop keyboard close up",
   "provider": "pexels",
   "min_s": 12
  },
  {
   "id": "team",
   "query": "colleagues talking at office desk",
   "provider": "pexels",
   "min_s": 12
  }
 ],
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "kicker": "Security essentials",
    "title": "Spot a Phishing Email",
    "sub": "Five red flags in two minutes",
    "icon": "mail"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Welcome. In the next few minutes you'll learn to spot a phishing email before it costs you."
    }
   ],
   "claims": [
    {
     "text": "Phishing emails try to trick people into clicking, paying or sharing data.",
     "general_knowledge": true
    }
   ],
   "duration_hint_s": 6
  },
  {
   "id": "s02_hook",
   "template": "broll",
   "props": {
    "shot": "hook",
    "chips": [
     "Phishing",
     "Email"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Most attacks on companies start with a single email. ^ It looks routine, it feels urgent, and it only needs one click."
    }
   ],
   "claims": [
    {
     "text": "Phishing email is the most common way attacks reach our staff.",
     "source_ids": [
      "S01#c2"
     ]
    }
   ],
   "duration_hint_s": 12
  },
  {
   "id": "s03_what",
   "template": "definition",
   "props": {
    "term": "Phishing",
    "def": "A fake message that pretends to be someone you trust, to make you click, pay or share data.",
    "note": "It can arrive by email, text, phone or chat.",
    "icon": "mail"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Phishing is a fake message that pretends to come from someone you trust. ^ And it isn't only email: texts, calls and chat messages count too."
    }
   ],
   "claims": [
    {
     "text": "Phishing impersonates a trusted sender to obtain clicks, payments or data.",
     "general_knowledge": true
    },
    {
     "text": "Phishing also arrives by SMS, voice and chat.",
     "general_knowledge": true
    }
   ],
   "duration_hint_s": 14
  },
  {
   "id": "s04_flow",
   "template": "steps",
   "props": {
    "title": "How the attack unfolds",
    "steps": [
     {
      "icon": "mail",
      "label": "Bait",
      "sub": "An urgent email arrives"
     },
     {
      "icon": "link",
      "label": "Hook",
      "sub": "A link or attachment"
     },
     {
      "icon": "key",
      "label": "Catch",
      "sub": "Login page steals your password"
     },
     {
      "icon": "alert",
      "label": "Damage",
      "sub": "Account takeover or malware"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Here's how it unfolds. ^ The bait: an urgent email. ^ The hook: a link or an attachment. ^ The catch: a fake login page takes your password. ^ And then the damage: account takeover or malware."
    }
   ],
   "claims": [
    {
     "text": "Typical phishing flow: email, link, credential page, account takeover.",
     "source_ids": [
      "S01#c3"
     ]
    }
   ],
   "duration_hint_s": 18
  },
  {
   "id": "s05_email",
   "template": "email_mock",
   "props": {
    "email": {
     "from": "Northwind IT Service Desk",
     "from_addr": "it-desk@northwlnd.example",
     "to": "you@northwind.example",
     "subject": "URGENT: Your mailbox will be closed today",
     "external": true,
     "body": [
      "Dear user,",
      "Your mailbox exceeded its limit and will be closed in 2 hours.",
      "Click below to keep your account active."
     ],
     "button": "Keep my mailbox"
    },
    "callouts": [
     {
      "cue": 0,
      "target": "addr",
      "label": "Look-alike domain",
      "tone": "warn"
     },
     {
      "cue": 1,
      "target": "b0",
      "label": "Generic greeting",
      "tone": "warn"
     },
     {
      "cue": 2,
      "target": "b1",
      "label": "Pressure and a deadline",
      "tone": "warn"
     },
     {
      "cue": 3,
      "target": "button",
      "label": "Hover before you click",
      "tone": "warn"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Let's check a real-looking example. ^ First, the sender's domain: northwlnd, with an L instead of an I."
    },
    {
     "who": "narrator",
     "text": "^ Second, a generic greeting instead of your name. ^ Third, pressure: closed in two hours."
    },
    {
     "who": "narrator",
     "text": "^ And finally, the button. Hover over it first and check where it really goes."
    }
   ],
   "claims": [
    {
     "text": "Look-alike domains, generic greetings, urgency and disguised links are phishing red flags.",
     "source_ids": [
      "S01#c4"
     ]
    }
   ],
   "visual": "Mock email from a look-alike domain with four orange callouts",
   "duration_hint_s": 26
  },
  {
   "id": "s06_signs",
   "template": "broll_panel",
   "props": {
    "shot": "inbox",
    "kicker": "Red flags",
    "title": "Pause if you see",
    "side": "right",
    "items": [
     {
      "text": "Unexpected attachment",
      "icon": "file",
      "tone": "warn"
     },
     {
      "text": "Request for passwords or codes",
      "icon": "key",
      "tone": "warn"
     },
     {
      "text": "Payment or bank-detail change",
      "icon": "money",
      "tone": "warn"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "A few more signs to pause for: ^ an attachment you didn't expect, ^ any request for a password or a code, ^ and any change to payment or bank details."
    }
   ],
   "claims": [
    {
     "text": "Unexpected attachments, credential requests and payment changes are red flags.",
     "source_ids": [
      "S01#c4",
      "S02#p1"
     ]
    }
   ],
   "duration_hint_s": 15
  },
  {
   "id": "s07_dodont",
   "template": "do_dont",
   "props": {
    "title": "What to do",
    "dont_head": "Don't",
    "do_head": "Do",
    "dont": [
     "Click links in unexpected emails",
     "Reply to ask if it's real"
    ],
    "do": [
     "Verify using a contact you already know",
     "Press Report Phishing"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "So what do you do? ^ Don't click the link, ^ and don't reply to ask if it's real. ^ Instead, verify using a contact you already know, ^ and press the Report Phishing button."
    }
   ],
   "claims": [
    {
     "text": "Staff must report suspicious email with the Report Phishing button.",
     "source_ids": [
      "S02#p2"
     ]
    }
   ],
   "duration_hint_s": 16
  },
  {
   "id": "s08_quiz",
   "template": "quiz",
   "props": {
    "quiz_item": "Q1",
    "q": "An urgent email asks you to log in to keep your mailbox. What do you do?",
    "options": [
     "Click the button quickly",
     "Reply and ask",
     "Report it, then check via the known portal"
    ],
    "answer": 2,
    "why": "Never use the email's own link; report it and verify independently."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Quick check. An urgent email asks you to log in to keep your mailbox. What do you do?",
     "pause": 2.2
    },
    {
     "who": "narrator",
     "text": "^ The answer is C. Report it, then check through the portal you already know."
    }
   ],
   "claims": [
    {
     "text": "Report suspicious email; verify independently.",
     "source_ids": [
      "S02#p2"
     ]
    }
   ],
   "hold": 3,
   "duration_hint_s": 14
  },
  {
   "id": "s09_recap",
   "template": "checklist",
   "props": {
    "title": "Recap",
    "items": [
     "Check the sender's domain",
     "Distrust urgency",
     "Hover before you click",
     "Report, don't reply"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Let's recap. ^ Check the domain. ^ Distrust urgency. ^ Hover before you click. ^ And report, don't reply."
    }
   ],
   "claims": [
    {
     "text": "Recap of red flags and reporting.",
     "source_ids": [
      "S01#c4",
      "S02#p2"
     ]
    }
   ],
   "duration_hint_s": 12
  },
  {
   "id": "s10_outro",
   "template": "outro",
   "props": {
    "title": "Thanks for watching",
    "line": "Pause. Check. Report.",
    "evidence_line": "Completion recorded for ISO/IEC 27001 A.6.3 awareness evidence."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Thanks for watching. Pause, check, report."
    }
   ],
   "claims": [
    {
     "text": "Closing line.",
     "general_knowledge": true
    }
   ],
   "duration_hint_s": 5
  }
 ]
}
```

## doodle — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M2L1",
 "title": "How Social Engineering Works",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "doodle"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  },
  "vex": {
   "provider": "openai",
   "voice": "verse",
   "instructions": "Smug, theatrical cartoon con-artist, playful not scary."
  }
 },
 "music": {
  "bed": "whiteboard",
  "volume": 0.12
 },
 "cast": [
  "host",
  "vex",
  "learner"
 ],
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "title": "How Social Engineering Works",
    "sub": "Hacking people, not computers",
    "icon": "users"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Welcome to a quick whiteboard session on social engineering."
    }
   ],
   "claims": [
    {
     "text": "Intro.",
     "general_knowledge": true
    }
   ],
   "duration_hint_s": 5
  },
  {
   "id": "s02_what",
   "template": "whiteboard",
   "props": {
    "title": "Social engineering",
    "items": [
     {
      "cue": 0,
      "kind": "person",
      "cast": "vex",
      "pose": "rub",
      "expr": "sly",
      "x": 380,
      "y": 880
     },
     {
      "cue": 1,
      "kind": "arrow",
      "x": 560,
      "y": 600,
      "to": {
       "x": 1180,
       "y": 600
      },
      "color": "attention"
     },
     {
      "cue": 1,
      "kind": "person",
      "cast": "learner",
      "pose": "phone",
      "expr": "neutral",
      "x": 1400,
      "y": 880
     },
     {
      "cue": 2,
      "kind": "note",
      "text": "tricks people",
      "x": 760,
      "y": 520,
      "color": "ink"
     },
     {
      "cue": 3,
      "kind": "icon",
      "icon": "key",
      "x": 1600,
      "y": 300,
      "color": "attention"
     },
     {
      "cue": 3,
      "kind": "circle",
      "x": 1600,
      "y": 300,
      "w": 180,
      "h": 180,
      "color": "attention"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Meet a social engineer. ^ Instead of breaking into computers, he goes straight for people, ^ using tricks to make them do what he wants, ^ like handing over a password."
    }
   ],
   "claims": [
    {
     "text": "Social engineering manipulates people into revealing information or granting access.",
     "general_knowledge": true
    }
   ],
   "duration_hint_s": 16
  },
  {
   "id": "s03_levers",
   "template": "whiteboard",
   "props": {
    "title": "The levers",
    "items": [
     {
      "cue": 0,
      "kind": "icon",
      "icon": "clock",
      "x": 420,
      "y": 420,
      "color": "ink"
     },
     {
      "cue": 0,
      "kind": "note",
      "text": "Urgency",
      "x": 420,
      "y": 600,
      "color": "ink"
     },
     {
      "cue": 1,
      "kind": "icon",
      "icon": "badge",
      "x": 960,
      "y": 420,
      "color": "ink"
     },
     {
      "cue": 1,
      "kind": "note",
      "text": "Authority",
      "x": 960,
      "y": 600,
      "color": "ink"
     },
     {
      "cue": 2,
      "kind": "icon",
      "icon": "heart",
      "x": 1500,
      "y": 420,
      "color": "ink"
     },
     {
      "cue": 2,
      "kind": "note",
      "text": "Helpfulness",
      "x": 1500,
      "y": 600,
      "color": "ink"
     },
     {
      "cue": 3,
      "kind": "underline",
      "x": 300,
      "y": 700,
      "w": 1320,
      "color": "attention"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Three levers do most of the work. ^ Urgency, ^ authority, ^ and our wish to be helpful. ^ Spot the lever, and you've spotted the trick."
    }
   ],
   "claims": [
    {
     "text": "Common levers: urgency, authority, helpfulness.",
     "source_ids": [
      "S03#c1"
     ]
    }
   ],
   "duration_hint_s": 15
  },
  {
   "id": "s04_rules",
   "template": "whiteboard",
   "props": {
    "title": "Three rules",
    "items": [
     {
      "cue": 0,
      "kind": "check",
      "x": 360,
      "y": 380,
      "color": "safe"
     },
     {
      "cue": 0,
      "kind": "note",
      "text": "Verify on a known number",
      "x": 820,
      "y": 380,
      "color": "ink"
     },
     {
      "cue": 1,
      "kind": "check",
      "x": 360,
      "y": 560,
      "color": "safe"
     },
     {
      "cue": 1,
      "kind": "note",
      "text": "Never share passwords",
      "x": 820,
      "y": 560,
      "color": "ink"
     },
     {
      "cue": 2,
      "kind": "check",
      "x": 360,
      "y": 740,
      "color": "safe"
     },
     {
      "cue": 2,
      "kind": "note",
      "text": "Report it",
      "x": 820,
      "y": 740,
      "color": "ink"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Three rules keep you safe. ^ Verify the person on a number you already know. ^ Never share a password, with anyone. ^ And report anything odd."
    }
   ],
   "claims": [
    {
     "text": "Verify identity, never share passwords, report.",
     "source_ids": [
      "S03#c2"
     ]
    }
   ],
   "duration_hint_s": 14
  },
  {
   "id": "s05_quiz",
   "template": "quiz",
   "props": {
    "quiz_item": "Q1",
    "q": "A caller from 'IT' needs your password to fix your account. You…",
    "options": [
     "Give it",
     "Hang up and call IT on the known number",
     "Email it instead"
    ],
    "answer": 1
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Quick check. A caller from IT needs your password. What do you do?",
     "pause": 2.2
    },
    {
     "who": "narrator",
     "text": "^ B. Hang up and call IT on the number you already know."
    }
   ],
   "claims": [
    {
     "text": "Never share passwords; verify on a known number.",
     "source_ids": [
      "S03#c2"
     ]
    }
   ],
   "hold": 3
  },
  {
   "id": "s06_outro",
   "template": "outro",
   "props": {
    "line": "Stop. Verify. Then act."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Stop, verify, then act."
    }
   ],
   "claims": [
    {
     "text": "Closing.",
     "general_knowledge": true
    }
   ]
  }
 ]
}
```

## cartoon — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M3L2",
 "title": "Midnight Push Notifications",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "cartoon"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  },
  "rookie": {
   "provider": "openai",
   "voice": "ballad",
   "instructions": "Good-natured, sleepy office worker in a comic cartoon; quick to panic."
  },
  "vex": {
   "provider": "openai",
   "voice": "verse",
   "instructions": "Smug, theatrical cartoon con-artist, playful not scary."
  },
  "mentor": {
   "provider": "openai",
   "voice": "echo",
   "instructions": "Calm, friendly security expert; warm, clear, a little dry humour."
  }
 },
 "music": {
  "bed": "cartoon",
  "volume": 0.12
 },
 "cast": [
  "rookie",
  "vex",
  "mentor"
 ],
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "kicker": "A micro-drama",
    "title": "Midnight Push Notifications",
    "icon": "smartphone"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Midnight push notifications: a short story about one sleepy tap."
    }
   ],
   "claims": [
    {
     "text": "Intro.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "s02_night",
   "template": "cartoon",
   "props": {
    "set": "home",
    "night": true,
    "people": [
     {
      "cast": "rookie",
      "x": 960,
      "y": 1060,
      "s": 1.3,
      "pose": "phone",
      "expr": "neutral",
      "holding": "phone"
     }
    ],
    "beats": [
     {
      "cue": 0,
      "cast": "rookie",
      "pose": "phone",
      "expr": "worried",
      "sfx": "ding"
     },
     {
      "cue": 1,
      "camera": {
       "zoom": 1.4,
       "x": 960,
       "y": 520
      }
     }
    ],
    "bubbles": [
     {
      "cue": 1,
      "out_cue": 2,
      "who": "rookie",
      "text": "Another login request? At midnight?",
      "think": true
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "It's midnight. ^ Sam's phone buzzes with a sign-in request he didn't make."
    },
    {
     "who": "rookie",
     "text": "^ Another login request? At midnight?"
    },
    {
     "who": "narrator",
     "text": "^ He taps Deny. Then it buzzes again."
    }
   ],
   "claims": [
    {
     "text": "Unexpected MFA prompts mean someone else is trying to sign in.",
     "source_ids": [
      "S04#c1"
     ]
    }
   ],
   "duration_hint_s": 14
  },
  {
   "id": "s03_spam",
   "template": "mfa_prompt",
   "props": {
    "app": "Northwind Sign-in",
    "place": "Unknown location",
    "count_to": 12,
    "caption": "Prompt after prompt"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ And again. And again. Twelve prompts in a few minutes. ^ The attacker already has Sam's password, and is hoping he'll tap Approve just to make it stop."
    }
   ],
   "claims": [
    {
     "text": "MFA fatigue: repeated prompts aim to make the user approve.",
     "source_ids": [
      "S04#c2"
     ]
    }
   ],
   "duration_hint_s": 12
  },
  {
   "id": "s04_vex",
   "template": "cartoon",
   "props": {
    "set": "den",
    "night": true,
    "people": [
     {
      "cast": "vex",
      "x": 960,
      "y": 1060,
      "s": 1.3,
      "pose": "rub",
      "expr": "sly",
      "holding": "laptop"
     }
    ],
    "beats": [
     {
      "cue": 0,
      "cast": "vex",
      "pose": "cross",
      "expr": "sly"
     }
    ],
    "bubbles": [
     {
      "cue": 0,
      "who": "vex",
      "text": "Everyone taps Approve eventually.",
      "tone": "villain"
     }
    ]
   },
   "narration": [
    {
     "who": "vex",
     "text": "^ Relax. Everyone taps Approve eventually."
    }
   ],
   "claims": [
    {
     "text": "Attackers rely on fatigue and annoyance.",
     "general_knowledge": true
    }
   ],
   "duration_hint_s": 6
  },
  {
   "id": "s05_mentor",
   "template": "cartoon",
   "props": {
    "set": "office",
    "people": [
     {
      "cast": "mentor",
      "x": 700,
      "y": 1060,
      "s": 1.2,
      "pose": "present",
      "expr": "happy"
     },
     {
      "cast": "rookie",
      "x": 1250,
      "y": 1060,
      "s": 1.2,
      "pose": "idle",
      "expr": "worried",
      "flip": true
     }
    ],
    "beats": [
     {
      "cue": 0,
      "cast": "mentor",
      "pose": "stop"
     },
     {
      "cue": 1,
      "cast": "rookie",
      "expr": "happy",
      "pose": "cheer"
     }
    ],
    "bubbles": [
     {
      "cue": 0,
      "who": "mentor",
      "text": "Didn't start a login? Deny and report.",
      "tone": "plain"
     }
    ]
   },
   "narration": [
    {
     "who": "mentor",
     "text": "Sam, ^ if you didn't start a sign-in, never approve it. Deny it, and report it to us straight away."
    },
    {
     "who": "mentor",
     "text": "^ Then we reset your password, so the prompts stop for good."
    }
   ],
   "claims": [
    {
     "text": "Deny unexpected prompts, report, reset password.",
     "source_ids": [
      "S04#c3"
     ]
    }
   ],
   "duration_hint_s": 14
  },
  {
   "id": "s06_steps",
   "template": "steps",
   "props": {
    "title": "If prompts keep coming",
    "steps": [
     {
      "icon": "x",
      "label": "Deny"
     },
     {
      "icon": "flag",
      "label": "Report to IT"
     },
     {
      "icon": "key",
      "label": "Change password"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "So if the prompts keep coming: ^ deny, ^ report, ^ and change your password."
    }
   ],
   "claims": [
    {
     "text": "Deny, report, change password.",
     "source_ids": [
      "S04#c3"
     ]
    }
   ]
  },
  {
   "id": "s07_quiz",
   "template": "quiz",
   "props": {
    "quiz_item": "Q1",
    "q": "Ten sign-in prompts you didn't start. Best move?",
    "options": [
     "Approve once",
     "Deny and report",
     "Ignore"
    ],
    "answer": 1
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Quick check. Ten sign-in prompts you didn't start. Best move?",
     "pause": 2.2
    },
    {
     "who": "narrator",
     "text": "^ Deny and report."
    }
   ],
   "claims": [
    {
     "text": "Deny and report.",
     "source_ids": [
      "S04#c3"
     ]
    }
   ],
   "hold": 3
  },
  {
   "id": "s08_outro",
   "template": "outro",
   "props": {
    "line": "Didn't start it? Don't approve it."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Didn't start it? Don't approve it."
    }
   ],
   "claims": [
    {
     "text": "Closing.",
     "general_knowledge": true
    }
   ]
  }
 ]
}
```

## comic — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M4L1",
 "title": "The Friendly Tailgater",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "9:16",
 "fps": 30,
 "formats": [
  "comic"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  },
  "learner": {
   "provider": "openai",
   "voice": "ash",
   "instructions": "Friendly, polite office worker."
  },
  "vex": {
   "provider": "openai",
   "voice": "verse",
   "instructions": "Over-friendly courier, smooth talker, playful not scary."
  }
 },
 "music": {
  "bed": "cartoon",
  "volume": 0.12
 },
 "cast": [
  "learner",
  "vex",
  "manager"
 ],
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "kicker": "Comic",
    "title": "The Friendly Tailgater",
    "icon": "door"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "The friendly tailgater. A three-panel story."
    }
   ],
   "claims": [
    {
     "text": "Intro.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "s02_strip1",
   "template": "comic",
   "props": {
    "layout": "3-row",
    "panels": [
     {
      "cue": 0,
      "set": "reception",
      "people": [
       {
        "cast": "vex",
        "x": 640,
        "y": 1000,
        "s": 1.0,
        "pose": "hold",
        "expr": "happy",
        "holding": "paper"
       }
      ],
      "caption": "8:58 a.m. Arms full of boxes."
     },
     {
      "cue": 1,
      "set": "reception",
      "people": [
       {
        "cast": "learner",
        "x": 420,
        "y": 1000,
        "s": 1.0,
        "pose": "idle",
        "expr": "neutral",
        "holding": "card"
       },
       {
        "cast": "vex",
        "x": 760,
        "y": 1000,
        "s": 1.0,
        "pose": "hold",
        "expr": "happy"
       }
      ],
      "bubbles": [
       {
        "who": "vex",
        "text": "Could you hold the door? My hands are full!"
       }
      ]
     },
     {
      "cue": 2,
      "set": "openOffice",
      "people": [
       {
        "cast": "vex",
        "x": 600,
        "y": 1000,
        "s": 1.0,
        "pose": "rub",
        "expr": "sly"
       }
      ],
      "bubbles": [
       {
        "who": "vex",
        "text": "Too easy.",
        "think": true
       }
      ],
      "sfx_word": "CLICK"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Nine o'clock. A courier with arms full of boxes waits by the secure door."
    },
    {
     "who": "vex",
     "text": "^ Could you hold the door? My hands are full!"
    },
    {
     "who": "narrator",
     "text": "^ One polite gesture, and a stranger is inside without a badge."
    }
   ],
   "claims": [
    {
     "text": "Tailgating: following an authorised person through a secure door.",
     "source_ids": [
      "S05#c1"
     ]
    }
   ],
   "duration_hint_s": 18
  },
  {
   "id": "s03_strip2",
   "template": "comic",
   "props": {
    "layout": "1+2",
    "panels": [
     {
      "cue": 0,
      "set": "reception",
      "people": [
       {
        "cast": "learner",
        "x": 640,
        "y": 1000,
        "s": 1.0,
        "pose": "stop",
        "expr": "neutral"
       }
      ],
      "bubbles": [
       {
        "who": "learner",
        "text": "Reception will sign you in."
       }
      ]
     },
     {
      "cue": 1,
      "set": "reception",
      "people": [
       {
        "cast": "manager",
        "x": 640,
        "y": 1000,
        "s": 1.0,
        "pose": "point",
        "expr": "happy"
       }
      ],
      "caption": "Visitors sign in at reception."
     },
     {
      "cue": 2,
      "set": "reception",
      "people": [
       {
        "cast": "learner",
        "x": 640,
        "y": 1000,
        "s": 1.0,
        "pose": "cheer",
        "expr": "happy"
       }
      ],
      "caption": "Kind and secure."
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Let's rewind. ^ This time, Nour smiles and points to reception."
    },
    {
     "who": "narrator",
     "text": "^ Visitors sign in there and get escorted. ^ Polite, and secure."
    }
   ],
   "claims": [
    {
     "text": "Visitors must sign in at reception and be escorted.",
     "source_ids": [
      "S05#c2"
     ]
    }
   ],
   "duration_hint_s": 14
  },
  {
   "id": "s04_dodont",
   "template": "do_dont",
   "props": {
    "title": "At secure doors",
    "dont": [
     "Hold the door for strangers"
    ],
    "do": [
     "Send visitors to reception",
     "Report unbadged people"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "At secure doors: ^ don't hold them for strangers. ^ Send visitors to reception, ^ and report anyone without a badge."
    }
   ],
   "claims": [
    {
     "text": "Door policy.",
     "source_ids": [
      "S05#c2"
     ]
    }
   ]
  },
  {
   "id": "s05_outro",
   "template": "outro",
   "props": {
    "line": "Kind is fine. Badge first."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Kind is fine. Badge first."
    }
   ],
   "claims": [
    {
     "text": "Closing.",
     "general_knowledge": true
    }
   ]
  }
 ]
}
```

## narrated-deck — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-finance-onboarding",
 "lesson_id": "M1L2",
 "title": "Submitting Expense Claims",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "narrated-deck"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  }
 },
 "music": {
  "bed": "executive",
  "volume": 0.12
 },
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "kicker": "Finance onboarding",
    "title": "Submitting Expense Claims",
    "sub": "Module 1 · Lesson 2",
    "icon": "invoice"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Welcome to lesson two: how to submit an expense claim that gets approved the first time."
    }
   ],
   "claims": [
    {
     "text": "Intro.",
     "general_knowledge": true
    }
   ],
   "notes": "Presenter: ask who has submitted a claim before."
  },
  {
   "id": "s02_rules",
   "template": "bullets",
   "props": {
    "title": "Before you start",
    "items": [
     {
      "text": "Claim within 30 days",
      "icon": "calendar"
     },
     {
      "text": "Attach an itemised receipt",
      "icon": "file"
     },
     {
      "text": "Choose the right cost centre",
      "icon": "layers"
     },
     {
      "text": "Personal items are not claimable",
      "icon": "x",
      "tone": "warn"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Before you start, four rules. ^ Claim within thirty days. ^ Attach an itemised receipt. ^ Choose the right cost centre. ^ And personal items aren't claimable."
    }
   ],
   "claims": [
    {
     "text": "Claims must be submitted within 30 days with itemised receipts.",
     "source_ids": [
      "S01#p3"
     ]
    },
    {
     "text": "Cost-centre and personal-item rules.",
     "source_ids": [
      "S01#p4"
     ]
    }
   ],
   "notes": "Speaker notes = narration. Slide shows the four rules; reveal one per click."
  },
  {
   "id": "s03_limits",
   "template": "table",
   "props": {
    "title": "Daily limits",
    "columns": [
     "Item",
     "Limit",
     "Needs approval above"
    ],
    "rows": [
     [
      "Meals",
      "40 per day",
      "Manager"
     ],
     [
      "Hotel",
      "150 per night",
      "Finance"
     ],
     [
      "Taxi",
      "Actual cost",
      "None"
     ]
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Here are the daily limits. Anything above them needs the approver in the right-hand column."
    }
   ],
   "claims": [
    {
     "text": "Daily limits table.",
     "source_ids": [
      "S01#p5"
     ]
    }
   ],
   "notes": "Currency per local policy; values illustrative (fictional Northwind policy)."
  },
  {
   "id": "s04_flow",
   "template": "process_flow",
   "props": {
    "title": "Approval path",
    "nodes": [
     {
      "id": "a",
      "label": "You submit",
      "kind": "start"
     },
     {
      "id": "b",
      "label": "Manager approves",
      "kind": "step"
     },
     {
      "id": "c",
      "label": "Above limit?",
      "kind": "decision"
     },
     {
      "id": "d",
      "label": "Finance review",
      "kind": "step"
     },
     {
      "id": "e",
      "label": "Paid with salary",
      "kind": "end"
     }
    ],
    "edges": [
     {
      "from": "a",
      "to": "b"
     },
     {
      "from": "b",
      "to": "c"
     },
     {
      "from": "c",
      "to": "d",
      "label": "yes"
     },
     {
      "from": "c",
      "to": "e",
      "label": "no"
     },
     {
      "from": "d",
      "to": "e"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ You submit. ^ Your manager approves. ^ If it's above a limit, finance reviews it. ^ Then it's paid with your next salary."
    }
   ],
   "claims": [
    {
     "text": "Approval path.",
     "source_ids": [
      "S01#p6"
     ]
    }
   ]
  },
  {
   "id": "s05_check",
   "template": "checklist",
   "props": {
    "title": "Before you press Submit",
    "items": [
     "Receipt attached",
     "Cost centre selected",
     "Within 30 days",
     "Business purpose written"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Before you press submit: ^ receipt, ^ cost centre, ^ thirty days, ^ and a one-line business purpose."
    }
   ],
   "claims": [
    {
     "text": "Submission checklist.",
     "source_ids": [
      "S01#p3",
      "S01#p4"
     ]
    }
   ]
  },
  {
   "id": "s06_quiz",
   "template": "quiz",
   "props": {
    "quiz_item": "Q2",
    "q": "A hotel night costs 180. Who must approve?",
    "options": [
     "Nobody",
     "Manager only",
     "Manager, then Finance"
    ],
    "answer": 2
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Quick check. A hotel night costs one hundred and eighty. Who approves?",
     "pause": 2.2
    },
    {
     "who": "narrator",
     "text": "^ Your manager, then finance, because it's above the limit."
    }
   ],
   "claims": [
    {
     "text": "Hotel limit 150.",
     "source_ids": [
      "S01#p5"
     ]
    }
   ],
   "hold": 3
  },
  {
   "id": "s07_outro",
   "template": "outro",
   "props": {
    "title": "Next: travel bookings",
    "line": "Receipt, cost centre, thirty days."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "That's it. Receipt, cost centre, thirty days."
    }
   ],
   "claims": [
    {
     "text": "Closing.",
     "general_knowledge": true
    }
   ]
  }
 ]
}
```

## mindmap — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M5L1",
 "title": "Data Classification at a Glance",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "mindmap"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  }
 },
 "music": {
  "bed": "explainer",
  "volume": 0.12
 },
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "title": "Data Classification at a Glance",
    "icon": "layers"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Data classification, at a glance."
    }
   ],
   "claims": [
    {
     "text": "Intro.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "s02_map",
   "template": "mindmap",
   "props": {
    "root": "Northwind data",
    "nodes": [
     {
      "id": "pub",
      "label": "Public",
      "parent": "root",
      "cue": 0,
      "icon": "globe",
      "tone": "safe"
     },
     {
      "id": "pub1",
      "label": "Website, brochures",
      "parent": "pub",
      "cue": 1
     },
     {
      "id": "int",
      "label": "Internal",
      "parent": "root",
      "cue": 2,
      "icon": "building",
      "tone": "info"
     },
     {
      "id": "int1",
      "label": "Org chart, policies",
      "parent": "int",
      "cue": 3
     },
     {
      "id": "con",
      "label": "Confidential",
      "parent": "root",
      "cue": 4,
      "icon": "lock",
      "tone": "warn"
     },
     {
      "id": "con1",
      "label": "Contracts, salaries",
      "parent": "con",
      "cue": 5
     },
     {
      "id": "con2",
      "label": "Customer personal data",
      "parent": "con",
      "cue": 6
     }
    ],
    "focus": [
     {
      "cue": 4,
      "node": "con"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "All our data sits in three levels. ^ Public: ^ things already on our website. ^ Internal: ^ fine to share with colleagues, like the org chart. ^ And Confidential: ^ contracts and salaries, ^ and any personal data about customers."
    }
   ],
   "claims": [
    {
     "text": "Three classification levels with examples.",
     "source_ids": [
      "S06#c1",
      "S06#c2"
     ]
    }
   ],
   "duration_hint_s": 24
  },
  {
   "id": "s03_rule",
   "template": "definition",
   "props": {
    "term": "Confidential",
    "def": "Share only with people who need it for their job, through approved tools.",
    "icon": "lock"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ The rule for confidential data: share only with people who need it, using approved tools."
    }
   ],
   "claims": [
    {
     "text": "Need-to-know rule.",
     "source_ids": [
      "S06#c3"
     ]
    }
   ]
  },
  {
   "id": "s04_quiz",
   "template": "quiz",
   "props": {
    "quiz_item": "Q1",
    "q": "A customer list with phone numbers is…",
    "options": [
     "Public",
     "Internal",
     "Confidential"
    ],
    "answer": 2
   },
   "narration": [
    {
     "who": "narrator",
     "text": "A customer list with phone numbers. Which level?",
     "pause": 2.2
    },
    {
     "who": "narrator",
     "text": "^ Confidential: it's personal data."
    }
   ],
   "claims": [
    {
     "text": "Customer personal data is confidential.",
     "source_ids": [
      "S06#c2"
     ]
    }
   ],
   "hold": 3
  },
  {
   "id": "s05_outro",
   "template": "outro",
   "props": {
    "line": "Label it, then share it right."
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Label it, then share it right."
    }
   ],
   "claims": [
    {
     "text": "Closing.",
     "general_knowledge": true
    }
   ]
  }
 ]
}
```

## branching — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-it",
 "lesson_id": "M2L3",
 "title": "The Urgent Reset Call",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "branching",
  "cartoon"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  },
  "support": {
   "provider": "openai",
   "voice": "nova",
   "instructions": "Helpful, busy help-desk agent; friendly and quick."
  },
  "vex": {
   "provider": "openai",
   "voice": "verse",
   "instructions": "Stressed-sounding caller pretending to be an executive; pushy but polite."
  },
  "mentor": {
   "provider": "openai",
   "voice": "echo",
   "instructions": "Calm security lead giving feedback."
  }
 },
 "music": {
  "bed": "cartoon",
  "volume": 0.12
 },
 "cast": [
  "support",
  "vex",
  "mentor"
 ],
 "branching": {
  "start": "n_intro",
  "nodes": [
   {
    "id": "n_intro",
    "scenes": [
     "b01_call",
     "b02_choice1"
    ],
    "outcome": "continue"
   },
   {
    "id": "n_reset",
    "scenes": [
     "b03_reset"
    ],
    "outcome": "bad",
    "score": 0,
    "feedback": "You reset an account on an unverified call. That's exactly what the attacker needed."
   },
   {
    "id": "n_verify",
    "scenes": [
     "b04_verify",
     "b05_choice2"
    ],
    "outcome": "continue",
    "score": 5
   },
   {
    "id": "n_cave",
    "scenes": [
     "b06_cave"
    ],
    "outcome": "bad",
    "score": 2,
    "feedback": "Pressure won. Escalation is the right move, not a shortcut."
   },
   {
    "id": "n_good",
    "scenes": [
     "b07_good"
    ],
    "outcome": "good",
    "score": 10,
    "feedback": "You verified through a known channel and escalated. Attack stopped."
   }
  ]
 },
 "scenes": [
  {
   "id": "b01_call",
   "template": "cartoon",
   "props": {
    "set": "office",
    "desk": true,
    "people": [
     {
      "cast": "support",
      "x": 900,
      "y": 1060,
      "s": 1.3,
      "pose": "phone",
      "expr": "neutral",
      "lowerHidden": true
     }
    ],
    "bubbles": [
     {
      "cue": 0,
      "who": "vex",
      "text": "I'm the CFO, I'm locked out, board meeting in five minutes!",
      "tone": "villain"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "You're on the help desk. The phone rings."
    },
    {
     "who": "vex",
     "text": "^ It's the CFO. I'm locked out and the board meets in five minutes. Reset my password and MFA now!"
    }
   ],
   "claims": [
    {
     "text": "Help-desk impersonation calls use urgency and authority.",
     "source_ids": [
      "S07#c1"
     ]
    }
   ]
  },
  {
   "id": "b02_choice1",
   "template": "decision",
   "props": {
    "prompt": "What do you do?",
    "choices": [
     {
      "id": "a",
      "label": "Reset it now. It's the CFO.",
      "next": "n_reset",
      "correct": false
     },
     {
      "id": "b",
      "label": "Call back on the number in the directory",
      "next": "n_verify",
      "correct": true
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "What do you do?"
    }
   ],
   "claims": [
    {
     "text": "Decision point.",
     "general_knowledge": true
    }
   ],
   "hold": 1
  },
  {
   "id": "b03_reset",
   "template": "statement",
   "props": {
    "text": "The caller wasn't the CFO.",
    "sub": "The attacker now controls an executive account.",
    "icon": "alert"
   },
   "narration": [
    {
     "who": "mentor",
     "text": "^ The caller wasn't the CFO. An unverified reset handed the attacker an executive account."
    }
   ],
   "claims": [
    {
     "text": "Unverified resets enable account takeover.",
     "source_ids": [
      "S07#c2"
     ]
    }
   ]
  },
  {
   "id": "b04_verify",
   "template": "cartoon",
   "props": {
    "set": "office",
    "people": [
     {
      "cast": "support",
      "x": 900,
      "y": 1060,
      "s": 1.3,
      "pose": "phone",
      "expr": "think"
     }
    ],
    "bubbles": [
     {
      "cue": 0,
      "who": "vex",
      "text": "No time! Just do it or I'll escalate!",
      "tone": "villain"
     }
    ]
   },
   "narration": [
    {
     "who": "support",
     "text": "I'll call you back on your directory number."
    },
    {
     "who": "vex",
     "text": "^ No time! Just do it or I'll escalate!"
    }
   ],
   "claims": [
    {
     "text": "Callback verification via directory number.",
     "source_ids": [
      "S07#c3"
     ]
    }
   ]
  },
  {
   "id": "b05_choice2",
   "template": "decision",
   "props": {
    "prompt": "The caller pushes back. Now?",
    "choices": [
     {
      "id": "a",
      "label": "Make an exception, just this once",
      "next": "n_cave",
      "correct": false
     },
     {
      "id": "b",
      "label": "Hold the line; escalate to security",
      "next": "n_good",
      "correct": true
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "The caller pushes back. Now what?"
    }
   ],
   "claims": [
    {
     "text": "Decision point.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "b06_cave",
   "template": "statement",
   "props": {
    "text": "Pressure is the attack.",
    "icon": "alert"
   },
   "narration": [
    {
     "who": "mentor",
     "text": "^ Pressure is the attack. Exceptions are what the caller is counting on."
    }
   ],
   "claims": [
    {
     "text": "Pressure tactics.",
     "source_ids": [
      "S07#c1"
     ]
    }
   ]
  },
  {
   "id": "b07_good",
   "template": "cartoon",
   "props": {
    "set": "office",
    "people": [
     {
      "cast": "support",
      "x": 760,
      "y": 1060,
      "s": 1.2,
      "pose": "cheer",
      "expr": "happy"
     },
     {
      "cast": "mentor",
      "x": 1200,
      "y": 1060,
      "s": 1.2,
      "pose": "point",
      "expr": "happy",
      "flip": true
     }
    ]
   },
   "narration": [
    {
     "who": "mentor",
     "text": "^ Perfect. The real CFO was in the building and never called. You stopped it."
    }
   ],
   "claims": [
    {
     "text": "Verification and escalation stop help-desk SE.",
     "source_ids": [
      "S07#c3"
     ]
    }
   ]
  }
 ]
}
```

## screencast-sim — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-finance-onboarding",
 "lesson_id": "M1L3",
 "title": "Practice: File an Expense Claim",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "screencast-sim"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  }
 },
 "music": {
  "bed": "explainer",
  "volume": 0.12
 },
 "scenes": [
  {
   "id": "s01_title",
   "template": "title",
   "props": {
    "title": "File an Expense Claim",
    "sub": "Watch, then try it yourself",
    "icon": "click"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Let's file a claim. Watch once, then try it yourself."
    }
   ],
   "claims": [
    {
     "text": "Intro.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "s02_demo",
   "template": "screencast",
   "props": {
    "app": {
     "kind": "form",
     "title": "Northwind Expenses · New claim",
     "fields": [
      {
       "id": "date",
       "label": "Date",
       "kind": "date"
      },
      {
       "id": "cat",
       "label": "Category",
       "kind": "select"
      },
      {
       "id": "amount",
       "label": "Amount",
       "kind": "amount"
      },
      {
       "id": "receipt",
       "label": "Receipt",
       "kind": "file"
      },
      {
       "id": "submit",
       "label": "Submit",
       "kind": "button"
      }
     ]
    },
    "actions": [
     {
      "cue": 0,
      "do": "click",
      "target": "date"
     },
     {
      "cue": 1,
      "do": "select",
      "target": "cat",
      "value": "Taxi"
     },
     {
      "cue": 2,
      "do": "type",
      "target": "amount",
      "value": "23.50"
     },
     {
      "cue": 3,
      "do": "click",
      "target": "receipt",
      "label": "Attach the photo"
     },
     {
      "cue": 4,
      "do": "click",
      "target": "submit"
     },
     {
      "cue": 5,
      "do": "toast",
      "label": "Claim sent to your manager"
     }
    ],
    "sim": {
     "mode": "demo"
    }
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Pick the date. ^ Choose the category, Taxi. ^ Type the amount. ^ Attach the receipt photo. ^ Press submit, ^ and the claim goes to your manager."
    }
   ],
   "claims": [
    {
     "text": "Expense portal steps.",
     "source_ids": [
      "S08#c1"
     ]
    }
   ],
   "duration_hint_s": 22
  },
  {
   "id": "s03_try",
   "template": "screencast",
   "props": {
    "app": {
     "kind": "form",
     "title": "Northwind Expenses · New claim",
     "fields": [
      {
       "id": "date",
       "label": "Date",
       "kind": "date"
      },
      {
       "id": "cat",
       "label": "Category",
       "kind": "select"
      },
      {
       "id": "amount",
       "label": "Amount",
       "kind": "amount"
      },
      {
       "id": "receipt",
       "label": "Receipt",
       "kind": "file"
      },
      {
       "id": "submit",
       "label": "Submit",
       "kind": "button"
      }
     ]
    },
    "actions": [
     {
      "cue": 0,
      "do": "highlight",
      "target": "cat",
      "label": "Your turn: pick the category"
     },
     {
      "cue": 1,
      "do": "callout",
      "target": "receipt",
      "label": "Don't forget the receipt"
     }
    ],
    "sim": {
     "mode": "practice",
     "task": "File a 23.50 taxi claim for today",
     "expect": [
      {
       "target": "cat",
       "value": "Taxi"
      },
      {
       "target": "amount",
       "value": "23.50"
      },
      {
       "target": "receipt",
       "value": "*"
      },
      {
       "target": "submit"
      }
     ],
     "hints": {
      "receipt": "Itemised receipts are mandatory."
     },
     "max_attempts": 3,
     "on_fail": "replay_demo"
    }
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Your turn. File a taxi claim for twenty-three fifty. ^ And don't forget the receipt."
    }
   ],
   "claims": [
    {
     "text": "Receipts mandatory.",
     "source_ids": [
      "S01#p3"
     ]
    }
   ],
   "notes": "Video target shows the guided overlay; lesson/SCORM target makes it interactive."
  },
  {
   "id": "s04_recap",
   "template": "checklist",
   "props": {
    "title": "You did it",
    "items": [
     "Date",
     "Category",
     "Amount",
     "Receipt",
     "Submit"
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Date, ^ category, ^ amount, ^ receipt, ^ submit. That is the whole flow."
    }
   ],
   "claims": [
    {
     "text": "Expense portal steps.",
     "source_ids": [
      "S08#c1"
     ]
    }
   ]
  }
 ]
}
```

## job-aid — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-basics",
 "lesson_id": "M1L1-jobaid",
 "title": "Phishing Red-Flag Card",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "16:9",
 "fps": 30,
 "formats": [
  "job-aid"
 ],
 "wpm": 150,
 "objective_ids": [
  "O1",
  "O2"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  }
 },
 "music": {
  "bed": "explainer",
  "volume": 0.12
 },
 "scenes": [
  {
   "id": "j01_header",
   "template": "title",
   "props": {
    "kicker": "Job aid · keep at your desk",
    "title": "Phishing Red-Flag Card",
    "icon": "shieldAlert"
   },
   "narration": [],
   "claims": [
    {
     "text": "Header.",
     "general_knowledge": true
    }
   ]
  },
  {
   "id": "j02_flags",
   "template": "checklist",
   "props": {
    "title": "Pause if you see",
    "items": [
     "Look-alike sender domain",
     "Urgency or a deadline",
     "Generic greeting",
     "Unexpected attachment or link",
     "Request for passwords or codes",
     "Change of bank details"
    ]
   },
   "narration": [],
   "claims": [
    {
     "text": "Red flags.",
     "source_ids": [
      "S01#c4",
      "S02#p1"
     ]
    }
   ]
  },
  {
   "id": "j03_do",
   "template": "do_dont",
   "props": {
    "title": "Then",
    "dont": [
     "Click, reply or forward"
    ],
    "do": [
     "Press Report Phishing",
     "Verify via a known contact"
    ]
   },
   "narration": [],
   "claims": [
    {
     "text": "Reporting rule.",
     "source_ids": [
      "S02#p2"
     ]
    }
   ]
  },
  {
   "id": "j04_clicked",
   "template": "steps",
   "props": {
    "title": "Clicked already?",
    "danger": true,
    "steps": [
     {
      "icon": "wifi",
      "label": "Disconnect"
     },
     {
      "icon": "phone",
      "label": "Call the service desk"
     },
     {
      "icon": "key",
      "label": "Change your password"
     }
    ]
   },
   "narration": [],
   "claims": [
    {
     "text": "If you clicked: disconnect, call, change password.",
     "source_ids": [
      "S02#p3"
     ]
    }
   ]
  },
  {
   "id": "j05_contacts",
   "template": "table",
   "props": {
    "title": "Who to contact",
    "columns": [
     "What",
     "Where"
    ],
    "rows": [
     [
      "Suspicious email",
      "Report Phishing button"
     ],
     [
      "Clicked a link",
      "Service desk, ext. 4400"
     ]
    ]
   },
   "narration": [],
   "claims": [
    {
     "text": "Contacts.",
     "source_ids": [
      "S02#p3"
     ]
    }
   ],
   "notes": "Extension numbers are fictional placeholders; replace from the client's policy."
  }
 ]
}
```

## series — example.storyboard.json
```json
{
 "schema_version": "1.0",
 "course_id": "northwind-security-series",
 "lesson_id": "E03N1",
 "title": "Nudge: Smishing in 45 Seconds",
 "language": "en-US",
 "direction": "ltr",
 "subtitle_languages": [
  "ar-EG"
 ],
 "aspect": "9:16",
 "fps": 30,
 "formats": [
  "series"
 ],
 "wpm": 150,
 "objective_ids": [
  "O3"
 ],
 "theme": {
  "preset": "neutral",
  "logo": null
 },
 "voices": {
  "narrator": {
   "provider": "openai",
   "model": "gpt-4o-mini-tts",
   "voice": "marin",
   "lang": "en-US",
   "instructions": "Warm, confident corporate trainer speaking to colleagues. Clear, friendly, natural pace; brief pauses between list items. Never robotic."
  }
 },
 "music": {
  "bed": "explainer",
  "volume": 0.12
 },
 "scenes": [
  {
   "id": "n01_hook",
   "template": "chat_mock",
   "props": {
    "device": "phone",
    "title": "Messages",
    "messages": [
     {
      "text": "NorthPost: your parcel is on hold. Pay 1.99 to release it: npost-delivery.example/pay",
      "warn": true,
      "cue": 0
     }
    ],
    "callouts": [
     {
      "cue": 1,
      "label": "Odd link, tiny fee, urgency",
      "tone": "warn"
     }
    ]
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ A text says your parcel's on hold, pay a tiny fee. ^ Odd link, small fee, urgency. That's smishing."
    }
   ],
   "claims": [
    {
     "text": "Smishing uses delivery-fee lures with links.",
     "source_ids": [
      "S09#c1"
     ]
    }
   ],
   "duration_hint_s": 12
  },
  {
   "id": "n02_card",
   "template": "flashcard",
   "props": {
    "front": "Parcel text with a payment link?",
    "back": "Don't tap. Check the courier's own app or site.",
    "icon": "smartphone"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "^ Flip it: don't tap. Check the courier's own app instead."
    }
   ],
   "claims": [
    {
     "text": "Verify via official app.",
     "source_ids": [
      "S09#c2"
     ]
    }
   ],
   "duration_hint_s": 10
  },
  {
   "id": "n03_quiz",
   "template": "quiz",
   "props": {
    "quiz_item": "Q7",
    "q": "Safest move?",
    "options": [
     "Tap and pay 1.99",
     "Open the courier's own app"
    ],
    "answer": 1
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Safest move?",
     "pause": 2.0
    },
    {
     "who": "narrator",
     "text": "^ Open the courier's own app. Plus ten points!"
    }
   ],
   "claims": [
    {
     "text": "Verify via official app.",
     "source_ids": [
      "S09#c2"
     ]
    }
   ],
   "hold": 2
  },
  {
   "id": "n04_outro",
   "template": "outro",
   "props": {
    "line": "Streak +1 · Episode 4 drops Monday"
   },
   "narration": [
    {
     "who": "narrator",
     "text": "Streak plus one. See you Monday."
    }
   ],
   "claims": [
    {
     "text": "Series nudge closing.",
     "general_knowledge": true
    }
   ]
  }
 ]
}
```
