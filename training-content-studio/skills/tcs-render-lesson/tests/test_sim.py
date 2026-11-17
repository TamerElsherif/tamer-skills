#!/usr/bin/env python3
"""Runtime test for interactive screencast sims (props.sim guided/practice/assess) in a rendered lesson.

Usage: .venv/bin/python skills/tcs-render-lesson/tests/test_sim.py <lesson dir> --scene s03_try
Drives the sim with headless Chrome: a wrong step (expects a hint/attempt message), then the correct sequence from
sim.expect (expects 'Task complete').
"""
import argparse
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _common import chrome  # noqa: E402

DRIVER = r"""<script>
(function(){var R={},root=document.querySelector('#s-__SCENE__ [data-sim]'),C=JSON.parse(root.getAttribute('data-sim'));
function f(t){return root.querySelector('[data-sim-field="'+t+'"]');}
function fire(el,v){if(el.tagName==='BUTTON'){el.click();return;} if(el.type==='checkbox'){el.checked=true;}else{ if(el.tagName==='SELECT'&&v&&![].some.call(el.options,function(o){return o.value===v;})){var o=document.createElement('option');o.value=o.textContent=v;el.appendChild(o);} el.value=(v==='*'||v==null)?'x':v;} el.dispatchEvent(new Event('change'));}
var last=C.expect[C.expect.length-1].target, first=C.expect[0].target;
if(last!==first){fire(f(last)); R.wrong=root.querySelector('.sim-msg').textContent;}
C.expect.forEach(function(e){fire(f(e.target),e.value);});
R.done=root.querySelector('.sim-msg').textContent;R.mode=C.mode;
var pre=document.createElement('pre');pre.id='simout';pre.textContent=JSON.stringify(R);document.body.appendChild(pre);})();
</script></body>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lesson", type=Path)
    ap.add_argument("--scene", required=True)
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp(prefix="tcs-sim-")) / "l"
    shutil.copytree(a.lesson, tmp)
    idx = tmp / "index.html"
    idx.write_text(idx.read_text(encoding="utf-8").replace("</body>", DRIVER.replace("__SCENE__", a.scene)), encoding="utf-8")
    r = chrome([f"--user-data-dir={tmp.parent / 'p'}", "--virtual-time-budget=3000", "--dump-dom", idx.as_uri() + f"#s-{a.scene}"])
    m = re.search(r'<pre id="simout">(.*?)</pre>', r.stdout, re.S)
    if not m:
        sys.exit("FAIL: no result\n" + r.stderr[-800:])
    R = json.loads(html.unescape(m.group(1)))
    ok_wrong = "wrong" not in R or bool(R["wrong"].strip())
    ok_done = "complete" in R["done"].lower() or "تمّت" in R["done"]
    print(("PASS" if ok_wrong else "FAIL"), "wrong step gives feedback:", R.get("wrong"))
    print(("PASS" if ok_done else "FAIL"), f"correct sequence completes ({R['mode']}):", R["done"])
    sys.exit(0 if ok_wrong and ok_done else 1)


if __name__ == "__main__":
    main()
