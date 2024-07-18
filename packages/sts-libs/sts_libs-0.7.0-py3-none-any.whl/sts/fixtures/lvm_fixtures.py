from collections.abc import Generator
from os import getenv

import pytest

from sts import lvm
from sts.linux import install_package, log_kernel_version, log_package_version

LVM_RPM_NAME = 'lvm2'
VDO_MODULE_NAME = 'kmod-kvdo'


# TODO: create/assign a block device(s) to be used as PV? Accept PV/VG names and sizes
@pytest.fixture(scope='class')
def _lvm_test() -> Generator:
    """Installs lvm and logs package versions."""
    assert install_package(LVM_RPM_NAME)
    log_kernel_version()
    log_package_version(LVM_RPM_NAME)
    # TODO log block device and filesystem info?
    yield  # noqa: PT022
    # TODO cleanup after testing


@pytest.fixture(scope='class')
def vdo_test(_lvm_test) -> Generator:  # noqa: ANN001
    # TODO handle in-kernel vdo
    assert install_package(VDO_MODULE_NAME)
    log_package_version(VDO_MODULE_NAME)
    vg_name = getenv('VDO_VG_NAME', 'vdovg')
    lv_name = getenv('VDO_LV_NAME', 'vdolv')
    dev_path = f'/dev/{vg_name}/{lv_name}'
    pv_dev = '/dev/sda'
    vg = lvm.VG()
    lv = lvm.LV()
    pv = lvm.PV()
    assert vg.vgcreate([vg_name, pv_dev]).succeeded
    assert lv.vdocreate(['--name', lv_name, '--extents', '5%vg', vg_name]).succeeded

    # TODO: yield object
    yield {'dev_path': dev_path, 'vg_name': vg_name, 'lv_name': lv_name}

    assert lv.lvremove([vg_name, lv_name])
    assert vg.vgremove([vg_name])
    assert pv.pvremove([pv_dev])
