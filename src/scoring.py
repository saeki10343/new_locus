# src/scoring.py

import numpy as np

def cosine_similarity(vec1, vec2):
    if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
        return 0.0
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def NL_score(bug_vec, hunk_vec):
    return cosine_similarity(bug_vec, hunk_vec)  # 式 (3)

def CE_score(bug_vec, hunk_vec):
    return cosine_similarity(bug_vec, hunk_vec)  # 式 (4)

def Fix_score(timestamps):
    scores = [1 / (1 + np.exp(-12 * t + 12)) for t in timestamps]  # 式 (5)
    return sum(scores)

def Time_score(rank_dict, change):
    ranks = [rank_dict[s] for s in change]  # t(c) に属する s
    return max([1 / (rank + 1) for rank in ranks])  # 式 (6)

def source_score(nl_scores, ce_scores, fix_score, alpha, beta1):
    max_score = max(nl + alpha * ce for nl, ce in zip(nl_scores, ce_scores))
    return max_score + beta1 * fix_score  # 式 (7)

def change_score(nl_scores, ce_scores, time_score, alpha, beta2):
    max_score = max(nl + alpha * ce for nl, ce in zip(nl_scores, ce_scores))
    return max_score + beta2 * time_score  # 式 (8)

def determine_alpha(split_token_count, ce_token_count, lam=5):
    ratio = ce_token_count / split_token_count if split_token_count else 0
    alpha = lam * ratio
    return alpha if alpha > 1 else 1  # 式 (9)
