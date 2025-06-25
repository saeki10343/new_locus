import json
import math
from collections import defaultdict


def evaluate_ranking(predictions: dict, fix_hunk_map: dict, topk_list=[1, 5, 10]):
    """
    :param predictions: {bug_id: [(hunk_id, score), ...]}  ← score降順
    :param fix_hunk_map: {bug_id: [hunk_id, ...]} ← ground truth
    :param topk_list: 評価する Top@k のリスト
    :return: 評価指標を含む dict
    """
    map_total = 0.0
    mrr_total = 0.0
    topk_counts = defaultdict(int)
    valid_bug_count = 0

    for bug_id, pred_list in predictions.items():
        if bug_id not in fix_hunk_map:
            continue

        gt_hunks = set(fix_hunk_map[bug_id])
        ranks = []
        for rank, (hunk_id, _) in enumerate(pred_list, 1):
            if hunk_id in gt_hunks:
                ranks.append(rank)

        if not ranks:
            continue

        ranks.sort()
        valid_bug_count += 1

        # MAP: mean of (relevant数 / rank位置)
        map_total += sum([1 / r for r in ranks]) / len(gt_hunks)

        # MRR: 最初に正解だった位置の逆数
        mrr_total += 1 / ranks[0]

        for k in topk_list:
            if any(r <= k for r in ranks):
                topk_counts[k] += 1

    if valid_bug_count == 0:
        print("\u26a0 Ground truth に該当するバグが存在しません（評価対象 0 件）")
        return {}

    result = {
        "MAP": round(map_total / valid_bug_count, 4),
        "MRR": round(mrr_total / valid_bug_count, 4),
    }
    for k in topk_list:
        result[f"Top@{k}"] = round(topk_counts[k] / valid_bug_count, 4)

    return result


if __name__ == "__main__":
    with open("output/scores.json") as f:
        predictions = json.load(f)

    with open("data/fix_hunk_map.json") as f:
        fix_hunk_map = json.load(f)

    result = evaluate_ranking(predictions, fix_hunk_map)

    print("\n=== Evaluation Result (Hunk Level) ===")
    for k, v in result.items():
        print(f"{k}: {v:.4f}")
