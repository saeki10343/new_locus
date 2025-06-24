# Data acquisition for Locus
# Contains functions to fetch repository data and bug reports.

import os
from dataclasses import dataclass
from typing import List, Dict, Optional

# PyDriller and requests would be used for real data collection.
# They are optional here since network access may not be available.
try:
    from pydriller import RepositoryMining
except ImportError:  # pragma: no cover
    RepositoryMining = None

import logging

logging.basicConfig(level=logging.INFO)

@dataclass
class BugReport:
    bug_id: str
    summary: str
    description: str
    fix_commit: str
    report_date: str  # ISO format date string
    inducing_commit: Optional[str] = None


def mine_bug_fix_commits(repo_path: str) -> List[BugReport]:
    """Return a list of bug reports linked with fix commits.

    This is a simplified placeholder that scans commit messages for the
    word 'Bug' followed by an id. In a real implementation, this would
    query the Git history with PyDriller and fetch bug report text from
    Bugzilla.
    """
    if RepositoryMining is None:
        logging.warning("PyDriller is not installed; cannot mine commits.")
        return []

    bug_reports: List[BugReport] = []
    pattern = r"Bug\s+(\d+)"

    for commit in RepositoryMining(repo_path).traverse_commits():
        if 'Bug ' in commit.msg:
            import re
            m = re.search(pattern, commit.msg)
            if m:
                bug_id = m.group(1)
                bug_reports.append(
                    BugReport(
                        bug_id=bug_id,
                        summary=commit.msg,
                        description='',
                        fix_commit=commit.hash,
                        report_date=str(commit.author_date.date()),
                    )
                )
    return bug_reports


def fetch_bug_details(bug_id: str) -> Dict[str, str]:
    """Fetch bug title and description from Bugzilla.

    This function is a stub; real implementation would use requests to
    call the Bugzilla API.
    """
    logging.info("Fetching bug %s", bug_id)
    return {"summary": "", "description": ""}

