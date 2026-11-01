"""Temporary public link for files too big for the Postiz upload API (Cloudflare caps request bodies at 100 MB).

Postiz's `uploadFromUrlTool` makes the Postiz server download the file, so only a small request crosses Cloudflare.
This script gives local files a short-lived public URL:

  python tunnel_upload.py start <file> [<file> ...]   # hard-links files into a temp folder, starts a localhost
                                                      # server + cloudflared quick tunnel, prints one URL per file
  python tunnel_upload.py wait                        # blocks until no download has been open for 15 s
  python tunnel_upload.py stop                        # stops tunnel + server, deletes the temp folder (links only)

Storage: the temp folder sits on the same drive as the first file and holds hard links, so it uses no extra space and
deleting it never touches the originals. A file on another drive is copied (and that copy is deleted on stop).
Only the temp folder is served. Strangers scan new trycloudflare.com addresses within seconds: never put anything
else in it, and always run `stop` when done (also after an error).
"""
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

STATE = Path(os.environ.get("TEMP", ".")) / "rabet_tunnel_state.json"
CLOUDFLARED = [r"C:\Program Files (x86)\cloudflared\cloudflared.exe", r"C:\Program Files\cloudflared\cloudflared.exe",
               "cloudflared"]

sys.stdout.reconfigure(encoding="utf-8")


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def cloudflared_exe():
    for c in CLOUDFLARED:
        if c == "cloudflared" or os.path.exists(c):
            return c


def start(files):
    if STATE.exists():
        sys.exit(f"A tunnel is already open ({STATE}); run `stop` first.")
    files = [Path(f).resolve() for f in files]
    for f in files:
        if not f.is_file():
            sys.exit(f"missing: {f}")
    tmp = Path(files[0].anchor) / "rabet_tunnel_tmp"
    tmp.mkdir(exist_ok=True)
    names = {}
    for i, f in enumerate(files, 1):
        name = f"f{i:02d}{f.suffix.lower()}"  # ASCII names: no URL-encoding issues with Arabic file names
        dst = tmp / name
        try:
            os.link(f, dst)
        except OSError:
            shutil.copy2(f, dst)
        names[name] = str(f)
    port = free_port()
    log = tmp.parent / "rabet_tunnel_cloudflared.log"
    flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=tmp,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
    cf = subprocess.Popen([cloudflared_exe(), "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{port}"],
                          stdout=open(log, "w"), stderr=subprocess.STDOUT, creationflags=flags)
    STATE.write_text(json.dumps({"tmp": str(tmp), "log": str(log), "port": port, "pids": [srv.pid, cf.pid]}))
    url = None
    for _ in range(60):
        m = re.search(r"https://[a-z0-9-]+\.trycloudflare\.com", log.read_text(errors="ignore"))
        if m:
            url = m.group(0)
            break
        time.sleep(1)
    if not url:
        stop()
        sys.exit("cloudflared gave no URL; stopped and cleaned up")
    time.sleep(5)  # the address needs a few seconds before it resolves
    st = json.loads(STATE.read_text())
    st["url"] = url
    STATE.write_text(json.dumps(st))
    for name, src in names.items():
        print(f"{url}/{name}\t{os.path.getsize(src) / 1048576:.0f} MB\t{src}")


def open_downloads(port):
    out = subprocess.run(["netstat", "-an"], capture_output=True, text=True).stdout
    return sum(1 for l in out.splitlines() if f"127.0.0.1:{port}" in l and "ESTABLISHED" in l)


def wait(limit=3600):
    st = json.loads(STATE.read_text())
    idle, t = 0, 0
    while idle < 3 and t < limit:
        idle = idle + 1 if open_downloads(st["port"]) == 0 else 0
        time.sleep(5)
        t += 5
    print(f"no open downloads after {t}s")


def stop():
    if not STATE.exists():
        print("nothing open")
        return
    st = json.loads(STATE.read_text())
    for pid in st["pids"]:
        if os.name == "nt":
            subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
        else:
            try:
                os.kill(pid, 9)
            except OSError:
                pass
    time.sleep(2)
    shutil.rmtree(st["tmp"], ignore_errors=True)  # hard links / temp copies only
    try:
        os.remove(st["log"])
    except OSError:
        pass
    STATE.unlink()
    print(f"tunnel closed, removed {st['tmp']}")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "start" and len(sys.argv) > 2:
        start(sys.argv[2:])
    elif cmd == "wait":
        wait()
    elif cmd == "stop":
        stop()
    else:
        sys.exit(__doc__)
