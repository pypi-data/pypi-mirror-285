#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from os import getenv

from sts import lvm


def test_ack_threads() -> None:
    vg_name = getenv('VDO_VG_NAME', 'vdovg')
    lv_name = getenv('VDO_LV_NAME', 'vdolv')
    ack_threads = getenv('VDO_ACK_THREADS', '0 1 100')
    values = ack_threads.split()
    lvm.VGCreate(vg_name=vg_name, physical_vols=['/dev/sda'])
    for value in values:
        assert (
            lvm.LVCreate()
            .vdo(volume_group=vg_name, name=lv_name, extents='5%vg', vdosettings=f'vdo_ack_threads={value}')
            .succeeded
        )
        assert f'ack {value}' in lvm.run(f'dmsetup table {vg_name}-vpool0-vpool').stdout
        assert lvm.LVRemove(lv_name=lv_name, vg_name=vg_name)
    assert lvm.VGRemove(vg_name=vg_name)
    assert lvm.PVRemove(disk='/dev/sda')
