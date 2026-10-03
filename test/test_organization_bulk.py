from types import SimpleNamespace
from unittest.mock import Mock, patch

from compass_contributor.organization import OrganizationService
from compass_contributor.contributor_org import ContributorOrgService


def test_bulk_writes_flush_at_1000_and_skip_empty_batches():
    for service_type, module in (
        (OrganizationService, 'compass_contributor.organization'),
        (ContributorOrgService, 'compass_contributor.contributor_org'),
    ):
        service = object.__new__(service_type)
        service.client = object()
        service.organizations_index = 'org' if service_type is OrganizationService else None
        service.contributors_org_index = 'contributor-org' if service_type is ContributorOrgService else None
        bulk = Mock()
        with patch(f'{module}.helpers', return_value=SimpleNamespace(bulk=bulk)):
            service.batch_save([])
            assert bulk.call_count == 0
            service.batch_save([SimpleNamespace(id=str(i)) for i in range(1001)])
        assert [len(call.kwargs['actions']) for call in bulk.call_args_list] == [1000, 1]
