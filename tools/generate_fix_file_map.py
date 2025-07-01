import json
import os
from collections import defaultdict

def load_json(path):
    with open(path) as f:
        return json.load(f)

def build_fix_file_map(fix_hunk_map, hunks):
    # hunk_id → filename のマップを作る
    hunk_id_to_file = {}
    for hunk in hunks:
        hunk_id = f"{hunk['commit_id']}:{hunk['index']}"
        hunk_id_to_file[hunk_id] = hunk['filename']

    # bug_id → 修正ファイル一覧を構築
    fix_file_map = {}
    for bug_id, hunk_ids in fix_hunk_map.items():
        files = set()
        for hunk_id in hunk_ids:
            filename = hunk_id_to_file.get(hunk_id)
            if filename:
                files.add(filename)
        if files:
            fix_file_map[bug_id] = sorted(files)

    return fix_file_map

def main():
    fix_hunk_map_path = "data/fix_hunk_map.json"
    hunks_path = "data/hunks.json"
    output_path = "data/fix_file_map.json"

    if not os.path.exists(fix_hunk_map_path) or not os.path.exists(hunks_path):
        print("Missing input files.")
        return

    fix_hunk_map = load_json(fix_hunk_map_path)
    hunks = load_json(hunks_path)

    fix_file_map = build_fix_file_map(fix_hunk_map, hunks)

    with open(output_path, "w") as f:
        json.dump(fix_file_map, f, indent=2)

    print(f"fix_file_map.json written to {output_path}")

if __name__ == "__main__":
    main()
