#!/usr/bin/env python3
"""End-to-end runtime test: unpack a SCORM zip, launch a SCO inside a mock SCORM 1.2 LMS (headless Chrome),
drive the lesson (navigation, branching, knowledge checks, final check) and assert the cmi.* values.

Usage: .venv/bin/python skills/tcs-render-lesson/tests/test_runtime.py <package.zip> [--sco M1L1]
Fixture expectations match tests/fixtures/en.storyboard.json + en.quiz.json.
"""
import argparse
import html
import json
import re
import sys
import tempfile
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from _common import chrome  # noqa: E402

HARNESS = r"""<!doctype html><html><head><meta charset="utf-8"><title>mock LMS</title><script>
var DB = {"cmi.core.lesson_status":"not attempted","cmi.core.entry":"ab-initio","cmi.suspend_data":"","cmi.core.lesson_location":""};
var LOG = [];
window.API = {
  LMSInitialize:function(){LOG.push("init");return "true";},
  LMSFinish:function(){LOG.push("finish");return "true";},
  LMSGetValue:function(k){return DB[k]||"";},
  LMSSetValue:function(k,v){DB[k]=v;return "true";},
  LMSCommit:function(){LOG.push("commit");return "true";},
  LMSGetLastError:function(){return "0";},LMSGetErrorString:function(){return "";},LMSGetDiagnostic:function(){return "";}
};
</script></head><body><iframe id="f" src="__SCO__" style="width:1200px;height:900px"></iframe><pre id="out"></pre>
<script>
var R = {steps:[]}, pass = 0;
function active(d){ var a = d.querySelector(".scene.active"); return a ? a.getAttribute("data-scene") : null; }
function step(name, v){ R.steps.push([name, v]); }
document.getElementById("f").addEventListener("load", function(){
  var w = this.contentWindow, d = w.document;
  pass++;
  if (pass === 1) {
    var next = d.getElementById("nav-next");
    step("start", active(d));
    for (var i = 0; i < 5; i++) next.click();
    step("at_decision", active(d)); step("next_disabled_on_decision", next.disabled);
    d.querySelector('.choice[data-choice="b"]').click();
    step("after_choice", active(d));
    next.click(); step("outcome", active(d)); step("outcome_text", d.querySelector(".oc-fb").textContent);
    next.click(); step("after_branch", active(d));
    var q1 = d.querySelector('form[data-q="Q1"]'); q1.querySelector('input[value="b"]').checked = true; q1.requestSubmit();
    step("q1_feedback", q1.querySelector(".q-fb").textContent.slice(0, 40));
    next.click(); next.click(); next.click(); next.click();
    step("final_check", active(d));
    var f = function(id){ return d.querySelector('#s-__check form[data-q="'+id+'"]'); };
    f("Q2").querySelector('input[value="a"]').checked = true; f("Q2").querySelector('input[value="c"]').checked = true;
    f("Q3").querySelector('input[value="f"]').checked = true;
    var o = {a:"2", b:"1", c:"3"}; Object.keys(o).forEach(function(k){ f("Q4").querySelector('select[data-opt="'+k+'"]').value = o[k]; });
    f("Q5").querySelector('select[data-opt="a"]').value = "Report button"; f("Q5").querySelector('select[data-opt="b"]').value = "IT Service Desk";
    d.querySelector("[data-submit-all]").click();
    step("end", active(d)); step("end_score", d.getElementById("end-score").textContent);
    R.first = JSON.parse(JSON.stringify(DB));
    DB["cmi.core.entry"] = "resume";
    // go back to a mid-lesson scene to test bookmarking
    d.querySelector("#menu-btn").click(); d.querySelector('[data-jump="checklist"]').click();
    step("jumped", active(d));
    this.src = this.src; // reload -> pagehide -> LMSFinish, then resume
  } else {
    step("resumed_at", active(d));
    R.second = JSON.parse(JSON.stringify(DB)); R.log = LOG;
    document.getElementById("out").textContent = JSON.stringify(R);
  }
});
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zip", type=Path)
    ap.add_argument("--sco", default="M1L1")
    a = ap.parse_args()
    tmp = Path(tempfile.mkdtemp(prefix="tcs-rt-"))
    zipfile.ZipFile(a.zip).extractall(tmp)
    (tmp / "harness.html").write_text(HARNESS.replace("__SCO__", f"{a.sco}/index.html"), encoding="utf-8")
    prof = tmp / "profile"
    r = chrome(["--disable-web-security", f"--user-data-dir={prof}", "--virtual-time-budget=8000", "--dump-dom",
                (tmp / "harness.html").as_uri()])
    m = re.search(r'<pre id="out">(.*?)</pre>', r.stdout, re.S)
    if not m or not m.group(1).strip():
        print(r.stdout[-2000:], r.stderr[-2000:])
        sys.exit("FAIL: harness produced no result")
    R = json.loads(html.unescape(m.group(1)))
    st = dict(R["steps"])
    first, second = R["first"], R["second"]
    checks = [
        ("starts at intro", st["start"] == "intro"),
        ("branch entered at decision", st["at_decision"] == "dec_payroll"),
        ("Next disabled on decision", st["next_disabled_on_decision"] is True),
        ("choice routes to node scene", st["after_choice"] == "report_result"),
        ("outcome card shown", st["outcome"] == "__outcome" and "Exactly right" in st["outcome_text"]),
        ("linear resumes after branch block", st["after_branch"] == "check1"),
        ("feedback shown", st["q1_feedback"].startswith("Correct")),
        ("final check reached", st["final_check"] == "__check"),
        ("end reached", st["end"] == "__end" and "100%" in st["end_score"]),
        ("score.raw = 100", first.get("cmi.core.score.raw") == "100"),
        ("score.min/max", first.get("cmi.core.score.min") == "0" and first.get("cmi.core.score.max") == "100"),
        ("status passed", first.get("cmi.core.lesson_status") == "passed"),
        ("suspend_data JSON", bool(json.loads(first.get("cmi.suspend_data") or "{}").get("a"))),
        ("bookmark resume", st["resumed_at"] == "checklist" and second.get("cmi.core.lesson_location") == "checklist"),
        ("pass not downgraded", second.get("cmi.core.lesson_status") == "passed"),
        ("LMSFinish + session_time", "finish" in R["log"] and re.match(r"^\d{4}:\d{2}:\d{2}\.\d{2}$", second.get("cmi.core.session_time", ""))),
    ]
    bad = 0
    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
        bad += not ok
    if bad:
        print(json.dumps(R, indent=1, ensure_ascii=False)[:3000])
    print(f"{len(checks) - bad}/{len(checks)} runtime checks passed")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
