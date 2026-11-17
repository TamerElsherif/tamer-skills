/* tcs-render-lesson player: navigation, branching, knowledge checks, reveals, screencast sim, bookmarking.
   Optional LMS adapter: window.TCS_LMS = {init()->stateString|null, save(state, location), score(raw,min,max),
   status('completed'|'passed'|'failed'|'incomplete'), finish()} — provided by scorm12.js in SCORM packages. */
(function () {
  "use strict";
  var D = JSON.parse(document.getElementById("tcs-data").textContent);
  var T = D.ui, RTL = D.rtl;
  document.documentElement.classList.remove("no-js");
  document.documentElement.classList.add("js");
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };
  var LMS = window.TCS_LMS || null;
  var KEY = "tcs:" + D.lesson_id;

  // ---------------------------------------------------------------- state
  var branchScenes = {};
  (D.branching ? D.branching.nodes : []).forEach(function (n) { n.scenes.forEach(function (s) { branchScenes[s] = n.id; }); });
  var linear = D.order.slice(); // includes virtual __check / __end
  var firstBranchIdx = -1, lastBranchIdx = -1;
  linear.forEach(function (id, i) { if (branchScenes[id]) { if (firstBranchIdx < 0) firstBranchIdx = i; lastBranchIdx = i; } });
  var S = { cur: null, hist: [], ans: {}, chk: {}, path: [], bscore: 0, bdone: false, visited: {}, done: false };

  function nodeById(id) { return D.branching && D.branching.nodes.filter(function (n) { return n.id === id; })[0]; }
  function save() {
    var st = JSON.stringify({ c: S.cur, a: S.ans, k: S.chk, p: S.path, b: S.bscore, d: S.bdone, v: Object.keys(S.visited), x: S.done });
    try { if (LMS) LMS.save(st, sceneOf(S.cur)); else localStorage.setItem(KEY, st); } catch (e) {}
  }
  function load() {
    var st = null;
    try { st = LMS ? LMS.init() : localStorage.getItem(KEY); } catch (e) {}
    if (!st) return;
    try {
      var o = JSON.parse(st);
      S.cur = o.c; S.ans = o.a || {}; S.chk = o.k || {}; S.path = o.p || []; S.bscore = o.b || 0; S.bdone = !!o.d; S.done = !!o.x;
      (o.v || []).forEach(function (v) { S.visited[v] = 1; });
    } catch (e) {}
  }

  // cursor: {m:'l', i} linear  |  {m:'b', n:nodeId, k}  branch  |  {m:'o', n:nodeId} outcome card
  function sceneOf(c) {
    if (!c) return linear[0];
    if (c.m === "l") return linear[c.i];
    if (c.m === "b") return nodeById(c.n).scenes[c.k];
    return "__outcome";
  }
  function enterBranch(peek) { if (!peek) { S.path = []; S.bscore = 0; } return goNode(D.branching.start, peek); }
  function goNode(id, peek) {
    var n = nodeById(id);
    if (!n) return null;
    if (!peek) { S.path.push(id); S.bscore += n.score || 0; }
    if (!n.scenes.length) return { m: "o", n: id };
    return { m: "b", n: id, k: 0 };
  }
  function linearAfterBranch() { var i = lastBranchIdx + 1; return { m: "l", i: Math.min(i, linear.length - 1) }; }
  function nextOf(c, peek) {
    if (c.m === "l") {
      var i = c.i + 1;
      while (i < linear.length && branchScenes[linear[i]]) {
        if (D.branching && !S.bdone && i === firstBranchIdx) return enterBranch(peek);
        i++;
      }
      return i < linear.length ? { m: "l", i: i } : null;
    }
    if (c.m === "b") {
      var n = nodeById(c.n);
      if (c.k + 1 < n.scenes.length) return { m: "b", n: c.n, k: c.k + 1 };
      if (n.outcome && n.outcome !== "continue") return { m: "o", n: c.n };
      var idx = D.branching.nodes.indexOf(n);
      var nx = D.branching.nodes[idx + 1];
      return nx ? goNode(nx.id, peek) : { m: "o", n: c.n };
    }
    if (!peek) S.bdone = true;
    return linearAfterBranch();
  }

  // ---------------------------------------------------------------- rendering
  var scenes = {};
  $$(".scene").forEach(function (el) { scenes[el.getAttribute("data-scene")] = el; });
  var outcomeEl = scenes.__outcome;
  var btnNext = $("#nav-next"), btnBack = $("#nav-back"), pos = $("#nav-pos"), bar = $(".progress i"), live = $("#live");

  function show(c, focus) {
    S.cur = c;
    var id = sceneOf(c);
    Object.keys(scenes).forEach(function (k) { scenes[k].classList.toggle("active", k === id); });
    var el = scenes[id];
    if (id === "__outcome") renderOutcome(nodeById(c.n));
    if (id === "__end") renderEnd();
    S.visited[id] = 1;
    $$("audio, video", document).forEach(function (m) { if (!el.contains(m) && m.tagName === "AUDIO") m.pause(); });
    var isDecision = el && el.getAttribute("data-template") === "decision" && c.m === "b";
    btnNext.disabled = !nextOf(c, true) || isDecision;
    btnBack.disabled = !S.hist.length;
    var total = Object.keys(scenes).length - 1, seen = Object.keys(S.visited).length;
    bar.style.width = Math.min(100, Math.round(100 * seen / total)) + "%";
    var label = (el && el.getAttribute("aria-label")) || "";
    pos.textContent = label;
    live.textContent = label;
    $$("[data-count]", el).forEach(countUp);
    layoutFlows(el);
    if (focus !== false) { var h = $(".scene-title", el) || el; h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); window.scrollTo(0, 0); }
    if (id === "__end" || (!nextOf(c, true) && !D.hasQuiz)) complete();
    save();
  }
  function go(c) { if (!c) return; S.hist.push(S.cur); show(c); }
  btnNext.addEventListener("click", function () { go(nextOf(S.cur, false)); });
  btnBack.addEventListener("click", function () { if (S.hist.length) show(S.hist.pop()); });
  document.addEventListener("keydown", function (e) {
    if (e.target.closest("input,select,textarea,button,summary,[contenteditable]") || e.altKey || e.ctrlKey || e.metaKey) return;
    var fwd = RTL ? "ArrowLeft" : "ArrowRight", bwd = RTL ? "ArrowRight" : "ArrowLeft";
    if (e.key === fwd && !btnNext.disabled) btnNext.click();
    if (e.key === bwd && !btnBack.disabled) btnBack.click();
  });

  // menu
  var menu = $("#menu"), menuBtn = $("#menu-btn");
  menuBtn.addEventListener("click", function () { var o = menu.hidden; menu.hidden = !o; menuBtn.setAttribute("aria-expanded", String(o)); if (o) $("button", menu).focus(); });
  $$("[data-jump]", menu).forEach(function (b) {
    b.addEventListener("click", function () {
      var id = b.getAttribute("data-jump"), i = linear.indexOf(id);
      menu.hidden = true; menuBtn.setAttribute("aria-expanded", "false");
      if (branchScenes[id]) go(enterBranch()); else if (i >= 0) go({ m: "l", i: i });
    });
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && !menu.hidden) { menu.hidden = true; menuBtn.focus(); } });

  // ---------------------------------------------------------------- decisions (branching)
  $$(".choice[data-choice]").forEach(function (b) {
    b.addEventListener("click", function () {
      var sc = b.closest(".scene"), fb = $(".dec-fb", sc), nx = b.getAttribute("data-next"), ok = b.getAttribute("data-correct") === "1";
      $$(".choice", sc).forEach(function (x) { x.classList.remove("picked"); x.setAttribute("aria-pressed", "false"); });
      b.classList.add("picked"); b.setAttribute("aria-pressed", "true");
      if (D.branching && S.cur.m === "b") {
        if (nodeById(nx)) return go(goNode(nx));
        var nid = branchScenes[nx];
        if (nid) { S.path.push(nid); return go({ m: "b", n: nid, k: nodeById(nid).scenes.indexOf(nx) }); }
        var li = linear.indexOf(nx); if (li >= 0) { S.bdone = true; return go({ m: "l", i: li }); }
      }
      fb.innerHTML = '<p class="res ' + (ok ? "ok" : "bad") + '">' + (ok ? T.correct : T.incorrect) + "</p>";
      var li2 = linear.indexOf(nx); if (li2 >= 0 && !branchScenes[nx]) setTimeout(function () { go({ m: "l", i: li2 }); }, 900);
    });
  });
  function renderOutcome(n) {
    var o = n.outcome || "neutral", icon = o === "good" ? "✓" : o === "bad" ? "!" : "•";
    $(".outcome", outcomeEl).className = "outcome " + o;
    $(".oc-ico", outcomeEl).textContent = icon;
    $(".oc-fb", outcomeEl).textContent = n.feedback || "";
    $(".oc-score", outcomeEl).textContent = T.score + ": " + S.bscore;
  }
  var replay = $("[data-branch-replay]");
  if (replay) replay.addEventListener("click", function () { S.bdone = false; go(enterBranch()); });

  // ---------------------------------------------------------------- quiz
  function grade(form) {
    var type = form.getAttribute("data-type"), ok = true, picked = [];
    if (type === "ordering" || type === "matching") {
      $$("select", form).forEach(function (s) {
        var good = s.value !== "" && s.value === s.getAttribute("data-key");
        s.closest("li").classList.toggle("ok", good); s.closest("li").classList.toggle("bad", !good);
        if (!good) ok = false;
      });
      return { ok: ok, picked: picked };
    }
    var inputs = $$("input", form);
    if (!inputs.some(function (i) { return i.checked; })) return null;
    inputs.forEach(function (i) {
      var c = i.getAttribute("data-correct") === "1";
      if (i.checked) picked.push(i.value);
      if (i.checked !== c) ok = false;
      i.closest("li").classList.toggle("ok", c);
      i.closest("li").classList.toggle("bad", i.checked && !c);
    });
    return { ok: ok, picked: picked };
  }
  $$("form.qitem").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      e.preventDefault();
      var r = grade(f), out = $(".q-fb", f);
      if (!r) { out.textContent = T.choose; return; }
      var q = f.getAttribute("data-q"), fbm = JSON.parse(f.getAttribute("data-fb") || "{}");
      if (!(q in S.ans)) S.ans[q] = r.ok ? 1 : 0; // first attempt counts
      var msg = '<p class="res ' + (r.ok ? "ok" : "bad") + '">' + (r.ok ? T.correct : T.incorrect) + "</p>";
      r.picked.forEach(function (p) { if (fbm[p]) msg += "<p>" + esc(fbm[p]) + "</p>"; });
      if (f.getAttribute("data-expl")) msg += "<p>" + esc(f.getAttribute("data-expl")) + "</p>";
      out.innerHTML = msg;
      syncQuiz(); save(); updateScore();
    });
  });
  function esc(s) { var d = document.createElement("div"); d.textContent = s; return d.innerHTML; }
  function syncQuiz() { $$("form.qitem").forEach(function (f) { var q = f.getAttribute("data-q"); if (q in S.ans) f.classList.add("answered"); }); }
  function scoreNow() {
    var tot = 0, got = 0, n = 0;
    D.quiz.forEach(function (q) { tot += q.points; if (q.id in S.ans) { n++; got += S.ans[q.id] * q.points; } });
    return { raw: tot ? Math.round(100 * got / tot) : 0, all: n === D.quiz.length, tot: tot };
  }
  function updateScore() {
    if (!D.hasQuiz) return;
    var s = scoreNow();
    if (s.all && LMS) { LMS.score(s.raw, 0, 100); LMS.status(s.raw >= D.passMark ? "passed" : "failed"); }
  }
  var submitAll = $("[data-submit-all]");
  if (submitAll) submitAll.addEventListener("click", function () {
    $$("#s-__check form.qitem").forEach(function (f) { var q = f.getAttribute("data-q"); if (!(q in S.ans)) { if (grade(f)) f.requestSubmit(); else S.ans[q] = 0; } });
    updateScore(); save(); go({ m: "l", i: linear.indexOf("__end") });
  });
  function renderEnd() {
    var box = $("#end-score");
    if (!box) return;
    var html = "";
    if (D.hasQuiz) {
      var s = scoreNow(), pass = s.raw >= D.passMark;
      html += '<p class="ring">' + s.raw + "%</p><p><strong>" + (pass ? T.pass : T.fail) + "</strong> · " + T.pass_mark + " " + D.passMark + "%</p>";
    }
    if (D.branching && S.path.length) html += "<p>" + T.outcome + ": " + T.score + " " + S.bscore + "</p>";
    box.innerHTML = html;
  }
  var retry = $("[data-retry]");
  if (retry) retry.addEventListener("click", function () {
    S.ans = {}; $$("form.qitem").forEach(function (f) { f.reset(); f.classList.remove("answered"); $(".q-fb", f).innerHTML = ""; $$("li", f).forEach(function (l) { l.classList.remove("ok", "bad"); }); });
    if (LMS) LMS.status("incomplete");
    save(); go({ m: "l", i: Math.max(0, linear.indexOf("__check")) });
  });
  function complete() {
    if (S.done && !D.hasQuiz) return;
    S.done = true;
    if (!LMS) return;
    if (D.hasQuiz) { var s = scoreNow(); if (s.all) { LMS.score(s.raw, 0, 100); LMS.status(s.raw >= D.passMark ? "passed" : "failed"); } }
    else LMS.status("completed");
  }

  // ---------------------------------------------------------------- checklists, flashcards, reveals, callouts
  $$("[data-check]").forEach(function (c) {
    var k = c.getAttribute("data-check");
    c.addEventListener("change", function () { S.chk[k] = c.checked ? 1 : 0; save(); });
  });
  $$("[data-flip]").forEach(function (b) { b.addEventListener("click", function () { b.setAttribute("aria-pressed", String(b.getAttribute("aria-pressed") !== "true")); }); });
  $$("[data-reveal-scope]").forEach(function (sc) {
    var els = $$("[data-reveal]", sc), cues = [];
    els.forEach(function (e) { var c = +e.getAttribute("data-reveal"); if (cues.indexOf(c) < 0) cues.push(c); });
    cues.sort(function (a, b) { return a - b; });
    var step = 0, next = $("[data-reveal-next]", sc), all = $("[data-reveal-all]", sc);
    var focus = JSON.parse(sc.getAttribute("data-focus") || "[]");
    function apply() {
      var upto = cues[step - 1];
      els.forEach(function (e) { e.classList.toggle("on", step > 0 && +e.getAttribute("data-reveal") <= upto); });
      $$(".mm-n", sc).forEach(function (n) { n.classList.remove("focus"); });
      focus.forEach(function (f) { if (f.cue === upto) { var n = $('[data-node="' + f.node + '"]', sc); if (n) n.classList.add("focus"); } });
      if (next) next.disabled = step >= cues.length;
    }
    if (next) next.addEventListener("click", function () { step = Math.min(cues.length, step + 1); apply(); });
    if (all) all.addEventListener("click", function () { step = cues.length; apply(); });
    if (!next) step = cues.length;
    else step = Math.min(1, cues.length);
    apply();
  });
  $$("[data-reveal-co]").forEach(function (b) {
    var sc = b.closest(".scene"), n = 0, items = $$(".co", sc);
    b.addEventListener("click", function () {
      if (n >= items.length) return;
      items[n].classList.add("on");
      $$('.mock .pin[data-co="' + n + '"]', sc).forEach(function (p) { p.classList.add("on"); });
      n++; if (n >= items.length) b.disabled = true;
    });
  });

  // ---------------------------------------------------------------- screencast simulation
  $$("[data-screencast]").forEach(function (root) {
    var acts = $$(".sc-steps li", root), hs = $(".hotspot", root), toast = $(".toast", root), body = $(".app-body", root);
    var status = $(".sc-status", root), i = 0;
    function target(a) { var t = a.getAttribute("data-target"); return t ? $('.sc-f[data-target="' + t + '"]', root) : null; }
    function place() {
      acts.forEach(function (a, k) { a.classList.toggle("cur", k === i); a.classList.toggle("done", k < i); });
      $$(".sc-f", root).forEach(function (f) { f.classList.remove("hot"); });
      hs.hidden = true;
      if (i >= acts.length) { status.textContent = T.done; return; }
      status.textContent = T.step + " " + (i + 1) + " " + T.of + " " + acts.length;
      var tg = target(acts[i]);
      if (tg) {
        tg.classList.add("hot");
        var br = body.getBoundingClientRect(), r = tg.getBoundingClientRect();
        if (r.width) {
          hs.style.left = (r.left - br.left - 4) + "px"; hs.style.top = (r.top - br.top - 4) + "px";
          hs.style.width = (r.width + 8) + "px"; hs.style.height = (r.height + 8) + "px"; hs.hidden = false;
          hs.setAttribute("aria-label", T.next_step + ": " + acts[i].textContent.trim());
        }
      }
    }
    function perform() {
      if (i >= acts.length) return;
      var a = acts[i], tg = target(a), d = a.getAttribute("data-do"), v = a.getAttribute("data-value");
      if (tg) {
        var val = $("[data-val]", tg);
        if ((d === "type" || d === "select") && val && v) val.firstChild ? (val.firstChild.nodeType === 3 ? val.firstChild.nodeValue = v : val.insertBefore(document.createTextNode(v), val.firstChild)) : (val.textContent = v);
        if (d === "click" && val && val.classList.contains("sc-cb")) val.classList.add("on");
        tg.classList.add("done");
      }
      var lbl = a.textContent.replace(/^\d+/, "").trim();
      if (d === "toast" || d === "callout" || d === "highlight") { toast.textContent = lbl; toast.hidden = !lbl; }
      i++; place();
    }
    hs.addEventListener("click", perform);
    var nb = $("[data-sc-next]", root), rb = $("[data-sc-reset]", root);
    if (nb) nb.addEventListener("click", perform);
    if (rb) rb.addEventListener("click", function () { i = 0; toast.hidden = true; $$(".sc-f", root).forEach(function (f) { f.classList.remove("done"); }); place(); });
    root._place = place;
  });

  // ---------------------------------------------------------------- interactive sim (guided / practice / assess)
  $$("[data-sim]").forEach(function (root) {
    var C = JSON.parse(root.getAttribute("data-sim")), msg = $(".sim-msg", root), toast = $(".toast", root);
    var k = 0, tries = 0, failed = false, done = false, demoing = false;
    function fld(t) { return $('.sc-f[data-target="' + t + '"]', root); }
    function say(cls, text) { msg.innerHTML = '<span class="' + cls + '">' + esc(text) + "</span>"; }
    function guide() {
      $$(".sc-f", root).forEach(function (f) { f.classList.remove("hot", "hint-on"); });
      if (done || k >= C.expect.length) return;
      var t = C.expect[k].target, f = fld(t);
      if (C.mode === "guided" && f) { f.classList.add("hot"); if (C.hints[t]) say("", C.hints[t]); }
    }
    function finish(ok) {
      done = true; guide();
      say(ok ? "ok" : "bad", ok ? T.sim_done : T.sim_fail);
      if (C.mode === "assess" && !(C.item in S.ans)) { S.ans[C.item] = ok ? 1 : 0; save(); updateScore(); }
    }
    function fail(t) {
      tries++;
      var hint = C.mode !== "assess" ? (C.hints[t] || C.hints[C.expect[k].target] || "") : "";
      say("bad", T.sim_wrong + (hint ? " " + hint : "") + " (" + tries + "/" + C.max + ")");
      if (tries < C.max) return;
      failed = true;
      if (C.mode === "assess") return finish(false);
      if (C.on_fail === "replay_demo") return demo();
      if (C.on_fail === "continue") return finish(false);
      var f = fld(C.expect[k].target); if (f) f.classList.add("hint-on");
    }
    function value(el) { return el.type === "checkbox" ? (el.checked ? "on" : "") : el.hasAttribute("data-file") ? "attached" : (el.value || "").trim(); }
    function act(el) {
      if (done || demoing) return;
      var t = el.getAttribute("data-sim-field"), e = C.expect[k];
      if (!e) return;
      var v = value(el), isBtn = el.tagName === "BUTTON";
      if (t !== e.target) { if (isBtn || v) fail(t); return; }
      var want = e.value;
      var ok = want == null ? true : want === "*" ? !!v : v.replace(",", ".").toLowerCase() === String(want).replace(",", ".").toLowerCase();
      if (!ok) return fail(t);
      fld(t).classList.add("done"); k++;
      say("ok", T.correct + (k < C.expect.length ? " · " + T.step + " " + (k + 1) + " " + T.of + " " + C.expect.length : ""));
      if (k >= C.expect.length) finish(!failed); else guide();
    }
    function reset(keepFail) {
      k = 0; tries = 0; done = false; if (!keepFail) failed = false;
      $$("[data-sim-field]", root).forEach(function (el) { if (el.type === "checkbox") el.checked = false; else if (el.tagName !== "BUTTON") el.value = ""; });
      $$(".sc-f", root).forEach(function (f) { f.classList.remove("done", "hot", "hint-on"); });
      msg.textContent = ""; toast.hidden = true; guide();
    }
    function demo() {
      demoing = true; reset(true);
      var i = 0;
      (function nx() {
        if (i >= C.demo.length) { demoing = false; reset(true); say("", T.try_again); return; }
        var a = C.demo[i++], f = a.target && fld(a.target);
        $$(".sc-f", root).forEach(function (x) { x.classList.remove("hot"); });
        if (f) { f.classList.add("hot"); var el = $("[data-sim-field]", f); if (el && a.value && el.tagName !== "BUTTON") el.value = a.value; }
        setTimeout(nx, 900);
      })();
    }
    $$("[data-sim-field]", root).forEach(function (el) {
      el.addEventListener(el.tagName === "BUTTON" ? "click" : "change", function () { act(el); });
      if (el.tagName === "INPUT" && el.type === "text") el.addEventListener("keydown", function (e) { if (e.key === "Enter") act(el); });
    });
    $("[data-sim-reset]", root).addEventListener("click", function () { reset(false); });
    guide();
  });

  // ---------------------------------------------------------------- process flow edges
  function layoutFlows(scope) {
    $$(".flow", scope).forEach(function (fl) {
      fl.classList.toggle("vertical", fl.clientWidth < 620);
      var svg = $(".flow-svg", fl), edges = JSON.parse(fl.getAttribute("data-edges") || "[]"), fr = fl.getBoundingClientRect();
      if (!fr.width) return;
      var ns = "http://www.w3.org/2000/svg", out = "";
      out += '<defs><marker id="fa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="#5B6385"/></marker></defs>';
      edges.forEach(function (e, k) {
        var a = $('[data-node="' + e.from + '"]', fl), b = $('[data-node="' + e.to + '"]', fl);
        if (!a || !b) return;
        var ra = a.getBoundingClientRect(), rb = b.getBoundingClientRect();
        var ax = ra.left + ra.width / 2 - fr.left, ay = ra.top + ra.height / 2 - fr.top, bx = rb.left + rb.width / 2 - fr.left, by = rb.top + rb.height / 2 - fr.top;
        // clip to box edges
        function clip(x, y, tx, ty, r) { var dx = tx - x, dy = ty - y, sx = Math.abs(dx) ? (r.width / 2 + 2) / Math.abs(dx) : 1e9, sy = Math.abs(dy) ? (r.height / 2 + 2) / Math.abs(dy) : 1e9, s = Math.min(sx, sy); return [x + dx * s, y + dy * s]; }
        var p1 = clip(ax, ay, bx, by, ra), p2 = clip(bx, by, ax, ay, rb);
        out += '<line x1="' + p1[0] + '" y1="' + p1[1] + '" x2="' + p2[0] + '" y2="' + p2[1] + '" stroke="#5B6385" stroke-width="2" marker-end="url(#fa)"/>';
        var lab = $('.elabel[data-e="' + k + '"]', fl);
        if (lab) { lab.style.left = (p1[0] + p2[0]) / 2 + "px"; lab.style.top = (p1[1] + p2[1]) / 2 + "px"; }
      });
      svg.innerHTML = out;
    });
    $$("[data-screencast]", scope).forEach(function (r) { if (r._place) r._place(); });
  }
  window.addEventListener("resize", function () { var el = scenes[sceneOf(S.cur)]; if (el) layoutFlows(el); });
  function countUp(el) {
    var n = $(".n", el), to = parseFloat(el.getAttribute("data-count"));
    if (!n || isNaN(to) || window.matchMedia("(prefers-reduced-motion: reduce)").matches || el._done) return;
    el._done = 1; var t0 = performance.now(), dec = (String(to).split(".")[1] || "").length;
    (function f(t) { var k = Math.min(1, (t - t0) / 900); n.textContent = (to * k).toLocaleString(D.lang, { minimumFractionDigits: dec, maximumFractionDigits: dec }); if (k < 1) requestAnimationFrame(f); })(t0);
  }

  // print: open transcripts + reveal everything
  function finalCounts() { $$("[data-count]").forEach(function (el) { el._done = 1; var n = $(".n", el); if (n) n.textContent = parseFloat(el.getAttribute("data-count")).toLocaleString(D.lang); }); }
  window.addEventListener("beforeprint", function () {
    finalCounts();
    $$("details.transcript").forEach(function (d) { d.setAttribute("open", ""); });
    Object.keys(scenes).forEach(function (k) { layoutFlows(scenes[k]); });
  });
  window.addEventListener("pagehide", function () { save(); if (LMS && LMS.finish) LMS.finish(); });

  // ---------------------------------------------------------------- boot
  load();
  $$("[data-check]").forEach(function (c) { if (S.chk[c.getAttribute("data-check")]) c.checked = true; });
  syncQuiz();
  var hashScene = location.hash.replace(/^#s-/, "");
  if (/[?&]all=1/.test(location.search)) { finalCounts(); $$("details.transcript").forEach(function (d) { d.setAttribute("open", ""); }); document.documentElement.classList.remove("js"); $$("[data-reveal-scope] [data-reveal]").forEach(function (e) { e.classList.add("on"); }); Object.keys(scenes).forEach(function (k) { layoutFlows(scenes[k]); }); return; }
  var start = { m: "l", i: 0 };
  if (hashScene && linear.indexOf(hashScene) >= 0) start = branchScenes[hashScene] ? { m: "b", n: branchScenes[hashScene], k: nodeById(branchScenes[hashScene]).scenes.indexOf(hashScene) } : { m: "l", i: linear.indexOf(hashScene) };
  else if (S.cur && sceneOf(S.cur) && scenes[sceneOf(S.cur)]) start = S.cur;
  if (start.m === "l" && branchScenes[linear[start.i]] && D.branching) start = enterBranch();
  show(start, false);
  if (/[?&]reveal=1/.test(location.search)) { // QA: reveal every progressive element
    $$("[data-reveal-all]").forEach(function (b) { b.click(); });
    $$("[data-reveal-co]").forEach(function (b) { for (var k = 0; k < 8; k++) b.click(); });
  }
  setTimeout(function () { window.scrollTo(0, 0); }, 0);
})();
