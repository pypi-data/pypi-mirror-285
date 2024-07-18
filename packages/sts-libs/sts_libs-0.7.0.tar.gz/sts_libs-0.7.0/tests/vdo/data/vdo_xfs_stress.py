#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from os import getenv

import pytest

from sts import fio, linux


def run_fio_stress(device: str) -> None:
    f = fio.FIO(filename=device)
    f.load_fs_params()
    f.update_parameters({'runtime': '120'})  # adding runtime cap of 2 minutes
    f.run()


@pytest.mark.usefixtures('vdo_test')
def test_xfs_stress(vdo_test: dict) -> None:
    mount_point = getenv('VDO_MOUNT_POINT', '/mnt/vdo_xfs_test')
    vdo_dict = vdo_test
    assert linux.mkfs(device_name=vdo_dict['dev_path'], fs_type='xfs -fK')
    assert linux.mkdir(mount_point)
    assert linux.mount(device=vdo_dict['dev_path'], mountpoint=mount_point)
    run_fio_stress(f'{mount_point}/file')
    assert linux.umount(mountpoint=mount_point)
    # TODO this should be in cleanup phase that runs always
    assert linux.rmdir(mount_point)
