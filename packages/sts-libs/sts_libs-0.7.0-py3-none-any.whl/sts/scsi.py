"""scsi.py: Module to manipulate SCSI devices."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os.path
import re
from pathlib import Path

from sts import linux, lvm, md, mp, net
from sts.utils import size
from sts.utils.cmdline import exists, run, run_ret_out

# I'm still note sure whether to use /sys/class/scsi_disk or /sys/class/scsi_device

sys_disk_path = '/sys/class/scsi_disk'
host_path = '/sys/class/scsi_host'

# add /lib/udev to PATH because scsi_id is located there on RHEL7
os.environ['PATH'] += ':/lib/udev'


def get_regex_scsi_id():  # noqa: ANN201
    return '([0-9]+):([0-9]+):([0-9]+):([0-9]+)'


def is_scsi_device(scsi_device):  # noqa: ANN001, ANN201
    return bool(re.match('^sd[a-z]+$', scsi_device))


def get_scsi_disk_ids():  # noqa: ANN201
    """Return an array of scsi_ids. If an scsi_device name is given as
    parameter, then just the id of the device is returned (TODO)
    The arguments are:
    None
    Device name: eg. sda
    Returns:
    array: Return an array of SCSI IDs.
    """
    cmd = f'ls {sys_disk_path}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        return None
    return output.split()


def get_scsi_disk_name(device_id):  # noqa: ANN001, ANN201
    if not device_id:
        logging.error('get_scsi_disk_name() requires scsi_device_id as parameter')
        return None

    cmd = f'ls {sys_disk_path}/{device_id}/device/block'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        return None
    return output


def get_scsi_disk_vendor(device_id):  # noqa: ANN001, ANN201
    if not device_id:
        logging.error('get_scsi_disk_vendor() requires scsi_device_id as parameter')
        return None

    cmd = f'cat {sys_disk_path}/{device_id}/device/vendor'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        return None
    return output


def get_scsi_disk_model(device_id):  # noqa: ANN001, ANN201
    if not device_id:
        logging.error('get_scsi_disk_model() requires scsi_device_id as parameter')
        return None

    cmd = f'cat {sys_disk_path}/{device_id}/device/model'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        return None
    return output


def query_all_scsi_disks(scsi_disk=None):  # noqa: ANN001, ANN201
    """Query information of all SCSI disks and return them as a dict
    SCSI id is the dict key.
    If an SCSI disk is given as argument, return its info
    Parameter:
    scsi_disk (option):        SCSI disk name. eg: 'sda'.
    """
    disk_ids = get_scsi_disk_ids()
    if not disk_ids:
        # Could not find any SCSI device
        return None

    scsi_disks = {}
    for disk_id in disk_ids:
        scsi_name = get_scsi_disk_name(disk_id)
        if scsi_disk and scsi_name and scsi_disk != scsi_name:
            # optimization in case we requested specific disk, do not query all
            continue
        if not scsi_name:
            logging.warning(f"Could not get scsi_name for disk_id '{disk_id}'.")
            scsi_wwid = scsi_wwn = udev_wwn = size_bytes = state = timeout = None
        else:
            scsi_wwid = wwid_of_disk(scsi_name)
            scsi_wwn = wwn_of_disk(scsi_name)
            udev_wwn = udev_wwn_of_disk(scsi_name)
            size_bytes = size_of_disk(scsi_name)
            state = disk_sys_check(scsi_name)
            timeout = timeout_of_disk(scsi_name)
        scsi_vendor = get_scsi_disk_vendor(disk_id)
        scsi_model = get_scsi_disk_model(disk_id)
        m = re.match(get_regex_scsi_id(), disk_id)
        host_id = None
        driver = None
        if m:
            host_id = m.group(1)
            driver = scsi_driver_of_host_id(host_id)
        scsi_info = {
            'name': scsi_name,
            'wwid': scsi_wwid,
            'wwn': scsi_wwn,  # Uses scsi_id to query WWN
            'udev_wwn': udev_wwn,  # Used udevadm to query WWN
            'size': size_bytes,
            'size_human': size.size_bytes_2_size_human(size_bytes),
            'state': state,
            'timeout': timeout,
            'vendor': scsi_vendor,
            'model': scsi_model,
            'host_id': host_id,
            'driver': driver,
            'scsi_id': disk_id,
        }
        scsi_disks[disk_id] = scsi_info

    if scsi_disk:
        for disk_id in list(scsi_disks.keys()):
            if scsi_disk == scsi_disks[disk_id]['name']:
                return scsi_disks[disk_id]
        return None

    return scsi_disks


def get_scsi_name_by_vendor(vendor):  # noqa: ANN001, ANN201
    """Query information of all SCSI disks and return all scsi device names that
    are from the requested vendor
    Parameter:
    vendor:        SCSI disk Vendor. eg: 'LIO'
    Return:
    List:          List of SCSI names.
    """
    if not vendor:
        logging.error('get_scsi_name_by_vendor() - requires vendor parameter')
        return None

    all_scsi_disks_info = query_all_scsi_disks()
    if not all_scsi_disks_info:
        return None

    return [
        scsi_info['name']
        for scsi_info in all_scsi_disks_info.values()
        if 'vendor' in scsi_info and scsi_info['vendor'] == vendor
    ]


def scsi_host_of_scsi_name(scsi_name):  # noqa: ANN001, ANN201
    if not scsi_name:
        logging.error('scsi_host_of_scsi_name() - requires scsi_name parameter')
        return None

    scsi_disk_info = query_all_scsi_disks(scsi_name)
    if not scsi_disk_info:
        logging.warning(f'scsi_host_of_scsi_name() did not query info for {scsi_name}')
        return None
    return scsi_disk_info['host_id']


def scsi_name_2_scsi_id(scsi_name):  # noqa: ANN001, ANN201
    if not scsi_name:
        logging.error('scsi_name_2_scsi_id() - requires scsi_name parameter')
        return None

    scsi_disk_info = query_all_scsi_disks(scsi_name)
    if not scsi_disk_info:
        logging.warning(f'scsi_name_2_scsi_id() did not query info for {scsi_name}')
        return None
    return scsi_disk_info['scsi_id']


def delete_disk(device_name):  # noqa: ANN001, ANN201
    """device_name:    eg. sda."""
    if not device_name:
        logging.error('delete_disk() requires scsi_device_name as parameter')
        return None

    device_id = scsi_name_2_scsi_id(device_name)
    if not device_id:
        logging.error(f'delete_disk() could not find disk {device_name}')
        return None

    cmd = f'echo "1" >  {sys_disk_path}/{device_id}/device/delete'
    if run(cmd).rc != 0:
        return None
    return True


def get_hosts(somethings=None):  # noqa: ANN001, ANN201
    """Return a list with all SCSI hosts.
    The arguments are:
    None
    or
    scsi_disk     e.g. sda
    or
    scsi_id       e.g. 3:0:0:1
    Returns:
    Host list     if no problem executing command
    None          if something went wrong.
    """
    cmd = f'ls {host_path}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        return None
    # remove 'host' prefix
    all_host_ids = re.sub('host', '', output).split()
    if not somethings:
        return all_host_ids

    scsi_host_ids = None
    # If something is a single string, convert it to list
    for something in somethings if not isinstance(somethings, str) else [somethings]:
        if something is None:
            logging.error('get_hosts() - Invalid input')
            print(somethings)
            return None
        m = re.match(get_regex_scsi_id(), something)
        if m and m.group(1) in all_host_ids:
            if not scsi_host_ids:
                scsi_host_ids = []
            if m.group(1) not in scsi_host_ids:
                scsi_host_ids.append(m.group(1))
        else:
            # Assume it is scsi_disk name, such as sda
            scsi_id = scsi_name_2_scsi_id(something)
            m = re.match(get_regex_scsi_id(), scsi_id)
            if m and m.group(1) in all_host_ids:
                if not scsi_host_ids:
                    scsi_host_ids = []
                if m.group(1) not in scsi_host_ids:
                    scsi_host_ids.append(m.group(1))

    if not scsi_host_ids:
        return None
    return list(set(scsi_host_ids))


def query_scsi_host_info(host_id):  # noqa: ANN001, ANN201
    """Usage
        query_scsi_host_info(scsi_host_id)
    Purpose
        Save sysfs info of "/sys/class/scsi_host/host$scsi_host_id" to
            scsi_host_info
        We also check these folders:
            /sys/class/iscsi_host/host$scsi_host_id/
            /sys/class/fc_host/host$scsi_host_id/
    Parameter
        scsi_host_id           # like '0' for host0
    Returns
        scsi_host_info
            or
        None.
    """
    if not host_id:
        logging.error('query_scsi_host_info() - requires host_id')
        return None

    sysfs_folder = Path(f'/sys/class/scsi_host/host{host_id}')
    if not sysfs_folder.is_dir():
        logging.error(f'{host_id} is not a valid directory')
        return None

    scsi_host_info = {
        'scsi_host_id': host_id,
        'pci_id': pci_id_of_host_id(host_id),
        'driver': scsi_driver_of_host_id(host_id),
    }

    param_files = list(sysfs_folder.iterdir())
    for param in param_files:
        ret, output = run_ret_out(f'cat {sysfs_folder}/{param}', return_output=True)
        if ret != 0:
            # For some reason could not read the file
            continue
        scsi_host_info[param] = ', '.join(output.split('\n'))

    sysfs_hosts = [
        f'/sys/class/iscsi_host/host{host_id}',
        f'/sys/class/fc_host/host{host_id}',
    ]
    for sysfs_host in sysfs_hosts:
        path = Path(sysfs_host)
        if not path.is_dir():
            continue
        host_files = list(path.iterdir())
        for param in host_files:
            ret, output = run_ret_out(f'cat {sysfs_host}/{param}', return_output=True)
            if ret != 0:
                # For some reason could not read the file
                continue
            scsi_host_info[param] = ', '.join(output.split('\n'))

    return scsi_host_info


def scsi_driver_of_host_id(host_id):  # noqa: ANN001, ANN201
    if not host_id:
        logging.error('scsi_driver_of_host_id() - requires host_id parameter')
        return None
    scsi_drv_sysfs = f'/sys/class/scsi_host/host{host_id}/proc_name'
    if not Path(scsi_drv_sysfs).is_file():
        logging.error(f'{scsi_drv_sysfs} is not a valid path')
        return None

    output = run(f'cat {scsi_drv_sysfs}').stdout.rstrip()
    scsi_driver = output
    if not scsi_driver or scsi_driver == '(null)':
        # Driver information was not exported, let try to find it out some other way
        lpfc_sysfs_file = f'/sys/class/scsi_host/host{host_id}/lpfc_drvr_version'
        if Path(lpfc_sysfs_file).is_file():
            return 'lpfc'

        driver_sysfs_file = f'/sys/class/scsi_host/host{host_id}/driver_name'
        if Path(driver_sysfs_file).is_file():
            return run(f'cat {driver_sysfs_file}').stdout.rstrip()

        model_sysfs_file = f'/sys/class/scsi_host/host{host_id}/model_name'
        if Path(model_sysfs_file).is_file():
            output = run(f'cat {model_sysfs_file}').stdout.rstrip()
            if re.match('^QLE', output):
                return 'qla2xxx'

        symbolic_sysfs_file = f'/sys/class/fc_host/host{host_id}/symbolic_name'
        if Path(symbolic_sysfs_file).is_file():
            output = run(f'cat {symbolic_sysfs_file}').stdout.rstrip()
            if re.search('bnx2fc', output):
                return 'bnx2fc'

        pci_id = pci_id_of_host_id(host_id)
        if pci_id:
            lspci_regex = r'Kernel modules:\s+(\S+)'
            if not exists('lspci'):
                logging.error("pciutils is not installed. Can't query driver name using pci_id.")
                return None
            output = run(
                f'lspci -s "{pci_id}" -v | grep "Kernel modules:"',
            ).stdout.rstrip()
            if output:
                m = re.search(lspci_regex, output)
                if m:
                    return m.group(1)

        logging.error(f'Could not get driver name for SCSI host{host_id}')
        return None
    if scsi_driver == 'fcoe':
        drv_version_path = f'/sys/class/fc_host/host{host_id}/driver_version'
        output = run(f'cat {drv_version_path}').stdout.rstrip()
        if re.search('ixgbe', output):
            return 'ixgbe'
    return scsi_driver


def pci_id_of_host_id(host_id):  # noqa: ANN001, ANN201
    """Usage
        pci_id_of(scsi_host_id);
    Purpose
        Find out which PCI id providing the SCSI Host via:
            readlink("/sys/class/scsi_host/host'scsi_host_id'");
    Parameter
        $scsi_host_id           # like '0' for host0
    Returns
        pci_id                 # like '0000:00:1c.0'.
    """
    if not host_id:
        logging.error('pci_id_of_host_id() - requires host_id parameter')
        return None
    sys_path = Path(f'/sys/class/scsi_host/host{host_id}')
    if not sys_path.exists():
        logging.error(f'{sys_path} is not a valid path')
        return None

    link_path = Path.readlink(sys_path).as_posix()

    regex_pci_id = linux.get_regex_pci_id()
    m = re.search(f'({regex_pci_id})/host{host_id}/scsi_host', link_path)
    # print("DEBUG: pci_id_of_host_id - %s" % link_path)
    if m:
        return m.group(1)

    # for example ixgbe need to check the PCI id from the network device
    # check for network interface name
    m = re.compile(r'devices/virtual/net/(.*)\.').search(link_path)
    if m:
        return net.get_pci_id_of_nic(m.group(1))

    return None


def rescan_host(host=None):  # noqa: ANN001, ANN201
    """Rescan for devices for specific host
    If no host is given it will scan all SCSI hosts
    The arguments are:
    Host:      e.g. 1 for host1
    Returns:
    True if no problem executing command
    False if something went wrong.
    """
    host_list = [host] if host else list(get_hosts())

    error = 0

    if not host_list:
        logging.warning('No host found on server to rescan')
        return True

    for h in host_list:
        logging.info(f'Rescanning host{h}')
        cmd = f'echo "- - -" > {host_path}/host{h}/scan'
        if run(cmd).rc != 0:
            error += 1
            logging.error(f'there was some problem scanning host{h}')

    return not error


def rescan_disk(scsi_disk=None):  # noqa: ANN001, ANN201
    """Rescan a specific SCSI disk.
    If no disk is given, rescann all SCSI disks
    echo 1 > /sys/block/<scsi_disk>/device/rescan
    Host:      e.g. 1 for host1
    Returns:
    True if no problem executing command
    False if something went wrong.
    """
    scsi_disks = [scsi_disk] if scsi_disk else [get_scsi_disk_name(_id) for _id in get_scsi_disk_ids()]

    error = 0
    for disk in scsi_disks:
        cmd = f'echo 1 > /sys/block/{disk}/device/rescan'
        if run(cmd).rc != 0:
            logging.error(f'Could not rescan {disk}')
            error += 1

    return not error


def size_of_disk(scsi_disk):  # noqa: ANN001, ANN201
    """Usage
        size_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda
    Parameter
        scsi_disk
    Returns
        size in bytes.

    """
    if not scsi_disk:
        return None

    cmd = f'cat /sys/block/{scsi_disk}/queue/logical_block_size'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'size_of_disk() - Could not get size for disk {scsi_disk}')
        print(output)
        return None
    if not output:
        return None
    logical_block_size = output

    cmd = f'cat /sys/block/{scsi_disk}/size'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'size_of_disk() - Could not get sectore size for disk {scsi_disk}')
        print(output)
        return None
    if not output:
        return None

    sector_size = output

    return int(logical_block_size) * int(sector_size)


def wwid_of_disk(scsi_disk=None):  # noqa: ANN001, ANN201
    """Usage
        wwid_of_disk(disk)
    Purpose
        Given a scsi_disk name. E.g. sda, mpatha
    Parameter
        scsi_disk   device to get wwid for
    Returns
        wwid:       e.g. 360fff19abdd9f5fb943525d45126ca27.
    """
    if not scsi_disk:
        logging.error('wwid_of_disk() - requires scsi_disk parameter')
        return None

    if linux.is_dm_device(scsi_disk):
        return linux.get_udev_property(scsi_disk, 'DM_SERIAL')

    return linux.get_udev_property(scsi_disk, 'ID_SERIAL')


def scsi_ids_of_wwid(wwid):  # noqa: ANN001, ANN201
    """Usage
        scsi_ids_of_wwid(wwid)
    Purpose
        Find out all SCSI id for WWID.
    Parameter
        wwid
    Returns
        scsi_ids.
    """
    if not wwid:
        logging.error('scsi_ids_of_wwid(): Got NULL input for WWID')
        return None

    all_scsi_info = query_all_scsi_disks()
    if not all_scsi_info:
        # Could not find any SCSI device
        return None

    scsi_ids = [_id for _id in all_scsi_info if all_scsi_info[_id]['wwid'] == wwid]

    if scsi_ids:
        scsi_ids = list(set(scsi_ids))  # dedup
    return scsi_ids


def wwn_of_disk(scsi_disk):  # noqa: ANN001, ANN201
    """Usage
        wwn_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda
    Parameter
        scsi_disk
    Returns
        wwid:       eg. 0x60a980003246694a412b45673342616e.
    """
    if not scsi_disk:
        logging.error('wwn_of_disk() - requires scsi_disk parameter')
        return None

    key_regex = 'ID_WWN_WITH_EXTENSION=(.*)'

    # cmd = "udevadm info --name=%s --query=all" % scsi_disk
    # retcode, output = run_ret_out(cmd, return_output=True)
    # if (retcode != 0):
    # #logging.error("wwn_of_disk() - Could not query %s" % scsi_disk)
    # #print output

    # return None

    # udev_wwn = None
    # lines = output.split("\n")
    # for line in lines:
    # m = re.search(key_regex, line)
    # if m:
    # udev_wwn = m.group(1)

    cmd = f'scsi_id --whitelisted --export /dev/{scsi_disk}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        # logging.error("wwn_of_disk() - Could not query %s" % scsi_disk)
        # print output
        return None

    lines = output.split('\n')
    for line in lines:
        m = re.search(key_regex, line)
        if m:
            return m.group(1)

    # if udev_wwn and scsi_wwn:
    # if udev_wwn == scsi_wwn:
    # return udev_wwn
    # print("udevadm WWN is %s" % udev_wwn)
    # print("scsi_id WWN is %s" % scsi_wwn)
    # logging.error("wwn_of_disk() - udevadm WWN and scsi_id WWN for %s do not match" % scsi_disk)
    # return None

    return None


def udev_wwn_of_disk(scsi_disk):  # noqa: ANN001, ANN201
    """Usage
        udev_wwn_of_disk(disk)
    Purpose
        Given an scsi_disk name. Eg. sda
    Parameter
        scsi_disk
    Returns
        wwid:       eg. 0x60a980003246694a412b45673342616e.
    """
    if not scsi_disk:
        logging.error('udev_wwn_of_disk() - requires scsi_disk parameter')
        return None

    key_regex = 'ID_WWN_WITH_EXTENSION=(.*)'

    cmd = f'udevadm info --name={scsi_disk} --query=all'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        # logging.error("udev_wwn_of_disk() - Could not query %s" % scsi_disk)
        # print output
        return None

    lines = output.split('\n')
    for line in lines:
        m = re.search(key_regex, line)
        if m:
            return m.group(1)
    return None


def query_scsi_driver_info(driver):  # noqa: ANN001, ANN201
    if not driver:
        logging.error('query_scsi_driver_info() - requires driver parameter')
        return None

    all_scsi_host_ids = get_hosts()
    if not all_scsi_host_ids:
        logging.error('query_scsi_driver_info() - Host does not have any SCSI host')
        return None

    # Check which SCSI hosts are using the driver we want
    driver_host_ids = [host_id for host_id in all_scsi_host_ids if scsi_driver_of_host_id(host_id) == driver]

    if not driver_host_ids:
        logging.error(f' No SCSI disk found from driver {driver}')
        return None

    scsi_driver_info = {'scsi_host': {}}
    for host_id in driver_host_ids:
        scsi_driver_info['scsi_host'][host_id] = query_scsi_host_info(host_id)

    scsi_driver_info['driver_name'] = driver
    # Add general driver info to this dict
    scsi_driver_info.update(linux.get_driver_info(driver))

    return scsi_driver_info


def get_free_disks(  # noqa: ANN201
    exclude_boot_device=True,  # noqa: ANN001
    exclude_lvm_device=True,  # noqa: ANN001
    exclude_mpath_device=True,  # noqa: ANN001
    exclude_md_device=True,  # noqa: ANN001
    filter_only=None,  # noqa: ANN001
):
    """Return a dict of free SCSI devices.
    By default, it excludes devices used for boot, lvm or multipath
    Optional "filter_only" argument should be a dict. E.g. filter_only={'state': 'running'}.
    """
    all_scsi_disks = query_all_scsi_disks()
    if not all_scsi_disks:
        # could not find any SCSI disk
        return None

    pvs = lvm.pv_query()
    md_devices = md.md_query()
    boot_dev = linux.get_boot_device()
    boot_wwid = None
    # if for some reason we boot from a single disk, but this disk is part of multipath device
    # the mpath device should be skipped as well
    if boot_dev:
        boot_wwid = linux.get_device_wwid(boot_dev)

    all_mp_info = None
    if (mp.is_multipathd_running()) and exclude_mpath_device:
        all_mp_info = mp.multipath_query_all()
        if all_mp_info and 'by_wwid' not in list(all_mp_info.keys()):
            # Fail querying mpath, setting it back to None
            all_mp_info = None

    chosen_disks = {}
    for scsi_disk in list(all_scsi_disks.keys()):
        scsi_info = all_scsi_disks[scsi_disk]
        # Skip if mpath device is used for boot
        if boot_wwid == scsi_info['wwid'] and exclude_boot_device:
            print(f"DEBUG: get_free_disks() - skip {scsi_info['name']} as it is used for boot")
            continue

        # Skip if disk is used by multipath
        if all_mp_info and scsi_info['wwid'] in list(all_mp_info['by_wwid'].keys()) and exclude_mpath_device:
            print(f"DEBUG: get_free_disks() - skip {scsi_info['name']} as it is used for mpath")
            continue

        # Skip if it is used by Soft RAID
        if md_devices and exclude_md_device:
            used_by_md = False
            for md_dev in md_devices:
                storage_devs = md.md_get_storage_dev(md_dev)
                if not storage_devs:
                    continue
                for dev in storage_devs:
                    dev_wwid = wwid_of_disk(dev)
                    if not dev_wwid:
                        continue
                    if dev_wwid == scsi_info['wwid']:
                        print(f"DEBUG: get_free_disks() - skip {scsi_info['name']} as it is used for md")
                        used_by_md = True
                        continue
            if used_by_md:
                continue

        # Skip if filter_only is specified
        filtered = False
        if filter_only is not None:
            for key in filter_only:
                if scsi_info[key] != filter_only[key]:
                    print(
                        'DEBUG: get_free_disks() - filtered {} as {} is not {}'.format(
                            scsi_info['name'],
                            key,
                            filter_only[key],
                        ),
                    )
                    filtered = True
                    continue
        if filtered:
            continue

        chosen_disks[scsi_info['name']] = scsi_info

        # Skip if it is used by LVM
        if pvs and exclude_lvm_device:
            for pv in list(pvs.keys()):
                if '/' + get_scsi_disk_name(scsi_disk) in pv:
                    print(f"DEBUG: get_free_disks() - skip {scsi_info['name']} as it is used for LVM")
                    chosen_disks.pop(scsi_info['name'])

    return chosen_disks


def scsi_device_2_scsi_name(scsi_device):  # noqa: ANN001, ANN201
    """Convert an specific SCSI device to scsi_name
    Eg. /dev/sdap1 => sda.
    """
    scsi_dev_regex = r'/dev\/(sd.*)'
    m = re.match(scsi_dev_regex, scsi_device)
    if m:
        # remove partition if it has
        device_name = m.group(1)
        m = re.match(r'(.*)\d+', device_name)
        if m:
            device_name = m.group(1)
        return device_name
    # does not seem to be a valid SCSI device
    return None


def disk_sys_trigger(scsi_disk, action):  # noqa: ANN001, ANN201
    """Usage
        disk_sys_trigger(scsi_disk, action)
    Purpose
        Bring disk online/offline, via
            /sys/block/sdX/device/state
        action could be 'UP|DOWN|other', for UP, we change it into 'running'.
        for DOWN, we change it into 'offline'.
    Parameter
        scsi_disk      # like 'sda'
        action         # 'UP|DOWN|other'
    Returns
        True               # got expected /sys/block/sdX/device/state
            or
        False.
    """
    if not scsi_disk or not action:
        logging.error('disk_sys_trigger() - requires scsi_disk and action parameters')
        return False

    sys_path = f'/sys/block/{scsi_disk}/device/state'
    if not Path(sys_path).is_file():
        logging.error(f'No such file: {sys_path}')
        return False

    if action == 'UP':
        action = 'running'
    if action == 'DOWN':
        action = 'offline'

    cmd = f'echo {action} > {sys_path}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'disk_sys_trigger() - Could not execute {cmd}')
        print(output)
        return None

    # cmd = "cat %s 2>/dev/null" % sys_path
    new_state = disk_sys_check(scsi_disk)
    if not new_state:
        logging.error(f'disk_sys_trigger() - Could not get state of {scsi_disk}')
        return False

    if action != new_state:
        logging.error(f"disk_sys_trigger() - Current state is '{new_state}' expected '{action}'")
        return False

    return True


def disk_sys_check(scsi_disk):  # noqa: ANN001, ANN201
    """Usage
        disk_sys_check(scsi_disk)
    Purpose
        Check state of specific disk
            /sys/block/sdX/device/state
    Parameter
        scsi_disk      # like 'sda'
    Returns
        running/offline       # got expected /sys/block/sdX/device/state
            or
        None.
    """
    if not scsi_disk:
        logging.error('disk_sys_check() - requires scsi_disk parameter')
        return None

    sys_path = f'/sys/block/{scsi_disk}/device/state'
    if not Path(sys_path).is_file():
        logging.error(f'disk_sys_check() - No such file: {sys_path}')
        return None

    cmd = f'cat {sys_path} 2>/dev/null'
    state = run(cmd).stdout.rstrip()
    if not state:
        logging.error(f'disk_sys_check() - Could not read from {sys_path}')
        return None

    return state


def timeout_of_disk(scsi_disk):  # noqa: ANN001, ANN201
    """Usage
        timeout_of_disk(scsi_disk)
    Purpose
        Check timeout of specific disk
            /sys/block/sdX/device/timeout
    Parameter
        scsi_disk      # like 'sda'
    Returns
        timeout in seconds       # got expected /sys/block/sdX/device/timeout
            or
        None.
    """
    if not scsi_disk:
        logging.error('timeout_of_disk() - requires scsi_disk parameter')
        return None

    sys_path = f'/sys/block/{scsi_disk}/device/timeout'
    if not Path(sys_path).is_file():
        logging.error(f'timeout_of_disk() - No such file: {sys_path}')
        return None

    cmd = f'cat {sys_path} 2>/dev/null'
    timeout = run(cmd).stdout.rstrip()
    if not timeout:
        logging.error(f'timeout_of_disk() - Could not read from {sys_path}')
        return None

    return timeout
