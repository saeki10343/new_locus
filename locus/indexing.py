"""TF-IDF indexing and similarity computation for Locus."""

from typing import List
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer


def build_tfidf_matrix(docs: List[List[str]]) -> TfidfVectorizer:
    corpus = [" ".join(tokens) for tokens in docs]
    vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
    vectorizer.fit(corpus)
    return vectorizer


def transform(vectorizer: TfidfVectorizer, docs: List[List[str]]) -> sparse.csr_matrix:
    corpus = [" ".join(tokens) for tokens in docs]
    return vectorizer.transform(corpus)

