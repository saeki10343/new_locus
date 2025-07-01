from src.vectorizer import preprocess, build_vectorizer, vectorize, preprocess_ce, build_vectorizer_ce
from src.scoring import NL_score, CE_score, Fix_score, Time_score, change_score, determine_alpha
import numpy as np
import datetime

def compute_scores(nl_corpus, ce_corpus, bug_reports, fix_hunk_map, hunks, commit_unix_time, change_map=None):
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
    hunk_vecs_ce = {}
    bug_ce_pool = {}

    for bug_id, hunk_tokens in ce_corpus.items():
        for hunk_id, tokens in hunk_tokens.items():
            vec = vectorize([preprocess_ce(tokens)], ce_vectorizer).toarray()[0]
            hunk_vecs_ce[hunk_id] = vec
            bug_ce_pool.setdefault(bug_id, {})[hunk_id] = vec

    # --- スコアリング ---
    for bug in bug_reports:
        bug_id = str(bug['id'])
        bvec_nl = bug_vecs_nl[bug_id]

        # --- 評価対象の CE ベクトルを除いた bug_vec_ce を作成 ---
        fix_hunks = fix_hunk_map.get(bug_id, [])
        ce_pool = bug_ce_pool.get(bug_id, {})
        ce_vectors = [v for hid, v in ce_pool.items() if hid not in fix_hunks]

        if ce_vectors:
            bvec_ce = np.mean(ce_vectors, axis=0)
        else:
            bvec_ce = np.zeros_like(bvec_nl)

        # --- Fix スコアの計算 ---
        try:
            dt = datetime.datetime.strptime(bug["creation_ts"], "%Y-%m-%dT%H:%M:%SZ")
            bug_time = int(dt.timestamp())
        except Exception as e:
            print(f"[Warning] Failed to parse timestamp for bug {bug_id}: {e}")
            continue

        timestamps = []
        for fix_hunk_id in fix_hunks:
            commit_id = fix_hunk_id.split(":")[0]
            hunk_time = commit_unix_time.get(commit_id)
            if hunk_time:
                t = abs(bug_time - hunk_time) / 604800
                timestamps.append(t)
        fix = Fix_score(timestamps) if timestamps else 0.0
        alpha = determine_alpha(len(bvec_nl), len(bvec_ce))
        beta1 = 0.1
        beta2 = 0.1

        # --- hunk -> change マップ（Time_score用）を準備 ---
        change_dict = {}
        if change_map and bug_id in change_map:
            for file_path, changes in change_map[bug_id].items():
                for cid, hids in changes.items():
                    for hid in hids:
                        change_dict[hid] = cid

        # --- スコアリング ---
        scores = {}
        for hunk_id, hvec_nl in hunk_vecs_nl.items():
            hvec_ce = hunk_vecs_ce.get(hunk_id, np.zeros_like(bvec_nl))
            nl = NL_score(bvec_nl, hvec_nl)
            ce = CE_score(bvec_ce, hvec_ce)
            final = nl + alpha * ce + beta1 * fix

            # --- Time_score と Change_score を統合 ---
            if change_map:
                # 各 change_id に属する hunk の順位情報
                ranked = sorted(hunk_vecs_nl.keys(), key=lambda x: nl + alpha * ce + beta1 * fix, reverse=True)
                rank_dict = {h: i for i, h in enumerate(ranked)}
                change_id = change_dict.get(hunk_id)
                if change_id:
                    change_hunks = [h for h, cid in change_dict.items() if cid == change_id]
                    t_score = Time_score(rank_dict, change_hunks)
                    c_score = change_score([nl], [ce], t_score, alpha, beta2)
                    final = c_score  # 上書き（式8）

            scores[hunk_id] = final

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        results[bug_id] = sorted_scores

    return results
