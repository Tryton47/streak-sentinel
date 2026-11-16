"""
Unit test for GitHub Streak Checker.
"""
import unittest
from unittest.mock import MagicMock, patch
from github_checker import GitHubStreakChecker

class TestStreakChecker(unittest.TestCase):

    @patch("httpx.Client.get")
    def test_has_committed_today(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = [
            {
                "type": "PushEvent",
                "created_at": "2026-11-16T04:00:11Z",
                "payload": {"commits": [{"message": "feat: test"}]},
                "repo": {"name": "Tryton47/scrapton-3platform"}
            }
        ]
        mock_get.return_value = mock_resp

        checker = GitHubStreakChecker("Tryton47")
        committed, count, repos = checker.has_committed_today()
        self.assertTrue(committed)
        self.assertGreaterEqual(count, 1)
        self.assertIn("Tryton47/scrapton-3platform", repos)

if __name__ == "__main__":
    unittest.main()
