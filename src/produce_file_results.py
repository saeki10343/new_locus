import json
from collections import defaultdict

# 入力ファイル
HUNKS_FILE = "data/hunks.json"
SCORES_FILE = "output/scores.json"
OUTPUT_FILE = "output/file_scores.json"

# 1. ハンクファイルを読み込む
with open(HUNKS_FILE) as f:
    hunks = json.load(f)

# 2. スコアファイル（scores.json）を読み込み、hunk_id をキーに変換
with open(SCORES_FILE) as f:
    hunk_scores_raw = json.load(f)

hunk_scores = {}
for bug_id, scored_hunks in hunk_scores_raw.items():
    for hunk_id, score in scored_hunks:
        hunk_scores[hunk_id] = score

# 3. hunk_id からファイル名を集計
file_scores = defaultdict(float)

for hunk in hunks:
    hunk_id = f"{hunk['commit_id']}:{hunk['index']}"
    if hunk_id in hunk_scores:
        file_path = hunk["filename"]
        file_scores[file_path] += hunk_scores[hunk_id]

# 4. スコア順にソートして保存
sorted_file_scores = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(sorted_file_scores, f, indent=2)

print(f"file_scores.json saved with {len(sorted_file_scores)} entries.")
