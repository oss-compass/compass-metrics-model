from unittest.mock import Mock

from compass_contributor.organization import OrganizationService
from compass_contributor.contributor_org import ContributorOrgService


def paged_client(records):
    client = Mock()
    client.search.return_value = {
        '_scroll_id': 'scroll-1', 'hits': {'total': {'value': 2}, 'hits': [{'_source': records[0]}]},
    }
    client.scroll.side_effect = [
        {'_scroll_id': 'scroll-1', 'hits': {'hits': [{'_source': records[1]}]}},
        {'_scroll_id': 'scroll-1', 'hits': {'hits': []}},
    ]
    return client


def test_organization_domains_include_later_pages():
    service = object.__new__(OrganizationService)
    service.organizations_index = 'organizations'
    service.client = paged_client([
        {'domain': 'first.org', 'org_name': 'First'},
        {'domain': 'second.org', 'org_name': 'Second'},
    ])

    assert service.get_dict_domain_exist() == {'first.org': 'First', 'second.org': 'Second'}
    service.client.clear_scroll.assert_called_once()


def test_contributor_organizations_include_later_pages():
    service = object.__new__(ContributorOrgService)
    service.contributors_org_index = 'contributors-org'
    service.source = 'github'
    service.client = paged_client([
        {'modify_type': 'URL', 'contributor': 'first'},
        {'modify_type': 'URL', 'contributor': 'second'},
    ])

    result = service.get_dict_by_contributor_name(['first', 'second'], None, None)

    assert set(result) == {'URL&&first', 'URL&&second'}
    service.client.clear_scroll.assert_called_once()
