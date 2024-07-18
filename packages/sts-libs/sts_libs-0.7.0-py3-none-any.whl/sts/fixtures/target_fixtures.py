from collections.abc import Generator

import pytest
from _pytest.fixtures import SubRequest

from sts import lio
from sts.linux import log_kernel_version
from sts.loopdev import create_loopdev, delete_loopdev


@pytest.fixture()
def _target_test() -> Generator:
    """Installs userspace utilities and does target cleanup before and after the test."""
    assert lio.lio_install()
    lio.log_versions()
    log_kernel_version()
    lio.lio_clearconfig()
    yield
    lio.lio_clearconfig()


@pytest.fixture()
def loopdev_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates loopback device before the test and delete it after the test."""
    name = request.param['name']
    size = request.param['size']
    dev_path = create_loopdev(name, size)
    assert dev_path
    yield dev_path
    assert delete_loopdev(dev_path)


@pytest.fixture()
def backstore_block_setup(loopdev_setup: Generator, request: SubRequest) -> Generator:
    """Creates block backstore before test and delete it after the test."""
    loop_dev = loopdev_setup
    name = request.param['name']

    bs = lio.BackstoreBlock(name=name)
    result = bs.create_backstore(dev=loop_dev)
    assert result.succeeded
    assert f'Created block storage object {name} using {loop_dev}.\n' in result.stdout
    yield bs
    assert bs.delete_backstore().succeeded


@pytest.fixture()
def backstore_fileio_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates fileio backstore before test and delete it after the test."""
    name = request.param['name']
    size = request.param['size']
    file_or_dev = request.param['file_or_dev']
    size_in_byte = request.param['size_in_byte']

    bs = lio.BackstoreFileio(name=name)
    result = bs.create_backstore(size=size, file_or_dev=file_or_dev)
    assert result.succeeded
    assert f'Created fileio {name} with size {size_in_byte}\n' in result.stdout
    yield bs
    assert bs.delete_backstore().succeeded


@pytest.fixture()
def backstore_ramdisk_setup(_target_test: None, request: SubRequest) -> Generator:
    """Creates ramdisk backstore before test and delete it after the test."""
    name = request.param['name']
    size = request.param['size']

    bs = lio.BackstoreRamdisk(name=name)
    result = bs.create_backstore(size=size)
    assert result.succeeded
    assert f'Created ramdisk {name} with size {size}.\n' in result.stdout
    yield bs
    assert bs.delete_backstore().succeeded


@pytest.fixture()
def _iscsi_setup(_target_test: None, request: SubRequest) -> Generator:
    t_iqn = request.param['t_iqn']
    assert lio.Iscsi(target_wwn=t_iqn).create_target().succeeded
    yield
    assert lio.Iscsi(target_wwn=t_iqn).delete_target().succeeded
