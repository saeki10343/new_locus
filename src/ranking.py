# src/ranking.py

from src.vectorizer import preprocess, build_vectorizer, vectorize
from src.scoring import NL_score, CE_score, Fix_score, source_score, determine_alpha
import numpy as np
import math

def compute_scores(nl_corpus, ce_corpus, bug_reports, fix_hunk_map, hunks, commit_unix_time):
    results = {}

    hunk_id_map = {f"{h['commit_id']}:{h['index']}": i for i, h in enumerate(hunks)}
    hunk_texts = {hid: preprocess(hunks[i]['diff']) for hid, i in hunk_id_map.items()}
    bug_texts = {str(b['id']): preprocess(b['summary'] + '\n' + b.get('description', '')) for b in bug_reports}

    vectorizer = build_vectorizer(list(bug_texts.values()) + list(hunk_texts.values()))
    bug_vecs = {bid: vectorize([text], vectorizer).toarray()[0] for bid, text in bug_texts.items()}
    hunk_vecs = {hid: vectorize([text], vectorizer).toarray()[0] for hid, text in hunk_texts.items()}

    for bug in bug_reports:
        bug_id = str(bug['id'])
        bvec_nl = bug_vecs[bug_id]
        bvec_ce = bvec_nl  # ★ 現状同一（将来的にCE特徴量と分ける）

        # --- Fixスコア用 timestamp 抽出 ---
        fix_hunks = fix_hunk_map.get(bug_id, [])
        timestamps = []
        for fix_hunk_id in fix_hunks:
            commit_id = fix_hunk_id.split(":")[0]
            t = commit_unix_time.get(commit_id)
            if t is not None:
                timestamps.append(t)

        # --- 正規化 ---
        if timestamps:
            min_ts = min(timestamps)
            max_ts = max(timestamps)
            if max_ts > min_ts:
                normalized_ts = [(t - min_ts) / (max_ts - min_ts) for t in timestamps]
            else:
                normalized_ts = [0.0 for _ in timestamps]
            fix = Fix_score(normalized_ts)
        else:
            fix = 0.0

        alpha = determine_alpha(len(bvec_nl), len(bvec_ce))
        beta1 = 0.1

        scores = []
        for hunk_id, hvec_nl in hunk_vecs.items():
            hvec_ce = hvec_nl  # ★ 現状同一（将来的に分ける）

            nl = NL_score(bvec_nl, hvec_nl)
            ce = CE_score(bvec_ce, hvec_ce)

            final = source_score([nl], [ce], fix, alpha, beta1)
            scores.append((hunk_id, final))

        scores.sort(key=lambda x: x[1], reverse=True)
        results[bug_id] = scores

    return results
