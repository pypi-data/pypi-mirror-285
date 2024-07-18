from typing import Callable

import pytest

from sts import rdma


@pytest.fixture()
def _exists_rdma() -> None:
    """Skips the test if no rdma device found."""
    if not rdma.exists_rdma():
        pytest.skip(reason='Skipping, no rdma device found.')


@pytest.fixture(scope='class')
def rdma_device() -> Callable[[str], rdma.Device]:
    """Returns factory function _device_factory which can create and return rdma.Device.

    Returns: The factory function _device_factory which can take hca_id argument.
    We can conveniently pass argument to this fixture.
    """

    def _device_factory(hca_id: str) -> rdma.Device:
        assert rdma.exists_specific_rdma(hca_id), 'Oops, no such device found.'
        device: rdma.Device = rdma.Device(hca_id)
        return device

    return _device_factory
