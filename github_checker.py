"""
GitHub Activity Checker.
Fetches user public events and determines whether a commit has been pushed today.
"""
from datetime import datetime, timezone
import httpx

class GitHubStreakChecker:
    """Checks GitHub activity using the official public events API."""

    def __init__(self, username: str):
        self.username = username
        self.api_url = f"https://api.github.com/users/{username}/events/public"

    def has_committed_today(self) -> tuple[bool, int, list[str]]:
        """
        Returns (has_committed, commit_count_today, list_of_repos_touched)
        Evaluates UTC today vs event timestamps.
        """
        headers = {
            "User-Agent": "GitHub-Streak-Sentinel/1.0",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            with httpx.Client(timeout=15.0) as client:
                res = client.get(self.api_url, headers=headers)
                if res.status_code != 200:
                    return False, 0, []

                events = res.json()
        except Exception:
            return False, 0, []

        now_utc = datetime.now(timezone.utc)
        today_date = now_utc.date()

        push_events_today = 0
        repos_touched = set()

        for event in events:
            if event.get("type") != "PushEvent":
                continue

            created_at_str = event.get("created_at")
            if not created_at_str:
                continue

            try:
                # Format: 2026-11-16T04:00:11Z
                dt = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if dt.date() == today_date:
                    payload = event.get("payload", {})
                    commits = payload.get("commits", [])
                    push_events_today += max(1, len(commits))
                    repo_name = event.get("repo", {}).get("name", "")
                    if repo_name:
                        repos_touched.add(repo_name)
            except Exception:
                continue

        return (push_events_today > 0), push_events_today, list(repos_touched)
