"""Plugin-wide validation.

usage: .venv/bin/python tools/validate.py [--examples] [--quiet]

Checks
  1. Every schemas/*.schema.json is a valid Draft 2020-12 schema.
  2. Every contract file in the repo (*.storyboard.json, *quiz.json, sources.yaml, curriculum.yaml,
     decisions.json, grounding_report.json, state.json) validates against its schema.
  3. Every skills/*/SKILL.md: frontmatter name == folder, description present, < 300 lines,
     no absolute user paths, no secrets.
  4. Trigger distinctness: (a) pairwise description similarity below a threshold,
     (b) every request in tools/trigger_cases.yaml routes to its expected skill by best description match,
     with a clear margin over the runner-up.
Exit code 1 on any failure.
"""
import json, math, re, sys
from collections import Counter
from pathlib import Path

import jsonschema
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {p.name.split('.')[0]: json.loads(p.read_text()) for p in (ROOT / 'schemas').glob('*.schema.json')}
FILE_RULES = [
    (re.compile(r'(^|[./_-])storyboard\.json$|\.storyboard\.json$'), 'storyboard'),
    (re.compile(r'(^|[./_-])quiz\.json$|\.quiz\.json$'), 'quiz'),
    (re.compile(r'(^|/)sources\.ya?ml$'), 'sources'),
    (re.compile(r'(^|/)curriculum\.ya?ml$'), 'curriculum'),
    (re.compile(r'(^|/)decisions\.json$'), 'decisions'),
    (re.compile(r'(^|/)grounding_report\.json$'), 'grounding_report'),
    (re.compile(r'(^|/)state\.json$'), 'run_state'),
]
SKIP_DIRS = {'node_modules', '.venv', '.git', 'invalid', 'attachments'}
SECRET = re.compile(r'(sk-[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}|ghp_[A-Za-z0-9]{30,})')
ABSPATH = re.compile(r'/Users/[A-Za-z0-9._-]+/')
STOP = set('a an the and or of to for in on with by from as is are be it this that when use used using not do does any your you user users its into via per each only also than then their them which what who how get make made'.split())

fails = []


def fail(msg):
    fails.append(msg)
    print('FAIL', msg)


def check_schemas():
    for name, s in SCHEMAS.items():
        try:
            jsonschema.Draft202012Validator.check_schema(s)
        except Exception as e:  # noqa: BLE001
            fail(f'schema {name}: {e}')


def contract_files():
    for p in ROOT.rglob('*'):
        if not p.is_file() or SKIP_DIRS & set(p.relative_to(ROOT).parts):
            continue
        rel = p.relative_to(ROOT).as_posix()
        for rx, kind in FILE_RULES:
            if rx.search(rel):
                yield p, kind
                break


def check_contracts(quiet):
    n = 0
    for p, kind in contract_files():
        data = yaml.safe_load(p.read_text()) if p.suffix in ('.yaml', '.yml') else json.loads(p.read_text())
        errs = sorted(jsonschema.Draft202012Validator(SCHEMAS[kind]).iter_errors(data), key=lambda e: list(e.path))
        n += 1
        if errs:
            fail(f'{p.relative_to(ROOT)} ({kind}): {errs[0].message[:160]} at {"/".join(map(str, errs[0].path))}')
        elif not quiet:
            print('ok  ', p.relative_to(ROOT), f'[{kind}]')
    print(f'{n} contract files checked')


def frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n', text, re.S)
    return yaml.safe_load(m.group(1)) if m else None


def tokens(s):
    return [w for w in re.findall(r'[a-z0-9]+', s.lower().replace('-', ' ')) if w not in STOP and len(w) > 2]


def check_skills():
    skills = {}
    for sk in sorted((ROOT / 'skills').glob('*/SKILL.md')):
        text = sk.read_text()
        fm = frontmatter(text)
        name = sk.parent.name
        if not fm or fm.get('name') != name:
            fail(f'{name}: frontmatter name mismatch ({fm and fm.get("name")})')
            continue
        if not fm.get('description') or len(fm['description']) < 80:
            fail(f'{name}: description missing/too short')
        lines = text.count('\n') + 1
        if lines >= 300:
            fail(f'{name}: SKILL.md has {lines} lines (limit 300)')
        for f in sk.parent.rglob('*'):
            if f.is_file() and f.suffix in ('.md', '.py', '.yaml', '.yml', '.json', '.ts', '.tsx', '.js', '.html', '.sh') \
                    and not (SKIP_DIRS & set(f.relative_to(ROOT).parts)):
                t = f.read_text(errors='ignore')
                if SECRET.search(t):
                    fail(f'{f.relative_to(ROOT)}: looks like a secret')
                if ABSPATH.search(t):
                    fail(f'{f.relative_to(ROOT)}: absolute user path')
        skills[name] = fm['description']
    print(f'{len(skills)} skills checked')
    return skills


def positive(desc):
    """Routing text = description minus its exclusion sentences ("Not for …", "Not when …")."""
    return ' '.join(x for x in re.split(r'(?<=[.!?])\s+', desc) if not re.match(r'\s*\(?not\b', x, re.I))


def tfidf(docs):
    docs = {k: positive(v) for k, v in docs.items()}
    df = Counter(w for d in docs.values() for w in set(tokens(d)))
    n = len(docs)
    vec = {}
    for k, d in docs.items():
        tf = Counter(tokens(d))
        vec[k] = {w: (c / len(tf)) * math.log((n + 1) / (df[w] + 0.5)) for w, c in tf.items()}
    return vec, df


def cos(a, b):
    num = sum(v * b.get(w, 0) for w, v in a.items())
    den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
    return num / den if den else 0.0


def check_triggers(skills, max_sim=0.45, margin=1.10):
    vec, df = tfidf(skills)
    names = sorted(skills)
    worst = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            s = cos(vec[a], vec[b])
            worst.append((s, a, b))
            if s > max_sim:
                fail(f'trigger overlap {a} ~ {b}: cosine {s:.2f} > {max_sim}')
    worst.sort(reverse=True)
    print('most similar pairs:', ', '.join(f'{a}~{b} {s:.2f}' for s, a, b in worst[:3]))
    cases_f = ROOT / 'tools' / 'trigger_cases.yaml'
    if not cases_f.exists():
        return
    cases = yaml.safe_load(cases_f.read_text())
    n = len(skills)
    ok = 0
    for c in cases:
        req = re.sub(r'\b(without|not|no)\s+(using\s+)?[\w-]+', ' ', c['request'], flags=re.I)  # negated terms are exclusions
        q = Counter(tokens(req))
        qv = {w: math.log((n + 1) / (df.get(w, 0) + 0.5)) * cnt for w, cnt in q.items()}
        ranked = sorted(((cos(qv, vec[k]), k) for k in names), reverse=True)
        (s1, top), (s2, second) = ranked[0], ranked[1]
        if top != c['expect']:
            fail(f'route "{c["request"][:60]}" → {top} ({s1:.2f}), expected {c["expect"]}')
        elif s1 < s2 * margin:
            fail(f'route "{c["request"][:60]}" ambiguous: {top} {s1:.2f} vs {second} {s2:.2f}')
        else:
            ok += 1
    print(f'trigger routing: {ok}/{len(cases)} cases routed uniquely')


if __name__ == '__main__':
    quiet = '--quiet' in sys.argv
    check_schemas()
    check_contracts(quiet)
    sk = check_skills()
    if sk:
        check_triggers(sk)
    print('PASS' if not fails else f'{len(fails)} FAILURES')
    sys.exit(1 if fails else 0)
