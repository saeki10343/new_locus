import json
from collections import defaultdict

def generate_change_map(hunks):
    """
    change_map[file_path][change_id] = [hunk_id1, hunk_id2, ...]
    """
    change_map = defaultdict(lambda: defaultdict(list))

    for hunk in hunks:
        file_path = hunk['filename']
        commit_id = hunk['commit_id']
        change_id = f"{commit_id}:{file_path}"  # ファイル内の変更をユニークに識別
        hunk_id = f"{commit_id}:{hunk['index']}"
        change_map[file_path][change_id].append(hunk_id)

    return change_map
