from collections.abc import Generator

import pytest

from sts import iscsi, lio
from sts.linux import log_kernel_version, log_package_version


@pytest.fixture(scope='class')
def _iscsi_test() -> Generator:
    """Installs userspace utilities and makes cleanup before and after the test."""
    assert iscsi.install()
    log_kernel_version()
    log_package_version('iscsi-initiator-utils')
    iscsi.cleanup()
    yield
    iscsi.cleanup()


@pytest.fixture(scope='class')
def _iscsi_localhost_test(_iscsi_test) -> Generator:  # noqa: ANN001
    """Installs userspace utilities incl. targetcli and makes cleanup before and after the test."""
    assert lio.lio_install()
    lio.log_versions()
    lio.lio_clearconfig()
    yield
    lio.lio_clearconfig()
