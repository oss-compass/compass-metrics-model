from unittest.mock import Mock

from compass_contributor.bot import BotService


def test_repo_entries_contain_contributor_names():
    service = object.__new__(BotService)
    service.bots_index = "bots"
    service.client = Mock()
    service.client.search.return_value = {"hits": {"hits": [
        {"_source": {"community": "org", "repo": "org/project", "contributor": "dependabot"}},
        {"_source": {"community": "org", "repo": "org/project", "contributor": "renovate"}},
    ]}}

    result = service.get_dict_by_source("github")

    assert result["repo"] == {"org/project": ["dependabot", "renovate"]}
