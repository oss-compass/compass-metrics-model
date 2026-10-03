from types import SimpleNamespace
from unittest.mock import Mock, patch

from compass_contributor.contributor_org import ContributorOrgService


def test_gitdm_affiliations_are_saved_in_date_order():
    service = object.__new__(ContributorOrgService)
    service.source = 'github'
    service.batch_save = Mock()

    def head(url):
        return SimpleNamespace(status_code=200 if url.endswith('company_developers1.txt') else 404)

    with patch('compass_contributor.contributor_org.requests.head', side_effect=head), \
         patch('compass_contributor.contributor_org.requests.get', return_value=SimpleNamespace(
             text='Later:\nalice: example.com from 2022-01-01\n'
                  'Earlier:\nalice: example.com from 2020-01-01\n')):
        service.save_by_cncf_gitdm_url()

    affiliations = service.batch_save.call_args.args[0][0].org_change_date_list
    assert [item['org_name'] for item in affiliations] == ['Earlier', 'Later']
