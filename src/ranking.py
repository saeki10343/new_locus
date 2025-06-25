# src/ranking.py

from src.vectorizer import preprocess, build_vectorizer, vectorize
from src.scoring import NL_score, CE_score, Fix_score, Time_score, source_score, change_score, determine_alpha
import numpy as np

def compute_scores(nl_corpus, ce_corpus, bug_reports, fix_hunk_map, hunks):
    results = {}

    hunk_id_map = {f"{h['commit_id']}:{h['index']}": i for i, h in enumerate(hunks)}
    hunk_texts = {hid: preprocess(hunks[i]['diff']) for hid, i in hunk_id_map.items()}
    bug_texts = {str(b['id']): preprocess(b['summary'] + '\n' + b.get('description', '')) for b in bug_reports}

    vectorizer = build_vectorizer(list(bug_texts.values()) + list(hunk_texts.values()))
    bug_vecs = {bid: vectorize([text], vectorizer).toarray()[0] for bid, text in bug_texts.items()}
    hunk_vecs = {hid: vectorize([text], vectorizer).toarray()[0] for hid, text in hunk_texts.items()}

    for bug_id in bug_texts:
        bvec_nl = bug_vecs[bug_id]
        bvec_ce = bvec_nl

        scores = []
        for hunk_id in hunk_vecs:
            hvec_nl = hunk_vecs[hunk_id]
            hvec_ce = hvec_nl

            nl = NL_score(bvec_nl, hvec_nl)
            ce = CE_score(bvec_ce, hvec_ce)

            alpha = determine_alpha(len(bvec_ce), len(bvec_nl))
            timestamps = [0.5]  # 仮置き

            fix = Fix_score(timestamps)
            final = source_score([nl], [ce], fix, alpha, beta1=0.1)

            scores.append((hunk_id, final))

        scores.sort(key=lambda x: x[1], reverse=True)
        results[bug_id] = scores

    return results
