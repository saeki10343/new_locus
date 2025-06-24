# main.py
from src.data_acquisition import fetch_tomcat_repo, fetch_bug_reports
from src.preprocessing import extract_hunks_and_tokens
from src.ranking import compute_scores
from src.evaluation import evaluate_results


def main():
    print("[1/4] Cloning and processing Tomcat repo...")
    commits, hunks = fetch_tomcat_repo("data/commits.json", "data/hunks.json")

    print("[2/4] Fetching bug reports from Bugzilla...")
    bug_reports = fetch_bug_reports("data/bug_reports.json")

    print("[3/4] Extracting hunks and computing tokens...")
    hunk_map = {f"{h['commit_id']}:{h['index']}": h for h in hunks}
    nl_corpus, ce_corpus = extract_hunks_and_tokens(bug_reports, hunks)

    print("[4/4] Computing VSM+Boosting scores and evaluating...")
    results = compute_scores(nl_corpus, ce_corpus, bug_reports, hunk_map)
    evaluate_results(results)



if __name__ == "__main__":
    main()
