# Preprocessing module
# src/preprocessing.py
import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from pathlib import Path

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()


# NL: summary + description
# CE: diff

def tokenize_nl(text):
    tokens = re.findall(r"[A-Za-z]+", text.lower())
    return [stemmer.stem(t) for t in tokens if t not in stop_words]


def tokenize_ce(diff):
    tokens = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", diff)
    return list(set(tokens))


def extract_hunks_and_tokens(bug_reports, hunks, fix_hunk_map):
    hunk_map = {}
    for h in hunks:
        hunk_id = f"{h['commit_id']}:{h['index']}"
        hunk_map[hunk_id] = h

    nl_corpus = {}
    ce_corpus = {}

    for bug in bug_reports:
        bug_id = str(bug["id"])
        nl_text = bug["summary"] + "\n" + bug.get("description", "")
        nl_tokens = tokenize_nl(nl_text)
        nl_corpus[bug_id] = nl_tokens

        ce_corpus[bug_id] = {}
        for hunk_id in fix_hunk_map.get(bug_id, []):
            h = hunk_map.get(hunk_id)
            if h:
                ce_tokens = tokenize_ce(h["diff"])
                ce_corpus[bug_id][hunk_id] = ce_tokens

    return nl_corpus, ce_corpus
