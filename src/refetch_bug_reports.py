# src/refetch_bug_reports.py
import json
import requests
from pathlib import Path

BUGZILLA_COMMENT_API = "https://bz.apache.org/bugzilla/rest.cgi/bug/{}/comment"
BUGZILLA_BUG_API = "https://bz.apache.org/bugzilla/rest.cgi/bug/{}"

BUGZILLA_API_KEY = 'azVGl7F6Kj4iw3xIn4DiMbtqYrfPfznyOTsF0BJW'
BUG_IDS = [43846, 58373, 65106, 43241, 65677, 66084, 61086, 65770, 42753, 69338]

def fetch_bug_and_comments(bug_id: int):
    try:
        # fetch bug main info
        bug_url = BUGZILLA_BUG_API.format(bug_id) + f"?Bugzilla_api_key={BUGZILLA_API_KEY}"
        bug_res = requests.get(bug_url, timeout=10)
        bug_data = bug_res.json()

        if "bugs" not in bug_data or not bug_data["bugs"]:
            print(f"[Warning] Bug {bug_id} not found in main API")
            return None

        bug = bug_data["bugs"][0]

        if bug.get("status") != "RESOLVED" or bug.get("resolution") != "FIXED":
            print(f"[Info] Bug {bug_id} is not RESOLVED/FIXED")
            return None

        # fetch comments
        comment_url = BUGZILLA_COMMENT_API.format(bug_id) + f"?Bugzilla_api_key={BUGZILLA_API_KEY}"
        comment_res = requests.get(comment_url, timeout=10)
        comment_data = comment_res.json()
        comment_list = comment_data.get("bugs", {}).get(str(bug_id), {}).get("comments", [])
        comments = [c["text"].strip() for c in comment_list[1:]]
        description = comment_list[0].get("text", "").strip()


        return {
            "id": bug["id"],
            "summary": bug.get("summary", ""),
            "description": description,
            "creation_ts": bug.get("creation_time", ""),
            "fixes": [bug["id"]],
            "comments": comments
        }

    except Exception as e:
        print(f"[Error] Failed to fetch Bug {bug_id}: {e}")
        return None

def main():
    output_file = "data/refetched_bug_reports.json"
    bug_reports = []

    for bug_id in BUG_IDS:
        print(f"Fetching bug {bug_id}...")
        result = fetch_bug_and_comments(bug_id)
        if result:
            bug_reports.append(result)

    Path(output_file).write_text(json.dumps(bug_reports, indent=2))
    print(f"Saved {len(bug_reports)} bug reports to {output_file}")

if __name__ == "__main__":
    main()
