"""Surgical cut points: never cut inside a word.

Whisper word times are approximate (often 50-150 ms off, worst at word ends) and sheet
ranges are whole seconds, so neither is a cut point. A cut goes in the first real gap after
the last kept word (or the last gap before the first kept word), where "level" is the louder of the
full-band and the high-frequency (pre-emphasised) energy, so the hiss of a final "s"
counts as speech. Short dips inside a word (stop closures like the "t" in "costs") are
shallower than a real word gap, and the window starts at the kept word's own end.
Never pick the deepest dip: a deeper pause after the NEXT word would swallow that word.

    from cutsafe import Env, CutError
    env = Env(src)
    t_in  = env.snap_in(lo, hi)     # LAST gap in the window: lo = previous word's end - 0.25, hi = first kept word's start + 0.12
    t_out = env.snap_out(lo, hi)    # FIRST gap in the window: lo = last kept word's end - 0.08, hi = next word's start + 0.3
    env.margin(t)                   # dB of quiet at t below the gap threshold (>= 0 is safe)
    env.pauses(a, b, 0.30)          # inner pauses long enough to jump-cut out

CutError means the speech runs on with no real gap: end the clip at another phrase break.
"""
import subprocess
import numpy as np

SR, HOP, WIN = 48000, 240, 480      # 5 ms hop, 10 ms window
GAP_DB = 20.0                        # a word gap is at least this far under the speech level
PAUSE_DB = 30.0                      # a pause (safe to remove) is this far under it
MIN_GAP = 0.015                      # shortest run under the threshold that counts as a word gap
SPEECH_DB = 18.0                     # within this of the speech level counts as a spoken sound
TIERS = (GAP_DB, 15.0, 12.0)         # tried in order; the depth used is left in env.last_depth


class CutError(RuntimeError):
    pass


class Env:
    def __init__(self, src, pad=6.0):
        self.src, self.pad, self._cache = src, pad, {}

    def _win(self, t):
        a = max(0.0, np.floor((t - self.pad) / 4) * 4)          # 4 s grid, >= 6 s context each side
        if a not in self._cache:
            x = np.frombuffer(subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{2 * self.pad + 4:.3f}", "-i", self.src,
                 "-vn", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout, np.float32)
            def db(s):
                n = (len(s) - WIN) // HOP
                fr = np.lib.stride_tricks.as_strided(s, (n, WIN), (s.strides[0] * HOP, s.strides[0]))
                return 10 * np.log10((fr ** 2).mean(1) + 1e-12)
            level = np.maximum(db(x), db(np.diff(x, prepend=0).astype(np.float32)) - 6)
            self._cache[a] = (a, level, float(np.percentile(level, 90)))
        return self._cache[a]

    def _range(self, lo, hi):
        a, level, speech = self._win((lo + hi) / 2)
        i0, i1 = max(0, int(round((lo - a) * 200))), min(len(level), int(round((hi - a) * 200)))
        return a, level, speech, i0, i1

    def _valleys(self, lo, hi, depth, min_len):
        a, level, speech, i0, i1 = self._range(lo, hi)
        q = level[i0:i1] < speech - depth
        out, i = [], 0
        while i < len(q):
            if q[i]:
                j = i
                while j < len(q) and q[j]: j += 1
                s, e = a + (i0 + i) / 200 + WIN / SR / 2, a + (i0 + j) / 200 + WIN / SR / 2
                if e - s >= min_len:
                    out.append((s, e))
                i = j
            else:
                i += 1
        return out

    def _snap(self, lo, hi, side):
        for depth in TIERS:                               # connected speech: the dip between two words is shallower
            v = self._valleys(lo, hi, depth, MIN_GAP)
            if side == "in":                              # the gap must open before the first kept word starts
                v = [g for g in v if g[0] <= hi - 0.10]
            # a real word boundary has speech on the kept side: an out gap closes a spoken stretch,
            # an in gap opens one (otherwise it is the quiet onset of a word, e.g. a plosive's closure)
            v = [g for g in v if self._speech_near(g, side)]
            if v: break
        else:
            raise CutError(f"no word gap in {lo:.2f}-{hi:.2f}s: use another phrase break")
        self.last_depth = depth
        s, e = v[0] if side == "out" else v[-1]          # first gap after the kept word / last gap before it
        if side == "out":                                 # soft tails only happen at word ends
            s, e = self._to_pause(s, e, side)
        if e - s > 0.16:                                  # a real pause: keep a little air by the speech
            return float(e - 0.07 if side == "in" else s + 0.09)
        if side == "in":                                  # just before the onset: the previous word's soft tail stays out
            return float(max((s + e) / 2, e - 0.03))
        return float((s + e) / 2)

    def _to_pause(self, s, e, side, reach=0.30):
        """A shallow dip right next to a real pause is still the word's soft tail (or onset):
        if no speech returns before a pause begins, cut in the pause instead."""
        a, level, speech = self._win(s)
        quiet, pause = speech - SPEECH_DB, speech - PAUSE_DB
        step = 1 if side == "out" else -1
        i = int(round(((e if side == "out" else s) - a) * 200))
        for k in range(int(reach * 200)):
            j = i + step * k
            if j < 0 or j >= len(level) or level[j] >= quiet:
                return s, e                               # speech came back first: keep the dip
            if level[j] < pause:
                v = self._valleys(*sorted((a + j / 200 - 0.5 * step, a + j / 200 + 0.5 * step)), PAUSE_DB, 0.05)
                g = min(v, key=lambda g: abs((g[0] + g[1]) / 2 - (a + j / 200)), default=None)
                return g if g else (s, e)
        return s, e

    def _speech_near(self, g, side, span=0.35):
        a, level, speech = self._win(g[0])
        if side == "out":
            i0, i1 = int((g[0] - span - a) * 200), int((g[0] - a) * 200)
        else:
            i0, i1 = int((g[1] - a) * 200), int((g[1] + span - a) * 200)
        seg = level[max(0, i0):max(0, i1)]
        return len(seg) and seg.max() >= speech - SPEECH_DB

    def snap_in(self, lo, hi):
        return self._snap(lo, hi, "in")

    def snap_out(self, lo, hi):
        return self._snap(lo, hi, "out")

    def margin(self, t):
        a, level, speech = self._win(t)
        i = int(round((t - WIN / SR / 2 - a) * 200))
        return float(speech - GAP_DB - level[max(0, i - 2):i + 3].max())

    def on_grid(self, t, fps):
        """The neighbouring frame time (floor or ceil) that sits deeper in the gap."""
        f = np.floor(t * fps)
        return max((f / fps, (f + 1) / fps), key=self.margin)

    def safe_in(self, t, before=0.50, after=0.05):
        """Snap a rough start (a sheet second or a silencedetect edge) back to the last gap before it; keeps t if none."""
        try:
            return self.snap_in(t - before, t + after)
        except CutError as e:
            print(f"  cutsafe: start {t:.2f}s kept, {e}")
            return t

    def safe_out(self, t, before=0.0, after=0.50):
        """Snap a rough end forward to the first real gap, so the word spoken at t is kept; keeps t if none."""
        try:
            return self.snap_out(t - before, t + after)
        except CutError as e:
            print(f"  cutsafe: end {t:.2f}s kept, {e}")
            return t

    def pauses(self, lo, hi, min_len):
        return [(s, e) for s, e in self._valleys(lo, hi, PAUSE_DB, min_len) if s > lo + 0.05 and e < hi - 0.05]
