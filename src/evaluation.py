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

    print("\n=== Evaluation Result (Hunk Level) ===")
    print(f"MAP: {map_total/total:.4f}")
    print(f"MRR: {mrr_total/total:.4f}")
    print(f"TOP@1: {top1/total:.4f}")
    print(f"TOP@5: {top5/total:.4f}")
    print(f"TOP@10: {top10/total:.4f}")

def evaluate_ranking(scores, fix_hunk_map):
    map_total, mrr_total = 0.0, 0.0
    top1, top5, top10 = 0, 0, 0
    total = 0

    for bug_id, relevant_hunks in fix_hunk_map.items():
        bug_id_str = str(bug_id) 
        if bug_id_str not in scores:
            continue
        ranked_hunks = scores[bug_id]
        total += 1
        ranks = [i for i, (hunk_id, _) in enumerate(ranked_hunks) if hunk_id in relevant_hunks]

        if not ranks:
            continue
        first = min(ranks)
        map_total += sum(1.0 / (r + 1) for r in ranks) / len(relevant_hunks)
        mrr_total += 1.0 / (first + 1)
        if first == 0:
            top1 += 1
        if first < 5:
            top5 += 1
        if first < 10:
            top10 += 1

    if total == 0:
        return {"MAP": 0.0, "MRR": 0.0, "TOP@1": 0.0, "TOP@5": 0.0, "TOP@10": 0.0}

    return {
        "MAP": map_total / total,
        "MRR": mrr_total / total,
        "TOP@1": top1 / total,
        "TOP@5": top5 / total,
        "TOP@10": top10 / total,
    }