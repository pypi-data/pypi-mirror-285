"""mp.py: Module to manage multipath devices."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import re
from pathlib import Path
from typing import Literal

from sts import fc, iscsi, linux, lvm, net, scsi
from sts.utils.cmdline import run, run_ret_out
from sts.utils.size import size_human_2_size_bytes

MULTIPATH_CONF_PATH = '/etc/multipath.conf'
aug_conf_path = '/files/etc/multipath.conf'
package_name = 'device-mapper-multipath'


def mp_service_name():  # noqa: ANN201
    """Return the name of multipath service."""
    return 'multipathd'


def mp_start_service():  # noqa: ANN201
    """Start multipath service."""
    if linux.is_installed(package_name) and not Path(MULTIPATH_CONF_PATH).is_file():
        mpathconf_enable()
    return linux.service_start(mp_service_name())


def mp_stop_service():  # noqa: ANN201
    """Stop multipath service."""
    return linux.service_stop(mp_service_name())


def is_multipathd_running():  # noqa: ANN201
    """Check if multipathd is running."""
    return linux.is_service_running(mp_service_name())


def mpathconf_enable(find_mpaths: Literal['yes', 'no', 'strict', 'greedy', 'smart', None] = None) -> bool:
    """Runs 'mpathconf --enable' command."""
    cmd = 'mpathconf --enable'
    if find_mpaths:
        cmd += f' --find_multipaths {find_mpaths}'
    return run(cmd).rc == 0


def mp_enable() -> bool:
    """Installs and enable multipath."""
    if not is_multipathd_running():
        linux.install_package('device-mapper-multipath')
        mpathconf_enable()
        if not linux.service_start(mp_service_name()):
            return False

    return True


def is_mpath_device(mpath_name: str) -> bool:
    """Checks if given device is multipath.

    Args:
      mpath_name: name of device to check
      print_fail: Should we print "FAIL: ..." in case of fail?

    Returns:
      True / False.
    """
    return run(f'multipath -l {mpath_name}').succeeded


def get_mpath_of_disk(disk):  # noqa: ANN001, ANN201
    """Get the multipath device of a disk
    The arguments are:
    Disk:   Disk
    Returns:
    String: Return the name of multipath device.
    """
    # BZ891921 - Multipath provides the mpath device of given scsi block device
    cmd = 'pidof multipathd'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error('For some reason multipathd is not running')
        print(output)
        return None
    fmt = '"%d %m"'
    cmd = f'multipathd show paths format {fmt} | egrep "^{disk}" | awk \'{{print$2}}\''
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'to find multipath of disk {disk}')
        print(output)
        return None
    mpath = output

    if not mpath:
        logging.warning(f'Could not find multipath for {disk}')
        return None
    return mpath


def get_disks_of_mpath(mpath_name):  # noqa: ANN001, ANN201
    """Return all SCSI devices that belong to this mpath."""
    if not mpath_name:
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    if 'disk' not in list(mpath_dict.keys()):
        logging.warning(f'mpath {mpath_name} has no disk')
        return None

    return list(mpath_dict['disk'].keys())


def get_disks_of_mpath_by_wwpn(mpath_name, wwpn):  # noqa: ANN001, ANN201
    """From a specific mpath device, return the devices
    connected to this WWPN.
    """
    if not mpath_name or not wwpn:
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    scsi_devices = []
    wwpn = fc.standardize_wwpn(wwpn)
    if wwpn and 'disk' in list(mpath_dict.keys()):
        port_entries = ['h_wwpn', 't_wwpn']
        for disk in list(mpath_dict['disk'].keys()):
            for port_entry in port_entries:
                if port_entry in list(mpath_dict['disk'][disk].keys()):  # noqa: SIM102
                    if mpath_dict['disk'][disk][port_entry] and wwpn in mpath_dict['disk'][disk][port_entry]:
                        scsi_devices.append(disk)
    return scsi_devices


def get_disks_of_mpath_by_iqn(mpath_name, iqn):  # noqa: ANN001, ANN201
    """From a specific mpath device, return the devices
    connected to this IQN.
    """
    if not mpath_name or not iqn:
        return None

    if not iscsi.is_iqn(iqn):
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    scsi_devices = []
    if 'disk' in list(mpath_dict.keys()):
        port_entries = ['h_iqn', 't_iqn']
        for disk in list(mpath_dict['disk'].keys()):
            for port_entry in port_entries:
                if port_entry in list(mpath_dict['disk'][disk].keys()):  # noqa: SIM102
                    if mpath_dict['disk'][disk][port_entry] and iqn in mpath_dict['disk'][disk][port_entry]:
                        scsi_devices.append(disk)
    return scsi_devices


def get_disks_of_mpath_by_mac(mpath_name, mac):  # noqa: ANN001, ANN201
    """From a specific mpath device, return the devices
    connected to this MAC.
    """
    if not mpath_name or not mac:
        return None

    if not net.is_mac(mac):
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        return None

    scsi_devices = []
    if 'disk' in list(mpath_dict.keys()):
        port_entries = ['iface_mac']
        for disk in list(mpath_dict['disk'].keys()):
            for port_entry in port_entries:
                if port_entry in list(mpath_dict['disk'][disk].keys()):  # noqa: SIM102
                    if mpath_dict['disk'][disk][port_entry] and mac in mpath_dict['disk'][disk][port_entry]:
                        scsi_devices.append(disk)
    return scsi_devices


def multipath_query_all(mpath_name=None):  # noqa: ANN001, ANN201
    # Not sure with of these 2 commands I should use
    # multipath -ll
    # will force multipath to issue its own (synchronous) path checker call,
    # and report that result.
    # multipathd show top
    # multipath will not run a checker on the paths. It will simply report the
    # current state. This means that you get the results from the last time
    # that multipathd ran the path checker.  If there is no IO going to the
    # device, the kernel won't return an error on the path, and so you will
    # not see any errors until the next checker is run after you bring the
    # port down.
    cmd = 'multipath -ll'
    if mpath_name:
        cmd += f' {mpath_name}'
    # cmd = "multipathd -k\"show top\""
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        print(f'FAIL: Could not execute "{cmd}"')
        return None

    if not output:
        # logging.error("Got no output from \"%s\"" % cmd)
        return None

    regex_mpath = r'^(?:create\:\ ){0,1}'  # might have when creating mpath
    regex_mpath += r'(?:reload\:\ ){0,1}'  # might have when creating mpath
    regex_mpath += r'([^ ]+?)\ +'  # 1. mpath_name
    regex_mpath += r'(?:\((\S+)\)\ +){0,1}'  # 2. wwid if different from #1
    regex_mpath += r'(?:(dm\-[0-9]+)\ +){0,1}'  # 3. dm_name if known
    regex_mpath += r'(?:([^,]+),){0,1}'  # 4. vendor, might not have
    regex_mpath += r'(?:([^,]+)){0,1}$'  # 5. product,  might not have

    regex_feature = r'size=([0-9\.]+[A-Z])\ +'  # 1. size
    regex_feature += r'features=\'([^\']+)\'\ +'  # 2. features
    regex_feature += r'hwhandler=\'([^\']+)\'\ +'  # 3. hardware handler
    regex_feature += r'(?:wp=([rw]+)){0,1}'  # 4. write permission if known

    regex_pg = r'[^a-z]+policy=\'([^\`]+)\'\ +'  # 1. policy of this PG path_selector
    regex_pg += r'(?:prio=([0-9\-]+)\ +){0,1}'  # 2. priority of this PG if known
    regex_pg += r'(?:status=([a-z]+)){0,1}'  # 3. status of this PG if known (active or enable, etc)

    regex_disk = r'[^0-9]+'
    regex_disk += r'([0-9]+:[0-9]+:[0-9]+:[0-9]+)\ +'  # 1. scsi_id
    regex_disk += r'([a-z]+)\ +'  # 2. dev_name
    regex_disk += r'([0-9]+:[0-9]+)\ +'  # 3. major:minor
    regex_disk += r'(?:([a-z]+)\ +){0,1}'  # 4. dm_status if known, kernel level
    #   failed or active
    regex_disk += r'(?:([a-z]+)\ +){0,1}'  # 5. path_status if known, maintained
    #   by multipathd path_checker
    #   ready  or ghost or
    #   faulty or shaky
    regex_disk += r'(?:([a-z]+)){0,1}'  # 6. online_status: running or offline

    _mpath_name = None
    pg_id = None
    size = None
    size_human = None
    size_bytes = None
    wwid = None

    all_mpath_dict = {'by_wwid': {}, 'by_mpath_name': {}, 'by_scsi_id': {}}
    mpath_dict = {}

    scsi_host_id_2_driver = {}
    scsi_host_id_2_h_wwpn = {}
    fc_target_id_2_t_wwpn = {}

    all_scsi_host_ids = scsi.get_hosts()

    for host_id in all_scsi_host_ids:
        scsi_driver = scsi.scsi_driver_of_host_id(host_id)
        if scsi_driver:
            scsi_host_id_2_driver[host_id] = scsi_driver
        scsi_host_id_2_h_wwpn[host_id] = fc.get_fc_host_wwpn(host_id)
        t_wwpns_of_host = fc.t_wwpn_of_host(host_id)
        if t_wwpns_of_host:
            for t_wwpn in t_wwpns_of_host:
                t_ids = fc.fc_target_id_of_wwpn(t_wwpn)
                if t_ids:
                    for t_id in t_ids:
                        fc_target_id_2_t_wwpn[t_id] = t_wwpn

    lines = output.split('\n')

    for line in lines:
        m = re.match(regex_feature, line)
        if m:
            if not wwid or not mpath_dict:
                continue
            size = m.group(1)
            size_human = size + 'iB'
            size_bytes = size_human_2_size_bytes(size_human)
            mpath_dict['size_mp'] = size
            mpath_dict['size_human'] = size_human
            mpath_dict['size_bytes'] = size_bytes
            mpath_dict['feature'] = m.group(2)
            mpath_dict['hw_handleer'] = m.group(3)
            mpath_dict['permission'] = m.group(4)
            mpath_dict['disk'] = {}
            mpath_dict['t_wwpns'] = []
            mpath_dict['h_wwpns'] = []
            mpath_dict['t_iqns'] = []
            mpath_dict['h_iqns'] = []
            mpath_dict['map_info'] = []
            mpath_dict['iface_macs'] = []
            mpath_dict['iface_names'] = []
            mpath_dict['target_ips'] = []
            mpath_dict['persist_ips'] = []
            mpath_dict['transport_types'] = []
            mpath_dict['scsi_drivers'] = []
            mpath_dict['host_ids'] = []
            # print("\n\nDEBUG - Feature - query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]

            continue

        m = re.match(regex_pg, line)
        if m:
            if not wwid or not mpath_dict:
                continue
            pg_id += 1
            mpath_dict['path_group'][pg_id] = {}
            mpath_dict['path_group'][pg_id]['wwid'] = wwid
            mpath_dict['path_group'][pg_id]['mpath_name'] = _mpath_name
            mpath_dict['path_group'][pg_id]['wwid'] = wwid
            mpath_dict['path_group'][pg_id]['pg_id'] = pg_id
            mpath_dict['path_group'][pg_id]['policy'] = m.group(1)
            mpath_dict['path_group'][pg_id]['prio'] = m.group(2)
            mpath_dict['path_group'][pg_id]['status'] = m.group(3)
            mpath_dict['path_group'][pg_id]['disk'] = {}
            # print("\n\nDEBUG - PG : query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]

            continue

        m = re.match(regex_disk, line)
        if m:
            if not wwid or not mpath_dict or not pg_id:
                continue
            scsi_id = m.group(1)
            scsi_disk = m.group(2)
            major_minor = m.group(3)
            dm_status = m.group(4)
            path_status = m.group(5)
            online_status = m.group(6)
            # host id is the first numbers of scsi_id
            host_id = None
            m = re.match(r'(\d+):.*', scsi_id)
            if m:
                host_id = m.group(1)

            t_wwpn = None
            h_wwpn = None
            h_iqn = None
            t_iqn = None
            iface_name = None
            iface_mac = None
            target_ip = None
            persist_ip = None
            scsi_driver = 'N/A'

            match_scsi_id = re.search(scsi.get_regex_scsi_id(), line)
            if match_scsi_id:
                scsi_host_id = match_scsi_id.group(1)
                fc_target_id = f'{match_scsi_id.group(1)}:{match_scsi_id.group(2)}:{match_scsi_id.group(3)}'
                if scsi_host_id in list(scsi_host_id_2_driver.keys()):
                    scsi_driver = scsi_host_id_2_driver[scsi_host_id]

                if scsi_host_id in list(scsi_host_id_2_h_wwpn.keys()):
                    h_wwpn = scsi_host_id_2_h_wwpn[scsi_host_id]

                if h_wwpn:
                    if fc_target_id in list(fc_target_id_2_t_wwpn.keys()):
                        t_wwpn = fc_target_id_2_t_wwpn[fc_target_id]
                else:
                    iscsi_session = iscsi.get_iscsi_session_by_scsi_id(scsi_id)
                    if iscsi_session:
                        h_iqn = iscsi_session['h_iqn']
                        t_iqn = iscsi_session['t_iqn']
                        iface_name = iscsi_session['iface']
                        iface_mac = iscsi_session['mac']
                        target_ip = iscsi_session['target_ip']
                        persist_ip = iscsi_session['persist_ip']

            disk_info_dict = {
                'scsi_id': scsi_id,
                'host_id': host_id,
                'scsi_disk': scsi_disk,
                'scsi_driver': scsi_driver,
                'pg_id': pg_id,
                'mpath_name': _mpath_name,
                'wwid': wwid,
                'dm_status': dm_status,
                'path_status': path_status,
                'online_status': online_status,
                'major_minor': major_minor,
                'size': size,
                'size_human': size_human,
                'size_bytes': size_bytes,
                't_wwpn': t_wwpn,
                'h_wwpn': h_wwpn,
                't_iqn': t_iqn,
                'h_iqn': h_iqn,
                'iface_name': iface_name,
                'iface_mac': iface_mac,
                'target_ip': target_ip,
                'persist_ip': persist_ip,
                'transport_type': 'UNKNOWN',
            }

            if h_iqn:
                disk_info_dict['transport_type'] = 'iSCSI'

            if h_wwpn:
                disk_info_dict['transport_type'] = fc.fc_host_transport_type(fc.fc_host_id_of_wwpn(h_wwpn))

            if scsi_driver == 'scsi_debug':
                disk_info_dict['transport_type'] = 'scsi_debug'

            # Each disk has its own information, we should add each disk from mpath info to mpath info
            if disk_info_dict['transport_type'] not in mpath_dict['transport_types']:
                mpath_dict['transport_types'].append(disk_info_dict['transport_type'])

            if scsi_driver and scsi_driver not in mpath_dict['scsi_drivers']:
                mpath_dict['scsi_drivers'].append(scsi_driver)

            if host_id and host_id not in mpath_dict['host_ids']:
                mpath_dict['host_ids'].append(host_id)

            if t_wwpn and t_wwpn not in mpath_dict['t_wwpns']:
                mpath_dict['t_wwpns'].append(t_wwpn)

            if h_wwpn and h_wwpn not in mpath_dict['h_wwpns']:
                mpath_dict['h_wwpns'].append(h_wwpn)

            if h_wwpn and t_wwpn:
                map_info = {'t_wwpn': t_wwpn, 'h_wwpn': h_wwpn}
                mpath_dict['map_info'].append(map_info)

            if t_iqn and t_iqn not in mpath_dict['t_iqns']:
                mpath_dict['t_iqns'].append(t_iqn)

            if h_iqn and h_iqn not in mpath_dict['h_iqns']:
                mpath_dict['h_iqns'].append(h_iqn)

            if h_iqn and t_iqn:
                map_info = {'t_iqn': t_iqn, 'h_iqn': h_iqn}
                mpath_dict['map_info'].append(map_info)

            if iface_mac and iface_mac not in mpath_dict['iface_macs']:
                mpath_dict['iface_macs'].append(iface_mac)

            if iface_name and h_iqn not in mpath_dict['iface_names']:
                mpath_dict['iface_names'].append(iface_name)

            if target_ip and target_ip not in mpath_dict['target_ips']:
                mpath_dict['target_ips'].append(target_ip)

            if persist_ip and persist_ip not in mpath_dict['persist_ips']:
                mpath_dict['persist_ips'].append(persist_ip)

            mpath_dict['disk'][disk_info_dict['scsi_disk']] = disk_info_dict
            mpath_dict['path_group'][pg_id]['disk'][scsi_id] = disk_info_dict
            all_mpath_dict['by_scsi_id'][scsi_id] = disk_info_dict
            # print("\n\nDEBUG - Disk: query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]

            continue

        # as regex_mpath is an aggressive regex, we leave it at the last
        # one to check.
        m = re.match(regex_mpath, line)
        if m:
            if re.match(r'^\|', line):
                continue

            _mpath_name = m.group(1)
            pg_id = 0
            wwid = _mpath_name
            if m.group(2):
                wwid = m.group(2)

            dm_name = None
            if m.group(3):
                dm_name = m.group(3)

            vendor_raw = None
            vendor = vendor_raw
            if m.group(4):
                vendor_raw = m.group(4)
                vendor = re.sub('[ ]+$', '', vendor_raw)

            product_raw = None
            product = product_raw
            if m.group(5):
                product_raw = m.group(5)
                product = re.sub('[ ]+$', '', product_raw)

            mpath_dict = {
                'mpath_name': _mpath_name,
                'wwid': wwid,
                'dm_name': dm_name,
                'vendor': vendor,
                'vendor_raw': vendor_raw,
                'product': product,
                'product_raw': product_raw,
                'h_wwpns': [],
                't_wwpns': [],
                'disk': {},
                'path_group': {},
                'transport_types': [],
            }

            all_mpath_dict['by_wwid'][wwid] = mpath_dict
            all_mpath_dict['by_mpath_name'][_mpath_name] = mpath_dict
            # print("\n\nDEBUG: query all mpath [%s]" % line)
            # print all_mpath_dict["by_mpath_name"]
            continue
    if mpath_name:
        if mpath_name in list(all_mpath_dict['by_mpath_name'].keys()):
            return all_mpath_dict['by_mpath_name'][mpath_name]
        return None

    return all_mpath_dict


def mpath_name_of_wwid(wwid):  # noqa: ANN001, ANN201
    if not wwid:
        logging.error('mpath_name_of_wwid() - requires wwid parameter')
        return None

    mp_devs = multipath_query_all()
    if not mp_devs:
        return None

    if wwid in list(mp_devs['by_wwid'].keys()):
        return mp_devs['by_wwid'][wwid]['mpath_name']

    return None


def mpath_names_of_vendor(vendor):  # noqa: ANN001, ANN201
    """Given a Vendor return a list with all multipath device names with this vendor."""
    if not vendor:
        logging.error('mpath_names_of_vendor() - requires vendor parameter')
        return None

    mp_devs = multipath_query_all()
    if not mp_devs:
        return None

    return [
        mpath_info['mpath_name']
        for mpath_info in mp_devs['by_mpath_name'].values()
        if 'vendor' in mpath_info and mpath_info['vendor'] == vendor
    ]


def mpath_check_disk_status(mpath_name, scsi_disk):  # noqa: ANN001, ANN201
    """Check the online status of a specific SCSI disk from a mpath device."""
    if not mpath_name or not scsi_disk:
        logging.error('mpath_check_disk_status() - requires mpath_name and scsi_disk parameters')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'mpath_check_disk_status() - Could not get mpath info for {mpath_name}')
        return None

    if 'disk' not in list(mpath_dict.keys()):
        logging.error(f'mpath_check_disk_status() - Could not find any SCSI disk for {mpath_name}')
        return None

    for disk in list(mpath_dict['disk'].keys()):
        if scsi_disk == mpath_dict['disk'][disk]['scsi_disk']:
            return mpath_dict['disk'][disk]['online_status']

    return None


def mpath_check_disk_dm_status(mpath_name, scsi_disk):  # noqa: ANN001, ANN201
    """Check the dm status of a specific SCSI disk from a mpath device."""
    if not mpath_name or not scsi_disk:
        logging.error('mpath_check_disk_dm_status() - requires mpath_name and scsi_disk parameters')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'mpath_check_disk_dm_status() - Could not get mpath info for {mpath_name}')
        return None

    if 'disk' not in list(mpath_dict.keys()):
        logging.error(f'mpath_check_disk_dm_status() - Could not find any SCSI disk for {mpath_name}')
        return None

    for disk in list(mpath_dict['disk'].keys()):
        if scsi_disk == mpath_dict['disk'][disk]['scsi_disk']:
            return mpath_dict['disk'][disk]['dm_status']

    return None


def mpath_check_disk_path_status(mpath_name, scsi_disk):  # noqa: ANN001, ANN201
    """Check the path status of a specific SCSI disk from a mpath device."""
    if not mpath_name or not scsi_disk:
        logging.error('mpath_check_disk_path_status() - requires mpath_name and scsi_disk parameters')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'mpath_check_disk_path_status() - Could not get mpath info for {mpath_name}')
        return None

    if 'disk' not in list(mpath_dict.keys()):
        logging.error(f'mpath_check_disk_path_status() - Could not find any SCSI disk for {mpath_name}')
        return None

    for disk in list(mpath_dict['disk'].keys()):
        if scsi_disk == mpath_dict['disk'][disk]['scsi_disk']:
            return mpath_dict['disk'][disk]['path_status']

    return None


def mpath_get_active_disk(mpath_name):  # noqa: ANN001, ANN201
    """From specific mpath device get which disk is the active one
    Return
    List of active SCSI disks.
    """
    if not mpath_name:
        logging.error('mpath_get_active_disk() - requires mpath_name parameter')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'mpath_get_active_disk() - Could not get mpath info for {mpath_name}')
        return None

    if 'disk' not in list(mpath_dict.keys()):
        logging.error(f'mpath_get_active_disk() - Could not find any SCSI disk for {mpath_name}')
        return None

    active_disks = []
    for disk in list(mpath_dict['disk'].keys()):
        pg = mpath_dict['disk'][disk]['pg_id']
        if mpath_dict['path_group'][pg]['status'] == 'active':
            active_disks.append(disk)

    if active_disks:
        return active_disks

    logging.error(f'mpath_get_active_disk() - Could not find any active disk for {mpath_name}')
    return None


def get_free_mpaths(exclude_boot_device=True, exclude_lvm_device=True):  # noqa: ANN001, ANN201
    """Return a dict of free mpath devices."""
    all_mp_info = multipath_query_all()
    if not all_mp_info:
        # could not query multipath devices
        return None

    if 'by_wwid' not in list(all_mp_info.keys()):
        # mpath device was not found
        print(list(all_mp_info.keys()))
        return None

    pvs = lvm.pv_query()
    boot_dev = linux.get_boot_device(parent_device=True)
    boot_wwid = None
    # if for some reason we boot from a single disk, but this disk is part of multipath device
    # the mpath device should be skipped as well
    if boot_dev:
        boot_wwid = linux.get_device_wwid(boot_dev)

    chosen_mpaths = {}

    for mp_wwid in list(all_mp_info['by_wwid'].keys()):
        mp_info = all_mp_info['by_wwid'][mp_wwid]
        # Skip if mpath device is used for boot
        if boot_wwid == mp_info['wwid'] and exclude_boot_device:
            print(f"DEBUG: get_free_mpaths() - skip {mp_info['mpath_name']} as it is used for boot")
            continue

        # Skip if it is used by LVM
        if pvs and exclude_lvm_device:
            mp_used_by_lvm = False
            for pv in list(pvs.keys()):
                if mpath_device_2_mpath_name(pv) == mp_info['mpath_name']:
                    mp_used_by_lvm = True
                    print(f"DEBUG: get_free_mpaths() - skip {mp_info['mpath_name']} as it is used for LVM")
                    continue
            if mp_used_by_lvm:
                continue

        chosen_mpaths[mp_info['mpath_name']] = mp_info

    return chosen_mpaths


def h_wwpns_of_mpath(mpath_name):  # noqa: ANN001, ANN201
    """Return the h_wwpns of specific mpath device."""
    if not mpath_name:
        logging.error('h_wwpns_of_mpath() - requires mpath_name parameter')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'h_wwpns_of_mpath() - Could not get mpath info for {mpath_name}')
        return None

    if 'h_wwpns' in mpath_dict:
        return mpath_dict['h_wwpns']
    return None


def t_wwpns_of_mpath(mpath_name):  # noqa: ANN001, ANN201
    """Return the h_wwpns of specific mpath device."""
    if not mpath_name:
        logging.error('t_wwpns_of_mpath() - requires mpath_name parameter')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f't_wwpns_of_mpath() - Could not get mpath info for {mpath_name}')
        return None

    if 't_wwpns' in mpath_dict:
        return mpath_dict['t_wwpns']
    return None


def iface_macs_of_mpath(mpath_name):  # noqa: ANN001, ANN201
    """Return the iface_macs_of_mpath of specific mpath device."""
    if not mpath_name:
        logging.error('iface_macs_of_mpath() - requires mpath_name parameter')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'iface_macs_of_mpath() - Could not get mpath info for {mpath_name}')
        return None

    if 'iface_macs' in mpath_dict:
        return mpath_dict['iface_macs']
    return None


def transport_types_of_mpath(mpath_name):  # noqa: ANN001, ANN201
    """Return the transport_types of specific mpath device."""
    if not mpath_name:
        logging.error('transport_types_of_mpath() - requires mpath_name parameter')
        return None

    mpath_dict = multipath_query_all(mpath_name)
    if not mpath_dict:
        logging.error(f'transport_types_of_mpath() - Could not get mpath info for {mpath_name}')
        return None

    if 'transport_types' in mpath_dict:
        return mpath_dict['transport_types']
    return None


def multipath_show(mpath_name=None):  # noqa: ANN001, ANN201
    cmd = 'multipath -ll'
    if mpath_name:
        cmd += f' {mpath_name}'
    run(cmd)


def multipath_reload(mpath_name=None):  # noqa: ANN001, ANN201
    """Usage
    multipath_reload()
    Purpose
        Execute 'multipath -r'
    Parameter
        N/A
    Returns
        1
            or
        undef
    Exceptions
        N/A.
    """
    cmd = 'multipath -r'
    if mpath_name:
        cmd += f' {mpath_name}'
    return run(cmd).rc == 0


def remove_mpath(mpath_name):  # noqa: ANN001, ANN201
    """Remove specific mpath."""
    if not mpath_name:
        logging.error('remove_mpath() - requires mpath_name parameter')
        return False
    if run(f'multipath -f {mpath_name}').rc != 0:
        logging.error(f'Could not remove mpath {mpath_name}')
        return False
    return True


def flush_all():  # noqa: ANN201
    """Flush all unused multipath device maps."""
    cmd = 'multipath -F'
    return run(cmd).rc == 0


def multipath_backup_conf(bak_file):  # noqa: ANN001, ANN201
    """backup_mp_conf ()
    Usage
    backup_mp_conf(bak_file)
    Purpose
    Check if bak_file exists, if not, copy current to it.
    Parameter
    bak_file       # like "/etc/multipath.conf.bak"
    Returns
    true
        or
    False           # file exists or source file not exists;
    Exceptions
    N/A.
    """
    if not Path(MULTIPATH_CONF_PATH).is_file():
        logging.error(f'{MULTIPATH_CONF_PATH} does not exist')
        return False

    if Path(bak_file).is_file():
        logging.error(f'mpath backup file {bak_file} already exists')
        return False

    logging.info(f'Backing up {MULTIPATH_CONF_PATH} to {bak_file}')
    cmd = f'cp -f {MULTIPATH_CONF_PATH} {bak_file}'
    ret, output = run_ret_out(cmd, return_output=True)
    if ret != 0:
        logging.error(f'Could not backup {MULTIPATH_CONF_PATH}')
        print(output)
        return False

    return True


def multipath_restore_conf(bak_file):  # noqa: ANN001, ANN201
    """multipath_restore_conf ()
    Usage
    multipath_restore_conf(bak_file)
    Purpose
    Check if bak_file exists, if so, copy it to '/etc/multipath.conf'
    and reload mpath conf.
    Parameter
    bak_file       # like "/etc/multipath.conf.bak"
    Returns
    True
        or
    False           # file exists or source file not exists;
    Exceptions
    N/A.
    """
    if not Path(bak_file).is_file():
        logging.error(f'{bak_file} does not exist')
        return False

    logging.info(f'Restoring multipath configuration from {bak_file}')
    cmd = f'cp -f {bak_file} {MULTIPATH_CONF_PATH}'
    ret, output = run_ret_out(cmd, return_output=True)
    if ret != 0:
        logging.error(f'Could not restore backup from {bak_file}')
        print(output)
        return False

    multipath_reload_conf()
    return True


def multipath_reload_conf():  # noqa: ANN201
    """Usage
    multipath_reload_conf()
    Purpose
        Execute "multipathd -k'reconfig'" to load configuration.
        After that execute 'multipath -r'
    Parameter
        N/A
    Returns
        1
            or
        undef
    Exceptions
        N/A.
    """
    cmd = "multipathd -k'reconfig'"
    ret = run(cmd).rc

    multipath_reload()
    return ret == 0


def multipath_setup_blacklist():  # noqa: ANN201
    """multipath_setup_blacklist ()
    Usage
    multipath_setup_blacklist()
    Purpose
    Add 'wwid .*' into blacklist and all exists mpath wwid to
    'blacklist_exceptions'. This will prevent mpath take over newly
    created LUN. This function DO NOT back up configuration, use
    backup_mp_conf() in stead.
    Parameter
    N/A
    Returns
    1
        or
    undef
    Exceptions
    N/A.
    """
    all_mp_info_dict = multipath_query_all()
    if not all_mp_info_dict:
        return False
    current_wwids = list(all_mp_info_dict['by_wwid'].keys())
    if not current_wwids:
        return False

    if not mpath_conf_set('/blacklist/wwid', '.*'):
        return False

    for wwid in current_wwids:
        if not mpath_conf_set('/blacklist_exceptions/wwid[last()+1]', wwid):
            return False

    logging.info('Reloading updated multipath configuration')
    multipath_reload_conf()
    return True


def mpath_conf_remove(path, value):  # noqa: ANN001, ANN201
    """Remove parameter from multipath config using augeas.
    For non-unique paths, use return of mpath_conf_match as path
    For valid options use 'man multipath.conf'.

    Args:
      path: eg. "/blacklist/wwid"
      value: eg. "<device wwid>"

    Returns:
      boolean

    Raises:
      IOError: Augeas save fails. Check if multipath.conf changes are valid.
    """
    matched_path = mpath_conf_match(path, value)

    if matched_path:
        out = run(f'augtool -s rm "{matched_path}"').stdout.rstrip()
        if 'Saved 1 file(s)' not in out:
            logging.error(f'unable to set {path} to {value}')
            return False

    return True


def mpath_conf_match(path, value):  # noqa: ANN001, ANN201
    """Checks if parameter is set in multipath.conf using augeas
    Use path expressions to get non-unique paths: https://github.com/hercules-team/augeas/wiki/Path-expressions
    e.g. path="/devices/device[*]/vendor" value="LIO-ORG"
    Successfully matches even if "end of the path" is not unique. e.g. path="/blacklist_exceptions/wwid" value="$wwid".

    Args:
      path: eg. "/blacklist/wwid"
      value: eg. "<device wwid>"

    Returns:
      matched path or None
    """
    if not linux.install_package('augeas'):
        logging.error('Could not install augeas')
        return None

    full_path = path if path.startswith(aug_conf_path) else aug_conf_path + path

    # successfully matches also when end of path is not unique - path[*] value, but not path[*]/path value
    out = run(f'augtool match "{full_path}" "{value}"').stdout.rstrip()

    # augtool prints path when matched, return codes seems useless
    if aug_conf_path in out:
        # returning path, as it can be useful when modifying non-unique paths
        return out
    return None


def mpath_conf_set(path, value):  # noqa: ANN001, ANN201
    """Change multipath.conf parameters using augeas.
    To append to non-unique paths, use [last()+1].
    eg. path="/devices/device[last()+1]/vendor" value="LIO-ORG"
    For valid options use 'man multipath.conf'.

    Args:
      path: eg. "/defaults/path_selector" or "/files/etc/multipath.conf/defaults/path_selector"
      value: eg. "round-robin"

    Returns:
      boolean

    Raises:
      IOError: Augeas save fails. Check if multipath.conf changes are valid.
    """
    full_path = path if path.startswith(aug_conf_path) else aug_conf_path + path

    # Need to check if not already exists to avoid duplicates
    path_to_match = re.sub(r'\[[^]]*]', '[.]', path)  # in case path expressions are being used
    matched_path = mpath_conf_match(path_to_match, value)

    if not matched_path:
        if not linux.is_installed('augeas'):
            logging.error('Could not install augeas')
            return False
        out = run(f'augtool -s set "{full_path}" "{value}"').stdout
        if 'Saved 1 file(s)' not in out:
            logging.error(f'unable to set {path} to {value}. Try')
            return False

    return True


def mp_query_conf(config_str):  # noqa: ANN001, ANN201
    """Parse string containing multipath config to a dict."""
    regex_option = r'^[ \t]*'
    regex_option += r'([^\ #=\t]+)'
    regex_option += r'[\ \t]+'
    regex_option += r"(?:'|\"){0,1}"
    regex_option += r"([^'\"]+)"
    regex_option += r"(?:'|\"){0,1}"
    regex_option += r'(?:\#.*){0,1}'  # we remove '|"

    regex_section = r'[ \t]*([a-z_]+)[ \t]*\{'
    if not config_str:
        return None

    config_dict = {}

    current_section = None
    section_name = None
    for line in config_str.split('\n'):
        m = re.match(regex_section, line)
        if m:
            key = m.group(1)
            if key == 'device':
                if not section_name:
                    continue
                if 'devs' not in list(config_dict[section_name].keys()):
                    config_dict[section_name]['devs'] = []
                # We are in a subsection, need to update current_section
                tmp_dict = {}
                config_dict[section_name]['devs'].append(tmp_dict)
                # poiting current_section to last item in the list
                current_section = config_dict[section_name]['devs'][-1]
                continue

            if key == 'multipath':
                if not section_name:
                    continue
                if 'mpaths' not in list(config_dict[section_name].keys()):
                    config_dict[section_name]['mpaths'] = []
                # We are in a subsection, need to update current_section
                tmp_dict = {}
                config_dict[section_name]['mpaths'].append(tmp_dict)
                # pointing current_section to last item in the list
                current_section = config_dict[section_name]['mpaths'][-1]
                continue

            if key not in config_dict:
                config_dict[key] = {}
            current_section = config_dict[key]
            section_name = key
            continue
        m = re.match(regex_option, line)
        if m:
            key = m.group(1)
            value = m.group(2)
            if current_section is None:
                continue
            if key == 'devnode':
                if 'devnodes' not in list(current_section.keys()):
                    current_section['devnodes'] = []
                current_section['devnodes'].append(value)
                continue

            match_section = re.match('^blacklist', section_name)
            if key == 'wwid' and match_section:
                if 'wwids' not in list(current_section.keys()):
                    current_section['wwids'] = []
                current_section['wwids'].append(value)
                continue

            current_section[key] = value
            continue

    return config_dict


def mp_query_saved_conf():  # noqa: ANN201
    """Usage
        mp_query_saved_conf()
    Purpose
        Load multipath config file and return it as a dict
    Parameter
        N/A
    Returns
        mp_conf_dict.
    """
    if not Path(MULTIPATH_CONF_PATH).is_file():
        logging.error(f'{MULTIPATH_CONF_PATH} does not exist')
        return None

    cfg_text = _load_config(MULTIPATH_CONF_PATH)
    if not cfg_text:
        return None

    return mp_query_conf(cfg_text)


def _load_config(config_file):  # noqa: ANN001, ANN202
    """Parse multipath config file to dict."""
    with Path(config_file).open() as f:
        return f.read()


def _save_config(config_dict, config_file=MULTIPATH_CONF_PATH):  # noqa: ANN001, ANN202
    """Convert multipath config dict to string and save to file."""
    config_str = ''
    if 'defaults' in list(config_dict.keys()):
        config_str += 'defaults {\n'
        for key in list(config_dict['defaults'].keys()):
            config_str += f"\t{key} {config_dict['defaults'][key]}\n"
        config_str += '}\n'

    blacklist_sections = ['blacklist', 'blacklist_exceptions']
    for b_section in blacklist_sections:
        if b_section in list(config_dict.keys()):
            config_str += '%s {\n' % b_section  # noqa: UP031

            if 'devnodes' in list(config_dict[b_section].keys()):
                for node in config_dict[b_section]['devnodes']:
                    config_str += f'\tdevnode "{node}"\n'

            if 'wwids' in list(config_dict[b_section].keys()):
                for wwid in config_dict[b_section]['wwids']:
                    config_str += f'\twwid "{wwid}"\n'

            if 'devs' in list(config_dict[b_section].keys()):
                for device in config_dict[b_section]['devs']:
                    config_str += '\tdevice {\n'
                    for key in list(device.keys()):
                        config_str += f'\t\t{key} {device[key]}\n'
                    config_str += '\t}\n'

            config_str += '}\n'

    if 'devices' in list(config_dict.keys()):
        config_str += 'devices {\n'
        for vendor in list(config_dict['devices'].keys()):
            for product in config_dict['devices'][vendor]:
                config_str += '\tdevice {\n'
                for name in list(product.keys()):
                    config_str += f'\t\t{name} {product[name]}\n'
                config_str += '\t}\n'
        config_str += '}\n'

    if 'multipaths' in list(config_dict.keys()):
        config_str += 'multipaths {\n'
        for key in list(config_dict['multipaths'].keys()):
            config_str += '\tmultipath {\n'
            for wwid in config_dict['multipaths'][key]:
                config_str += f'\t\t{key} {wwid}\n'
            config_str += '}\n'
        config_str += '}\n'

    with Path(config_file).open('w') as f:
        f.write(config_str)

    return True


def mpath_device_2_mpath_name(mpath_device):  # noqa: ANN001, ANN201
    """Convert a specific multipath device to mpath_name
    E.g. /dev/mapper/mpathap1 => mpatha.
    """
    multipath_dev_regex = r'/dev/mapper\/(.*)'
    m = re.match(multipath_dev_regex, mpath_device)
    if m:
        # need to remove partition information
        # Multipath names has changed on RHEL7 and if a device name ends in letter the
        # partition number is just append to the device number, if it ends in digit
        # it appends 'p' before the partition number
        # So we can have device partitions as below...
        # device_name = "mapper/360a98000572d5765636f69746f6a4f6a1"
        # device_name = "mapper/360a98000572d5765636f69746f6a4f61p1"
        device_name = m.group(1)
        m = re.match(r'(.*)p?\d', device_name)
        if not m:
            # does not seem to be a valid mpath device
            return None
        device_name = m.group(1)
        # remove trailing p if it exists
        return re.sub(r'(\S+)p$', r'\1', device_name)
    return None
