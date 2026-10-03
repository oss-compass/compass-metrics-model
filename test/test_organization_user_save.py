from unittest.mock import Mock

from compass_contributor.organization import OrganizationService


def test_save_by_user_id_creates_organization():
    service = object.__new__(OrganizationService)
    service.save = Mock()

    service.save_by_user_id('Example Org', 'user-42')

    organization = service.save.call_args.args[0]
    assert organization.domain is None
    assert organization.org_name == 'Example Org'
    assert organization.user_id == 'user-42'
    assert organization.id
