"""Upload local media to the user's Postiz media library (public API) -> prints JSON {id, path} per file.

Postiz URL + token come from ~/.rabet-reels.json (postiz_url, postiz_token_file) or POSTIZ_URL / POSTIZ_API_KEY.
The token is never printed.
Results are cached in uploads.json next to the first file so re-runs don't re-upload.

usage: python postiz_upload.py <file> [file ...]
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

CFG = config.load()
BASE, key = config.postiz_url(CFG), config.postiz_token(CFG)

files = [Path(f) for f in sys.argv[1:]]
cache_p = files[0].parent / "uploads.json"
cache = json.loads(cache_p.read_text()) if cache_p.exists() else {}
out = {}
for f in files:
    k = f"{f.name}:{f.stat().st_size}"
    if k not in cache:
        r = subprocess.run(["curl", "-s", "-m", "900", "-X", "POST", f"{BASE}/api/public/v1/upload",
                            "-A", "curl/8.9.1", "-H", f"Authorization: {key}", "-F", f"file=@{f}"], capture_output=True, text=True)
        d = json.loads(r.stdout)
        if "path" not in d:
            sys.exit(f"upload failed for {f.name}: {r.stdout[:300]}")
        cache[k] = {"id": d["id"], "path": d["path"]}
        cache_p.write_text(json.dumps(cache, indent=1))
    out[f.name] = cache[k]
print(json.dumps(out, indent=1))
