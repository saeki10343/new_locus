"""Compute similarity scores and apply boosting for Locus."""

from typing import List, Dict
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from .preprocessing import Hunk


def compute_similarity(query_vec: csr_matrix, doc_matrix: csr_matrix) -> List[float]:
    sim = cosine_similarity(query_vec, doc_matrix)[0]
    return sim.tolist()


def combine_scores(nl_scores: List[float], ce_scores: List[float], alpha: float) -> List[float]:
    return [nl + alpha * ce for nl, ce in zip(nl_scores, ce_scores)]


