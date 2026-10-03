from unittest.mock import patch

from compass_contributor.contributor_dev_org_repo import ContributorDevOrgRepo


def test_configured_company_is_preserved():
    args = ('repo.json', 'github-issues', 'prs', 'issue-comments', 'pr-comments',
            'git', 'contributors', 'enriched', '2020-01-01', '2021-01-01', 'repos')
    with patch('compass_contributor.contributor_dev_org_repo.get_all_repo', return_value=[]):
        assert ContributorDevOrgRepo(*args, company='Example Inc').company == 'Example Inc'
        assert ContributorDevOrgRepo(*args, company='None').company is None
