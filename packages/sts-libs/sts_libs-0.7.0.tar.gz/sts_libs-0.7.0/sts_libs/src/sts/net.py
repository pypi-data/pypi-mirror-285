"""net.py: Module to manipulate network devices."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import ipaddress
import logging
import re
from os import listdir
from pathlib import Path

from sts import host_init, linux
from sts.utils.cmdline import exists, run, run_ret_out

__author__ = 'Bruno Goncalves'
__copyright__ = 'Copyright (c) 2016 Red Hat, Inc. All rights reserved.'

sysfs_class_net_path = '/sys/class/net'


def is_mac(mac):  # noqa: ANN001, ANN201
    """Check if given MAC is  on valid format."""
    return bool(standardize_mac(mac))


def get_nics() -> list[str]:
    """Return list of all NICs on the host."""
    host = host_init()
    return host.interface.names()


def get_eth_nics() -> list[str]:
    """Return list of interfaces with link/ether."""
    nics = get_nics()
    return [i for i in nics if get_mac_of_nic(i)]


def get_mac_of_nic(nic: str) -> str | None:
    """Given a NIC name return its MAC address."""
    cp = run(f'ip -o link show {nic}').stdout.rstrip()
    if not cp:
        return None
    ip_link = cp.split()
    try:
        mac = ip_link[ip_link.index('link/ether') + 1]
    except ValueError:
        return None

    return mac


def get_nic_of_mac(mac_address):  # noqa: ANN001, ANN201
    """Give an MAC address return the server interface name."""
    if not mac_address:
        logging.error('get_nic_of_mac() - requires mac as argument')
        return None

    mac = mac_address.lower()

    if not is_mac(mac):
        logging.error(f'get_nic_of_mac() - {mac} does not seem to be a valid MAC')
        return None

    nics = get_eth_nics()
    if not nics:
        return None

    for nic in nics:
        if mac == get_mac_of_nic(nic):
            return nic

    return None


def get_ip_addresses_of_nic(nic: str) -> list[str] | None:
    """Get IPv4 of specific network interface."""
    host = host_init()
    if not host.interface(nic).exists:
        return None

    return host.interface(nic).addresses


def get_nic_of_ip(ip: str) -> str | None:
    """Given an IP address return the NIC name using it."""
    nics = get_nics()

    for nic in nics:
        addresses = get_ip_addresses_of_nic(nic)
        if addresses and ip in addresses:
            return nic

    return None


def nic_2_driver():  # noqa: ANN201
    """Return a dictionary where nic name is the key and driver name is the value.
    Will skip sub interfaces, loop device, tun, vboxnet0.
    The arguments are:
    None
    return_output (Dict): Return a dictionary
    Returns:
    dict: Return dict containing all NICs.
    """
    nic_dict = {}
    for nic in listdir(sysfs_class_net_path):
        if (
            nic in {'.', '..', 'lo'}
            or re.match('^tun[0-9]+', nic)  # loop
            or re.match('^vboxnet[0-9]+', nic)  # TUN NIC
            or re.search(r'\.', nic)  # virtualbox NIC.
        ):  # sub-interface
            continue
        nic_dict[nic] = driver_of_nic(nic)
    # print nic_dict
    return nic_dict


# End of nic_2_driver()


def driver_of_nic(nic):  # noqa: ANN001, ANN201
    """Given a specific NIC name it returns its driver name
    Find out the driver of certain NIC via sysfs file:
        /sys/class/net/eth0/device/driver   # it's a link.
    The arguments are:
    nic: NIC name, e.g. eth0
    Returns:
    str: Driver name.
    """
    nic = phy_nic_of(nic)
    nic_file = Path(sysfs_class_net_path)
    if not (nic_file / nic).exists():
        logging.error(f'No such NIC exists: {nic}')
        print(nic_file)
        return None
    driver_file = Path(f'/sys/class/net/{nic}/device/driver')
    if not driver_file.exists():
        logging.error(f'path {driver_file} does not exist')
        return None
    # from a symlink get real path
    real_path = Path.readlink(driver_file)
    m = re.match('.*drivers/(.*)$', real_path.as_posix())
    if not m:
        logging.error(f'Could not find driver name for {nic}')
        return None
    return m.group(1)


# End of driver_of_nic()


def phy_nic_of(nic):  # noqa: ANN001, ANN201
    """Translate sub-interface of NIC 'eth0.802-fcoe' to physical NIC 'eth0'.
    The arguments are:
    nic: NIC name, e.g. eth0.802-fcoe
    Returns:
    str: phy NIC, e.g. eth0.
    """
    if not nic:
        return None
    return re.sub(r'\..+$', '', nic)


def get_pci_id_of_nic(nic):  # noqa: ANN001, ANN201
    """From a specific network interface return its PCI id."""
    regex_pci_id = linux.get_regex_pci_id()
    sys_path = Path(f'{sysfs_class_net_path}/{nic}')
    link_path = Path.readlink(sys_path).as_posix()
    # print("DEBUG: get_pci_id_of_nic - %s" % link_path)
    m = re.search(f'({regex_pci_id})/net/{nic}', link_path)
    if m:
        return m.group(1)
    return None


def get_ip_version(addr):  # noqa: ANN001, ANN201
    """Given an address, tries to check if it is IPv6 or not
    The arguments are:
    addr:     Network address
    Returns:
    4:        If it is a valid IPv4 address
    6:        If it is a valid IPv6 address
    None:     addr is not an IPv4 or IPv6 address.
    """
    try:
        ipver = ipaddress.ip_address(addr).version
    except ValueError as e:
        print(repr(e))
        return None
    else:
        return ipver


def standardize_mac(mac):  # noqa: ANN001, ANN201
    """Usage
        standardize_mac(mac)
    Purpose
        Convert all possible format mac into stand type:
            (?:[0-9A-F]{2}:){5}[0-9A-F]{2} #like: F0:DE:F1:0D:D3:C9
        Return STRING or ARRAY base on context.
    Parameter
        mac           # any format mac, like "0005.73dd.9a19"
    Returns
        mac
            or
        None.
    """
    if not mac:
        return None
    regex_standard_mac = '^(?:[0-9A-F]{2}:){5}[0-9A-F]{2}$'

    mac = mac.lower()
    mac = re.sub('^0x', '', mac)
    mac = re.sub('[^0-9A-Fa-f]', '', mac)
    # If mac given has no ':' we will add it
    if re.match('[0-9a-f]{12}', mac):
        mac_regex = re.compile('(.{2})')
        mac = mac_regex.sub(r'\g<1>:', mac)
        mac = re.sub(':$', '', mac)

    if re.match(regex_standard_mac, mac, re.IGNORECASE):
        return mac

    return None


def convert_netmask(netmask='255.255.255.0'):  # noqa: ANN001, ANN201
    """Converts subnet mask to CIDR prefix.
    netmask: common subnet mask.
    """
    try:
        cidr = ipaddress.IPv4Network((0, netmask)).prefixlen
    except ValueError as e:
        print(e)
        return None
    else:
        return cidr


def if_down(nic_or_mac):  # noqa: ANN001, ANN201
    """Bring the interface down using ifdown tool
    Parameters:
     Interface name, or it's MAC address.
    """
    if not nic_or_mac:
        logging.error('if_down() - requires nic or mac as argument')
        return None

    # ifup/ifdown scripts are not shipped by default on RHEL-8+
    if (
        not exists('ifdown')
        and linux.is_installed('NetworkManager')
        and not linux.install_package('NetworkManager-initscripts-updown')
    ):
        print('FAIL: unable to run "ifdown" command')
        return False

    nic = get_nic_of_mac(nic_or_mac) if is_mac(nic_or_mac) else nic_or_mac

    return run(f'ifdown {nic}')


def if_up(nic_or_mac):  # noqa: ANN001, ANN201
    """Bring the interface up using ifup tool
    Parameters:
     Interface name, or it's MAC address.
    """
    if not nic_or_mac:
        logging.error('if_up() - requires nic or mac as argument')
        return None

    # ifup/ifdown scripts are not shipped by default on RHEL-8+
    if (
        not exists('ifup')
        and linux.is_installed('NetworkManager')
        and not linux.install_package('NetworkManager-initscripts-updown')
    ):
        print('FAIL: unable to run "ifup" command')
        return False

    nic = get_nic_of_mac(nic_or_mac) if is_mac(nic_or_mac) else nic_or_mac

    return bool(run(f'ifup {nic}'))


def iface_up(nic_or_mac):  # noqa: ANN001, ANN201
    """Bring the interface up
    Parameters:
     Interface name, or it's MAC address.
    """
    if not nic_or_mac:
        logging.error('iface_up() - requires nic or mac as argument')
        return False

    nic = get_nic_of_mac(nic_or_mac) if is_mac(nic_or_mac) else nic_or_mac

    retcode, output = run_ret_out(f'ip link set {nic} up', return_output=True)
    if retcode != 0:
        print(output)
        return False
    return True


def iface_down(nic_or_mac):  # noqa: ANN001, ANN201
    """Bring the interface down
    Parameters:
     Interface name, or it's MAC address.
    """
    if not nic_or_mac:
        logging.error('iface_down() - requires nic or mac as argument')
        return False

    nic = get_nic_of_mac(nic_or_mac) if is_mac(nic_or_mac) else nic_or_mac
    retcode, output = run_ret_out(f'ip link set {nic} down', return_output=True)
    if retcode != 0:
        print(output)
        return False
    return True


def nm_get_conn(nic_or_mac):  # noqa: ANN001, ANN201
    """Returns NetworkManager connection UUID
    nic_or_mac: interface name or mac address.
    """
    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
        if not nic:
            logging.error("Couldn't find NIC from MAC.")
            return None
    else:
        nic = nic_or_mac

    conn = nm_get_conn_from_dev(nic)
    if not conn:
        logging.warning(f'{nic} not used in any active connection. Trying connections with same name')
        # Check connection with same name as device
        if nm_get_conn_iface(nic) == nic:
            return nm_get_conn_uuid(nic)
        return None
    conn = str(conn)
    return nm_get_conn_uuid(conn)


def nm_get_conn_iface(conn):  # noqa: ANN001, ANN201
    """Returns interface name used by NM connection
    conn: connection id or uuid.
    """
    cmd = f"nmcli -g connection.interface-name con show '{conn}'"
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"Couldn't get connection.interface-name for connection {conn}")
        print(output)
        return None
    return output


def nm_get_conn_uuid(conn):  # noqa: ANN001, ANN201
    """Returns NetworkManager connection UUID
    conn: connection id.
    """
    cmd = f"nmcli -g connection.uuid conn show '{conn}'"
    print(cmd)
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"Couldn't get NM connection uuid using {conn}")
        print(output)
        return None
    return output


def nm_get_conn_from_dev(nic):  # noqa: ANN001, ANN201
    """Returns connection id(name) using specified device.
    nic: network interface - device.
    """
    nic = str(nic)
    cmd = 'nmcli -g GENERAL.CONNECTION device show ' + nic

    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"Couldn't get NM connection using device {nic}")
        print(output)
        return None
    return output


def nm_get_dev_from_conn(conn):  # noqa: ANN001, ANN201
    """Returns a device used by specified connection
    conn: networkmanager connection id(name) or uuid.
    """
    conn = str(conn)
    cmd = f"nmcli -g connection.interface-name con show '{conn}'"

    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f"Couldn't get device used by NM connection {conn}")
        print(output)
        return None
    return output


def nm_conn_up(conn):  # noqa: ANN001, ANN201
    """Uses nmcli to activate connection
    conn: connection id(name) or uuid.
    """
    cmd = f'nmcli conn up "{conn}"'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to activate the connection: {conn}')
        return False
    print(output)
    return True


def nm_conn_down(conn):  # noqa: ANN001, ANN201
    """Uses nmcli to deactivate connection
    conn: connection id(name) or uuid.
    """
    cmd = f'nmcli conn down "{conn}"'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to deactivate the connection: {conn}')
        return False
    print(output)
    return True


def nm_conn_reload():  # noqa: ANN201
    """Runs `nmcli conn reload`. Does not support RHEL6."""
    cmd = 'nmcli conn reload'
    retcode = run(cmd).rc
    if retcode != 0:
        logging.error('Unable to reload NetworkManager')
        return False
    return True


def nm_conn_show(conn):  # noqa: ANN001, ANN201
    """Use nmcli conn to show all connection parameters. Does not support RHEL6
    conn: networkmanager connection id(name) or uuid.
    """
    if not conn:
        logging.error('No conn specified')
        return False

    cmd = f'nmcli conn show "{conn}"'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error('Unable to show conn')
        return False
    print(output)
    return True


def nm_conn_del(conn):  # noqa: ANN001, ANN201
    """Deletes NetworkManager connection using nmcli
    conn: connection id(name) or uuid.
    """
    cmd = f'nmcli conn delete {conn}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to delete the conn {conn}')
        return False
    print(output)
    return True


def nm_add_conn(name=None, nic_or_mac=None, nic_type='ethernet'):  # noqa: ANN001, ANN201
    """Use it to add new connection for devices without one
    cmd="nmcli con add type ethernet ifname enp5s0f1 con-name enp5s0f1 ".
    """
    if is_mac(nic_or_mac):
        nic = get_nic_of_mac(nic_or_mac)
        if not nic:
            logging.error("Couldn't find NIC from MAC.")
            return False
    else:
        nic = nic_or_mac

    if not name:
        name = nic

    conn = None
    if nic:
        conn = nm_get_conn_from_dev(nic)
    # Exit if there is a connection already
    if conn:
        print(f'Connection already exists. Linked to: {conn} ')
        return True

    cmd = f'nmcli conn add type {nic_type} con-name {name}'
    if nic:
        cmd += f' ifname {nic}'
    if '_' in cmd:
        cmd = cmd.replace('_', '-')
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to add con with cmd {cmd} ')
        print(output)
        return False
    nm_conn_reload()
    return True


def nm_conn_mod(conn, key, value):  # noqa: ANN001, ANN201
    """Modify one or more properties of the NetworkManager connection profile.
    nm_con_mod("enp17s0f1","connection.autoconnect", "yes")
    nmcli c modify ens2f1 connection.autoconnect yes
    Examples compared to network-scripts:
    ipv4.method manual     >> BOOTPROTO=none
    ipv4.method auto       >> BOOTPROTO=dhcp
    ipv4.address "192.168.0.10/24"   >> IPADDR=192.168.0.10
    ipv4.gateway 192.168.0.1  >> GATEWAY=192.168.0.1
    ipv4.dns 8.8.8.8   >> DNS1=8.8.8.8
    connection.autoconnect yes   >> ONBOOT=yes
    connection.id eth0   >> NAME=eth0
    connection.interface-name eth0   >> DEVICE=eth0
    802-3-ethernet.mac-address 08:00:27:4b:7a:80 >> HWADDR=08:00:27:4b:7a:80
    ipv4.never-default no   >> DEFROUTE=yes.
    """
    if not conn:
        logging.error('No connection specified')
        return False
    conn_uuid = nm_get_conn_uuid(conn)
    if not conn_uuid:
        return False
    cmd = f'nmcli conn modify {conn_uuid}'

    cmd += f' {key} {value}'

    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to modify conn {conn} with cmd {cmd} ')
        print(output)
        return False
    return True


def nm_dev_mod(dev, key, value):  # noqa: ANN001, ANN201
    """Modify one or more properties that are currently active on the device without modifying
    the connection profile. The changes have immediate effect.
    nmcli dev modify em1 ipv4.method shared
    nmcli dev modify em1 ipv4.address xx.
    """
    cmd = f'nmcli device modify {dev}'
    cmd += f' {key} {value}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to modify dev {dev} with cmd {cmd} ')
        print(output)
        return False
    return True


def nm_set_ip(conn, ip, netmask='24', activate=True):  # noqa: ANN001, ANN201
    """Uses nmcli to set static IP, netmask and activates connection.
    conn: networkmanager connection id(name) or uuid
    ip: IPv4 or IPv6.
    """
    ip = str(ip)
    ipver = get_ip_version(ip)

    if ipver == 4:
        cmd_ip = 'ipv4'
    elif ipver == 6:
        cmd_ip = 'ipv6'
    else:
        logging.error('Invalid IP format')
        return False

    if '.' in netmask:
        netmask = convert_netmask(netmask)

    cmd = f'nmcli conn modify {conn} {cmd_ip}.method manual {cmd_ip}.addr {ip}/{netmask}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Unable to set IP using nmcli: {conn} {ip}')
        print(output)
        return False

    if activate and not nm_conn_up(conn):  # noqa: SIM103
        return False
    return True
