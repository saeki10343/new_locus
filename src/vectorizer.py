# src/vectorizer.py

from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()


def preprocess(text):
    """
    論文に記載された前処理（英語ストップワード除去、記号除去、ステミング）を行う
    """
    # camelCase -> split
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    tokens = re.findall(r'\b\w+\b', text.lower())
    tokens = [t for t in tokens if t not in stop_words]
    tokens = [stemmer.stem(t) for t in tokens]
    return ' '.join(tokens)


def build_vectorizer(corpus_texts, max_features=10000):
    """
    corpus_texts: List[str] - すべての bug reports および hunks の前処理済みテキスト
    return: fitted TfidfVectorizer
    """
    vectorizer = TfidfVectorizer(max_features=max_features)
    vectorizer.fit(corpus_texts)
    return vectorizer


def vectorize(texts, vectorizer):
    """
    texts: List[str] - 前処理済みテキスト群
    vectorizer: 学習済み TfidfVectorizer
    return: scipy sparse matrix (TF-IDF ベクトル群)
    """
    return vectorizer.transform(texts)

def preprocess_ce(tokens):
    """
    CEトークン（identifier）を文字列化してベクトル化可能にする（重複は保持）
    """
    return ' '.join(tokens)


def build_vectorizer_ce(ce_corpus, max_features=10000):
    """
    ce_corpus: Dict[bug_id][hunk_id] = List[str]
    → 全CEトークンを文字列化してベクトル化（TF-IDF）
    """
    all_texts = []
    for bug_ce in ce_corpus.values():
        for tokens in bug_ce.values():
            all_texts.append(preprocess_ce(tokens))
    
    vectorizer = TfidfVectorizer(max_features=max_features)
    vectorizer.fit(all_texts)
    return vectorizer
