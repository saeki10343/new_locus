# tools/generate_fix_map.py

import json
from collections import defaultdict

BUG_FILE = "data/bug_reports.json"
HUNK_FILE = "data/hunks.json"
OUT_FILE = "data/fix_hunk_map.json"

with open(BUG_FILE) as f:
    bugs = json.load(f)

with open(HUNK_FILE) as f:
    hunks = json.load(f)

fix_hunk_map = {}

for bug in bugs:
    bug_id = str(bug["id"])
    matched_hunks = []

    for h in hunks:
        msg = h.get("msg", "")
        if bug_id in msg:
            hunk_id = f"{h['commit_id']}:{h['index']}"
            matched_hunks.append(hunk_id)

    if matched_hunks:
        fix_hunk_map[bug_id] = matched_hunks

with open(OUT_FILE, "w") as f:
    json.dump(fix_hunk_map, f, indent=2)

print(f"Saved fix_hunk_map.json with {len(fix_hunk_map)} entries.")
