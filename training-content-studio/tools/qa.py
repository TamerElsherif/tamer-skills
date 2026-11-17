"""Per-lesson QA gate for a run folder → runs/<id>/qa/<L>.qa.json (read by tcs-autopilot report.py).

usage: .venv/bin/python tools/qa.py runs/<id> [--lesson M1L1] [--lang ar-EG] [--today YYYY-MM-DD]

Runs, for each lesson: tcs-storyboard validate_storyboard.py --stage final, tcs-assessment validate_quiz.py,
tcs-grounding-check check.py (writes <L>.grounding_report.json), then re-applies <L>.verdicts.yaml (LLM pass) if present. Result = pass only if all three pass.
Exit 0 = all lessons pass, 2 = at least one lesson needs fixes, 1 = bad input.
"""
import argparse, datetime as dt, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
SB = ROOT / 'skills/tcs-storyboard/scripts/validate_storyboard.py'
QZ = ROOT / 'skills/tcs-assessment/scripts/validate_quiz.py'
GR = ROOT / 'skills/tcs-grounding-check/scripts/check.py'


def run(cmd):
    p = subprocess.run([PY, *map(str, cmd)], capture_output=True, text=True)
    try:
        data = json.loads(p.stdout)
    except ValueError:
        data = {'stdout': p.stdout[-2000:], 'stderr': p.stderr[-2000:]}
    return p.returncode, data


def qa_lesson(rd, lid, lang, today):
    ld = rd / 'lessons' / lid
    suffix = f'.{lang}' if lang else ''
    sb = ld / f'{lid}{suffix}.storyboard.json'
    qz = ld / f'{lid}{suffix}.quiz.json'
    if not qz.exists():
        qz = ld / f'{lid}.quiz.json'
    cur = rd / 'curriculum.yaml'
    src = rd / 'sources.yaml'
    out = {'lesson_id': lid, 'lang': lang or 'primary', 'at': dt.datetime.now().isoformat(timespec='seconds'), 'checks': {}}
    if not sb.exists():
        out.update(result='fail', reason=f'missing {sb.name}')
        return out
    rc, d = run([SB, sb, '--stage', 'final', '--json'] + (['--quiz', qz] if qz.exists() else []))
    out['checks']['storyboard'] = {'exit': rc, 'report': d}
    if qz.exists():
        rc, d = run([QZ, qz, '--storyboard', sb, '--json'] + (['--sources', src] if src.exists() else []))
        out['checks']['quiz'] = {'exit': rc, 'report': d}
    if src.exists():
        gout = ld / f'{lid}{suffix}.grounding_report.json'
        cmd = [GR, '--sources', src, '--storyboard', sb, '--lesson-id', lid, '--out', gout, '--today', today]
        if qz.exists():
            cmd += ['--quiz', qz]
        if cur.exists():
            cmd += ['--curriculum', cur]
        rc, d = run(cmd)
        verd = ld / f'{lid}{suffix}.verdicts.yaml'
        if verd.exists() and gout.exists():  # re-apply the LLM verification pass (check.py rewrites the report)
            rc, _ = run([ROOT / 'skills/tcs-grounding-check/scripts/apply_verdicts.py', gout, verd])
        out['checks']['grounding'] = {'exit': rc, 'report': str(gout.relative_to(rd)) if gout.exists() else d,
                                      'llm_verdicts': verd.exists()}
    else:
        out['checks']['grounding'] = {'exit': 0, 'note': 'no sources.yaml: all claims must be general_knowledge (checked by storyboard lint)'}
    out['result'] = 'pass' if all(c['exit'] == 0 for c in out['checks'].values()) else 'fail'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('run_dir')
    ap.add_argument('--lesson')
    ap.add_argument('--lang')
    ap.add_argument('--today', default=dt.date.today().isoformat())
    a = ap.parse_args()
    rd = Path(a.run_dir).resolve()
    if not (rd / 'lessons').is_dir():
        print(f'no lessons/ in {rd}', file=sys.stderr)
        return 1
    lids = [a.lesson] if a.lesson else sorted(p.name for p in (rd / 'lessons').iterdir() if p.is_dir())
    (rd / 'qa').mkdir(exist_ok=True)
    bad = 0
    for lid in lids:
        r = qa_lesson(rd, lid, a.lang, a.today)
        name = f'{lid}.{a.lang}.qa.json' if a.lang else f'{lid}.qa.json'
        (rd / 'qa' / name).write_text(json.dumps(r, indent=1, ensure_ascii=False))
        print(f"{lid}{'.' + a.lang if a.lang else ''}: {r['result']}  " +
              ' '.join(f"{k}={v['exit']}" for k, v in r['checks'].items()))
        bad += r['result'] != 'pass'
    return 2 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
