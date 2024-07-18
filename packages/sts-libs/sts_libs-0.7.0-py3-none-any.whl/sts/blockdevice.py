# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import functools
import json
from typing import TYPE_CHECKING

from sts.lvm import pv_query
from sts.utils.cmdline import check_output

if TYPE_CHECKING:
    from collections.abc import Generator


class BlockDevice:
    """Information for block device.

    Should be used with sudo or under root.

    If device is not a block device, RuntimeError is raised.
    """

    @property
    def _data(self) -> dict:
        raise NotImplementedError

    def __init__(self, device: str, _data_cache: dict | None = None) -> None:
        self.device = device
        self._data_cache = _data_cache

    @classmethod
    def _iter_blockdevices(cls) -> Generator:
        raise NotImplementedError

    @property
    def is_partition(self) -> bool:
        """Return True if the device is a partition.

        >>> host.block_device("/dev/sda1").is_partition
        True

        >>> host.block_device("/dev/sda").is_partition
        False


        """
        return self._data['start_sector'] > 0

    @property
    def size(self) -> int:
        """Return size if the device in bytes.

        >>> host.block_device("/dev/sda1").size
        512110190592

        """
        return self._data['size']

    @property
    def sector_size(self) -> int:
        """Return sector size for the device in bytes.

        >>> host.block_device("/dev/sda1").sector_size
        512
        """
        return self._data['sector_size']

    @property
    def block_size(self) -> int:
        """Return block size for the device in bytes.

        >>> host.block_device("/dev/sda").block_size
        4096
        """
        return self._data['block_size']

    @property
    def start_sector(self) -> int:
        """Return start sector of the device on the underlying device.

           Usually the value is zero for full devices and is non-zero
           for partitions.

        >>> host.block_device("/dev/sda1").start_sector
        2048

        >>> host.block_device("/dev/md0").start_sector
        0
        """
        return self._data['sector_size']

    @property
    def is_writable(self) -> bool:
        """Return True if device is writable (have no RO status).

        >>> host.block_device("/dev/sda").is_writable
        True

        >>> host.block_device("/dev/loop1").is_writable
        False
        """
        mode = self._data['rw_mode']
        if mode == 'rw':
            return True
        if mode == 'ro':
            return False
        raise ValueError(f'Unexpected value for rw: {mode}')

    @property
    def ra(self) -> int:
        """Return Read Ahead for the device in 512-bytes sectors.

        >>> host.block_device("/dev/sda").ra
        256
        """
        return self._data['read_ahead']

    @classmethod
    def get_blockdevices(cls) -> list[BlockDevice]:
        """Returns a list of BlockDevice instances.

        >>> host.block_device.get_blockevices()
        [<BlockDevice(path=/dev/sda)>,
         <BlockDevice(path=/dev/sda1)>]
        """
        return [cls(device['name'], device) for device in cls._iter_blockdevices()]

    def __repr__(self) -> str:
        return f'<BlockDevice(path={self.device})>'


class LinuxBlockDevice(BlockDevice):
    @functools.cached_property
    def _data(self) -> dict:
        if self._data_cache:
            return self._data_cache
        # -J Use JSON output format
        # -O Output all available columns
        # -b Print the sizes in bytes
        command = f'lsblk -JOb {self.device}'
        out = check_output(command)
        blockdevs = json.loads(out)['blockdevices']
        if not blockdevs:
            raise RuntimeError(f'No data from {self.device}')
        # start sector is not available in older lsblk version,
        # but we can read it from SYSFS
        if 'start' not in blockdevs[0]:
            blockdevs[0]['start'] = 0
            # checking if device has internal parent kernel device name
            if blockdevs[0]['pkname']:
                try:
                    command = f"cat /sys/dev/block/{blockdevs[0]['maj:min']}/start"
                    out = check_output(command)
                    blockdevs[0]['start'] = int(out)
                except AssertionError:
                    blockdevs[0]['start'] = 0
        return blockdevs[0]

    @classmethod
    def _iter_blockdevices(cls) -> Generator:
        def children_generator(children_list: list[dict]) -> Generator:
            for child in children_list:
                if 'start' not in child:
                    try:
                        cmd = f"cat /sys/dev/block/{child['maj:min']}/start"
                        out = check_output(cmd)
                        child['start'] = int(out)
                    # At this point, the AssertionError only indicates that
                    # the device is a virtual block device (device mapper target).
                    # It can be assumed that the start sector is 0.
                    except AssertionError:
                        child['start'] = 0
                if 'children' in child:
                    yield from children_generator(child['children'])
                yield child

        command = 'lsblk -JOb'
        blockdevices = json.loads(check_output(command))['blockdevices']
        for device in blockdevices:
            if 'start' not in device:
                # Parent devices always start from 0
                device['start'] = 0
            if 'children' in device:
                yield from children_generator(device['children'])
            yield device

    @property
    def is_partition(self) -> bool:
        return self._data['type'] == 'part'

    @property
    def sector_size(self) -> int:
        return self._data['log-sec']

    @property
    def block_size(self) -> int:
        return self._data['phy-sec']

    @property
    def start_sector(self) -> int:
        if self._data['start']:
            return self._data['start']
        return 0

    @property
    def is_writable(self) -> bool:
        return self._data['ro'] == 0

    @property
    def ra(self) -> int:
        return self._data['ra']

    @property
    def is_removable(self) -> bool:
        """Return True if device is removable.

        >>> host.block_device("/dev/sda").is_removable
        False

        """
        return self._data['rm']

    @property
    def hctl(self) -> str:
        """Return Host:Channel:Target:Lun for SCSI.

        >>> host.block_device("/dev/sda").hctl
        '1:0:0:0'

        >>> host.block_device("/dev/nvme1n1").hctl
        None

        """
        return self._data['hctl']

    @property
    def model(self) -> str | None:
        """Return device identifier.

        >>> host.block_device("/dev/nvme1n1").model
        'Samsung SSD 970 EVO Plus 500GB'

        >>> host.block_device("/dev/nvme1n1p1").model
        None

        """
        return self._data['model']

    @property
    def state(self) -> str | None:
        """Return state of the device.

        >>> host.block_device("/dev/nvme1n1").state
        'live'

        >>> host.block_device("/dev/nvme1n1p1").state
        None

        """
        return self._data['state']

    @property
    def partition_type(self) -> str | None:
        """Return partition table type.

        >>> host.block_device("/dev/nvme1n1p1").partition_type
        'gpt'

        >>> host.block_device("/dev/nvme1n1").partition_type
        None

        """
        return self._data['pttype']

    @property
    def wwn(self) -> str:
        """Return unique storage identifier.

        >>> host.block_device("/dev/nvme1n1").wwn
        'eui.00253856a5ebaa6f'

        >>> host.block_device("/dev/nvme1n1p1").wwn
        'eui.00253856a5ebaa6f'

        """
        return self._data['wwn']

    @property
    def filesystem_type(self) -> str | None:
        """Return filesystem type.

        >>> host.block_device("/dev/nvme1n1p1").filesystem_type
        'vfat'

        >>> host.block_device("/dev/nvme1n1").filesystem_type
        None

        """
        return self._data['fstype']

    @property
    def is_mounted(self) -> bool:
        """Return True if the device is mounted.

        >>> host.block_device("/dev/nvme1n1p1").is_mounted
        True

        """
        return bool(self._data['mountpoint'])

    @property
    def type(self) -> str:
        """Return device type.

        >>> host.block_device("/dev/nvme1n1").type
        'disk'

        >>> host.block_device("/dev/nvme1n1p1").type
        'part'

        >>> host.block_device("/dev/mapper/vg-lvol0").type
        'lvm'

        """
        return self._data['type']

    @property
    def transport_type(self) -> str:
        """Return device transport type.

        >>> host.block_device("/dev/nvme1n1p1").transport_type
        'nvme'

        >>> host.block_device("/dev/sdc").transport_type
        'iscsi'

        """
        return self._data['tran']


class LinuxBlockDeviceExtended(LinuxBlockDevice):
    @classmethod
    def get_free_disks(cls) -> list[LinuxBlockDeviceExtended]:
        free_devices = []
        for device in cls._iter_blockdevices():
            # skip children
            if device['pkname']:
                continue
            # skip if device contains children
            if device.get('children'):
                continue
            # skip lvm PV
            if f'/dev/{device["name"]}' in pv_query():
                continue
            free_devices.append(cls(device['name'], device))

        return free_devices
