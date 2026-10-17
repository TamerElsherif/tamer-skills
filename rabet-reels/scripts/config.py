"""Per-user settings for rabet-reels, kept OUTSIDE the skill so the skill folder stays portable.

Looked up in order: $RABET_REELS_CONFIG, then ~/.rabet-reels.json. See config.example.json for every key.
Environment variables override single keys: POSTIZ_URL, POSTIZ_API_KEY, POSTIZ_TOKEN_FILE.
"""
import json
import os
import re
from pathlib import Path


def load():
    p = Path(os.environ.get("RABET_REELS_CONFIG", Path.home() / ".rabet-reels.json"))
    cfg = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
    if os.environ.get("POSTIZ_URL"):
        cfg["postiz_url"] = os.environ["POSTIZ_URL"]
    if os.environ.get("POSTIZ_TOKEN_FILE"):
        cfg["postiz_token_file"] = os.environ["POSTIZ_TOKEN_FILE"]
    for k in ("output_dir", "postiz_token_file"):
        if cfg.get(k):
            cfg[k] = os.path.expanduser(cfg[k])
    return cfg


def postiz_url(cfg):
    url = cfg.get("postiz_url")
    if not url:
        raise SystemExit("set postiz_url in ~/.rabet-reels.json (or POSTIZ_URL), e.g. https://postiz.example.com")
    return url.rstrip("/")


def postiz_token(cfg):
    """API token: $POSTIZ_API_KEY, else the Bearer value inside postiz_token_file (e.g. the `claude mcp add` line)."""
    if os.environ.get("POSTIZ_API_KEY"):
        return os.environ["POSTIZ_API_KEY"]
    f = cfg.get("postiz_token_file")
    if not f or not Path(f).exists():
        raise SystemExit("no Postiz token: set POSTIZ_API_KEY or postiz_token_file in ~/.rabet-reels.json")
    m = re.search(r"Bearer\s+([^\s\"']+)", Path(f).read_text(encoding="utf-8"))
    return m.group(1) if m else Path(f).read_text(encoding="utf-8").strip()


def channels(cfg):
    """{key: {"id": <Postiz integration id>, "name": <label>}} — keys used by postiz_payload.py."""
    ch = cfg.get("channels")
    if not ch:
        raise SystemExit("add your Postiz channels to ~/.rabet-reels.json (see config.example.json)")
    return ch
