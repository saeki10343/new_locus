import json
import re
import argparse
from collections import defaultdict
from pathlib import Path

def load_vocab(vocab_path):
    with open(vocab_path, 'r', encoding='utf-8') as f:
        vocab = set(line.strip() for line in f if line.strip())
    return vocab

def extract_code_like_terms(text):
    return re.findall(r'\b[A-Za-z_][A-Za-z0-9_\.]*\b', text)

def filter_ce_terms(text, ce_vocab):
    terms = extract_code_like_terms(text)
    return [t for t in terms if t in ce_vocab]

def extract_ce_tokens_from_bug(bug, ce_vocab):
    summary = bug.get("summary", "")
    description = bug.get("description", "")
    comments = "\n".join(bug.get("comments", []))
    full_text = f"{summary}\n{description}\n{comments}"
    return filter_ce_terms(full_text, ce_vocab)

def extract_ce_tokens_from_hunk(hunk, ce_vocab):
    diff = hunk.get("diff", "")
    return filter_ce_terms(diff, ce_vocab)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bugs', type=str, required=True, help='Path to bug_reports.json')
    parser.add_argument('--hunks', type=str, required=True, help='Path to hunks.json')
    parser.add_argument('--vocab', type=str, required=True, help='Path to ce_vocab.txt')
    parser.add_argument('--out', type=str, required=True, help='Output path for ce_corpus.json')
    args = parser.parse_args()

    # Load inputs
    with open(args.bugs, 'r', encoding='utf-8') as f:
        bugs = json.load(f)
    with open(args.hunks, 'r', encoding='utf-8') as f:
        hunks = json.load(f)
    vocab = load_vocab(args.vocab)

    # Build CE corpus
    ce_corpus = defaultdict(dict)

    # Extract from bugs
    for bug in bugs:
        bug_id = str(bug["id"])
        ce_tokens = extract_ce_tokens_from_bug(bug, vocab)
        for hunk in hunks:
            hunk_id = f"{hunk['commit_id']}:{hunk['index']}"
            ce_corpus[bug_id][hunk_id] = list(ce_tokens)  # duplicate, filtered later if needed

    # Refine per hunk
    for hunk in hunks:
        hunk_id = f"{hunk['commit_id']}:{hunk['index']}"
        hunk_tokens = extract_ce_tokens_from_hunk(hunk, vocab)
        for bug in bugs:
            bug_id = str(bug["id"])
            if hunk_id in ce_corpus[bug_id]:
                combined = list(set(ce_corpus[bug_id][hunk_id]) | set(hunk_tokens))
                ce_corpus[bug_id][hunk_id] = combined

    # Output
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(ce_corpus, f, indent=2)

    print(f"CE corpus saved to {args.out}")

if __name__ == "__main__":
    main()
