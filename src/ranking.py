# src/ranking.py

from src.vectorizer import preprocess, build_vectorizer, vectorize, preprocess_ce, build_vectorizer_ce
from src.scoring import NL_score, CE_score, Fix_score, source_score, determine_alpha
import numpy as np
import math
import datetime

def compute_scores(nl_corpus, ce_corpus, bug_reports, fix_hunk_map, hunks, commit_unix_time):
    results = {}

    # --- Hunk ID とその NL 前処理済みテキスト ---
    hunk_id_map = {f"{h['commit_id']}:{h['index']}": i for i, h in enumerate(hunks)}
    hunk_texts_nl = {hid: preprocess(hunks[i]['diff']) for hid, i in hunk_id_map.items()}
    bug_texts_nl = {
        str(b['id']): preprocess(
            b.get('summary', '') + '\n' +
            b.get('description', '') + '\n' +
            '\n'.join(b.get('comments', []))
        )
        for b in bug_reports
    }

    # --- NLベクトル構築 ---
    vectorizer_nl = build_vectorizer(list(bug_texts_nl.values()) + list(hunk_texts_nl.values()))
    bug_vecs_nl = {bid: vectorize([text], vectorizer_nl).toarray()[0] for bid, text in bug_texts_nl.items()}
    hunk_vecs_nl = {hid: vectorize([text], vectorizer_nl).toarray()[0] for hid, text in hunk_texts_nl.items()}

    # --- CEベクトル構築 ---
    ce_vectorizer = build_vectorizer_ce(ce_corpus)
    bug_vecs_ce = {}
    hunk_vecs_ce = {}

    for bug_id in ce_corpus:
        bug_vecs_ce[bug_id] = {}
        for hunk_id, tokens in ce_corpus[bug_id].items():
            text = preprocess_ce(tokens)
            vec = vectorize([text], ce_vectorizer).toarray()[0]
            bug_vecs_ce[bug_id][hunk_id] = vec
            hunk_vecs_ce[hunk_id] = vec  # 各hunk_idのベクトルも保存

    # --- スコアリング ---
    for bug in bug_reports:
        bug_id = str(bug['id'])
        bvec_nl = bug_vecs_nl[bug_id]

        # CEベクトル：NLトークンと同じ形状のゼロベクトルを初期値に
        fix_hunks = fix_hunk_map.get(bug_id, [])
        ce_entries = {
            hid: vec for hid, vec in bug_vecs_ce.get(bug_id, {}).items()
            if hid not in fix_hunks  # ←評価対象を除外
        }

        if ce_entries:
            bvec_ce = np.mean(list(ce_entries.values()), axis=0)
        else:
            bvec_ce = np.zeros_like(bvec_nl)

        # --- Fixスコア計算 ---
        try:
            dt = datetime.datetime.strptime(bug["creation_ts"], "%Y-%m-%dT%H:%M:%SZ")
            bug_time = int(dt.timestamp())
        except Exception as e:
            print(f"[Warning] Failed to parse timestamp for bug {bug_id}: {e}")
            continue

        timestamps = []
        for fix_hunk_id in fix_hunk_map.get(bug_id, []):
            commit_id = fix_hunk_id.split(":")[0]
            hunk_time = commit_unix_time.get(commit_id)
            if hunk_time:
                t = abs(bug_time - hunk_time) / 604800
                timestamps.append(t)

        fix = Fix_score(timestamps) if timestamps else 0.0
        alpha = determine_alpha(len(bvec_nl), len(bvec_ce))
        beta1 = 0.1

        scores = []
        for hunk_id, hvec_nl in hunk_vecs_nl.items():
            hvec_ce = hunk_vecs_ce.get(hunk_id, np.zeros_like(bvec_nl))
            nl = NL_score(bvec_nl, hvec_nl)
            ce = CE_score(bvec_ce, hvec_ce)
            final = source_score([nl], [ce], fix, alpha, beta1)
            scores.append((hunk_id, final))

        scores.sort(key=lambda x: x[1], reverse=True)
        results[bug_id] = scores

    return results