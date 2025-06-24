# Ranking model module
# src/ranking.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def compute_scores(nl_corpus, ce_corpus, bug_reports, hunk_map, alpha=0.3, beta1=0.8, beta2=0.2):
    results = {}
    
    for bug in bug_reports:
        bug_id = str(bug["id"])
        if bug_id not in ce_corpus or not ce_corpus[bug_id]:
            continue
        nl_tokens = [" ".join(nl_corpus[bug_id])]
        hunk_ids = list(ce_corpus[bug_id].keys())

        ce_texts = [" ".join(ce_corpus[bug_id][h]) for h in hunk_ids]

        tfidf_nl = TfidfVectorizer().fit(nl_tokens + ce_texts)
        vec_bug = tfidf_nl.transform(nl_tokens)
        vec_hunks = tfidf_nl.transform(ce_texts)

        sim_nl = cosine_similarity(vec_bug, vec_hunks).flatten()

        sim_ce = []
        for h in hunk_ids:
            hunk_tokens = ce_corpus[bug_id][h]
            overlap = len(set(nl_corpus[bug_id]) & set(hunk_tokens))
            sim_ce.append(overlap / (len(hunk_tokens) + 1e-6))

        scores = []
        for i, h in enumerate(hunk_ids):
            fix_score = 1.0 if bug_id in hunk_map[h]["msg"] else 0.0
            time_score = 1.0 / (i + 1)  # naive recency boost
            score = (1 - alpha) * sim_nl[i] + alpha * sim_ce[i] + beta1 * fix_score + beta2 * time_score
            scores.append((h, score))

        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        results[bug_id] = [h for h, _ in sorted_scores]

    return results
