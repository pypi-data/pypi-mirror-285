import pytest


@pytest.mark.parametrize('_service_test', ['target.service'], indirect=True)
@pytest.mark.usefixtures('_target_test', '_service_test')
def test_target_service() -> None:
    """target.service, systemd service to restore the LIO kernel target settings on system restart.
    Make sure it can be enabled/disabled/started/restarted/stopped successfully.
    """
    assert True
