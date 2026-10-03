from types import SimpleNamespace
from unittest.mock import Mock, patch

from compass_contributor.contributor_org import ContributorOrgService


def test_gitdm_ignores_entries_before_their_headers():
    service = object.__new__(ContributorOrgService)
    service.source = 'github'
    service.batch_save = Mock()

    def head(url):
        return SimpleNamespace(status_code=200 if url.endswith('1.txt') else 404)

    def get(url):
        if 'company_developers' in url:
            return SimpleNamespace(text='orphan: example.com\nValid Org:\nalice: example.com\n')
        return SimpleNamespace(text='Orphan Company\nbob:\nValid Company\n')

    with patch('compass_contributor.contributor_org.requests.head', side_effect=head), \
         patch('compass_contributor.contributor_org.requests.get', side_effect=get):
        service.save_by_cncf_gitdm_url()

    records = service.batch_save.call_args.args[0]
    assert {item.contributor for item in records} == {'alice', 'bob'}
