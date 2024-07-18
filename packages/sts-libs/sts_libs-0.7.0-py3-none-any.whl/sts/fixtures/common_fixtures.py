import time
from collections.abc import Generator

import pytest
from _pytest.fixtures import SubRequest

from sts import linux, scsi_debug
from sts.utils.cmdline import run


@pytest.fixture(scope='class', autouse=True)
def _log_check() -> Generator:
    """Checks if a new coredump entry was generated during the test."""
    last_dump = run('coredumpctl -1', msg='Checking dumps before test').stdout
    yield
    recent_dump = run('coredumpctl -1', msg='Checking dumps after test').stdout
    assert recent_dump == last_dump, 'New coredump appeared during the test'


@pytest.fixture(scope='class')
def scsi_debug_test() -> Generator:
    scsi_debug.scsi_debug_load_module()
    yield scsi_debug.get_scsi_debug_devices()
    scsi_debug.scsi_debug_unload_module()


@pytest.fixture()
def _service_test(request: SubRequest) -> None:
    """Enable/disable/start/restart/stop service tests."""
    service_name = request.param
    if linux.is_service_enabled(service_name):
        assert linux.service_disable(service_name)
        time.sleep(5)
        assert linux.service_enable(service_name)
    else:
        assert linux.service_enable(service_name)
        time.sleep(5)
        assert linux.service_disable(service_name)

    if linux.is_service_running(service_name):
        assert linux.service_stop(service_name)
        time.sleep(5)
        assert linux.service_start(service_name)
        time.sleep(5)
        assert linux.service_restart(service_name)
    else:
        assert linux.service_start(service_name)
        time.sleep(5)
        assert linux.service_restart(service_name)
        time.sleep(5)
        assert linux.service_stop(service_name)
