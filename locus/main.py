"""Example entry point for Locus bug localization pipeline."""

import argparse
from . import data_acquisition as da
from . import preprocessing as pp
from . import indexing
from . import ranking


def main(repo_path: str):
    bugs = da.mine_bug_fix_commits(repo_path)
    if not bugs:
        print("No bug reports mined. Exiting.")
        return

    # Example using first bug for brevity
    bug = bugs[0]
    print(f"Processing bug {bug.bug_id}")
    # In a complete implementation, we would extract hunks and build indices
    # For now, just placeholder steps
    print("TODO: implement full pipeline")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", help="Path to Git repository")
    args = parser.parse_args()
    main(args.repo)

