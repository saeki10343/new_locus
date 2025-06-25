# src/data_acquisition.py
import json
import re
import requests
from pydriller import RepositoryMining
from pathlib import Path
from tqdm import tqdm

BUGZILLA_API = "https://bz.apache.org/bugzilla/rest.cgi/bug/"


def fetch_tomcat_repo(commits_file, hunks_file):
    repo_url = "https://github.com/apache/tomcat.git"
    print("Cloning Tomcat repository via PyDriller...")

    commits = []
    hunks = []

    for commit in tqdm(RepositoryMining(repo_url, only_modifications_with_file_types=['.java']).traverse_commits()):
        msg = commit.msg
        if not re.search(r'(BZ|Bugzilla|Bug|bug)[ #:]*([0-9]{4,7})', msg, re.IGNORECASE):
            continue

        for idx, mod in enumerate(commit.modifications):
            if not mod.filename.endswith(".java") or mod.change_type.name == "DELETE":
                continue

            if not mod.diff or len(mod.diff.strip()) == 0:
                continue

            hunks.append({
                "commit_id": commit.hash,
                "index": idx,
                "filename": mod.new_path or mod.old_path,
                "diff": mod.diff,
                "content": mod.source_code or "",
                "msg": msg
            })

        commits.append({"hash": commit.hash, "msg": msg, "timestamp": int(commit.committer_date.timestamp())})

    Path(commits_file).write_text(json.dumps(commits, indent=2))
    Path(hunks_file).write_text(json.dumps(hunks, indent=2))

    return commits, hunks


def fetch_bug_reports(output_file):
    print("Start bug_reports")

    bug_ids = set()
    with open("data/commits.json") as f:
        commits = json.load(f)
        for c in commits:
            found = re.findall(r'(?:BZ|Bugzilla|Bug|bug)[ #:]*([0-9]{4,7})', c['msg'], re.IGNORECASE)
            bug_ids.update(found)

    bug_reports = []
    for bug_id in tqdm(bug_ids):
        try:
            res = requests.get(f"{BUGZILLA_API}{bug_id}?Bugzilla_api_key={'azVGl7F6Kj4iw3xIn4DiMbtqYrfPfznyOTsF0BJW'}", timeout=10)
            data = res.json()
            if "bugs" in data and data["bugs"]:
                bug = data["bugs"][0]
                if bug.get("status") == "RESOLVED" and bug.get("resolution") == "FIXED":
                    bug_reports.append({
                        "id": bug["id"],
                        "summary": bug["summary"],
                        "description": bug.get("description", ""),
                        "fixes": [bug["id"]]  # used to match against commit messages
                    })
        except Exception as e:
            print(f"[Warning] Bug {bug_id} fetch failed: {e}")

    with open(output_file, "w") as f:
        json.dump(bug_reports, f, indent=2)

    return bug_reports

if __name__ == "__main__":
    # fetch_tomcat_repo("data/commits.json", "data/hunks.json")
    fetch_bug_reports("data/bug_reports.json")