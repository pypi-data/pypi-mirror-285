"""md.py: Module to manipulate MD devices."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import re
from pathlib import Path

from sts.utils.cmdline import exists, run_ret_out


def _mdadm_query(md_device):  # noqa: ANN001, ANN202
    if not exists('mdadm'):
        logging.info('mdadm is not installed')
        return None

    cmd = f'mdadm -D /dev/{md_device}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"couldn't query {md_device}")
        return None
    return output


def md_query():  # noqa: ANN201
    """Query Soft RAID devices.
    The arguments are:
    Returns:
    dict: Return a list of md devices.
    """
    mdstat_file = '/proc/mdstat'

    if not Path(mdstat_file).exists():
        logging.info('there is no MD device')
        return False

    cmd = f'cat {mdstat_file}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.info('there is no MD device')
        return None

    md_name_regex = r'^(md\d+) :'
    md_devices = []
    for line in output.split('\n'):
        m = re.match(md_name_regex, line)
        if not m:
            continue
        md_devices.append(m.group(1))

    return md_devices


def md_get_info(md_device):  # noqa: ANN001, ANN201
    """Query information of an MD device.
    The arguments are:
    md_device: md device name to get information about
    Returns:
    dict: Return a dictionary with details about the md device.
    """
    if not md_device:
        return None

    if md_device not in md_query():
        logging.info(f'{md_device} is not a MD device')
        return None

    output = _mdadm_query(md_device)
    if not output:
        return None

    md_info = {}
    # Try to get general information about the device
    md_info_regex = r'\s+(.*) : (.*)'
    for line in output.split('\n'):
        info_match = re.match(md_info_regex, line)
        if not info_match:
            continue
        info_name = info_match.group(1).lower()
        info_name = info_name.replace(' ', '_')
        md_info[info_name] = info_match.group(2)

    # Try to get the storage devices linked to the MD
    storage_section = False
    storage_regex = r'\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(.*)\s+(\S+)$'
    for line in output.split('\n'):
        if re.search(r'Number\s+Major\s+Minor\s+RaidDevice\s+State', line):
            storage_section = True
            md_info['storage_devices'] = {}
        if not storage_section:
            continue
        storage_match = re.match(storage_regex, line)
        if not storage_match:
            continue
        storage_info = {
            'number': storage_match.group(1),
            'major': storage_match.group(2),
            'minor': storage_match.group(3),
            'raid_device': storage_match.group(4),
            'state': storage_match.group(5).strip(),
        }
        md_info['storage_devices'][storage_match.group(6)] = storage_info

    return md_info


def md_get_storage_dev(md_device):  # noqa: ANN001, ANN201
    """Get the storage devices of an MD device.
    The arguments are:
    md_device: md device name to get information about
    Returns:
    list: Return a list of storage devices.
    """
    if not md_device:
        return None

    md_info = md_get_info(md_device)
    if not md_info:
        return None

    if 'storage_devices' not in md_info:
        return None
    return md_info['storage_devices'].keys()


def md_stop(md_device):  # noqa: ANN001, ANN201
    """Stop a specific md device.
    The arguments are:
    md_device: md device name to get information about
    Returns:
    Boolean:
    True if success
    False in case of failure.
    """
    cmd = f'mdadm --stop /dev/{md_device}'
    retcode, _output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"couldn't stop {md_device}")
        return False
    return True


def md_clean(device):  # noqa: ANN001, ANN201
    """Clean a specific storage device.
    The arguments are:
    device: storage device like /dev/sda
    Returns:
    Boolean:
    True if success
    False in case of failure.
    """
    cmd = f'mdadm --zero-superblock {device}'
    retcode, _output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"couldn't clean {device}")
        return False
    return True


def md_remove(md_device, clean=False):  # noqa: ANN001, ANN201
    """Remove a specific md device.
    The arguments are:
    md_device: md device name to get information about
    Returns:
    Boolean:
    True if success
    False in case of failure.
    """
    sto_devices = md_get_storage_dev(md_device)

    if not md_stop(md_device):
        return False

    cmd = f'mdadm --remove /dev/{md_device}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if (
        retcode != 0
        and
        # error opening the device can be ignored
        f'mdadm: error opening /dev/{md_device}: No such file or directory' not in output
    ):
        logging.error(f"couldn't remove {md_device}")
        return False
    if clean and sto_devices:
        for device in sto_devices:
            if not md_clean(device):
                return False
    return True
