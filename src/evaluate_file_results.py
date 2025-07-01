import json
import os

def load_file_scores(path):
    with open(path) as f:
        return json.load(f)

def load_fix_map(path):
    with open(path) as f:
        return json.load(f)

def evaluate(file_scores, fix_map, top_k=10):
    metrics = {
        "MAP": 0.0,
        "MRR": 0.0,
        "TOP@1": 0,
        "TOP@5": 0,
        "TOP@10": 0,
        "Count": 0
    }

    for bug_id, fixed_files in fix_map.items():
        ranked_files = [path for path, _ in file_scores]

        relevant = set(fixed_files)
        if not relevant:
            continue

        ap = 0.0
        hit = False
        for rank, file in enumerate(ranked_files, 1):
            if file in relevant:
                if not hit:
                    metrics["MRR"] += 1.0 / rank
                    hit = True
                if rank <= top_k:
                    ap += 1.0 / rank
                if rank == 1:
                    metrics["TOP@1"] += 1
                if rank <= 5:
                    metrics["TOP@5"] += 1
                if rank <= 10:
                    metrics["TOP@10"] += 1

        if hit:
            metrics["MAP"] += ap / len(relevant)
        metrics["Count"] += 1

    if metrics["Count"] > 0:
        for key in ["MAP", "MRR"]:
            metrics[key] /= metrics["Count"]

    return metrics

def main():
    scores_path = "output/file_scores.json"
    fix_map_path = "data/fix_file_map.json"  # ← ファイル単位の修正 ground-truth

    if not os.path.exists(scores_path) or not os.path.exists(fix_map_path):
        print("Missing file_scores or fix_file_map.")
        return

    file_scores = load_file_scores(scores_path)
    fix_map = load_fix_map(fix_map_path)

    metrics = evaluate(file_scores, fix_map)

    print("=== Evaluation Result (File Level) ===")
    for key, value in metrics.items():
        print(f"{key}: {value:.4f}" if isinstance(value, float) else f"{key}: {value}")

if __name__ == "__main__":
    main()
