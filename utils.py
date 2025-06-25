# main.py
import json
import os
from src.data_acquisition import fetch_tomcat_repo, fetch_bug_reports
from src.preprocessing import extract_hunks_and_tokens
from src.ranking import compute_scores
from src.evaluation import evaluate_ranking

def generate_fix_hunk_map(bug_reports, hunks):
    fix_hunk_map = {}
    for bug in bug_reports:
        bug_id = str(bug["id"])
        matched_hunks = []
        for h in hunks:
            msg = h.get("msg", "")
            if bug_id in msg:
                hunk_id = f"{h['commit_id']}:{h['index']}"
                matched_hunks.append(hunk_id)
        if matched_hunks:
            fix_hunk_map[bug_id] = matched_hunks
    return fix_hunk_map

def main():
    with open("data/bug_reports.json") as f:
        bug_reports = json.load(f)

    with open("data/hunks.json") as f:
        hunks = json.load(f)

    fix_hunk_map = generate_fix_hunk_map(bug_reports, hunks)
    with open("data/fix_hunk_map.json", "w") as f:
        json.dump(fix_hunk_map, f, indent=2)

    # [3] 特徴抽出（NL/CEトークン化）
    nl_corpus, ce_corpus = extract_hunks_and_tokens(bug_reports, hunks, fix_hunk_map)

    # [4] ランキングスコアの計算（論文式に従ってNL, CE, Boostingを統合）
    scores = compute_scores(nl_corpus, ce_corpus, bug_reports, fix_hunk_map, hunks)
    with open("output/scores.json", "w") as f:
        json.dump(scores, f, indent=2)

    # [5] 評価（MAP, MRR, Top@k）
    result = evaluate_ranking(scores, fix_hunk_map)

    print("\n=== Evaluation Result (Hunk Level) ===")
    for k, v in result.items():
        print(f"{k}: {v:.4f}")

if __name__ == "__main__":
    main()
