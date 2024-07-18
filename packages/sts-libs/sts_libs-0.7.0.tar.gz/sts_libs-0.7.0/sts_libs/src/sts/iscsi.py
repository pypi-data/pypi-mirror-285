"""iscsi.py: Module with methods for iSCSI initiator."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal, TypedDict

from sts import linux, mp, net, scsi
from sts.utils.cmdline import run

if TYPE_CHECKING:
    from testinfra.backend.base import CommandResult

PACKAGE_NAME = 'iscsi-initiator-utils'
CLI_NAME = 'iscsiadm'
ISCSID_SERVICE_NAME = 'iscsid'
ISCSIUIO_SERVICE_NAME = 'iscsiuio'
DATABASE_ROOT = '/var/lib/iscsi'
ISCSID_CONF = '/etc/iscsi/iscsid.conf'


class IscsiAdm:
    """Class for `iscsiadm` cli tool (iscsi-initiator-utils)."""

    def __init__(
        self,
        debug_level: Literal[0, 1, 2, 3, 4, 5, 6, 7, 8] = 0,
        disable_check: bool = False,
    ) -> None:
        """Args:
        debug_level: print iscsiadm debug info (0-8)
        disable_check: disable argument validation.
        """
        self.disable_check = disable_check
        self.debug_level = debug_level

        if not linux.install_package(PACKAGE_NAME):
            logging.critical(f'Could not install {PACKAGE_NAME}')

    # available modes and respective short options available as per iscsiadm.c
    MODES: ClassVar[dict[str, str]] = {
        'discovery': 'DSIPdntplov',
        'discoverydb': 'DSIPdntplov',
        'node': 'RsPIdlSonvupTULW',
        'session': 'PiRdrusonuSv',
        'host': 'CHdPotnvxA',
        'iface': 'HIdnvPoCabci',
        'fw': 'dlWnv',
    }

    OPTIONS: ClassVar[dict[str, str]] = {
        'p': 'portal',
        'T': 'targetname',
        'I': 'interface',
        'o': 'op',
        't': 'type',
        'n': 'name',
        'v': 'value',
        'H': 'host',
        'r': 'sid',
        'R': 'rescan',
        'P': 'print',
        'D': 'discover',
        'l': 'login',
        'L': 'loginall',
        'u': 'logout',
        'U': 'logoutall',
        's': 'stats',
        'k': 'killiscsid',
        'd': 'debug',
        'S': 'show',
        'V': 'version',
        'h': 'help',
        'C': 'submode',
        'a': 'ip',
        'b': 'packetsize',
        'c': 'count',
        'i': 'interval',
        'x': 'index',
        'A': 'portal_type',
        'W': 'no_wait',
    }

    def validate_mode(self, mode: str) -> None:
        """Checks if mode is valid iscsiadm mode.

        Args:
          mode: Example: "discovery"
        """
        if mode not in self.MODES:
            err_msg = f'Invalid {CLI_NAME} mode: {mode}'
            raise ValueError(err_msg)

    def validate_arguments(self, mode: str, arguments: dict[str, str] | dict[str, str | None]) -> None:
        available_options: list[str] = self.get_short_options_list(mode) + self.get_long_options_list(mode)
        for key in arguments:
            key_to_check = key.strip('-')
            if key_to_check not in available_options:
                err_msg = f'Invalid {CLI_NAME} argument: {key}'
                raise ValueError(err_msg)

    def get_short_options_list(self, mode: str) -> list[str]:
        if mode not in self.MODES:
            raise ValueError
        return [*self.MODES[mode]]

    def get_long_options_list(self, mode: str) -> list[str]:
        if mode not in self.MODES:
            raise ValueError
        return [self.OPTIONS[short_option] for short_option in self.get_short_options_list(mode)]

    def available_options(self, mode: str) -> list[str]:
        return self.get_short_options_list(mode) + self.get_long_options_list(mode)

    def _run(
        self,
        mode: str = '',
        arguments: dict[str, str] | dict[str, str | None] | None = None,
    ) -> CommandResult:
        if mode is not None:
            self.validate_mode(mode)
        if arguments is not None and not self.disable_check:
            self.validate_arguments(mode, arguments)

        command_list: list[str] = [CLI_NAME, '--mode', mode]
        if arguments is not None:
            command_list += [k if v is None else f'{k} {v}' for k, v in arguments.items()]
        if self.debug_level:
            command_list = [*command_list, '--debug', str(self.debug_level)]
        command: str = ' '.join(command_list)
        return run(command)

    def iface(
        self,
        op: str,
        iface: str,
        name: str | None = None,
        value: str | None = None,
    ) -> CommandResult:
        return self._run(
            mode='iface',
            arguments={'-o': op, '-n': name, '-v': value, '-I': iface},
        )

    def iface_update(self, iface: str, name: str, value: str) -> CommandResult:
        return self.iface(op='update', iface=iface, name=f'iface.{name}', value=value)

    def iface_update_iqn(self, iface: str, iqn: str) -> CommandResult:
        return self.iface_update(iface=iface, name='initiatorname', value=iqn)

    def iface_update_ip(self, iface: str, ip: str) -> CommandResult:
        return self.iface_update(iface=iface, name='iface.ipaddress', value=ip)

    def iface_exists(self, iface: str) -> bool:
        return self.iface(op='show', iface=iface).succeeded

    def discovery(
        self,
        portal: str,
        type: str = 'st',  # noqa: A002
        interface: str | None = None,
        **kwargs: str,
    ) -> CommandResult:
        arguments = {'-t': type} | {'-p': portal} | kwargs
        if interface:
            arguments.update({'-I': interface})
        return self._run(mode='discovery', arguments=arguments)

    def node(self, **kwargs: str | str | None) -> CommandResult:
        return self._run(mode='node', arguments={**kwargs})

    def node_login(self, **kwargs: str) -> CommandResult:
        arguments = {'--login': None} | kwargs
        return self.node(**arguments)

    def node_logout(self, **kwargs: str) -> CommandResult:
        arguments = {'--logout': None} | kwargs
        return self.node(**arguments)

    def node_logoutall(self, how: Literal['all', 'manual', 'automatic', 'onboot'] = 'all') -> CommandResult:
        """Use `--logoutall all` to log out of all sessions except boot nodes."""
        arguments = {'--logoutall': how}
        return self.node(**arguments)

    def session(self, **kwargs: str | str | None) -> CommandResult:
        return self._run(mode='session', arguments={**kwargs})


class IfaceVars(TypedDict):
    hwaddress: str | None
    iscsi_ifacename: str
    net_ifacename: str | None
    transport_name: str | None
    initiatorname: str | None
    isid: str | None
    bootproto: str | None
    ipaddress: str | None
    prefix_len: str | None
    subnet_mask: str | None
    gateway: str | None
    primary_dns: str | None
    secondary_dns: str | None
    vlan_id: str | None
    vlan_priority: str | None
    vlan_state: str | None
    ipv6_linklocal: str | None
    ipv6_router: str | None
    ipv6_autocfg: str | None
    linklocal_autocfg: str | None
    router_autocfg: str | None
    state: str | None
    iface_num: str | None
    mtu: str | None
    port: str | None
    delayed_ack: str | None
    tcp_nagle: str | None
    tcp_wsf_state: str | None
    tcp_wsf: str | None
    tcp_timer_scale: str | None
    tcp_timestamp: str | None
    dhcp_dns: str | None
    dhcp_slp_da: str | None
    tos_state: str | None
    tos: str | None
    gratuitous_arp: str | None
    dhcp_alt_client_id_state: str | None
    dhcp_alt_client_id: str | None
    dhcp_req_vendor_id_state: str | None
    dhcp_vendor_id_state: str | None
    dhcp_vendor_id: str | None
    dhcp_learn_iqn: str | None
    fragmentation: str | None
    incoming_forwarding: str | None
    ttl: str | None
    gratuitous_neighbor_adv: str | None
    redirect: str | None
    ignore_icmp_echo_request: str | None
    mld: str | None
    flow_label: str | None
    traffic_class: str | None
    hop_limit: str | None
    nd_reachable_tmo: str | None
    nd_rexmit_time: str | None
    nd_stale_tmo: str | None
    dup_addr_detect_cnt: str | None
    router_adv_link_mtu: str | None
    def_task_mgmt_timeout: str | None
    header_digest: str | None
    data_digest: str | None
    immediate_data: str | None
    initial_r2t: str | None
    data_seq_inorder: str | None
    data_pdu_inorder: str | None
    erl: str | None
    max_receive_data_len: str | None
    first_burst_len: str | None
    max_outstanding_r2t: str | None
    max_burst_len: str | None
    chap_auth: str | None
    bidi_chap: str | None
    strict_login_compliance: str | None
    discovery_auth: str | None
    discovery_logout: str | None


class TargetVars(TypedDict):
    name: str | None  # iqn
    interface: str | None
    portal: str  # ip or hostname
    type: str  # discovery type


class ConfVars(TypedDict):
    initiatorname: str  # iqn.1994-05.redhat:example
    targets: list[TargetVars]
    ifaces: list[IfaceVars]


class AuthFields(TypedDict):
    tbl_idx: str | None
    authmethod: str | None
    username: str | None
    password: str | None
    password_length: str | None
    username_in: str | None
    password_in: str | None


def setup(variables: ConfVars) -> bool:
    """Configure iSCSI initiator based on env variables."""
    iscsiadm = IscsiAdm()

    if 'initiatorname' in variables:
        if not set_initiatorname(variables['initiatorname']):
            return False
        linux.service_restart(ISCSID_SERVICE_NAME)

    if 'ifaces' in variables:
        for iface in variables['ifaces']:
            ifacename = iface['iscsi_ifacename']
            if ('qedi' in ifacename or 'bnx2i' in ifacename) and not linux.is_service_running(ISCSIUIO_SERVICE_NAME):
                linux.service_enable(ISCSIUIO_SERVICE_NAME, now=True)
            if not iscsiadm.iface_exists(iface=ifacename):
                create_iscsi_iface(iface_name=ifacename)
            for n, v in iface.items():
                if n == 'iscsi_ifacename':
                    continue
                completed_process = iscsiadm.iface_update(iface=ifacename, name=n, value=str(v))
                ret = completed_process.rc
                out = completed_process.stdout.rstrip()
                if ret != 0:
                    logging.error(f'iscsi update command returned {ret}. Output: {out}')
                    return False

    if 'targets' in variables:
        for target in variables['targets']:
            if iscsiadm.discovery(**target) != 0:  # type: ignore[arg-type] # TargetVars should match discovery args TODO
                return False

    if not linux.is_service_enabled(ISCSID_SERVICE_NAME):
        linux.service_enable(ISCSID_SERVICE_NAME)
    return True


def cleanup() -> None:
    """Delete all iSCSI records."""
    iscsiadm = IscsiAdm()
    iscsiadm.node_logoutall()
    # Remove all send-targets discovery records
    run(f'rm -rf {DATABASE_ROOT}/send_targets/*')
    # Remove node directories except those with 'boot' in their name
    run(rf'find {DATABASE_ROOT}/nodes/* -maxdepth 0 -type d ! -name *boot* -exec rm -r {{}} \;')


@dataclass
class Session:
    driver: str
    sid: str
    ip: str
    port: str
    target_name: str

    def get_data(self) -> dict[str, str]:
        """Returns parsed 'session -r sid' output."""
        data = {}
        lines = run(f'iscsiadm -m session -r {self.sid} -S').stdout.split('\n')
        lines = [line for line in lines if line and not line.startswith('#')]
        for line in lines:
            key_val = line.split(' = ')
            data[key_val[0]] = key_val[1]
        return data

    def get_data_p2(self) -> dict[str, str]:
        """Returns parsed session printlevel 2 info."""
        data = {}
        lines = run(f'iscsiadm -m session -r {self.sid} -S -P 2').stdout.replace('\t', '').split('\n')
        lines = [line for line in lines if line and ': ' in line]
        for line in lines:
            key_val = line.split(': ')
            data[key_val[0]] = key_val[1]
        return data

    @dataclass
    class SessionDisk:
        name: str
        state: str
        scsi_n: str
        channel: str
        id: str
        lun: str

        def is_running(self) -> bool:
            return self.state == 'running'

    def get_disks(self) -> list[SessionDisk | None]:
        lines = run(f'iscsiadm -m session -r {self.sid} -P3').stdout
        if 'Attached scsi disk' not in lines:
            return []
        lines = lines.split('\n\t\tscsi')[1:]
        disks: list = []
        for line in lines:
            data = line.split('\t')
            scsi_info = data[0].split()  # eg. ['2', 'Channel', '00', 'Id', '0', 'Lun:', '0']
            disks.append(
                self.SessionDisk(
                    name=data[3].removeprefix('Attached scsi disk '),
                    state=data[5].removeprefix('State: ').rstrip(),
                    channel=scsi_info[2],
                    id=scsi_info[4],
                    lun=scsi_info[6],
                    scsi_n=scsi_info[0],
                ),
            )
        return disks


def get_sessions() -> list[Session] | None:
    cr = run('iscsiadm -m session')
    if not cr.stdout:
        return None

    def parse_session(session: str) -> Session:
        data = session.split(' ')

        return Session(
            driver=data[0][:-1],
            sid=data[1][1:-1],
            ip=data[2].split(':')[0],
            port=data[2].split(':')[1][:-2],
            target_name=data[3],
        )

    sessions = cr.stdout.split('\n')
    return [parse_session(s) for s in sessions if s]


def get_session_by_target(target_wwn: str) -> Session | None:
    """Get single Session object with matching target iqn."""
    sessions = get_sessions()
    if not sessions:
        return None
    for s in sessions:
        if s.target_name == target_wwn:
            return s
    logging.warning('No matching session found')
    return None


def discovery_login(iface_name, portal, iqn, iface_ip=None, subnet_mask=None, gateway=None) -> bool:  # noqa: ANN001
    if not iface_name or not portal or not iqn:
        logging.error('auto_conf() - Missing iface_name, portal or iqn')
        return False

    if iface_ip and not iface_set_ip(iface_name, iface_ip, subnet_mask, gateway):
        logging.error(f'auto_conf() - Could not set IP for {iface_name}')
        return False

    logging.info(f'IQN will be set to {iqn}')

    if not iface_set_iqn(iqn, iface_name):
        logging.error(f'auto_conf() - Could not set {iqn} to iface {iface_name}')
        return False

    if not discovery_st(portal, ifaces=iface_name, disc_db=True):
        logging.error(f'auto_conf() - Could not discover any target on {portal} using iface {iface_name}')
        return False

    if not node_login():
        logging.error('auto_conf() - Could not login to new discovered portal')
        return False
    logging.info(f'Iface {iface_name} logged in successfully to {portal}')

    return True


# used to match regex for each session information that we support
supported_discovery_info = {
    'address': r'.*DiscoveryAddress: (\S+)',
    'target': r'.*Target: (\S+)',
    'portal': r'.*Portal: (\S+):(\S+),(\S+)',
    'iface': r'.*Iface Name: (\S+)',
}

# used to match regex for each session information that we support
supported_session_info = {
    't_iqn': r'.*Target: (\S+)',
    'h_iqn': r'.*Iface Initiatorname: (\S+)',
    'iface': r'.*Iface Name: (\S+)',
    'transport': r'.*Iface Transport: (\S+)',
    'iface_ip': r'.*Iface IPaddress: (\S+)',
    'mac': r'.*Iface HWaddress: (\S+)',
    'sid': r'.*SID: (\S+)',
    'host': r'.*Host Number: (\S+).*State: (\S+)',  # e.g. Host Number: 6	State: running
    'disks': r'.*Attached scsi disk (\S+).*State: (\S+)',
    # eg. Attached scsi disk sdb		State: running
    'target_ip': r'.*Current Portal: (\S+):[0-9]+,',
    'persist_ip': r'.*Persistent Portal: (\S+):[0-9]+,',
    # negotiated parameters
    'header_digest': r'.*HeaderDigest: (\S+)',
    'data_digest': r'.*DataDigest: (\S+)',
    'max_recv': r'.*MaxRecvDataSegmentLength: (\S+)',
    'max_xmit': r'.*MaxXmitDataSegmentLength: (\S+)',
    'first_burst': r'.*FirstBurstLength: (\S+)',
    'max_burst': r'.*MaxBurstLength: (\S+)',
    'immediate_data': r'.*ImmediateData: (\S+)',
    'initial_r2t': r'.*InitialR2T: (\S+)',
    'max_outst_r2t': r'.*MaxOutstandingR2T: (\S+)',
}

host_path = '/sys/class/iscsi_host/'


def is_iqn(iqn):  # noqa: ANN001, ANN201
    return bool(re.match('^iqn\\.', iqn))


def install():  # noqa: ANN201
    """Install iscsiadm tool
    The arguments are:
    None
    Returns:
    True: If iscsiadm is installed correctly
    False: If some problem happened.
    """
    if not linux.install_package(PACKAGE_NAME):
        logging.error(f'Could not install {PACKAGE_NAME}')
        return False

    return True


def get_iscsi_hosts() -> list[str]:
    return run(f'ls {host_path}').stdout.rstrip().splitlines()


def get_iscsi_host_numbers() -> list[str]:
    hosts = get_iscsi_hosts()
    return [h.lstrip('host') for h in hosts]


# iSCSI discovery ###
def query_discovery() -> dict:
    """Query all iSCSI targets."""
    cp = run('iscsiadm -m discovery -P1')
    if cp.failed:
        # If no target is found iscsiadm returns error code
        return {}
    lines = cp.stdout.rstrip().splitlines()

    supported_discovery_modes = ['SENDTARGETS', 'iSNS', 'STATIC', 'FIRMWARE']
    supported_mode_type = {'SENDTARGETS': 'sendtargets', 'iSNS': 'isns'}

    discovery_info_dict = {}  # type: ignore  # noqa: PGH003
    discovery_address = None
    disc_mode = None
    target_name = None

    for line in lines:
        # print "(%s)" % line
        # Check if it is discovery mode information
        m = re.match('(^.*):', line)
        if m and m.group(1) in supported_discovery_modes:
            disc_mode = m.group(1)
            # We will use DiscoveryAddress as key
            discovery_info_dict[disc_mode] = {}
            discovery_address = None
            continue

        # We will use TargetAddress as key for the target dictionary
        m = re.match(supported_discovery_info['address'], line)
        if m:
            discovery_address = m.group(1)
            if discovery_address not in list(discovery_info_dict[disc_mode].keys()):
                discovery_info_dict[disc_mode][discovery_address] = {}
            disc_addr_regex = re.compile(r'(\S+),(\S+)')
            d = disc_addr_regex.match(discovery_address)
            if d:
                discovery_info_dict[disc_mode][discovery_address]['disc_addr'] = d.group(1)
                discovery_info_dict[disc_mode][discovery_address]['disc_port'] = d.group(2)

            if disc_mode in list(supported_mode_type.keys()):
                discovery_info_dict[disc_mode][discovery_address]['mode'] = supported_mode_type[disc_mode]
            continue

        m = re.match(supported_discovery_info['target'], line)
        if m:
            # FIRMWARE discovery might not use discovery address
            if not discovery_address:
                discovery_address = 'NotSet'
                discovery_info_dict[disc_mode][discovery_address] = {}

            target_name = m.group(1)
            if 'targets' not in list(discovery_info_dict[disc_mode][discovery_address].keys()):
                discovery_info_dict[disc_mode][discovery_address]['targets'] = {}
            discovery_info_dict[disc_mode][discovery_address]['targets'][target_name] = {}
            continue

        m = re.match(supported_discovery_info['portal'], line)
        if m:
            discovery_info_dict[disc_mode][discovery_address]['targets'][target_name]['portal'] = {}
            discovery_info_dict[disc_mode][discovery_address]['targets'][target_name]['portal']['address'] = m.group(1)
            discovery_info_dict[disc_mode][discovery_address]['targets'][target_name]['portal']['port'] = m.group(2)
            continue

        m = re.match(supported_discovery_info['iface'], line)
        if m:
            iface = m.group(1)
            if 'iface' not in list(discovery_info_dict[disc_mode][discovery_address]['targets'][target_name].keys()):
                discovery_info_dict[disc_mode][discovery_address]['targets'][target_name]['iface'] = []
            discovery_info_dict[disc_mode][discovery_address]['targets'][target_name]['iface'].append(iface)
            continue
            # print "Found %s: %s" % (key, m.group(1))

    return discovery_info_dict


def discovery_st(target, ifaces=None, disc_db=False):  # noqa: ANN001, ANN201
    """Discover iSCSI target
    The arguments are:
    target:   Address of target to be discovered
    ifaces:   iSCSI interfaces to be used, separated by space (optional)
    disc_db:  To use discoverydb instead of discovery (optional).

    Returns:
    True:     If it discovered an iSCSI target
    False:    If some problem happened.
    """
    max_retries = 5
    logging.info('Executing Discovery_ST() with these arges:')
    print(f'\tTarget: {target}')
    if ifaces:
        print(f'\tIfaces: {ifaces}')

    disc_opt = 'discovery'
    operation = None

    if disc_db:
        disc_opt = 'discoverydb -D'
        operation = 'new'

    cmd = f'iscsiadm -m {disc_opt} -p {target}'
    if operation:
        cmd += f' -o {operation}'

    if ifaces:
        if ('bnx2i' in ifaces or 'qedi' in ifaces) and linux.is_service_running(ISCSIUIO_SERVICE_NAME) != 0:
            linux.service_enable(ISCSIUIO_SERVICE_NAME, now=True)
        interfaces = ifaces.split(' ')
        for interface in interfaces:
            cmd += f' -I {interface}'
    cmd += ' -t st'
    retries = 0
    result = run(cmd)
    while result.failed and '(err 29)' in result.stderr and retries < max_retries:
        result = run(cmd)
        retries += 1
    if result.failed or retries == max_retries:
        logging.error(f'Could not discover iSCSI target. Return code: {result.rc}')
        return False
    return True


def is_target_discovered(t_iqn):  # noqa: ANN001, ANN201
    """Check if an iSCSI target is already discovered
    The arguments are:
    iSCSI Target:   iQN of iSCSI target
    Returns:
    True:     If target is discovered
    False:    If was not found.
    """
    if not t_iqn:
        logging.error('is_target_discovered() - requires target iqn as parameter')

    disc_dict = query_discovery()
    if not disc_dict:
        return False

    for disc_type in list(disc_dict.keys()):
        for disc_addr in list(disc_dict[disc_type].keys()):
            if 'targets' not in list(disc_dict[disc_type][disc_addr].keys()):
                continue
            if t_iqn in list(disc_dict[disc_type][disc_addr]['targets'].keys()):
                # Target is already discovered we do not need to do anything
                return True
    return False


def get_disc_ifaces_of_t_iqn(t_iqn):  # noqa: ANN001, ANN201
    """From given target IQN, return the interfaces that discovered it
    The arguments are:
    iSCSI Target:   iQN of iSCSI target
    Returns:
    List ifaces:     Discovered interfaces
    None:             If iface was not found.
    """
    if not t_iqn:
        logging.error('get_t_iqn_disc_ifaces() - requires target iqn')
        return None

    if not is_target_discovered(t_iqn):
        logging.error(f'get_t_iqn_disc_ifaces() - target iqn: {t_iqn} is not discovered')
        return None

    disc_dict = query_discovery()
    for disc_type in list(disc_dict.keys()):
        for disc_addr in list(disc_dict[disc_type].keys()):
            if 'targets' not in list(disc_dict[disc_type][disc_addr].keys()):
                continue
            if t_iqn in list(disc_dict[disc_type][disc_addr]['targets'].keys()) and 'iface' in list(
                disc_dict[disc_type][disc_addr]['targets'][t_iqn].keys(),
            ):
                return disc_dict[disc_type][disc_addr]['targets'][t_iqn]['iface']
    return None


def delete_discovery_target_portal(portal, port='3260', tp='st'):  # noqa: ANN001, ANN201
    """Delete discovered iSCSI target
    The arguments are:
    portal:   Address of target to be discovered
    port:     Port of iSCSI target to be deleted
    tp:       Discovery type, sendtargets, isns...

    Returns:
    True:     If deleted discovered iSCSI target
    False:    If some problem happened.
    """
    logging.info(f'Deleting target portal: {portal}')
    if net.get_ip_version(portal) == 6:
        # IF IPv6 we need to append squared brackets to the address
        portal = '[' + portal + ']'

    cmd = f'iscsiadm -m discoverydb --type {tp} --portal "{portal}:{port}" -o delete'
    if run(cmd).failed:
        logging.error('Could not delete discover iSCSI target')
        return False
    return True


def clean_up(portal='all'):  # noqa: ANN001, ANN201
    """Remove iSCSI session and discover information for specific target
    The arguments are:
    target:   Address of target to be removed
    Returns:
    True:     If iSCSI target is removed
    False:    If some problem happened.
    """
    error = 0
    # TODO: iSCSI boot clean up
    if is_iscsi_boot():
        boot_dev = linux.get_boot_device()
        if not boot_dev:
            logging.error('clean_up() - Could not determine boot device')
            return False

        boot_wwid = linux.get_device_wwid(boot_dev)
        if not boot_wwid:
            logging.error(f'clean_up() - Could not determine boot WWID for {boot_dev}')
            return False

        ses_ids = get_all_session_ids()
        if not ses_ids:
            logging.error('is_iscsi_boot() - It is iSCSI boot, but did not find any session id')
            return False

        if portal == 'all':
            # Logout from all iSCSI session, that do not have boot device
            for ses_id in ses_ids:
                iscsi_wwids = scsi_wwid_of_iscsi_session(sid=ses_id)
                if boot_wwid in iscsi_wwids:
                    logging.info(f"Can't log out of session {ses_id}, because it is used for iSCSI boot")
                else:
                    logging.info(f'Logging out of session {ses_id}')
                    session_logout(ses_id)
                    # TODO Clean up discovery info
        else:
            # TODO Logout single portal from iSCSI boot
            logging.error(f'clean_up() - Does not know how to clean up portal {portal} for iSCSI boot')
            return False

        return True

    # Not iSCSI boot
    if portal == 'all':
        # log out of all iSCSI sessions
        if get_all_session_ids():  # noqa: SIM102
            # There is at least one session
            if not node_logout():
                logging.error(f'Could not logout from {portal} iSCSI target')
                error += 1
    elif not node_logout(portal=portal):
        logging.error(f'Could not logout from {portal} iSCSI target')
        error += 1

    disc_dict = query_discovery()
    # If there is discovery information
    if disc_dict:
        # We will search for this portal on sendtargets and iSNS
        for mode in list(disc_dict.keys()):
            if mode not in {'SENDTARGETS', 'iSNS'}:
                # We only delete discover info for st and isns
                continue
            m_dict = disc_dict[mode]
            # Search for all discovered address if they match the one given
            for addr in list(m_dict.keys()):
                d_dict = m_dict[addr]

                disc_addr = d_dict['disc_addr']
                port = d_dict['disc_port']
                if portal in {disc_addr, 'all'}:  # noqa: SIM102
                    if not delete_discovery_target_portal(disc_addr, port=port, tp=d_dict['mode']):
                        logging.error(f"Deleting iSCSI target {d_dict['disc_addr']}")
                        error += 1

    return not error


# iSCSI session ###
# def query_sessions():
#    #cmd output: tcp: [21] 127.0.0.1:3260,1 iqn.2009-10.com.redhat:storage-1 (non-flash)
#    cmd = "iscsiadm -m session"
#    retcode, output = run_ret_out(cmd, return_output=True)
#    if (retcode != 0):
#        return None
#    lines = output.split("\n")
#    session_regex = re.compile("(\S+):\s[(\d+)]\s(\S+):(\S+),(\d+),(\S+)")
#    sessions_dict = {}
#    for line in lines:
#        m = session_regex.search(line)
#        if m:
#            sid = m.group(2)
#            ses_dict = {}
#            ses_dict["driver"] = m.group(1)
#            ses_dict["portal"] = m.group(3)
#            ses_dict["portal_port"] = m.group(4)
#            ses_dict["target_iqn"] = m.group(6)
#            sessions[sid] = ses_dict
#    return sessions_dict


def get_all_session_ids() -> list[str | None]:
    """Returns list of session ids."""
    session_info = run('iscsiadm -m session -P1').stdout.rstrip().splitlines()
    return [sid.removeprefix('\t\tSID: ') for sid in session_info if 'SID' in sid]


def query_iscsi_session(sid: str) -> dict:
    """Query information from a specific iSCSI session
    The arguments are:
    sid:      Session id
    Returns:
    Dict:     A dictionary with session info.
    """
    if not sid:
        logging.error('query_iscsi_session() - requires sid as argument')
        return {}

    regex_session_scsi_id = '^[ \t]+scsi([0-9]+) Channel ([0-9]+) Id ([0-9])+ Lun: ([0-9]+)$'

    lines = run(f'iscsiadm -m session -P3 -S -r {sid}').stdout.rstrip().splitlines()

    session_info_dict: dict = {}
    # dict with disk name and its status
    session_disks_dict = {}
    # store host number and status
    session_host_dict = {}
    for line in lines:
        # print "(%s)" % line

        m = re.match(regex_session_scsi_id, line)
        if m:
            host_id = m.group(1)
            target_id_only = m.group(2)
            bus_id_only = m.group(3)
            lun_id = m.group(4)
            target_id_only = re.sub('^0+(?=.)', '', target_id_only)
            scsi_id = f'{host_id}:{target_id_only}:{bus_id_only}:{lun_id}'

            if 'scsi_id_info' not in list(session_info_dict.keys()):
                session_info_dict['scsi_id_info'] = {}
            session_info_dict['scsi_id_info'][scsi_id] = {}
            session_info_dict['scsi_id_info'][scsi_id]['scsi_id'] = scsi_id

        # Could be more than one scsi disk, will add as dict
        m = re.match(supported_session_info['disks'], line)
        if m:
            disk_dict = {'status': m.group(2), 'wwid': scsi.wwid_of_disk(m.group(1))}
            # disk_dict["scsi_name"] = m.group(1)
            session_disks_dict[m.group(1)] = disk_dict
            continue

        # Could be more than one scsi disk, will add as dict
        m = re.match(supported_session_info['host'], line)
        if m:
            session_host_dict[m.group(1)] = m.group(2)
            continue
        # Generic search for keys and values
        for key in list(supported_session_info.keys()):
            m = re.match(supported_session_info[key], line)
            if not m:
                continue
            # print "Found %s: %s" % (key, m.group(1))
            session_info_dict[key] = m.group(1)
            if session_info_dict[key] == '<empty>':
                session_info_dict[key] = None
                if key == 'mac':  # noqa: SIM102
                    # Try to get based on iface IP address
                    if 'iface_ip' in list(session_info_dict.keys()):
                        nic = net.get_nic_of_ip(session_info_dict['iface_ip'])
                        if nic:
                            session_info_dict[key] = net.get_mac_of_nic(nic)
    # added info for the specific session
    session_info_dict['disks'] = session_disks_dict
    session_info_dict['host'] = session_host_dict
    return session_info_dict


def query_all_iscsi_sessions() -> dict | None:
    """First we get all iSCSI ids, later on we get the information of each session individually."""
    session_ids = get_all_session_ids()
    if not session_ids:
        return None

    iscsi_sessions = {}
    # Collecting info from each session
    for sid in session_ids:
        session_info_dict = query_iscsi_session(sid)  # type: ignore  # noqa: PGH003
        iscsi_sessions[sid] = session_info_dict

    # print iscsi_sessions
    return iscsi_sessions


def session_logout(sid=None):  # noqa: ANN001, ANN201
    run('iscsiadm -m session -u')
    cmd = 'iscsiadm -m session -u'
    if sid:
        cmd += f' -r {sid}'
    run('iscsiadm -m session -u')


def get_iscsi_session_by_scsi_id(scsi_id):  # noqa: ANN001, ANN201
    """Return the Session Dict that has the scsi_id."""
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for ses in sessions:
        if 'scsi_id_info' not in list(sessions[ses].keys()):
            continue
        if scsi_id in list(sessions[ses]['scsi_id_info'].keys()):
            return sessions[ses]
    return None


def h_iqn_of_sessions():  # noqa: ANN201
    """Usage
        h_iqn_of_sessions()
    Purpose
        Get the Host IQNs of all active iSCSI sessions
    Parameter
        None
    Returns
        List:   h_iqns
            or
        None.
    """
    h_iqns = None
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for key in list(sessions.keys()):
        info = sessions[key]
        if 'h_iqn' in list(info.keys()):
            if not h_iqns:
                h_iqns = []
            if info['h_iqn'] not in h_iqns:
                h_iqns.append(info['h_iqn'])
    return h_iqns


def t_iqn_of_sessions():  # noqa: ANN201
    """Usage
        t_iqn_of_sessions()
    Purpose
        Get the Target IQNs of all active iSCSI sessions
    Parameter
        None
    Returns
        List:   t_iqns
            or
        None.
    """
    t_iqns = None
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for key in list(sessions.keys()):
        info = sessions[key]
        if 't_iqn' in list(info.keys()):
            if not t_iqns:
                t_iqns = []
            if info['t_iqn'] not in t_iqns:
                t_iqns.append(info['t_iqn'])
    return t_iqns


def mac_of_iscsi_session():  # noqa: ANN201
    """Usage
        mac_of_iscsi_session()
    Purpose
        We only check host IQN in active iSCSI session.
    Parameter
        None
    Returns
        List:   macs
            or
        None.
    """
    macs = None
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    for key in list(sessions.keys()):
        info = sessions[key]
        if 'mac' in list(info.keys()):
            if not macs:
                macs = []
            if info['mac'] != '<empty>' and info['mac'] and info['mac'] not in macs:
                macs.append(info['mac'])
    return macs


def scsi_names_of_iscsi_session(h_iqn=None, t_iqn=None, sid=None):  # noqa: ANN001, ANN201
    """Usage
        scsi_names_of_iscsi_session();
        scsi_names_of_iscsi_session(sid=1);
        scsi_names_of_iscsi_session(h_iqn=h_iqn, t_iqn=t_iqn);
    # we should not support this method since the h_iqn for qla4xxx
    #    scsi_names_of_iscsi_session(t_iqn=t_iqn, h_iqn=h_iqn);
        scsi_names_of_iscsi_session(iface=iface,target_ip=target_ip,;
            t_iqn=t_iqn);
        scsi_names_of_iscsi_session(session_id=session_id);
    Purpose
        Query out all SCSI device names for certain iscsi session.
    Parameter
        h_iqn                  # the IQN used by the host
        t_iqn                  # the IQN used by iscsi target
        sid                    # the iSCSI session id
    Returns
        scsi_names
            or
        None.
    """
    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    if sid:
        if sid in list(sessions.keys()) and 'disks' in list(sessions[sid].keys()):
            return list(sessions[sid]['disks'].keys())
        return None

    scsi_names = None
    if not h_iqn and not t_iqn:
        for s in list(sessions.keys()):
            if 'disks' in list(sessions[s].keys()):
                if not scsi_names:
                    scsi_names = []
                scsi_names.extend(list(sessions[s]['disks'].keys()))
        return scsi_names

    if h_iqn and t_iqn:
        for s_id in list(sessions.keys()):
            if (sessions[s_id]['h_iqn'] == h_iqn and sessions[s_id]['t_iqn'] == t_iqn) and 'disks' in list(
                sessions[s_id].keys(),
            ):
                if not scsi_names:
                    scsi_names = []
                scsi_names.extend(list(sessions[s_id]['disks'].keys()))
        return scsi_names

    logging.error('scsi_names_of_iscsi_session() - Unsupported parameters given')
    return None


def scsi_wwid_of_iscsi_session(h_iqn=None, t_iqn=None, sid=None):  # noqa: ANN001, ANN201
    """Usage
        scsi_wwid_of_iscsi_session();
        scsi_wwid_of_iscsi_session(sid=1);
        scsi_wwid_of_iscsi_session(h_iqn=h_iqn, t_iqn=t_iqn);
    # we should not support this method since the h_iqn for qla4xxx
    #    scsi_wwid_of_iscsi_session(t_iqn=t_iqn, h_iqn=h_iqn);
        scsi_wwid_of_iscsi_session(iface=iface,target_ip=target_ip,;
            t_iqn=t_iqn);
        scsi_wwid_of_iscsi_session(session_id=session_id);
    Purpose
        Query out all SCSI WWIDs for certain iscsi session.
    Parameter
        h_iqn                  # the IQN used by the host
        t_iqn                  # the IQN used by iscsi target
        sid                    # the iSCSI session id
    Returns
        wwids
            or
        None.
    """
    wwids = None
    if sid:
        sid = str(sid)
        session_info = query_iscsi_session(sid)
        if not session_info:
            return None
        if 'disks' in list(session_info.keys()):
            if not wwids:
                wwids = []
            for scsi_name in list(session_info['disks'].keys()):
                wwid = session_info['disks'][scsi_name]['wwid']
                if wwid and wwid not in wwids:
                    wwids.append(wwid)
            return wwids
        return None

    sessions = query_all_iscsi_sessions()
    if not sessions:
        return None

    if not h_iqn and not t_iqn:
        for sid in list(sessions.keys()):
            if 'disks' in list(sessions[sid].keys()):
                if not wwids:
                    wwids = []
                for scsi_name in list(sessions[sid]['disks'].keys()):
                    wwid = scsi.wwid_of_disk(scsi_name)
                    if wwid and wwid not in wwids:
                        wwids.append(wwid)
        return wwids

    if h_iqn and t_iqn:
        for sid in list(sessions.keys()):
            if (sessions[sid]['h_iqn'] == h_iqn and sessions[sid]['t_iqn'] == t_iqn) and 'disks' in list(
                sessions[sid].keys(),
            ):
                if not wwids:
                    wwids = []
                for scsi_name in list(sessions[sid]['disks'].keys()):
                    wwid = scsi.wwid_of_disk(scsi_name)
                    if wwid and wwid not in wwids:
                        wwids.append(wwid)
        return wwids

    logging.error('scsi_wwid_of_iscsi_session() - Unsupported parameters given')
    return None


def is_iscsi_boot():  # noqa: ANN201
    iscsi_wwids = scsi_wwid_of_iscsi_session()
    if not iscsi_wwids:
        return False
    boot_dev = linux.get_boot_device()
    if not boot_dev:
        logging.error('is_iscsi_boot() - Could not determine boot device')
        return False

    boot_wwid = linux.get_device_wwid(boot_dev)
    if not boot_wwid:
        logging.warning(f'is_iscsi_boot() - Could not determine boot WWID for {boot_dev}')
        return False

    return boot_wwid in iscsi_wwids


# iSCSI node ###
def node_login(options=None, target=None, portal=None, udev_wait_time=15):  # noqa: ANN001, ANN201
    """Login to an iSCSI portal, or all discovered portals
    The arguments are:
    arget:    iSCSI targets to be used, separated by space (optional)
    options:   extra parameters. eg: "-T <target> -p <portal>"
    Returns:
    True:     If iSCSI node is logged in
    False:    If some problem happened.
    """
    # Going to delete discovered target information
    logging.info('Performing iSCSI login')
    cmd = 'iscsiadm -m node -l'
    if options:
        cmd += f' {options}'

    if target:
        for target_iqn in target.split():
            cmd += f' -T {target_iqn}'

    if portal:
        cmd += f' -p {portal}'

    result = run(cmd)
    if result.failed:
        logging.error('Could not login to iSCSI target')
        return False

    linux.wait_udev(udev_wait_time)
    return True


def node_logout(options=None, target=None, portal=None):  # noqa: ANN001, ANN201
    """Logout from an iSCSI node
    The arguments are:
    options:   extra parameters. eg: "-T <target> -p <portal>"
    Returns:
    True:     If iSCSI node is removed
    False:    If some problem happened.
    """
    ses_dict = query_all_iscsi_sessions()
    if not ses_dict:
        # There is no session to logout just skip
        return True
    logging.info('Performing iSCSI logout')
    cmd = 'iscsiadm -m node -u'
    if options:
        cmd += f' {options}'

    if target:
        cmd += f' -T {target}'

    if portal:
        cmd += f' -p {portal}'

    result = run(cmd)
    if result.failed:
        logging.error('Could not logout to iSCSI target')
        return False
    return True


def node_delete(options=None):  # noqa: ANN001, ANN201
    """Delete node information."""
    if not options:
        logging.error('node_delete() - requires portal and/or target parameters')
        return False

    cmd = 'iscsiadm -m node -o delete'
    if options:
        cmd += f' {options}'

    if run(cmd).failed:
        logging.error('Could not login to iSCSI target')
        return False
    return True


# iSCSI iface ###
def iface_query_all_info(iface_name=None):  # noqa: ANN001, ANN201
    """Return a dict with interface names as key with detailed information of
    interface.
    """
    ifaces = [iface_name] if iface_name else get_iscsi_iface_names()

    if not ifaces:
        return None

    all_iface_dict = {}
    iface_info_regex = re.compile(r'iface\.(\S+) = (\S+)')

    for iface in ifaces:
        cmd = f'iscsiadm -m iface -I {iface}'
        result = run(cmd)
        if result.failed:
            logging.warning('Could not login to iSCSI target')
            continue
        details = result.stdout.rstrip().splitlines()
        for info in details:
            m = iface_info_regex.match(info)
            if not m:
                continue
            if iface not in list(all_iface_dict.keys()):
                all_iface_dict[iface] = {}
            value = m.group(2)
            if value == '<empty>':
                value = None
            all_iface_dict[iface][m.group(1)] = value

    if iface_name:
        if iface_name not in list(all_iface_dict.keys()):
            return None
        return all_iface_dict[iface_name]

    return all_iface_dict


def iface_update(iface, name, value):  # noqa: ANN001, ANN201
    """Updates iSCSI interface parameter
    The arguments are:
    iface # Interface name (-I $)
    name  # Name of parameter (-n iface.$)
    value  # Value to set (-v $).

    Returns:
    True:     If value is set successfully
    False:    If some problem happened.
    """
    if not iface or not name or not value:
        logging.error('iface_update() - required parameters: iface, name, value')
        return False

    cmd = f'iscsiadm -m iface -I {iface} -o update -n iface.{name} -v {value}'
    result = run(cmd)
    if result.failed:
        logging.error('Could not login to iSCSI target')
        return False

    return True


def set_initiatorname(iqn: str) -> bool:
    initiatorname_file = '/etc/iscsi/initiatorname.iscsi'
    str_to_write = f'InitiatorName={iqn}'
    try:
        path = Path(initiatorname_file)
        if not path.is_file():
            linux.service_start(ISCSID_SERVICE_NAME)
        existing_name = path.read_text()
        if str_to_write != existing_name:
            with path.open(mode='w') as i:
                logging.info(f'Writing {iqn} to {initiatorname_file}')
                i.write(str_to_write)
            linux.service_restart(ISCSID_SERVICE_NAME)
    except Exception:
        logging.exception(f'Could not set iqn in {initiatorname_file}')
        return False
    return True


def iface_set_iqn(iqn, iface='default'):  # noqa: ANN001, ANN201
    """Set IQN in /etc/iscsi/initiatorname or for specific iface
    Return:
        True
        of
        False.
    """
    if not iqn:
        logging.error('iface_set_iqn() - requires iqn to be set')
        return False

    if iface == 'default':
        set_initiatorname(iqn=iqn)
        return True

    iscsiadm = IscsiAdm()
    return iscsiadm.iface_update(iface, name='initiatorname', value=iqn)


def iface_set_ip(iface, ip, mask=None, gw=None):  # noqa: ANN001, ANN201
    """Set IP information for specific iface
    Return:
        True
        of
        False.
    """
    if not iface or not ip:
        logging.error('iface_set_ip() - requires iface and ip parameters')
        return False

    if not iface_update(iface, 'ipaddress', ip):
        return False

    if mask and not iface_update(iface, 'subnet_mask', mask):
        return False

    return not (gw and not iface_update(iface, 'gateway', gw))


def get_iscsi_iface_names() -> list[str]:
    """Return a list with the name of all iSCSI interfaces on the host."""
    ifaces = run('iscsiadm -m iface').stdout.rstrip().splitlines()
    return [i.split(' ')[0] for i in ifaces if 'iSCSI ERROR' not in i]  # bz1997710


def set_iscsid_parameter(parameters: dict[str, str]) -> None:
    file_path = Path(ISCSID_CONF)
    if not file_path.is_file():
        msg = f'File {file_path} does not exist'
        raise OSError(msg)

    # Read the existing lines
    with file_path.open('r') as f:
        lines = f.readlines()

    # Modify the lines according to the given parameters
    for key in parameters:
        found = False
        for i, line in enumerate(lines):
            # Skip commented lines
            if line.strip().startswith('#'):
                continue

            # Parse existing keys
            if '=' in line:
                file_key, _ = (s.strip() for s in line.split('=', 1))
                if file_key == key:
                    lines[i] = f'{key} = {parameters[key]}\n'
                    found = True
                    break

        # If the key wasn't found in the file, add it
        if not found:
            lines.append(f'{key} = {parameters[key]}\n')

    # Write the modified lines back to the file
    with file_path.open('w') as f:
        f.writelines(lines)


def remove_iscsid_parameter(parameters: list[str]) -> None:
    file_path = Path(ISCSID_CONF)
    if not file_path.is_file():
        msg = f'File {file_path} does not exist'
        raise OSError(msg)

    # Read the existing lines
    with file_path.open('r') as f:
        lines = f.readlines()

    # Modify the lines according to the given parameters
    lines = [
        line
        for line in lines
        if not any(p in line.split('=')[0].strip() for p in parameters) or line.strip().startswith('#')
    ]

    # Write the modified lines back to the file
    with file_path.open('w') as f:
        f.writelines(lines)


def set_chap(target_user, target_pass, initiator_user=None, initiator_pass=None):  # noqa: ANN001, ANN201
    """Set CHAP authentication."""
    if not target_user or not target_pass:
        logging.error('set_chap() - requires username and password')
        return False

    parameters = {
        'node.session.auth.authmethod': 'CHAP',
        'node.session.auth.username': target_user,
        'node.session.auth.password': target_pass,
        'discovery.sendtargets.auth.authmethod': 'CHAP',  # NetApp array requires discovery authentication
        'discovery.sendtargets.auth.username': target_user,
        'discovery.sendtargets.auth.password': target_pass,
    }

    if initiator_user and initiator_pass:
        logging.info('Setting mutual two-way CHAP authentication')
        parameters['node.session.auth.username_in'] = initiator_user
        parameters['node.session.auth.password_in'] = initiator_pass
        parameters['discovery.sendtargets.auth.username_in'] = initiator_user
        parameters['discovery.sendtargets.auth.password_in'] = initiator_pass

    if not set_iscsid_parameter(parameters):
        logging.error('Unable to set CHAP authentication')
        return False

    if not linux.service_restart('iscsid'):
        logging.error('Unable to restart iscsid service')
        return False

    logging.info('CHAP authentication enabled')
    return True


def disable_chap():  # noqa: ANN201
    """Disable CHAP authentication in iscsid.conf and restarts the service."""
    # Removing all previously set auth parameters.
    parameters = [
        'node.session.auth.authmethod',
        'node.session.auth.username',
        'node.session.auth.password',
        'discovery.sendtargets.auth.authmethod',
        'discovery.sendtargets.auth.username',
        'discovery.sendtargets.auth.password',
        'node.session.auth.username_in',
        'node.session.auth.password_in',
        'discovery.sendtargets.auth.username_in',
        'discovery.sendtargets.auth.password_in',
    ]

    remove_iscsid_parameter(parameters)

    if not linux.service_restart('iscsid'):
        logging.error('Unable to restart iscsid service')
        return False

    return True


def multipath_timeo(seconds=None):  # noqa: ANN001, ANN201
    """If multipath is used for iSCSI session, session replacement
    timeout time should be decreased from default 120 seconds
    https://access.redhat.com/solutions/1171203
    multipathd service should be running when calling this
    The arguments are:
    Seconds - default 10 or number of seconds
    Returns:
    True: Successfully modified iscsid config file.
    False: There was some problem.
    """
    param = 'node.session.timeo.replacement_timeout'

    if not seconds:
        seconds = 10
    seconds = str(seconds)

    if mp.is_multipathd_running():
        logging.info('multipathd is running')
    else:
        logging.error('multipathd is not running')
        return False

    return set_iscsid_parameter({param: seconds})


def create_iscsi_iface(iface_name: str, mac: str | None = None) -> bool:
    """Create a new iSCSI interface, assign mac if specified."""
    if not iface_name:
        logging.error('create_iscsi_iface() - requires iface name as parameter')
        return False

    if iface_name in get_iscsi_iface_names():
        logging.info(f'iSCSI interface {iface_name} already exists')
        return True

    iscsiadm = IscsiAdm()
    if not iscsiadm.iface(op='new', iface=iface_name).succeeded:
        logging.error('Could not create iSCSI interface')
        return False

    if mac and not iscsiadm.iface_update(iface=iface_name, name='iface.hwaddress', value=mac).succeeded:
        logging.error('Unable to assign mac to newly created iSCSI interface')
        return False

    return True


def clone_iscsi_iface(new_iface_name, base_iface):  # noqa: ANN001, ANN201
    print(f'Cloning iface: {base_iface} to {new_iface_name}')
    if not create_iscsi_iface(new_iface_name):
        return False

    iface_info = iface_query_all_info(base_iface)
    if iface_info is None:
        logging.error(f'Could not query all info about iface: {base_iface}')
        return False

    if iface_info['hwaddress'] is not None and not iface_update(new_iface_name, 'hwaddress', iface_info['hwaddress']):
        return False

    if iface_info['transport_name'] is not None:  # noqa: SIM102
        if not iface_update(new_iface_name, 'transport_name', iface_info['transport_name']):
            return False

    if iface_info['initiatorname'] is not None:  # noqa: SIM102
        if not iface_update(new_iface_name, 'initiatorname', iface_info['initiatorname']):
            return False

    if iface_info['ipaddress'] is not None and not iface_update(new_iface_name, 'ipaddress', iface_info['ipaddress']):
        return False

    print(f'successfully cloned {base_iface}. new iface: {new_iface_name}')
    return True


def remove_iscsi_iface(iface_name):  # noqa: ANN001, ANN201
    if iface_name not in get_iscsi_iface_names():
        logging.info(f"iSCSI interface '{iface_name}' does not exist")
        return False

    cmd = f'iscsiadm -m iface -o delete -I {iface_name}'
    if run(cmd).failed:
        logging.error('Could not remove iSCSI interface')
        return False

    return True


def node_iface_info(iface_name):  # noqa: ANN001, ANN201
    cmd = f'iscsiadm -m node -I {iface_name}'
    result = run(cmd)
    if result.failed:
        logging.error('Could not get iface info!')
        return False
    return True


# iSCSI disks ###


def get_all_iscsi_disks():  # noqa: ANN201
    sessions = query_all_iscsi_sessions()
    disks = []
    if not sessions:
        # there is no iSCSI session
        return None

    # search for disks in each session
    for sid in list(sessions.keys()):
        ses = sessions[sid]
        if ses['disks']:
            # disk names are key values
            disks.extend(list(ses['disks'].keys()))

    return disks


def get_session_id_from_disk(disk_name: str):  # noqa: ANN201
    sids = query_all_iscsi_sessions()
    fail_msg = f"FAIL: Could not find disk '{disk_name}' in iscsi sessions."
    if not sids:
        print(fail_msg)
        return None
    for sid in sids:
        session = query_iscsi_session(sid)
        if not session:
            logging.error(f"Could not query iscsi session sid: '{sid}'.")
            continue
        if disk_name in session['disks']:
            return session['sid']
    print(fail_msg)
    return None
