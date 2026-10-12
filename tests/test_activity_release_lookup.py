"""Version metrics must find releases outside the first listing page."""
import unittest
from unittest.mock import Mock, patch

# The existing document utility creates global /data directories on import.
# Import the real metric without requiring those unrelated writable paths.
with patch("os.makedirs"):
    from compass_metrics import activity


class ActivityReleaseLookupTests(unittest.TestCase):
    def test_old_release_is_resolved_without_listing_pages(self):
        recent = [{"tag_name": "v%d" % i, "published_at": "2026-01-01T00:00:00Z"}
                  for i in range(40, 10, -1)]

        def response(url, **kwargs):
            if url.endswith("/releases/tags/v1"):
                return Mock(status_code=200, json=lambda: {
                    "tag_name": "v1", "published_at": "2024-01-01T00:00:00Z"})
            return Mock(status_code=200, json=lambda: recent)

        with patch.object(activity.requests, "get", side_effect=response) as get:
            self.assertEqual(activity.get_github_versionPublishAt(
                "https://github.com/owner/project", "v1"), "2024-01-01T00:00:00Z")
        self.assertEqual(get.call_count, 1)

    def test_tag_is_encoded_as_one_path_segment(self):
        release = {"tag_name": "release/1.0+build#1", "published_at": "2025-01-01T00:00:00Z"}

        def response(url, **kwargs):
            return Mock(status_code=200, json=lambda: release if "/releases/tags/" in url else [release])

        with patch.object(activity, "get_github_token", return_value="test-token"), \
             patch.object(activity.requests, "get", side_effect=response) as get:
            self.assertEqual(activity.get_github_versionPublishAt(
                "https://github.com/owner/project/", release["tag_name"]), release["published_at"])
        self.assertEqual(get.call_args.args[0],
                         "https://api.github.com/repos/owner/project/releases/tags/release%2F1.0%2Bbuild%231")
        self.assertEqual(get.call_args.kwargs["headers"]["Authorization"], "token test-token")

    def test_missing_or_failed_release_remains_unavailable(self):
        for status in (404, 403, 500):
            with self.subTest(status=status), patch.object(activity.requests, "get", return_value=Mock(status_code=status)):
                self.assertIsNone(activity.get_github_versionPublishAt("https://github.com/owner/project", "missing"))

    def test_quarterly_metric_receives_older_release_date(self):
        def response(url, **kwargs):
            if "/releases/tags/" in url:
                return Mock(status_code=200, json=lambda: {
                    "tag_name": "v1", "published_at": "2024-06-01T00:00:00Z"})
            return Mock(status_code=200, json=lambda: [])

        with patch.object(activity.requests, "get", side_effect=response), \
             patch.object(activity, "commit_count", return_value={
                 "commit_count": 3, "commit_count_bot": 1, "commit_count_without_bot": 2}) as count:
            result = activity.activity_quarterly_contribution(
                Mock(), "contributors", ["https://github.com/owner/project"], "v1")
        self.assertEqual(result["activity_quarterly_contribution"], [3] * 4)
        self.assertEqual(result["activity_quarterly_contribution_bot"], [1] * 4)
        self.assertEqual(result["activity_quarterly_contribution_without_bot"], [2] * 4)
        self.assertEqual(count.call_count, 4)


if __name__ == "__main__":
    unittest.main()
