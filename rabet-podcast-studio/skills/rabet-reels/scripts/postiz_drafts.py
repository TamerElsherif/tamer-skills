"""Create Postiz posts (draft or schedule — whatever the payload says) from a payload built by postiz_payload.py,
via the Postiz MCP endpoint (JSON-RPC over HTTP, tool integrationSchedulePostTool — the same one the Claude connector
uses). URL + token from ~/.rabet-reels.json; the token is never printed. Appends one row per post to <csv>.

usage: python postiz_drafts.py <payload.json> <reel id> <drafts.csv>
"""
import csv
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

CFG = config.load()
URL = os.environ.get("POSTIZ_MCP_URL", config.postiz_url(CFG) + "/api/mcp")
key = config.postiz_token(CFG)
NAMES = {v["id"]: v["name"] for v in config.channels(CFG).values()}
session = None


def rpc(method, params, rid=1):
    global session
    h = {"Authorization": f"Bearer {key}", "Content-Type": "application/json", "Accept": "application/json, text/event-stream", "User-Agent": "curl/8.9.1"}
    if session:
        h["mcp-session-id"] = session
    body = {"jsonrpc": "2.0", "method": method, "params": params}
    if rid is not None:
        body["id"] = rid
    req = urllib.request.Request(URL, json.dumps(body).encode(), h)
    with urllib.request.urlopen(req, timeout=300) as r:
        session = r.headers.get("mcp-session-id") or session
        txt = r.read().decode()
    if rid is None:
        return None
    for line in txt.splitlines():  # SSE or plain JSON
        line = line[5:].strip() if line.startswith("data:") else line.strip()
        if line.startswith("{"):
            return json.loads(line)
    raise RuntimeError(txt[:300])


def main(payload_p, reel, csv_p):
    payload = json.load(open(payload_p, encoding="utf-8"))
    rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "rabet-reels", "version": "1"}})
    rpc("notifications/initialized", {}, rid=None)
    res = rpc("tools/call", {"name": "integrationSchedulePostTool", "arguments": payload}, rid=2)
    if "error" in res or res["result"].get("isError"):
        sys.exit(f"draft creation failed: {json.dumps(res)[:500]}")
    content = res["result"].get("structuredContent") or json.loads(res["result"]["content"][0]["text"])
    out = content["output"]
    with open(csv_p, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for p, o in zip(payload["socialPost"], out):
            kind = next((s["value"] for s in p["settings"] if s["key"] == "post_type"), "short" if any(w in NAMES[o["integration"]] for w in ("YouTube", "TikTok")) else "post")
            kind += "+comment" if len(p["postsAndComments"]) > 1 else ""
            media = "clean" if kind.startswith("story") else "cover"
            w.writerow([reel, NAMES[o["integration"]], kind, p["date"][:16] + "Z", "", o["postId"], media])
    print(f"{len(out)} {payload['socialPost'][0]['type']} posts created for reel {reel}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
