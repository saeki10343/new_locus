# Ranking model module
# src/ranking.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.preprocessing import tokenize_ce
import numpy as np


def compute_scores(nl_corpus, ce_corpus, bug_reports, hunk_map, alpha=0.3, beta1=0.8, beta2=0.2):
    results = {}

    # 全ハンクのリスト（ランキング対象全体）
    all_hunks = list(hunk_map.keys())
    all_ce_texts = [" ".join(tokenize_ce(hunk_map[h]["diff"])) for h in all_hunks]

    tfidf_nl = TfidfVectorizer()
    tfidf_nl.fit([" ".join(v) for v in nl_corpus.values()])
    vec_all_hunks = tfidf_nl.transform(all_ce_texts)

    for bug_id in nl_corpus:
        nl_vec = tfidf_nl.transform([" ".join(nl_corpus[bug_id])])
        sim_scores = (nl_vec @ vec_all_hunks.T).toarray()[0]

        # 上位から並べてランキングリスト作成
        ranked = sorted(zip(all_hunks, sim_scores), key=lambda x: -x[1])
        results[bug_id] = [h[0] for h in ranked]

    return results
