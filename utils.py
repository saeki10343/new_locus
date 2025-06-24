# evaluate_only.py
from src.preprocessing import extract_hunks_and_tokens
from src.ranking import compute_scores
from src.evaluation import evaluate_results
import json

# Load saved inputs
with open("data/bug_reports.json") as f:
    bug_reports = json.load(f)

with open("data/hunks.json") as f:
    hunks = json.load(f)

# 構築: hunk_map
hunk_map = {f"{h['commit_id']}:{h['index']}": h for h in hunks}

# 特徴量抽出
nl_corpus, ce_corpus = extract_hunks_and_tokens(bug_reports, hunks)

# スコア計算 & 評価
results = compute_scores(nl_corpus, ce_corpus, bug_reports, hunk_map)
evaluate_results(results)
