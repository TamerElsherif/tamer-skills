/* tcs-render-lesson — SCORM 1.2 runtime adapter (plain SCORM 1.2, no vendor extensions).
   Finds the LMS API object (window.API in a parent/opener frame), then exposes window.TCS_LMS
   which lesson.js uses for bookmarking (cmi.suspend_data + cmi.core.lesson_location),
   score (cmi.core.score.raw/min/max) and status (cmi.core.lesson_status).
   If no API is found the lesson runs standalone and bookmarks to localStorage instead. */
(function () {
  "use strict";
  function scan(w) {
    var n = 0;
    while (w && !w.API && w.parent && w.parent !== w && n < 10) { n++; w = w.parent; }
    return (w && w.API) || null;
  }
  var api = null;
  try { api = scan(window) || (window.opener ? scan(window.opener) : null); } catch (e) { api = null; }
  if (!api) { if (window.console) console.info("[tcs] no SCORM API found; running standalone"); return; }

  var t0 = Date.now(), started = false, finished = false;
  var MAX_SUSPEND = 4096; // SCORM 1.2 cmi.suspend_data limit
  function get(k) { try { return String(api.LMSGetValue(k) || ""); } catch (e) { return ""; } }
  function set(k, v) { try { return api.LMSSetValue(k, String(v)); } catch (e) { return "false"; } }
  function commit() { try { api.LMSCommit(""); } catch (e) {} }
  function pad(n, w) { n = String(n); while (n.length < w) n = "0" + n; return n; }
  function span(ms) { // CMITimespan HHHH:MM:SS.SS
    var s = ms / 1000, h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = (s % 60).toFixed(2);
    return pad(h, 4) + ":" + pad(m, 2) + ":" + (sec.length < 5 ? "0" + sec : sec);
  }
  function fit(state) {
    if (state.length <= MAX_SUSPEND) return state;
    try { var o = JSON.parse(state); delete o.v; delete o.k; state = JSON.stringify(o); } catch (e) {}
    return state.length <= MAX_SUSPEND ? state : "";
  }

  window.TCS_LMS = {
    init: function () {
      if (!started) { started = String(api.LMSInitialize("")) === "true"; }
      var st = get("cmi.core.lesson_status");
      if (st === "" || st === "not attempted") { set("cmi.core.lesson_status", "incomplete"); commit(); }
      var entry = get("cmi.core.entry");
      return entry === "ab-initio" ? null : (get("cmi.suspend_data") || null);
    },
    save: function (state, location) {
      set("cmi.suspend_data", fit(state));
      if (location) set("cmi.core.lesson_location", String(location).slice(0, 255));
      var st = get("cmi.core.lesson_status");
      set("cmi.core.exit", (st === "passed" || st === "completed") ? "" : "suspend");
      commit();
    },
    score: function (raw, min, max) {
      set("cmi.core.score.min", min);
      set("cmi.core.score.max", max);
      set("cmi.core.score.raw", raw);
      commit();
    },
    status: function (s) {
      var cur = get("cmi.core.lesson_status");
      if (cur === "passed" && s !== "passed") return;           // never downgrade a pass
      if (cur === "completed" && s === "incomplete") return;
      set("cmi.core.lesson_status", s);
      if (s !== "incomplete") set("cmi.core.exit", "");
      commit();
    },
    finish: function () {
      if (finished || !started) return;
      finished = true;
      set("cmi.core.session_time", span(Date.now() - t0));
      commit();
      try { api.LMSFinish(""); } catch (e) {}
    }
  };
  window.addEventListener("beforeunload", function () { window.TCS_LMS.finish(); });
})();
