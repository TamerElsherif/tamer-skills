# DOMAIN PACK: security-awareness

## compliance.yaml
```yaml
# Compliance mapping: what training evidence to keep. This is general knowledge about the frameworks, not legal or audit
# advice — confirm scope and wording with the client's ISMS owner / auditor. Control titles paraphrased.
schema_version: "1.0"
general_knowledge: true
frameworks:
  iso27001_2022:
    name: "ISO/IEC 27001:2022"
    controls:
      - id: "A.6.3"
        title: "Information security awareness, education and training"
        meaning: "Personnel and relevant interested parties receive appropriate, regularly updated awareness, education and training relevant to their role."
      - id: "7.2"
        title: "Competence (clause)"
        meaning: "Determine needed competence, ensure it (e.g. through training), evaluate effectiveness, retain documented information as evidence."
      - id: "7.3"
        title: "Awareness (clause)"
        meaning: "People are aware of the policy, their contribution, and the implications of not conforming."
    evidence_line: "Completion recorded as ISO/IEC 27001:2022 A.6.3 awareness evidence."
  soc2:
    name: "SOC 2 (AICPA Trust Services Criteria)"
    controls:
      - id: "CC1.4"
        title: "Commitment to competence"
        meaning: "The entity attracts, develops and retains competent individuals — training records demonstrate development."
      - id: "CC2.2"
        title: "Internal communication"
        meaning: "The entity communicates information, including responsibilities for internal control, internally — awareness training is a common evidence item."
    evidence_line: "Completion recorded as SOC 2 CC1.4 / CC2.2 training evidence."
  optional_verify_before_use:
    - "PCI DSS v4.0 requirement 12.6 (security awareness programme) — only for card-data environments; verify sub-requirements."
    - "Local data-protection laws (e.g. Egypt Personal Data Protection Law No. 151 of 2020) — verify obligations with counsel."
records_to_keep:              # per learner per assignment; retained per client policy (commonly ≥ 1 audit cycle)
  - {field: learner_id, note: "pseudonymous id preferred; HR system key"}
  - {field: role_or_audience, note: "standard / IT / exec — shows role-relevant training"}
  - {field: course_id, note: "curriculum.yaml course.id"}
  - {field: lesson_id}
  - {field: content_version, note: "storyboard/quiz version or git commit + render date"}
  - {field: language, note: "en-US / ar-EG / ar-MSA"}
  - {field: assigned_at}
  - {field: completed_at}
  - {field: status, note: "completed / incomplete / exempt (with reason)"}
  - {field: score, note: "quiz score % and pass_mark"}
  - {field: attempts}
  - {field: policy_acknowledged, note: "true/false + policy version, if the lesson includes an acknowledgement"}
  - {field: delivery_channel, note: "LMS (SCORM), live session, email nudge"}
programme_records:            # once per programme/year
  - "Training plan / curriculum (curriculum.yaml + approval record)"
  - "Content inventory with versions and review dates (tracker export)"
  - "Grounding report per lesson (sources behind every claim)"
  - "Completion and score summary by audience; follow-up for non-completers"
  - "Phishing-simulation results and remedial micro-training, if run"
  - "Annual review of content for currency (threats change)"
scorm_mapping:                # how the LMS export carries evidence
  cmi.core.lesson_status: "passed / failed / completed / incomplete"
  cmi.core.score.raw: "quiz score %"
  cmi.core.session_time: "time spent"
  cmi.suspend_data: "content_version + language"
```

## format_defaults.yaml
```yaml
# NOTE: when this file and skills/tcs-autopilot/decision-rules.yaml disagree, decision-rules.yaml wins; this pack only fills gaps.
# Format defaults for security-awareness (orchestrator/autopilot use these when the request doesn't specify).
schema_version: "1.0"
default_formats_by_objective_type:
  concept: [explainer]            # what is phishing / BEC
  behavior: [cartoon, branching]  # micro-drama + branching + knowledge check (autopilot rule)
  procedure: [screencast-sim, job-aid]   # report button, enable MFA
  policy: [cartoon, job-aid]      # compliance policy → micro-drama + quiz + evidence; narrated-deck when audience is exec
  recall: [series]                # flashcards / nudges
default_formats_by_audience:
  standard: [cartoon, explainer]
  it: [explainer, branching]
  exec: [narrated-deck, explainer] # music: executive; theme: executive or midnight; shorter (2–4 min)
when_remaking_original:
  rule: "Match the original's format (explainer / cartoon / whiteboard→doodle); duration ≥ 90% of original (aim 100–120%); cover every original point."
blends:
  - [explainer, job-aid]
  - [cartoon, branching]
  - [cartoon, series]
  - [screencast-sim, job-aid]
durations_min: {micro: 1.5, standard: 3.5, exec: 3, deep: 6}
music_by_format: {explainer: explainer, cartoon: cartoon, doodle: whiteboard, comic: cartoon, branching: cartoon, narrated-deck: executive, mindmap: explainer, screencast-sim: explainer, series: cartoon}
music_exec_override: executive
theme: {default: neutral, exec: executive, doodle: whiteboard}
cast_defaults: {protagonist: rookie, spotter: learner, expert: mentor, attacker: vex}
standard_arc: [title, hook, what, how_it_works, example_mockup, warning_signs, consequences, what_to_do, report_it, quick_check, recap, outro]
evidence_line: "Completion recorded as ISO/IEC 27001:2022 A.6.3 awareness evidence."
always_include:
  - "How and where to report (client's channel — placeholder until provided)"
  - "At least one realistic mock-up with red-flag callouts"
  - "A quick-check question per objective"
```

## glossary.yaml
```yaml
# Security-awareness glossary (EN + AR). Use the same term everywhere (scripts, props, captions, quiz).
# ar = Modern Standard Arabic term; ar_eg = how Egyptian professionals usually say it in speech (often the English word);
# keep_en_in_ar: show the English term in brackets after the Arabic on first use.
# All entries are general knowledge (general_knowledge: true) unless a client source overrides the definition.
schema_version: "1.0"
general_knowledge: true
terms:
  - {term: phishing, en: "Phishing", ar: "التصيّد الاحتيالي", ar_eg: "فيشينج", keep_en_in_ar: true, definition: "A fake message that impersonates someone trusted to make you click, pay or share information."}
  - {term: spear-phishing, en: "Spear phishing", ar: "التصيّد الموجّه", ar_eg: "فيشينج موجّه", keep_en_in_ar: true, definition: "Phishing tailored to a specific person or role using researched details."}
  - {term: smishing, en: "Smishing", ar: "التصيّد عبر الرسائل النصية", ar_eg: "رسايل SMS نصب", keep_en_in_ar: true, definition: "Phishing by SMS or messaging apps."}
  - {term: vishing, en: "Vishing", ar: "التصيّد الصوتي", ar_eg: "مكالمات نصب", keep_en_in_ar: true, definition: "Phishing by phone or voice call."}
  - {term: quishing, en: "Quishing", ar: "التصيّد عبر رمز QR", ar_eg: "QR مضروب", keep_en_in_ar: true, definition: "Phishing that hides a malicious link in a QR code."}
  - {term: bec, en: "Business email compromise (BEC)", ar: "اختراق البريد الإلكتروني للأعمال", ar_eg: "اختراق إيميل الشغل", keep_en_in_ar: true, definition: "Fraud that uses a compromised or spoofed business email account to redirect payments or obtain data."}
  - {term: ceo-fraud, en: "CEO fraud", ar: "احتيال انتحال صفة المدير التنفيذي", ar_eg: "نصب باسم المدير", keep_en_in_ar: false, definition: "An attacker impersonates a senior leader to request an urgent payment or data."}
  - {term: social-engineering, en: "Social engineering", ar: "الهندسة الاجتماعية", ar_eg: "هندسة اجتماعية", keep_en_in_ar: true, definition: "Manipulating people into revealing information or granting access."}
  - {term: pretexting, en: "Pretexting", ar: "انتحال الذريعة", ar_eg: "حجة مفبركة", keep_en_in_ar: true, definition: "Inventing a believable story or role to obtain information."}
  - {term: tailgating, en: "Tailgating", ar: "الدخول خلف شخص مصرّح له", ar_eg: "الدخول ورا حد معاه كارت", keep_en_in_ar: true, definition: "Following an authorised person through a secure door without using your own access."}
  - {term: mfa, en: "Multi-factor authentication (MFA)", ar: "المصادقة متعددة العوامل", ar_eg: "MFA / التحقق بخطوتين", keep_en_in_ar: true, definition: "Signing in with two or more proofs, such as a password plus an app prompt or code."}
  - {term: mfa-fatigue, en: "MFA fatigue", ar: "إغراق طلبات المصادقة", ar_eg: "زنّ طلبات الـMFA", keep_en_in_ar: true, definition: "Sending repeated sign-in prompts hoping the user approves one."}
  - {term: password-manager, en: "Password manager", ar: "مدير كلمات المرور", ar_eg: "Password manager", keep_en_in_ar: true, definition: "An app that creates and stores unique strong passwords."}
  - {term: passkey, en: "Passkey", ar: "مفتاح المرور", ar_eg: "Passkey", keep_en_in_ar: true, definition: "A phishing-resistant sign-in credential stored on your device, unlocked by biometrics or PIN."}
  - {term: malware, en: "Malware", ar: "البرمجيات الخبيثة", ar_eg: "فيروسات / مالوير", keep_en_in_ar: true, definition: "Software designed to harm, spy on or take control of a device."}
  - {term: ransomware, en: "Ransomware", ar: "برمجيات الفدية", ar_eg: "رانسوموير", keep_en_in_ar: true, definition: "Malware that locks or encrypts data and demands payment."}
  - {term: infostealer, en: "Infostealer", ar: "برمجية سرقة المعلومات", ar_eg: "برنامج بيسرق الباسوردات", keep_en_in_ar: true, definition: "Malware that harvests saved passwords, cookies and card data."}
  - {term: deepfake, en: "Deepfake", ar: "التزييف العميق", ar_eg: "ديب فيك", keep_en_in_ar: true, definition: "AI-generated or altered audio, video or images that impersonate a real person."}
  - {term: spoofing, en: "Spoofing", ar: "الانتحال", ar_eg: "تزييف المرسِل", keep_en_in_ar: true, definition: "Faking a sender's name, address, number or website."}
  - {term: lookalike-domain, en: "Look-alike domain", ar: "نطاق مُشابه", ar_eg: "دومين شبه الأصلي", keep_en_in_ar: false, definition: "A web or email domain that imitates a trusted one with small changes."}
  - {term: usb-drop, en: "USB drop attack", ar: "هجوم وحدات USB المتروكة", ar_eg: "فلاشة متسابة", keep_en_in_ar: false, definition: "Leaving infected USB devices where people will find and plug them in."}
  - {term: help-desk-se, en: "Help-desk social engineering", ar: "الهندسة الاجتماعية ضد الدعم الفني", ar_eg: "نصب على الـhelp desk", keep_en_in_ar: false, definition: "Impersonating an employee to get the service desk to reset passwords or MFA."}
  - {term: ai-data-leakage, en: "AI data leakage", ar: "تسريب البيانات عبر أدوات الذكاء الاصطناعي", ar_eg: "تسريب بيانات في أدوات الـAI", keep_en_in_ar: false, definition: "Exposing confidential data by pasting it into unapproved AI tools."}
  - {term: least-privilege, en: "Least privilege", ar: "مبدأ أقل الصلاحيات", ar_eg: "أقل صلاحيات لازمة", keep_en_in_ar: true, definition: "Giving each person only the access their job needs."}
  - {term: patching, en: "Patching", ar: "التحديثات الأمنية", ar_eg: "التحديثات", keep_en_in_ar: false, definition: "Installing updates that fix security weaknesses."}
  - {term: data-breach, en: "Data breach", ar: "اختراق البيانات", ar_eg: "تسريب بيانات", keep_en_in_ar: false, definition: "Unauthorised access to, or disclosure of, protected data."}
  - {term: insider-threat, en: "Insider threat", ar: "التهديد الداخلي", ar_eg: "خطر من جوه الشركة", keep_en_in_ar: false, definition: "Risk from people inside the organisation, malicious or careless."}
  - {term: incident, en: "Security incident", ar: "حادث أمني", ar_eg: "حادثة أمنية", keep_en_in_ar: false, definition: "An event that threatens the confidentiality, integrity or availability of information."}
  - {term: report-phishing, en: "Report Phishing button", ar: "زر الإبلاغ عن التصيّد", ar_eg: "زرار Report", keep_en_in_ar: true, definition: "The mail-client button that sends a suspicious message to the security team."}
  - {term: vpn, en: "VPN", ar: "الشبكة الافتراضية الخاصة", ar_eg: "VPN", keep_en_in_ar: true, definition: "An encrypted connection to the company network over the internet."}
  - {term: encryption, en: "Encryption", ar: "التشفير", ar_eg: "تشفير", keep_en_in_ar: false, definition: "Scrambling data so only authorised people can read it."}
notes:
  - "Captions/props in Arabic: wrap Latin terms in bidi isolates (U+2066 … U+2069)."
  - "Egyptian narration may use ar_eg forms; MSA narration and job aids use ar forms."
```

## mockups.yaml
```yaml
# Mock-up presets: paste `props` into a scene with the given `template`. Shapes follow schemas/storyboard.schema.json.
# Callout `cue`s assume narration names the flags in the listed order (one ^ per callout).
# Fictional only: Northwind Co., *.example domains. Translate every string for Arabic (keep URLs/addresses LTR).
schema_version: "1.0"
presets:
  phish-mailbox:
    template: email_mock
    props:
      email:
        from: "Northwind IT Service Desk"
        from_addr: "it-desk@northwlnd.example"
        to: "you@northwind.example"
        subject: "URGENT: Your mailbox will be closed today"
        external: true
        body: ["Dear user,", "Your mailbox exceeded its limit and will be closed in 2 hours.", "Click below to keep your account active."]
        button: "Keep my mailbox"
      callouts:
        - {cue: 0, target: addr, label: "Look-alike domain", tone: warn}
        - {cue: 1, target: b0, label: "Generic greeting", tone: warn}
        - {cue: 2, target: b1, label: "Pressure and a deadline", tone: warn}
        - {cue: 3, target: button, label: "Hover before you click", tone: warn}
  bec-bank-change:
    template: email_mock
    props:
      email:
        from: "Dana Wells — Brightline Supplies"
        from_addr: "dana.wells@brightline-supplies.example"
        to: "accounts@northwind.example"
        subject: "Updated bank details for invoice 4471"
        external: true
        body: ["Hi team,", "Our bank has changed. Please use the new account below for today's payment.", "Please keep this between us until our audit is finished."]
        attachment: "New_bank_details.pdf"
        signature: ["Dana Wells", "Accounts Receivable"]
      callouts:
        - {cue: 0, target: b1, label: "New bank details", tone: warn}
        - {cue: 1, target: b1, label: "Pay today", tone: warn}
        - {cue: 2, target: b2, label: "Keep it secret", tone: warn}
        - {cue: 3, target: addr, label: "Check the domain", tone: warn}
  ceo-giftcards:
    template: chat_mock
    props:
      device: phone
      title: "Hana (CEO)"
      messages:
        - {text: "Are you at your desk? I need a quick favour.", cue: 0}
        - {me: true, text: "Yes, what do you need?"}
        - {text: "Buy six gift cards for a client. Keep it confidential, I'm in a meeting.", warn: true, cue: 1}
      callouts:
        - {cue: 1, label: "Unusual payment method", tone: warn}
        - {cue: 2, label: "Secrecy + authority", tone: warn}
  mfa-storm:
    template: mfa_prompt
    props: {app: "Northwind Sign-in", place: "Unknown location", count_to: 12, caption: "Prompts you didn't start"}
  smish-parcel:
    template: chat_mock
    props:
      device: phone
      title: "Messages"
      messages:
        - {text: "NorthPost: your parcel is on hold. Pay 1.99 to release it: npost-delivery.example/pay", warn: true, cue: 0}
      callouts:
        - {cue: 1, label: "Short, odd link", tone: warn}
        - {cue: 2, label: "Small fee, big hurry", tone: warn}
  quish-parking:
    template: browser_mock
    props:
      url: "park-northwind.example/pay"
      bad: true
      page: checkout
      brand: "City Parking"
      heading: "Pay for parking"
      lines: ["Enter card details to continue"]
      callouts:
        - {cue: 0, target: url, label: "Check the URL preview", tone: warn}
        - {cue: 1, target: form, label: "Card details? Stop.", tone: warn}
  fake-login:
    template: browser_mock
    props:
      url: "northwind-login.example/secure"
      bad: true
      page: login
      brand: "Northwind"
      heading: "Sign in to continue"
      callouts:
        - {cue: 0, target: url, label: "Not our real domain", tone: warn}
  ai-paste:
    template: browser_mock
    props:
      url: "free-ai-chat.example"
      bad: true
      page: article
      heading: "Ask me anything"
      lines: ["Summarise this customer contract: …"]
      callouts:
        - {cue: 0, target: url, label: "Unapproved AI tool", tone: warn}
        - {cue: 1, target: body, label: "Confidential data, public tool", tone: warn}
  fake-download:
    template: popup
    props: {title: "Free AI assistant!", body: "Finish a month of work in one click. Download now.", cta: "Download", tone: bad, icon: download}
```

## pack.yaml
```yaml
# Domain pack manifest — security-awareness
schema_version: "1.0"
id: security-awareness
title: "Security awareness"
version: "1.0.0"
languages: [en-US, en-GB, ar-EG, ar-MSA]
audiences: [standard, it, exec]
files:
  glossary: glossary.yaml           # EN + AR terms
  personas: personas.yaml           # adds vex (attacker) + role mapping
  scenarios: scenarios.md           # red-flag scenarios + micro-drama premises
  prioritization: prioritization.yaml   # weights, quotas, clusters
  compliance: compliance.yaml       # ISO/IEC 27001:2022 A.6.3, SOC 2 CC1.4/CC2.2 evidence
  format_defaults: format_defaults.yaml
  mockups: mockups.yaml             # email / sms / mfa / browser / popup presets
detect_keywords: [phishing, smishing, vishing, quishing, BEC, MFA, password, malware, ransomware, deepfake, social engineering, tailgating, USB, security awareness, cyber, ISO 27001, SOC 2]
facts_policy: "Threat descriptions and red flags may be general_knowledge; report channels, thresholds, contacts and policy rules must come from client sources."
```

## personas.yaml
```yaml
# Domain personas for security-awareness. Core personas (host, learner, manager, mentor, customer, rookie, colleague,
# exec, support) come from assets/characters/personas.yaml; this pack adds roles and one new persona.
schema_version: "1.0"
role_mapping:                 # how core personas are typically cast in this domain
  mentor: "IT & security team member (explains the rule, takes reports)"
  support: "service-desk agent (target of help-desk social engineering)"
  exec: "CEO/CFO (impersonated in BEC, deepfake voice and CEO-fraud scenarios)"
  manager: "line manager / payment approver"
  rookie: "employee who nearly falls for the trick"
  learner: "employee who spots it"
  customer: "supplier/customer whose identity is spoofed (invoice fraud)"
personas:
  vex:
    display_name: {en: "Vex", ar: "ڤيكس"}
    role: "The attacker / con artist. The ONLY persona wearing the attention colour #FF6700."
    kit_cast: vex
    look: "lanky man of indeterminate age, light-olive skin, slicked-back dark hair, thin moustache, orange jacket over a dark-grey turtleneck, charcoal trousers, pointed shoes; theatrical body language"
    palette: {skin: "#D8B08C", hair: "#1B1B1B", jacket: "#FF6700", turtleneck: "#3A3F55", bottom: "#2E3446"}
    personality: "Smug, theatrical, playful — a cartoon con artist, never scary or violent."
    voice: {provider: openai, voice: verse, instructions: "Smug, theatrical cartoon con-artist, playful not scary. Savouring every word."}
    poses: [rub, cross, point, shrug, handsHips]
    expressions: [sly, happy, angry, shocked]
    do: ["Narrate his tricks in asides (think bubbles)", "Lose at the end when someone verifies or reports"]
    dont: ["Hoodie-in-the-dark hacker cliché", "Resemble any real person, nationality stereotype or group", "Win in the final scene"]
    prompt: "Flat vector illustration of one original cartoon character for a corporate training video, full body, standing, front three-quarter view, clean uniform outlines, flat colours, simple rounded shapes, plain light #F4F7FB background, not a real person. Character: lanky cartoon con artist, light-olive skin, slicked-back dark hair, thin moustache, orange #FF6700 jacket over dark-grey turtleneck, charcoal trousers, theatrical playful pose. {SCENE}. no text, no letters, no numbers, no signage, no logos"
  voice_clone:
    display_name: {en: "Fake voice", ar: "صوت مزيّف"}
    role: "Deepfake stand-in: rendered as the impersonated persona (usually exec) with a glitch overlay; voiced with the exec voice, delivered slightly flat."
    kit_cast: exec
    overlay: glitch
    voice: {provider: openai, voice: cedar, instructions: "Imitate a composed senior executive, but slightly flat and rushed — subtle unnatural pauses."}
```

## prioritization.yaml
```yaml
# Prioritization config for security-awareness catalogues (used by tcs-curriculum when ranking many candidate topics,
# e.g. remaking a vendor catalogue). Formula: priority = Σ weight_i × score_i (scores 0–5) → filter → dedupe by cluster
# → audience quotas → rank → tiers. Output goes to curriculum.yaml `prioritization` (weights, quotas, items[]).
schema_version: "1.0"
weights: {impact: 0.30, frequency: 0.25, gap: 0.20, urgency: 0.15, compliance: 0.10}
scoring_anchors:              # 0 = none, 5 = maximum
  impact: "Severity if staff get it wrong: 5 = direct financial loss / org-wide compromise (BEC, ransomware, help-desk SE); 1 = minor inconvenience"
  frequency: "How often the threat reaches this audience: 5 = weekly (phishing, passwords, MFA prompts); 1 = rare"
  gap: "Not already covered by existing training: 5 = no coverage; 0 = already built/covered (mark previously-built)"
  urgency: "Emerging / rising threat or recent incident: 5 = active trend (deepfakes, AI tools, ClickFix, QR codes)"
  compliance: "Required for evidence: 5 = annual core course for ISO/IEC 27001 A.6.3 / SOC 2 / policy; 0 = optional"
quotas:                       # tier-1 picks per audience; rank within each quota
  standard: 10
  it: 5
  exec: 5
audiences:
  standard: ["Standard users", "All staff"]
  it: ["IT Department", "High-risk users", "Developers"]
  exec: ["Executives", "C-suite", "Senior management"]
tiers:
  tier-1: "quota picks (build now)"
  tier-2: "next 15 by priority (build next)"
  tier-3: "remaining in-scope items (backlog)"
filters_out_of_scope:         # decision: out-of-scope (record reason)
  - "Health & safety, HR conduct, harassment (not security)"
  - "Regional laws for markets the client does not operate in"
  - "Retired / blog-only items with no teachable content"
dedupe:
  rule: "Keep one item per cluster for the general audience; keep specialised variants only if they add a distinct objective or audience. Prefer the richest original (video > blog, longer, story/cartoon available)."
  decision_for_dropped: deprioritised-duplicate
validate_sources: "Before production confirm each kept item's source actually matches its title (catalogue folders can contain the wrong video); substitute a sibling if not."
clusters:                     # derived from the vendor catalogue topic groups used in the worked example
  phishing-email: {label: "Phishing & email threats", members: [phishing, preventing phishing, CEO fraud, email thread hijacking, callback phishing, fake website scams, chat-app phishing, search-engine phishing, typosquatting]}
  bec: {label: "Business email compromise & payment fraud", members: [business email compromise, invoice scams, gift card scams]}
  smishing-quishing: {label: "SMS & QR phishing", members: [smishing, quishing]}
  social-engineering: {label: "Social engineering & scams", members: [social engineering, preventing social engineering, vishing, tech-support scams, ClickFix scams, SIM hijacking, types of hackers]}
  help-desk-se: {label: "Help-desk social engineering", members: [help desk social engineering]}
  insider: {label: "Insider threat", members: [insider threat, minimising insider threat]}
  passwords-mfa: {label: "Passwords, MFA & accounts", members: [secure passwords, strong passwords, password managers, passkeys, MFA fatigue]}
  ai-threats: {label: "AI & emerging threats", members: [AI-driven phishing, deepfakes, staying safe from AI attacks]}
  ai-tools: {label: "Safe use of AI tools", members: [safe use of AI tools, LLM data exposure, LLM hallucinations, AI agents, AI notetakers]}
  malware: {label: "Malware & ransomware", members: [malware, ransomware, spyware & adware, denial of service]}
  devices: {label: "Mobile, devices & patching", members: [patching & updating, mobile device security, removable media, BYOD]}
  data-handling: {label: "Data handling & classification", members: [data loss, protecting information, data breaches]}
  physical: {label: "Physical security", members: [physical security, clear desk, tailgating]}
  remote-work: {label: "Remote work & home security", members: [working remotely, public Wi-Fi, videoconferencing, home network, IoT]}
  hygiene: {label: "Email, social media & cloud hygiene", members: [secure email use, social media, supply chain, file sharing]}
  leadership: {label: "Leadership & high-risk users", members: [C-suite intro, C-suite social engineering, secure culture, travel security, least privilege, effective security communication]}
  resilience: {label: "Business resilience", members: [disaster recovery, business continuity]}
  secure-dev: {label: "Secure development", members: [secure coding]}
  privacy: {label: "Data protection & privacy", members: [GDPR essentials, local data-protection law]}
  compliance-awareness: {label: "Standards awareness", members: [ISO 27001 awareness]}
example_item:                 # shape of curriculum.yaml prioritization.items[]
  id: bec
  title: "Business Email Compromise"
  audience: standard
  cluster: bec
  scores: {impact: 5, frequency: 4, gap: 4, urgency: 3, compliance: 3}
  priority: 4.05              # .30*5 + .25*4 + .20*4 + .15*3 + .10*3
  decision: include
  reason: "High financial impact; finance and assistants targeted weekly; no current coverage."
```

## scenarios.md
# Security-awareness scenarios

Red-flag scenarios and micro-drama premises. Red flags and safe actions below are widely published security-awareness
guidance (**general knowledge** — cite client policy/sources for anything procedural such as report channels, extensions,
approval thresholds). Fictional company: Northwind Co. (`northwind.example`); look-alikes use `.example` domains.
Mock-up presets referenced by id live in `mockups.yaml`. Cast ids: core personas + `vex`.

| # | Threat | Micro-drama premise (cast) | Red flags | Safe action | Templates / preset |
|---|---|---|---|---|---|
| 1 | Phishing (credential) | Friday 4:55 p.m.: rookie gets "mailbox closing in 2 hours" from IT Service Desk; nearly clicks; learner hovers the button (rookie, learner, vex) | look-alike sender domain, generic greeting, deadline, link text ≠ URL, request to log in | don't click; Report Phishing; open the service via a bookmark | `email_mock` → `phish-mailbox` |
| 2 | BEC / invoice fraud | Supplier "Dana" emails finance: "new bank details, pay today" from a near-identical domain (customer, manager, rookie, vex) | changed bank details, urgency, reply-to differs, slight domain change, secrecy | call the supplier on the number already on file; dual approval; report | `email_mock` → `bec-bank-change`, `do_dont` |
| 3 | CEO fraud | "Hana" (exec) emails from a personal address: "confidential acquisition, buy gift cards / wire now" (exec, rookie, vex) | authority + secrecy, unusual payment method, personal address, bypassing process | verify via known channel; follow payment process; report | `email_mock`, `chat_mock` → `ceo-giftcards` |
| 4 | MFA fatigue | Midnight push storm; rookie denies, then is tempted to approve "to make it stop"; vex gloats (rookie, vex, mentor) | prompts you didn't start, repeated prompts, odd location/time | never approve; deny; report; change password | `mfa_prompt` → `mfa-storm`, `cartoon` |
| 5 | Deepfake voice | Manager gets a call in the exec's voice asking for an urgent transfer; audio slightly flat (manager, voice_clone, mentor) | urgency, unusual request, call from new number, voice quirks, refusal to call back | hang up; call back on a known number; use a pre-agreed verification phrase/process | `cartoon` (glitch overlay), `steps` |
| 6 | Tailgating | Courier with boxes asks learner to hold the secure door (learner, vex, manager) | no visible badge, hands full, time pressure, friendliness | send to reception; don't hold secure doors; report unbadged people | `comic` / `cartoon` set `reception` |
| 7 | USB drop | Rookie finds a USB stick labelled (in the story, not on screen) "Salaries" in the car park (rookie, mentor) | unknown device, curiosity bait | don't plug it in; hand it to IT | `cartoon` set `street`, `popup` |
| 8 | Smishing | Parcel "on hold, pay a small fee" SMS with a short link (learner, vex) | unexpected delivery, small fee, short/odd link, urgency | don't tap; check in the courier's official app/site; report/delete | `chat_mock` → `smish-parcel` |
| 9 | Quishing | QR sticker on the office car-park sign "pay parking here" leads to a payment page (rookie, learner) | sticker over original QR, URL preview mismatch, card request | inspect the URL preview; use the official app; report the sticker | `browser_mock` → `quish-parking` |
| 10 | Help-desk SE | Caller claims to be the CFO, locked out before a board meeting; demands password + MFA reset (support, vex, mentor) | urgency, authority, refusal of callback, new device enrolment | verify via callback to directory number / manager approval; escalate | `branching` + `cartoon` (see tcs-format-branching example) |
| 11 | AI data leakage | Learner pastes a customer contract into a free AI chatbot to "summarise quickly" (learner, mentor) | confidential data, unapproved tool, personal account | use approved AI tools only; remove personal/confidential data; check policy | `browser_mock` → `ai-paste`, `do_dont` |
| 12 | Infostealer download | "Free AI productivity tool" pop-up offers a download (rookie, vex, mentor) | unofficial site, too-good offer, executable download | official app stores/IT portal only; report | `popup` → `fake-download`, `browser_mock` |

## Premise rules
- The mistake is relatable and recoverable; end with the right action modelled.
- Never use real brands, real people, real phone numbers or live URLs; use `.example` domains and fictional names.
- Show red flags with `callouts` on mock-ups (`cue` per flag) and say them in narration in the same order.
- One premise per lesson objective; reuse the same cast across a series.

## Reusable red-flag call-out vocabulary (on-screen ≤ 6 words)
"Look-alike domain" · "Generic greeting" · "Pressure and a deadline" · "Hover before you click" · "Unexpected attachment" ·
"Asks for your password" · "New bank details" · "Keep it secret" · "Prompt you didn't start" · "Short, odd link" ·
"Sticker over the original" · "Confidential data, public tool".

