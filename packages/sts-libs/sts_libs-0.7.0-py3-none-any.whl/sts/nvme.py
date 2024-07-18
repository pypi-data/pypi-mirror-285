"""nvme.py: Module to manipulate NVME devices."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
from os import listdir
from re import match

from sts.linux import get_boot_device, get_device_wwid
from sts.lvm import pv_query
from sts.md import md_get_storage_dev, md_query
from sts.mp import is_multipathd_running, multipath_query_all
from sts.utils.cmdline import run_ret_out
from sts.utils.size import size_bytes_2_size_human


def is_nvme_device(device: str) -> bool:
    """Checks if device is nvme device."""
    return bool(match('^nvme[0-9]n[0-9]$', device))


def get_nvme_device_names() -> list:
    """Return list of nvme devices.

    Returns:
    list: Return list of nvme devices
    """
    return [name for name in listdir('/sys/block') if is_nvme_device(name)]


def get_logical_block_size(nvme_device: str) -> str:
    cmd = f'cat /sys/block/{nvme_device}/queue/logical_block_size'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_logical_block_size() - Could not get logical block size for nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def get_physical_block_size(nvme_device: str) -> str:
    cmd = f'cat /sys/block/{nvme_device}/queue/physical_block_size'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_physical_block_size() - Could not get physical block size for nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def size_of_device(nvme_device: str) -> int:
    """Return size of device."""
    logical_block_size = get_logical_block_size(nvme_device)

    if not logical_block_size:
        return 0

    cmd = f'cat /sys/block/{nvme_device}/size'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'size_of_device() - Could not get sector size for device {nvme_device}')
        logging.debug(output)
        return 0
    if not output:
        return 0

    sector_size = output

    return int(logical_block_size) * int(sector_size)


def get_nvme_wwid(nvme_device: str) -> str:
    """Return wwid of device."""
    cmd = f'cat /sys/block/{nvme_device}/wwid'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_nvme_wwid() - Could not get wwid of nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def get_nvme_nqn(nvme_device: str) -> str:
    """Return nvme nqn of device."""
    cmd = f'cat /sys/block/{nvme_device}/device/subsysnqn'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_nvme_nqn() - Could not get nqn of nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def get_nvme_uuid(nvme_device: str) -> str:
    """Return nvme uuid nvme device."""
    cmd = f'cat /sys/block/{nvme_device}/uuid'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_nvme_uuid() - Could not get uuid of nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def get_nvme_state(nvme_device: str) -> str:
    """Return nvme device state."""
    cmd = f'cat /sys/block/{nvme_device}/device/state'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_nvme_subsystem_state() - Could not get state of nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def get_nvme_model(nvme_device: str) -> str:
    """Return model of nvme device."""
    cmd = f'cat /sys/block/{nvme_device}/device/model'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_nvme_model() - Could not get model of nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def get_nvme_transport(nvme_device: str) -> str:
    """Return transport of nvme device."""
    cmd = f'cat /sys/block/{nvme_device}/device/transport'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.warning(f'get_nvme_transport() - Could not get transport of nvme device: {nvme_device}')
        logging.debug(output)
        return ''
    if not output:
        return ''
    return output


def query_all_nvme_devices(nvme_device: str = '') -> dict:
    """Query information of all NVMe devices."""
    nvme_devices = {}
    for device in get_nvme_device_names():
        if nvme_device and nvme_device != device:
            # optimization in case we requested specific device, do not query all
            continue
        nvme_wwid = get_nvme_wwid(device)
        nvme_uuid = get_nvme_uuid(device)
        nvme_nqn = get_nvme_nqn(device)
        size_bytes = size_of_device(device)
        logical_block_size = get_logical_block_size(device)
        physical_block_size = get_physical_block_size(device)
        nvme_model = get_nvme_model(device)
        state = get_nvme_state(device)
        transport = get_nvme_transport(device)
        nvme_info = {
            'name': device,
            'wwid': nvme_wwid,
            'uuid': nvme_uuid,
            'nqn': nvme_nqn,  # Uses scsi_id to query WWN
            'size': size_bytes,
            'size_human': size_bytes_2_size_human(size_bytes),
            'logical_block_size': logical_block_size,
            'physical_block_size': physical_block_size,
            'state': state,
            'model': nvme_model,
            'transport': transport,
        }
        nvme_devices[device] = nvme_info

    return nvme_devices


def get_free_nvme_devices(
    exclude_boot_device: bool = True,
    exclude_lvm_device: bool = True,
    exclude_mpath_device: bool = True,
    exclude_md_device: bool = True,
    filter_only: dict[str, str] | None = None,
) -> dict:
    all_nvme_devices = query_all_nvme_devices()
    if not all_nvme_devices:
        # could not find any nvme devices
        return {}

    pvs = pv_query()
    md_devices = md_query()
    boot_dev = get_boot_device()
    # if for some reason we boot from a single device, but this device is part of multipath device
    # the mpath device should be skipped as well

    all_mp_info = None
    if (is_multipathd_running()) and exclude_mpath_device:
        all_mp_info = multipath_query_all()
        if all_mp_info and 'by_wwid' not in list(all_mp_info.keys()):
            # Fail querying mpath, setting it back to None
            all_mp_info = None

    chosen_devices = {}
    for nvme_device in list(all_nvme_devices.keys()):
        nvme_info = all_nvme_devices[nvme_device]
        # Skip if mpath device is used for boot
        if nvme_info['name'] in boot_dev and exclude_boot_device:
            logging.debug(f"get_free_nvme_devices() - skip {nvme_info['name']} as it is used for boot")
            continue

        # Skip if device is used by multipath
        if all_mp_info and nvme_info['wwid'] in list(all_mp_info['by_wwid'].keys()) and exclude_mpath_device:
            logging.debug(f"get_free_nvme_devices() - skip {nvme_info['name']} as it is used for mpath")
            continue

        # Skip if it is used by Soft RAID
        if md_devices and exclude_md_device:
            used_by_md = False
            for md_dev in md_devices:
                storage_devs = md_get_storage_dev(md_dev)
                if not storage_devs:
                    continue
                for dev in storage_devs:
                    dev_wwid = get_device_wwid(dev)
                    if not dev_wwid:
                        continue
                    if dev_wwid == nvme_info['wwid']:
                        logging.debug(f"get_free_nvme_devices() - skip {nvme_info['name']} as it is used for md")
                        used_by_md = True
                        continue
            if used_by_md:
                continue

        # Skip if filter_only is specified
        filtered = False
        if filter_only is not None:
            for key in filter_only:
                if nvme_info[key] != filter_only[key]:
                    logging.debug(
                        f"get_free_nvme_devices() - filtered {nvme_info['name']} as {key} is not {filter_only[key]}",
                    )
                    filtered = True
                    continue
        if filtered:
            continue

        # Skip if it is used by LVM
        if pvs and exclude_lvm_device and '/' + nvme_device in pvs:
            logging.debug(f"get_free_nvme_devices() - skip {nvme_info['name']} as it is used for LVM")
            continue

        chosen_devices[nvme_info['name']] = nvme_info

    return chosen_devices
