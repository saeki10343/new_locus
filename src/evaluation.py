# Evaluation metrics module
# src/evaluation.py

def mean_average_precision(ranked_list, relevant_items):
    hits = 0
    sum_precisions = 0
    for i, item in enumerate(ranked_list):
        if item in relevant_items:
            hits += 1
            sum_precisions += hits / (i + 1)
    return sum_precisions / max(len(relevant_items), 1)


def mean_reciprocal_rank(ranked_list, relevant_items):
    for i, item in enumerate(ranked_list):
        if item in relevant_items:
            return 1 / (i + 1)
    return 0


def hit_at_k(ranked_list, relevant_items, k):
    return int(any(item in relevant_items for item in ranked_list[:k]))


def evaluate_results(results):
    print("検出されたバグ数:", len(results))
    print("Bug ID 例:", list(results.keys())[:5])
    from pathlib import Path
    import json

    with open("data/hunks.json") as f:
        hunks = json.load(f)

    with open("data/bug_reports.json") as f:
        bug_reports = json.load(f)

    # Generate ground truth map
    ground_truth = {}
    for bug in bug_reports:
        bug_id = str(bug["id"])
        gt = []
        for hunk in hunks:
            if str(bug_id) in hunk["msg"]:
                gt.append(f"{hunk['commit_id']}:{hunk['index']}")
        ground_truth[bug_id] = gt

    map_total, mrr_total = 0, 0
    top1, top5, top10 = 0, 0, 0
    total = 0

    for bug_id, ranked in results.items():
        gt = ground_truth.get(bug_id, [])
        if not gt:
            print(f"⚠ No ground truth for bug {bug_id}")
            continue
        map_total += mean_average_precision(ranked, gt)
        mrr_total += mean_reciprocal_rank(ranked, gt)
        top1 += hit_at_k(ranked, gt, 1)
        top5 += hit_at_k(ranked, gt, 5)
        top10 += hit_at_k(ranked, gt, 10)
        total += 1
    if total == 0:
        print("⚠ Ground truth に該当するバグが存在しません（評価対象 0 件）")
        return


    print("\n=== Evaluation Result (Hunk Level) ===")
    print(f"MAP: {map_total/total:.4f}")
    print(f"MRR: {mrr_total/total:.4f}")
    print(f"TOP@1: {top1/total:.4f}")
    print(f"TOP@5: {top5/total:.4f}")
    print(f"TOP@10: {top10/total:.4f}")
