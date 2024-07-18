"""lio.py: Module to manipulate LIO target (using targetcli)."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
import re
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Literal
from uuid import uuid4

from sts import fc, linux
from sts.utils.cmdline import check_result, run, run_ret_out

if TYPE_CHECKING:
    from collections.abc import Generator

    from testinfra.backend.base import CommandResult

regex_tgtcli_wwpn = 'naa.\\S+'

TARGETCLI = 'targetcli'


class Targetcli:
    """Use to run targetcli commands.

    rtslib-fb API would normally be used in Python, however we want to test targetcli commands.
    """

    def __init__(self, path: str) -> None:
        self.path = path

    def _run(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        cmd = f"{TARGETCLI} {self.path} {' '.join(args)}"  # type: ignore [arg-type]
        arguments = {**kwargs}
        if arguments:
            arguments_unpacked = ' '.join([f'{key}={value}' for key, value in arguments.items()])
            cmd = f'{cmd} {arguments_unpacked}'
        return run(cmd)

    def set_(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        return self._run('set', *args, **kwargs)

    def set_parameter(self, parameter: str, value: str) -> CommandResult:
        return self.set_('parameter', **{parameter: value})

    def set_attribute(self, attribute: str, value: str) -> CommandResult:
        return self.set_('attribute', **{attribute: value})

    def set_attributes(self, **kwargs: str | None) -> CommandResult:
        return self.set_('attribute', **kwargs)

    def get(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        return self._run('get', *args, **kwargs)

    def get_parameter(self, parameter: str) -> CommandResult:
        return self.get('parameter', parameter)

    def get_attribute(self, parameter: str) -> CommandResult:
        return self.get('attribute', parameter)

    def get_attributes(self) -> dict:
        output = self.get('attribute').stdout.removeprefix('ATTRIBUTE CONFIG GROUP\n======================\n')
        return dict(_.split('=', 1) for _ in output.splitlines() if '=' in _)

    def create(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        return self._run('create', *args, **kwargs)

    def delete(self, *args: str | None, **kwargs: str | None) -> CommandResult:
        return self._run('delete', *args, **kwargs)

    def ls(self) -> CommandResult:
        return self._run('ls')

    def get_path(self) -> str:
        return self.path

    @contextmanager
    def temporary_path(self, temp_path: str) -> Generator:
        pathstring = 'path'
        old_value = getattr(self, pathstring)
        setattr(self, pathstring, temp_path)
        yield
        setattr(self, pathstring, old_value)


class Backstore(Targetcli):
    def __init__(self, backstore_type: Literal['block', 'fileio', 'pscsi', 'ramdisk']) -> None:
        self.backstore_type = backstore_type
        super().__init__(path=f'/backstores/{backstore_type}/')


class BackstoreFileio(Backstore):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(backstore_type='fileio')
        self.backstores_path = self.path
        self.path = f'{self.path}{self.name}'

    def create_backstore(self, size: str, file_or_dev: str) -> CommandResult:
        arguments = {
            'name': self.name,
            'size': size,
            'file_or_dev': file_or_dev,
        }
        with self.temporary_path(self.backstores_path):
            return self.create(**arguments)

    def delete_backstore(self) -> CommandResult:
        with self.temporary_path(self.backstores_path):
            return self.delete(self.name)


class BackstoreBlock(Backstore):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(backstore_type='block')
        self.backstores_path = self.path
        self.path = f'{self.path}{self.name}'

    def create_backstore(self, dev: str) -> CommandResult:
        arguments = {
            'name': self.name,
            'dev': dev,
        }
        with self.temporary_path(self.backstores_path):
            return self.create(**arguments)

    def delete_backstore(self) -> CommandResult:
        with self.temporary_path(self.backstores_path):
            return self.delete(self.name)


class BackstoreRamdisk(Backstore):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(backstore_type='ramdisk')
        self.backstores_path = self.path
        self.path = f'{self.path}{self.name}'

    def create_backstore(self, size: str) -> CommandResult:
        arguments = {
            'name': self.name,
            'size': size,
        }
        with self.temporary_path(self.backstores_path):
            return self.create(**arguments)

    def delete_backstore(self) -> CommandResult:
        with self.temporary_path(self.backstores_path):
            return self.delete(self.name)


class Iscsi(Targetcli):
    def __init__(self, target_wwn: str, tpg: int = 1) -> None:
        self.target_wwn = target_wwn
        self.tpg = tpg
        self.iscsi_path = '/iscsi/'
        self.target_path = f'{self.iscsi_path}{target_wwn}/tpg{tpg}/'
        super().__init__(path=self.target_path)

    def create_target(self) -> CommandResult:
        with self.temporary_path(self.iscsi_path):
            return self.create(wwn=self.target_wwn)

    def delete_target(self) -> CommandResult:
        with self.temporary_path(self.iscsi_path):
            return self.delete(wwn=self.target_wwn)


class LUNs(Targetcli):
    def __init__(self, target_wwn: str, tpg: int = 1) -> None:
        super().__init__(path=f'/iscsi/{target_wwn}/tpg{tpg}/luns/')

    def create_lun(self, storage_object: str) -> CommandResult:
        return self.create(storage_object)

    def delete_lun(self, lun_number: int) -> CommandResult:
        return self.delete(str(lun_number))


class ACL(Targetcli):
    def __init__(self, target_wwn: str, initiator_wwn: str, tpg: int = 1) -> None:
        self.target_wwn = target_wwn
        self.initiator_wwn = initiator_wwn
        self.acls_path = f'/iscsi/{target_wwn}/tpg{tpg}/acls/'
        super().__init__(path=f'{self.acls_path}{initiator_wwn}')

    def create_acl(self) -> CommandResult:
        with self.temporary_path(self.acls_path):
            return self.create(wwn=self.initiator_wwn)

    def delete_acl(self) -> CommandResult:
        with self.temporary_path(self.acls_path):
            return self.delete(wwn=self.initiator_wwn)

    def set_auth(
        self,
        userid: str = '',
        password: str = '',
        mutual_userid: str = '',
        mutual_password: str = '',
    ) -> CommandResult:
        # Passing empty strings in one command does not work
        self.set_('auth', userid=userid)
        self.set_('auth', password=password)
        self.set_('auth', mutual_userid=mutual_userid)
        self.set_('auth', mutual_password=mutual_password)
        return self.set_('attribute', authentication='1')

    def disable_auth(self) -> CommandResult:
        return self.set_('attribute', authentication='0')

    def map_lun(
        self,
        mapped_lun: int,
        tpg_lun_or_backstore: str,
        write_protect: bool = False,
    ) -> CommandResult:
        return self.create(
            mapped_lun=str(mapped_lun),
            tpg_lun_or_backstore=tpg_lun_or_backstore,
            write_protect=str(write_protect),
        )


class Portal(Targetcli):
    def __init__(self, target_wwn: str, portal: str, tpg: int = 1, ip_port: int = 3260) -> None:
        self.portal = portal
        self.ip_port = str(ip_port)
        self.portals_path = f'/iscsi/{target_wwn}/tpg{tpg}/portals/'
        self.portal_path = f'{self.portals_path}{self.portal}:{self.ip_port}'
        super().__init__(path=self.portal_path)

    def create_portal(self) -> CommandResult:
        with self.temporary_path(self.portals_path):
            return self.create(ip_address=self.portal, ip_port=self.ip_port)

    def delete_portal(self) -> CommandResult:
        with self.temporary_path(self.portals_path):
            return self.delete(ip_address=self.portal, ip_port=self.ip_port)

    def enable_offload(self) -> CommandResult:
        return self._run('enable_offload=True')

    def disable_offload(self) -> CommandResult:
        return self._run('enable_offload=False')


def create_basic_iscsi_target(
    target_wwn: str = '',
    initiator_wwn: str = '',
    size: str = '1G',
    userid: str = '',
    password: str = '',
    mutual_userid: str = '',
    mutual_password: str = '',
) -> bool:
    """Create simple iSCSI target using fileio backstore."""
    # TODO: use tmt env vars for target and initiator names
    if not target_wwn:
        target_wwn = f'iqn.2023-01.com.sts:target:{uuid4().hex[-9:]}'
    if not initiator_wwn:
        try:
            # Try to set localhost initiatorname
            initiator_wwn = Path('/etc/iscsi/initiatorname.iscsi').read_text().split('=')[1]
        except FileNotFoundError:
            initiator_wwn = f'iqn.1994-05.com.redhat:{uuid4().hex[-9:]}'
        logging.info(f'Initiator iqn: "{initiator_wwn}"')
    backstore_name = initiator_wwn.split(':')[1]

    if not linux.install_package(TARGETCLI):
        return False

    backstore = BackstoreFileio(name=backstore_name)
    if not check_result(
        backstore.create_backstore(size=size, file_or_dev=f'{backstore_name}_backstore_file'),
    ):
        return False

    if not check_result(Iscsi(target_wwn=target_wwn).create_target()):
        return False

    if not check_result(LUNs(target_wwn=target_wwn).create_lun(storage_object=backstore.path)):
        return False

    if not check_result(ACL(target_wwn=target_wwn, initiator_wwn=initiator_wwn).create_acl()):
        return False

    if userid and not check_result(  # noqa: SIM103
        ACL(target_wwn=target_wwn, initiator_wwn=initiator_wwn).set_auth(
            userid=userid,
            password=password,
            mutual_userid=mutual_userid,
            mutual_password=mutual_password,
        ),
    ):
        return False
    return True


def _tgt_wwn_2_wwn(wwn):  # noqa: ANN001, ANN202
    """On RHEL-6 targetcli stores WWN on WWN format,
    but on RHEL-7 it is something like: naa.200090e2baa397ca
    The arguments are:
    None
    Returns:
    String: WWN as: 20:00:90:e2:ba:a3:97:ca.
    """
    wwn_regex = r'naa\.'
    wwn = re.sub(wwn_regex, '', wwn)
    # append ":" after every 2nd character
    wwn = re.sub(r'(\S{2})', r'\1:', wwn)
    # remove trail :
    return re.sub(':$', '', wwn)


def _wwn_2_tgt_wwn(wwn) -> str:  # noqa: ANN001
    """On RHEL-6 targetcli stores WWN on WWN format,
    but on RHEL-7 it is something like: naa.200090e2baa397ca
    The arguments are:
    WWN:      20:00:90:e2:ba:a3:97:ca
    Returns:
    String: target WWN format as: naa.200090e2baa397ca.
    """
    # remove all ':'
    wwn = re.sub(':', '', wwn)
    # append "naa." after every 2nd character
    return 'naa.' + wwn


def lio_query(show_output=False):  # noqa: ANN001, ANN201
    """Query all information from targetcli using targetcli ls
    The arguments are:
    None
    Returns:
    dict: Return a dictionary with targetcli information.
    """
    cmd = 'targetcli ls'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error('Could not run targetcli')
        return None
    lio_data = output.split('\n')

    lio_field_regex = re.compile(r'o-\s(.*?)\s.*\[(.*)\]')
    # supported types for LIO
    lio_supported_types = ('backstores', 'iscsi', 'loopback', 'tcm_fc')
    lio_supported_backstores = (
        'block',
        'fileio',
        'pscsi',
        'ramdisk',
        'user:qcow',
        'user:rbd',
        'user:zbc',
    )

    lio_dict = {}
    data_type = None

    bs_type_dict = {}

    iscsi_dict = {}
    iscsi_init_iqn = None
    iscsi_tgt_iqn = None
    current_tpg = None
    iscsi_acls_dict = {}
    iscsi_luns = []
    iscsi_portals = []
    iscsi_processing_acls = False
    iscsi_processing_luns = False
    iscsi_processing_portals = False

    tcm_fc_dict = {}
    tcm_fc_wwn = None
    tcm_fc_init_wwn = None
    tcm_fc_acls_dict = {}
    tcm_fc_luns = []
    tcm_fc_processing_acls = False
    tcm_fc_processing_luns = False

    for data in lio_data:
        m = lio_field_regex.search(data)
        if not m:
            # Just ignore entry we can't parse
            # logging.error("(%s) does not match LIO field format" % data)
            continue
        entry = m.group(1)
        entry_details = m.group(2)

        if entry == '/':
            # Skip root
            continue

        # print "INFO: LIO field %s" % entry
        if entry in lio_supported_types:
            data_type = entry
            # bs_type_dict = {}
            lio_dict[data_type] = {}
            continue
        if not data_type:
            logging.critical(f'{entry} is does not belong to any supported data type')
            continue
        # print "INFO: %s is subitem of %s" % (entry, data_type)
        # ################# PROCESSING BACKSTORES data type ####################
        if data_type == 'backstores':
            if entry in lio_supported_backstores:
                # print "INFO: Processing backstores %s subtiems" % entry
                bs_type = entry
                bs_type_dict[bs_type] = {}
                lio_dict[data_type] = bs_type_dict
                continue
            if entry in {'alua', 'default_tg_pt_gp'}:
                continue
            details_regex = re.compile(r'(.*)\s+\((\S+)\)\s+(\S+)\s+(\S+)')
            details_dict = {}
            m = details_regex.search(entry_details)
            if m:
                details_dict['file_path'] = m.group(1)
                details_dict['lun_size'] = m.group(2)
            details_dict.update(lio_get_backstore_lun_details(bs_type, entry))
            if 'wwn' in list(details_dict.keys()):
                details_dict['wwid'] = _lun_wwn2wwid(details_dict['wwn'])
            # print "BRUNO DEBUG backstore %s (%s)" % (entry, entry_details)
            bs_type_dict[bs_type][entry] = details_dict
            lio_dict[data_type] = bs_type_dict

        # ################# PROCESSING iSCSI data type ####################
        if data_type == 'iscsi':
            iqn_regex = re.compile(r'iqn\..*')
            if iqn_regex.match(entry) and not iscsi_processing_acls:
                # print "INFO: Processing tcm_fc %s subtiems" % entry
                iscsi_tgt_iqn = entry
                # The target wwn is a dict key
                iscsi_dict[iscsi_tgt_iqn] = {}
                lio_dict[data_type] = iscsi_dict
                continue
            tpg_regex = re.compile(r'(tpg\d+)')
            m = tpg_regex.match(entry)
            if m:
                # print "INFO: Processing tcm_fc %s subtiems" % entry
                current_tpg = m.group(1)
                # The target wwn is a dict key
                iscsi_dict[iscsi_tgt_iqn][current_tpg] = {}
                iscsi_acls_dict = {}
                iscsi_luns = []
                iscsi_portals = []
                lio_dict[data_type] = iscsi_dict
                continue

            if entry == 'acls':
                iscsi_dict[iscsi_tgt_iqn][current_tpg]['acls'] = {}
                iscsi_processing_acls = True
                iscsi_processing_luns = False
                iscsi_processing_portals = False
            if entry == 'luns':
                iscsi_dict[iscsi_tgt_iqn][current_tpg]['luns'] = {}
                iscsi_processing_acls = False
                iscsi_processing_luns = True
                iscsi_processing_portals = False
                continue
            if entry == 'portals':
                iscsi_dict[iscsi_tgt_iqn][current_tpg]['portals'] = {}
                iscsi_processing_acls = False
                iscsi_processing_luns = False
                iscsi_processing_portals = True
                continue
            # ################# PROCESSING ACLS ####################
            # If we are processing ACLs entry
            if iscsi_processing_acls:
                # print "BRUNO ISCSI ACL init (%s)" % entry
                if iqn_regex.match(entry):
                    iscsi_init_iqn = entry
                    iscsi_acls_dict[iscsi_init_iqn] = []
                    iscsi_dict[iscsi_tgt_iqn][current_tpg]['acls'] = iscsi_acls_dict
                    lio_dict[data_type] = iscsi_dict
                    continue
                map_regex = re.compile(r'mapped_(lun.*)$')
                # Check if it is lun mapping information
                m = map_regex.match(entry)
                if m:
                    # print "INFO: found mapped lun: %s" % m.group(1)
                    iscsi_acls_dict[iscsi_init_iqn].append(m.group(1))
                    iscsi_dict[iscsi_tgt_iqn][current_tpg]['acls'] = iscsi_acls_dict
                lio_dict[data_type] = iscsi_dict

            # ################# PROCESSING LUNs ####################
            # If we are processing LUNs entry
            if iscsi_processing_luns:
                iscsi_luns.append(entry)
                iscsi_dict[iscsi_tgt_iqn][current_tpg]['luns'] = iscsi_luns
                lio_dict[data_type] = iscsi_dict
                continue
            # ################# PROCESSING Portlas ####################
            # If we are processing Portals entry
            if iscsi_processing_portals:
                iscsi_portals.append(entry)
                iscsi_dict[iscsi_tgt_iqn][current_tpg]['portals'] = iscsi_portals
                lio_dict[data_type] = iscsi_dict
                continue

        # ################# PROCESSING TCM_FC data type ####################

        if data_type == 'tcm_fc':
            # if tcm_fc_processing_luns is true, it is because we reached the end
            # of host wwn, and now we are probably processing next host wwn
            # so do not test it on the if below
            tmp_entry = _tgt_wwn_2_wwn(entry)
            if fc.is_wwn(tmp_entry) and not tcm_fc_processing_acls:
                # print "INFO: Processing tcm_fc %s subtiems" % tmp_entry
                tcm_fc_wwn = tmp_entry
                # The target wwn is a dict key
                tcm_fc_dict[tcm_fc_wwn] = {}
                tcm_fc_processing_acls = False
                tcm_fc_processing_luns = False
                lio_dict[data_type] = tcm_fc_dict
                continue

            if entry == 'acls':
                tcm_fc_acls_dict = {}
                tcm_fc_dict[tcm_fc_wwn]['acls'] = {}
                tcm_fc_processing_acls = True
                tcm_fc_processing_luns = False
                continue
            if entry == 'luns':
                tcm_fc_luns = {}
                tcm_fc_dict[tcm_fc_wwn]['luns'] = {}
                tcm_fc_processing_luns = True
                tcm_fc_processing_acls = False
                continue
            # ################# PROCESSING ACLS ####################
            # If we are processing ACLs entry
            if tcm_fc_processing_acls:
                # It can be initiator, but be using tag instead of wwn
                # TODO: lio_is_fc_tag causes the whole query command to be slow
                # need to find a better way to do it
                tmp_entry = _tgt_wwn_2_wwn(entry)
                if fc.is_wwn(tmp_entry) or lio_is_fc_tag(tcm_fc_wwn, entry):
                    tcm_fc_init_wwn = tmp_entry
                    tcm_fc_acls_dict[tcm_fc_init_wwn] = {}
                    tcm_fc_dict[tcm_fc_wwn]['acls'] = tcm_fc_acls_dict
                    continue
                map_regex = re.compile(r'mapped_(lun.*)$')
                # Check if it is lun mapping information
                m = map_regex.match(entry)
                if m:
                    t_lun_id_regex = re.compile(r'(lun\d+)\s(\S+)/(\S+)')
                    t = t_lun_id_regex.match(entry_details)
                    if t:
                        # print "INFO: found mapped lun: %s" % m.group(1)
                        # print "INFO: entry_details %s" % entry_details
                        tcm_fc_acls_dict[tcm_fc_init_wwn][t.group(1)] = m.group(1)
                        tcm_fc_dict[tcm_fc_wwn]['acls'] = tcm_fc_acls_dict
                        # Update mapping info on backstore session
                        bs_type = t.group(2)
                        lun_name = t.group(3)
                        # print "INFO: tcm_fc acls: bs_type %s lun_name %s is mapped to %s/%s" %
                        # (bs_type, lun_name, tcm_fc_wwn, tcm_fc_init_wwn)
                        details_dict = lio_dict['backstores'][bs_type][lun_name]
                        mapping_dict = {
                            't_wwpn': tcm_fc_wwn,
                            'h_wwpn': tcm_fc_init_wwn,
                            't_lun_id': t.group(1),
                            'h_lun_id': m.group(1),
                        }
                        if 'mapping' not in list(details_dict.keys()):
                            details_dict['mapping'] = []
                        details_dict['mapping'].append(mapping_dict)

            # ################# PROCESSING LUNS that are added to target wwn ####################
            # If we are processing LUNs entry
            if tcm_fc_processing_luns:
                t_lun_info_regex = re.compile(r'(\S+)/(\S+)\s.*')
                t = t_lun_info_regex.match(entry_details)
                # print "INFO: entry_details tcm_fc luns %s" % entry_details
                if t:
                    # print "INFO: found mapped lun: %s" % m.group(1)
                    # print "INFO: entry_details %s" % entry_details
                    tcm_fc_luns[entry] = {}
                    tcm_fc_luns[entry]['bs_type'] = t.group(1)
                    tcm_fc_luns[entry]['lun_name'] = t.group(2)
                tcm_fc_dict[tcm_fc_wwn]['luns'] = tcm_fc_luns

            lio_dict[data_type] = tcm_fc_dict

    if show_output:
        print(lio_dict)
    return lio_dict


##################################################
# ############### BACKSTORES ######################
##################################################
def lio_create_backstore(bs_type=None, lun_name=None, lun_size=None, device_name=None):  # noqa: ANN001, ANN201
    """Create new backstore device
    The arguments are:
    None
    Returns:
    True: Device was created
    False: There was some problem.
    """
    created = False
    if bs_type == 'block':
        created = _lio_create_backstore_block(lun_name, device_name)

    if bs_type == 'fileio':
        created = _lio_create_backstore_fileio(lun_name, lun_size=lun_size)

    if bs_type == 'pscsi':
        created = _lio_create_backstore_pscsi(lun_name, device_name)

    if not created:
        logging.error(f'Could not create lun using ({bs_type}) on lio_create_backstore')
        return False

    if lun_name not in list(lio_get_backstores(bs_type).keys()):
        logging.error(f'It seems {lun_name} was created, but it was not')
        return False

    return True


def lio_get_backstores(bs_type=None, lio_dict=None):  # noqa: ANN001, ANN201
    """Return a dict with all backstores. If a backstore type
    is provided return a list of backstore of this type
    The arguments are:
    bs_type (Optional): Backstore type
    lio_dict (Optional): For optmization, if we already have the lio query no need to do it again
    Returns:
    List
    Dict: if there are devices and backstore type was provided
    Dict
    Dict: All backstore devices.
    """
    if not lio_dict:
        lio_dict = lio_query()

    if 'backstores' not in list(lio_dict.keys()):
        logging.error('there is not backstore defined on targetcli')
        print(lio_dict)
        return None

    if not bs_type:
        return lio_dict['backstores']

    if bs_type not in list(lio_dict['backstores'].keys()):
        return None

    return lio_dict['backstores'][bs_type]


def lio_get_backstore_details(bs_type, lun_name, lio_dict=None):  # noqa: ANN001, ANN201
    """Get the size of specific Backstore device
    Returns:
    Dic:      Detailed information about this device
    None:     If something went wrong.
    """
    bs_dict = lio_get_backstores(bs_type, lio_dict=lio_dict)
    if not bs_dict:
        return None

    if lun_name not in list(bs_dict.keys()):
        logging.error(f'{lun_name} is not defined on {bs_type}')
        lio_dict = lio_query()
        print(lio_dict)
        return None

    return bs_dict[lun_name]


def lio_get_backstore_lun_details(bs_type, lun_name):  # noqa: ANN001, ANN201
    """Get the detailed information about the lun."""
    if not bs_type or not lun_name:
        logging.error('lio_get_backstore_lun_details() - requires bs_type and lun_name')
        return None

    cmd = f'targetcli /backstores/{bs_type}/{lun_name} info'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Could not get {bs_type} details for {lun_name}')
        return None

    details = output.split('\n')
    supported_details = {
        'dev': r'^dev: (\S+)',
        'name': r'^name: (\S+)',
        'size_bytes': r'^size: (\S+)',
        'write_back': r'^write_back: (\S+)',
        'wwn': r'^wwn: (\S+)',
    }

    lun_details = {}
    for info in details:
        for sup_detail in supported_details:
            m = re.match(supported_details[sup_detail], info)
            if m:
                lun_details[sup_detail] = m.group(1)

    return lun_details


def _lun_wwn2wwid(wwn):  # noqa: ANN001, ANN202
    """From the LUN WWN is possible to get WWID."""
    wwid = wwn.replace('-', '')
    # Just the first 26 bytes are the wwid
    wwid = wwid[:25]
    return '36001405' + wwid


def lio_delete_backstore(bs_type=None, lun_name=None):  # noqa: ANN001, ANN201
    """Delete backstore device
    The arguments are:
    Backstore type
    LUN name
    Returns:
    True: Device was deleted
    False: There was some problem.
    """
    deleted = False
    if bs_type == 'block':
        deleted = _lio_delete_backstore_block(lun_name)

    if bs_type == 'fileio':
        deleted = _lio_delete_backstore_fileio(lun_name)

    if bs_type == 'pscsi':
        deleted = _lio_delete_backstore_pscsi(lun_name)

    if not deleted:
        logging.error(f'Could not delete lun using ({bs_type}) on lio_create_backstore')
        return False

    if lun_name in list(lio_get_backstores(bs_type).keys()):
        logging.error(f'It seems {lun_name} was deleted, but it was not')
        return False

    return True


# ## BLOCK ###
def _lio_create_backstore_block(lun_name, device):  # noqa: ANN001, ANN202
    if not lun_name:
        logging.error('_lio_create_backstore_block needs lun_name parameter')
        return False
    if not device:
        logging.error('_lio_create_backstore_block needs device parameter')
        return False

    cmd = f'targetcli /backstores/block create {lun_name} {device}'
    if run(cmd).rc != 0:
        logging.error(f'Could not create block {lun_name}')
        return False
    return True


def _lio_delete_backstore_block(lun_name):  # noqa: ANN001, ANN202
    cmd = f'targetcli /backstores/block delete {lun_name}'
    if run(cmd).rc != 0:
        logging.error(f'Could not delete block {lun_name}')
        return False

    return True


# ## FILEIO ###
def _lio_create_backstore_fileio(lun_name, file_name=None, lun_size=None):  # noqa: ANN001, ANN202
    if not lun_name:
        print('_lio_create_backstore_fileio() - requires lun_name parameter')
        return False

    if not file_name:
        # Set default backend file name
        file_name = f'{lun_name}.img'

    # disable spare, to force targetcli to allocate the whole file to avoid problem
    # of running out of disk space and not have enough space to store data
    cmd = f'targetcli /backstores/fileio create {lun_name} {file_name} sparse=false'
    if lun_size:
        cmd += f' {lun_size}'

    if run(cmd).rc != 0:
        logging.error(f'Could not create fileio {lun_name}')
        return False
    return True


def _lio_delete_backstore_fileio(lun_name):  # noqa: ANN001, ANN202
    file_name = _lio_get_backstore_fileio_file(lun_name)

    if run(f'targetcli /backstores/fileio delete {lun_name}').rc != 0:
        logging.error(f'Could not delete fileio {lun_name}')
        return False

    if file_name and run(f'rm -f {file_name}').rc != 0:
        logging.warning(f'could not delete file {file_name}')

    return True


def _lio_get_backstore_fileio_file(lun_name):  # noqa: ANN001, ANN202
    """Get the file used by a specific LUN."""
    cmd = f'targetcli /backstores/fileio/{lun_name} ls'
    completed_process = run(cmd)
    if completed_process.rc != 0:
        logging.error(f'Could not get fileio file {lun_name}')
        return None

    m = re.compile(r'\[(.*)\s\(').search(completed_process.stdout)
    if m:
        return m.group(1)
    return None


# ## PSCSI ###
def _lio_create_backstore_pscsi(lun_name, device, lun_size=None):  # noqa: ANN001, ANN202
    cmd = f'targetcli /backstores/pscsi create {lun_name} {device}'
    if lun_size:
        cmd += f' {lun_size}M'

    if run(cmd).rc != 0:
        logging.error(f'Could not create pscsi {lun_name}')
        return False
    return True


def _lio_delete_backstore_pscsi(lun_name):  # noqa: ANN001, ANN202
    cmd = f'targetcli /backstores/pscsi delete {lun_name}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete pscsi {lun_name}')
        return False

    return True


##################################################
# ################# iSCSI ########################
##################################################
def lio_support_iscsi_target():  # noqa: ANN201
    """Check if host supports iSCSI target
    The arguments are:
    None
    Returns:
    True: Host supports iscsi
    False: Host does not support iscsi.
    """
    lio_dict = lio_query()

    return 'iscsi' in list(lio_dict.keys())
    # Host does not support iSCSI target


# ## iSCSI target ###
def lio_iscsi_create_target(iqn):  # noqa: ANN001, ANN201
    """Add the iqn to iSCSI target
    The arguments are:
    iqn:     Target IQN
    Returns:
    True: If target is added
    False: If some problem happened.
    """
    if not lio_support_iscsi_target():
        logging.error('server does not support iSCSI target')
        return False

    cmd = f'targetcli /iscsi/ create {iqn}'

    if run(cmd).rc != 0:
        logging.error(f'Could not create iSCSI target {iqn}')
        return False

    if iqn not in lio_iscsi_get_target():
        logging.error('It seems to have added iSCSI target, but it did not')
        lio_dict = lio_query()
        print(lio_dict['iscsi'])
        return False
    # targetcli by default enable only IPv$ connection
    # we want also IPv6
    if not lio_iscsi_delete_target_portal(iqn, 'tpg1', '0.0.0.0'):
        logging.error('could not remove default iSCSI target portal')
        lio_dict = lio_query()
        print(lio_dict['iscsi'])

    if not lio_iscsi_create_target_portal(iqn, 'tpg1', '::0'):
        logging.error('could not create IPv6 iSCSI target portal')
        lio_dict = lio_query()
        print(lio_dict['iscsi'])
    return True


def lio_iscsi_get_target():  # noqa: ANN201
    """Return a list of all iSCSI targets configured
    The arguments are:
    None
    Returns:
    list: Return a list of IQNs that are configured.
    """
    lio_dict = lio_query()

    if not lio_support_iscsi_target():
        # Host does not support iSCSI target
        return None

    return list(lio_dict['iscsi'].keys())


def lio_iscsi_target_set_parameter(tgt_iqn, tpg, group, attr_name, attr_value):  # noqa: ANN001, ANN201
    """Set a parameter to an iSCSI target
    if tgt_iqn is not set, set it globally
    The arguments are:
    tgt_iqn       HOST IQN
    tpg           Target Portal Group
    group         eg: attribute, parameter, discovery_auth...
    attr_name     Attribute name
    attr_value    Attribute value
    Returns:
    True: If target is attribute is set
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi set {group} {attr_name}={attr_value}'
    if tgt_iqn:
        cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/ set {group} {attr_name}={attr_value}'

    if run(cmd).rc != 0:
        logging.error(f'Could not set iSCSI target attribute {attr_name}')
        return False
    return True


# ## iSCSI ACLS ###
def lio_iscsi_create_acl(tgt_iqn, tpg, init_iqn):  # noqa: ANN001, ANN201
    """Add an initiator IQN to target IQN
    The arguments are:
    tgt_iqn:     Host IQN
    tpg:         Target Portal Group
    init_iqn:    Initiator IQN
    Returns:
    True: If init IQN is created
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/acls create {init_iqn} add_mapped_luns=false'

    if run(cmd).rc != 0:
        logging.error(f'Could not add iSCSI initiator {init_iqn}')
        return False
    return True


def lio_iscsi_delete_acl(tgt_iqn, tpg, init_iqn):  # noqa: ANN001, ANN201
    """Remove an initiator IQN from target IQN
    The arguments are:
    tgt_iqn:     Host IQN
    tpg:         Target Portal Group
    init_iqn:    Initiator IQN
    Returns:
    True: If init iqn is removed
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/acls delete {init_iqn}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete iSCSI initiator {init_iqn}')
        return False

    return True


# ## iSCSI LUNs ###
def lio_iscsi_add_lun(tgt_iqn, tpg, bs_type, lun_name):  # noqa: ANN001, ANN201
    """Add a LUN to target IQN
    The arguments are:
    tgt_iqn:      Host IQN
    tpg:          Target Portal Group
    bs_type:      Backstore type
    lun_name:     Lun Name
    Returns:
    True: If LUN is added
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/luns create /backstores/{bs_type}/{lun_name} add_mapped_luns=false'

    if run(cmd).rc != 0:
        logging.error(f'Could not add lun to iSCSI target {tgt_iqn}')
        return False

    return True


def lio_iscsi_remove_lun(tgt_iqn, tpg, lun_id):  # noqa: ANN001, ANN201
    """Remove a LUN target IQN
    The arguments are:
    tgt_iqn:     Target IQN
    tpg:         Target Portal Group
    lun_id:      Lun id
    Returns:
    True: If LUN is removed
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/luns delete {lun_id}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete LUN from iSCSI target {tgt_iqn}')
        return False

    return True


def lio_iscsi_get_luns(tgt_iqn, tpg):  # noqa: ANN001, ANN201
    """Return a list with all LUNs added to an iSCSI target.
    The arguments are:
    None
    Returns:
    List: list of luns
    None if something went wrong.
    """
    if tgt_iqn not in lio_iscsi_get_target():
        logging.error(f'{tgt_iqn} is not defined on targetcli')
        return None

    lio_dict = lio_query()
    if 'luns' not in list(lio_dict['iscsi'][tgt_iqn].keys()):
        logging.info('target %s does not have any LUN\n')
        return None

    return lio_dict['tcm_fc'][tgt_iqn][tpg]['luns']


# ## iSCSI Portals ###
def lio_iscsi_create_target_portal(tgt_iqn, tpg, portal_ip, portal_port='3260'):  # noqa: ANN001, ANN201
    """Remove a Portal target IQN
    The arguments are:
    tgt_iqn:     Target IQN
    tpg:         Target Portal Group
    portal_ip:   IP of host allowed to connect. (0.0.0.0) any IPv4 address
    portal_port  Port to listen for connection, default 3260
    Returns:
    True: If Portal is created
    False: If some problem happened.
    """
    lio_dict = lio_query()
    if 'portals' not in list(lio_dict['iscsi'][tgt_iqn][tpg].keys()):
        logging.info(f'target {tgt_iqn} does not have support Portal')
        return False

    portal = portal_ip + ':' + portal_port
    if portal in lio_dict['iscsi'][tgt_iqn][tpg]['portals']:
        logging.info(f'portal {portal} does already exist on target {tgt_iqn}')
        return True

    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/portals create {portal_ip} {portal_port}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete Portal from iSCSI target {tgt_iqn}')
        return False

    return True


def lio_iscsi_delete_target_portal(tgt_iqn, tpg, portal_ip, portal_port='3260'):  # noqa: ANN001, ANN201
    """Remove a Portal target IQN
    The arguments are:
    tgt_iqn:     Target IQN
    tpg:         Target Portal Group
    portal_ip:   IP of host allowed to connect. (0.0.0.0) any IPv4 address
    portal_port  Port to listen for connection, default 3260
    Returns:
    True: If Portal is removed
    False: If some problem happened.
    """
    lio_dict = lio_query()
    if 'portals' not in list(lio_dict['iscsi'][tgt_iqn][tpg].keys()):
        logging.info(f'target {tgt_iqn} does not have support Portal')
        return False

    portal = portal_ip + ':' + portal_port
    if portal not in lio_dict['iscsi'][tgt_iqn][tpg]['portals']:
        logging.info(f'portal {portal} does not exist on target {tgt_iqn}')
        return True

    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/portals delete {portal_ip} {portal_port}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete Portal from iSCSI target {tgt_iqn}')
        return False
    return True


# ## iSCSI LUNs mapping ###
def lio_iscsi_map_lun(tgt_iqn, tpg, init_iqn, init_lun_id, bs_type, lun_name):  # noqa: ANN001, ANN201
    """Map a LUN to target IQN / Initiator IQN
    The arguments are:
    tgt_iqn:      Target IQN
    tpg:          Target Portal group
    init_iqn:     Host IQN
    Returns:
    True: If LUN is mapped
    False: If some problem happened.
    """
    lun_path = f'/backstores/{bs_type}/{lun_name}'
    cmd = f'targetcli /iscsi/{tgt_iqn}/{tpg}/acls/{init_iqn} create {init_lun_id} {lun_path}'

    if run(cmd).rc != 0:
        logging.error(f'Could not map lun to iSCSI target {tgt_iqn}/{init_iqn}')
        return False

    if not lio_iscsi_get_lun_map(tgt_iqn, init_iqn, tpg, init_lun_id):
        logging.error(f'It seems to have mapped lun {init_lun_id}, but it did not')
        return False

    return True


def lio_iscsi_unmap_lun(tgt_iqn, init_iqn, tpg, init_lun_id):  # noqa: ANN001, ANN201
    """Un map LUN from tgt_wwn/init_wwn
    The arguments are:
    tgt_iqn:      Target IQN
    init_iqn:     Host IQN
    tpg:          Target Portal group
    init_lun_id   LUN id for the initiator
    Returns:
    True: If LUN is unmapped
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi/{tgt_iqn}/{init_iqn}/acls/{tpg} delete {init_lun_id}'

    if run(cmd).rc != 0:
        logging.error(f'Could not unmap LUN from target {tgt_iqn}/{init_iqn}')
        return False

    if not lio_iscsi_get_lun_map(tgt_iqn, init_iqn, tpg, init_lun_id):
        logging.error(f'It seems to have unmapped lun {init_lun_id}, but it did not')
        return False
    return True


def lio_iscsi_get_lun_map(tgt_iqn, init_iqn, tpg, tgt_lun_id):  # noqa: ANN001, ANN201
    """Check if a LUN is mapped to target WWN / Initiator port
    The arguments are:
    tgt_iqn:      Target IQN
    init_iqn:     Host IQN
    tpg:          Target Portal group no.
    init_lun_id   LUN id for the initiator
    Returns:
    True: If LUN is mapped
    False: If some problem happened.
    """
    cmd = f'targetcli /iscsi/{tgt_iqn}/tpg{tpg}/acls/{init_iqn} ls | grep {tgt_lun_id}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'Could not get mapping for lun {tgt_lun_id} on iSCSI target {tgt_iqn}/{init_iqn}')
        return False

    if not output:  # noqa: SIM103
        return False
    return True


def lio_add_iscsi_target(  # noqa: ANN201
    tgt_iqn=None,  # noqa: ANN001
    init_iqn=None,  # noqa: ANN001
    bs_type='fileio',  # noqa: ANN001
    lun_name=None,  # noqa: ANN001
    lun_size='1G',  # noqa: ANN001
    device_name=None,  # noqa: ANN001
    tgt_cnt=1,  # noqa: ANN001
    lun_cnt=1,  # noqa: ANN001
):
    """Create new iSCSI target, create LUNs and do LUN mapping
    The arguments are:
    tgt_iqn:          Target IQN, if not specified LIO will create a target IQN
    init_iqn:         Initiator IQN, set LUN map to specific IQN, otherwise any IQN will access the LUN
    bs_type:          Backstores storage type, default: 'fileio'
    lun_name:         LUN name when creating the target, if not set default lun name will be used
    lun_size:         LUN size when using  fileio, default: 1G
    device_name:      Device name when using block device, for example LV name
    tgt_cnt:          Number of targets to create, default: 1
    lun_cnt:          Number of LUNs to create, default: 1
    Returns:
    True: if iSCSI target is created
    False: If some problem happened.
    """
    new_tgt_iqns = []
    iqn_preffix = 'iqn.2009-10.com.redhat:storage-'
    # need to create new iSCSI targets, first get the existing targets
    if not tgt_iqn:
        existing_targets = lio_iscsi_get_target()
        iqn_suffix = 0
        # Create new target_iqn names
        while len(new_tgt_iqns) < tgt_cnt:
            tmp_iqn = '%s%d' % (iqn_preffix, iqn_suffix)
            if tmp_iqn not in existing_targets:
                new_tgt_iqns.append(tmp_iqn)
            iqn_suffix += 1
    else:
        new_tgt_iqns = [tgt_iqn]

    for target_iqn in new_tgt_iqns:
        if not lio_iscsi_create_target(target_iqn):
            logging.error(f"Could not create iSCSI target '{target_iqn}'")
            return False

        m = re.match(r'%s(\d+)' % iqn_preffix, target_iqn)  # noqa: UP031
        tgt_name = 'tgt%d' % int(m.group(1)) if m else target_iqn.split(':')[1]

        for lun_num in range(1, lun_cnt + 1):
            tgt_lun_name = '%s_lun%d' % (tgt_name, lun_num)
            # If lun name was passed as argument, try to use it
            if lun_name:
                tgt_lun_name = lun_name

            if not lio_create_backstore(
                bs_type=bs_type,
                lun_name=tgt_lun_name,
                lun_size=lun_size,
                device_name=device_name,
            ):
                logging.error('Could not create backstore for iSCSI target')
                return False

            tpg = 'tpg1'

            if not lio_iscsi_add_lun(target_iqn, tpg, bs_type, tgt_lun_name):
                logging.error('Could not add LUN to iSCSI target')
                return False

            # This is a global setting
            if not lio_iscsi_target_set_parameter(None, None, 'discovery_auth', 'enable', '0'):
                logging.error('Could not set Attr to iSCSI target')
                return False

            if not lio_iscsi_target_set_parameter(target_iqn, tpg, 'attribute', 'authentication', '0'):
                logging.error('Could not set Attr to iSCSI target')
                return False

            if not lio_iscsi_target_set_parameter(target_iqn, tpg, 'attribute', 'generate_node_acls', '1'):
                logging.error('Could not set Attr to iSCSI target')
                return False

            if not lio_iscsi_target_set_parameter(target_iqn, tpg, 'attribute', 'demo_mode_write_protect', '0'):
                logging.error('Could not set Attr to iSCSI target')
                return False

            lun_id = '0'
            if init_iqn:
                if not lio_iscsi_create_acl(target_iqn, tpg, init_iqn):
                    logging.error('Could not create iSCSI initiator ACL')
                    return False
                if not lio_iscsi_map_lun(target_iqn, tpg, init_iqn, lun_id, bs_type, tgt_lun_name):
                    logging.error('Could not map LUN to iSCSI initiator')
                    return False

    return True


def lio_setup_iscsi_target(  # noqa: ANN201
    tgt_iqn=None,  # noqa: ANN001
    init_iqn=None,  # noqa: ANN001
    bs_type='fileio',  # noqa: ANN001
    lun_name=None,  # noqa: ANN001
    lun_size='1G',  # noqa: ANN001
    device_name=None,  # noqa: ANN001
    tgt_cnt=1,  # noqa: ANN001
    lun_cnt=1,  # noqa: ANN001
):
    """Create a basic iSCSI target
    The arguments are:
    tgt_iqn:          Target IQN, if not specified LIO will create a target IQN
    init_iqn:         Initiator IQN, set LUN map to specific IQN, otherwise any IQN will access the LUN
    bs_type:          Backstores storage type, default: 'fileio'
    lun_name:         LUN name when creating the target, if not set default lun name will be used
    lun_size:         LUN size when using  fileio, default: 1G
    device_name:      Device name when using block device, for example LV name
    tgt_cnt:          Number of targets to create, default: 1
    lun_cnt:          Number of LUNs to create, default: 1
    Returns:
    True: if iSCSI target is created
    False: If some problem happened.
    """
    logging.info('Creating basic iSCSI target...')
    lio_install()
    lio_restart()
    lio_clearconfig()

    ver = lio_version()
    logging.info(f'Running targetcli version {ver}')

    if not lio_support_iscsi_target():
        logging.error('Server does not support iSCSI target')
        return False

    lio_add_iscsi_target(tgt_iqn, init_iqn, bs_type, lun_name, lun_size, device_name, tgt_cnt, lun_cnt)

    return True


##################################################
# ################# TCM_FC ########################
##################################################
def lio_support_fc_target():  # noqa: ANN201
    """Check if host supports FC target
    The arguments are:
    None
    Returns:
    True: Host supports tcm_fc
    False: Host does not support tcm_fc.
    """
    lio_dict = lio_query()

    return 'tcm_fc' in list(lio_dict.keys())
    # Host does not support FC target


# ## FC target ###
def lio_create_fc_target(wwn):  # noqa: ANN001, ANN201
    """Add the wwn to tcm_fc target
    The arguments are:
    wwn:     Host wwn
    Returns:
    True: If target is added
    False: If some problem happened.
    """
    if not wwn:
        logging.error('lio_create_fc_target() - requires wwn parameter')
        return False

    cmd = f'targetcli /tcm_fc/ create {wwn}'

    if run(cmd).rc != 0:
        logging.error(f'lio_create_fc_target() - Could not create FC target {wwn}')
        return False

    if wwn not in lio_get_fc_target():
        lio_dict = lio_query()
        run('targetcli ls')
        logging.error('lio_create_fc_target() - It seems to have added FC target, but it did not')
        print(lio_dict['tcm_fc'])
        print(lio_dict)

        return False

    return True


def lio_delete_fc_target(wwn):  # noqa: ANN001, ANN201
    """Delete the wwn to tcm_fc target
    The arguments are:
    wwn:     Host wwn
    Returns:
    True: If target is added
    False: If some problem happened.
    """
    if not wwn:
        logging.error('lio_delete_fc_target() - requires wwn parameter')
        return False

    cmd = f'targetcli /tcm_fc/ delete {wwn}'

    if run(cmd).rc != 0:
        logging.error(f'lio_delete_fc_target() - Could not delete FC target {wwn}')
        return False

    if wwn in lio_get_fc_target():
        lio_dict = lio_query()
        run('targetcli ls', return_output=False)
        logging.error('lio_delete_fc_target() - It seems to have deleted FC target, but it did not')
        print(lio_dict['tcm_fc'])
        print(lio_dict)

        return False

    return True


def lio_get_fc_target(lio_dict=None):  # noqa: ANN001, ANN201
    """Return a list of all FC targets configured
    The arguments are:
    None
    Returns:
    list: Return a list of wwns that are configured.
    """
    if not lio_dict:
        lio_dict = lio_query()

    if not lio_support_fc_target():
        # Host does not support FC target
        return None

    return list(lio_dict['tcm_fc'].keys())


# ## FC ACLS ###
def lio_create_fc_target_acl(tgt_wwn, init_wwn, lio_dict=None):  # noqa: ANN001, ANN201
    """Add an initiator WWN to target WWN port
    The arguments are:
    tgt_wwn:     Host WWN
    init_wwn:    Initiator WWN
    Returns:
    True: If init wwn is created
    False: If some problem happened.
    """
    tgt_acls = lio_get_fc_target_acl(tgt_wwn, lio_dict=lio_dict)
    if tgt_acls and (init_wwn in tgt_acls):
        logging.info(f'{init_wwn} is already added to target {tgt_wwn}')
        return True

    cmd = f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/acls create {init_wwn} add_mapped_luns=false'

    if run(cmd).rc != 0:
        logging.error(f'Could not add FC initiator {init_wwn}')
        return False

    return True


def lio_delete_fc_target_acl(tgt_wwn, init_wwn):  # noqa: ANN001, ANN201
    """Remove an initiator WWN from target WWN port
    The arguments are:
    tgt_wwn:     Host WWN
    init_wwn:    Initiator WWN
    Returns:
    True: If init wwn is removed
    False: If some problem happened.
    """
    cmd = f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/acls delete {init_wwn}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete FC initiator {init_wwn}')
        return False

    return True


def lio_get_fc_target_acl(tgt_wwn, lio_dict=None):  # noqa: ANN001, ANN201
    """Get all acls from a specifc target
    The arguments are:
    tgt_wwn:     Host WWN
    Returns:
    List: List of initiators
    None: If some problem happened.
    """
    if not tgt_wwn:
        logging.error('lio_get_fc_target_acl() - requires tgt_wwpn as argument')
        return None
    if not lio_dict:
        lio_dict = lio_query()
    if not lio_dict['tcm_fc'][tgt_wwn]:
        logging.error(f'{tgt_wwn} does not exist')
        print(lio_dict)
        return None

    if 'acls' not in list(lio_dict['tcm_fc'][tgt_wwn].keys()):
        # logging.error("%s does not have acls" % tgt_wwn)
        # print lio_dict
        return None

    return list(lio_dict['tcm_fc'][tgt_wwn]['acls'].keys())


# ## FC LUNs ###
def lio_create_fc_target_lun(tgt_wwn, bs_type, lun_name):  # noqa: ANN001, ANN201
    """Add a LUN to target WWN port
    The arguments are:
    tgt_wwn:      Host WWN
    bs_type:      Backstore type
    lun_name:     Lun Name
    Returns:
    True: If LUN is created
    False: If some problem happened.
    """
    cmd = (
        f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/luns create '
        f'/backstores/{bs_type}/{lun_name} add_mapped_luns=false'
    )

    if run(cmd).rc != 0:
        logging.error(f'Could not add lun to FC target {tgt_wwn}')
        return False

    return True


def lio_delete_fc_target_lun(tgt_wwn, lun_id):  # noqa: ANN001, ANN201
    """Remove an initiator WWN from target WWN port
    The arguments are:
    tgt_wwn:     Target WWN
    lun_id:      Lun id
    Returns:
    True: If LUN is removed
    False: If some problem happened.
    """
    cmd = f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/luns delete {lun_id}'

    if run(cmd).rc != 0:
        logging.error(f'Could not delete LUN from target {tgt_wwn}')
        return False

    return True


def lio_get_fc_target_luns(tgt_wwn, lio_dict=None):  # noqa: ANN001, ANN201
    """Return a dict with all backstores. If a backstore type
    is provided return a list of backstore of this type
    The arguments are:
    None
    Returns:
    List: list of luns
    None if something went wrong.
    """
    if not lio_dict:
        lio_dict = lio_query()

    if tgt_wwn not in lio_get_fc_target(lio_dict=lio_dict):
        logging.error(f'{tgt_wwn} is not defined on targetcli')
        return None

    if 'luns' not in list(lio_dict['tcm_fc'][tgt_wwn].keys()):
        logging.info(f'target {tgt_wwn} does not have any LUN\n')
        return None

    return lio_dict['tcm_fc'][tgt_wwn]['luns']


def lio_get_fc_target_lun_id(tgt_wwn, bs_type, lun_name, lio_dict=None):  # noqa: ANN001, ANN201
    """Return the target LUN id.
    The arguments are:
    tgt_wwn:      Target WWN
    bs_type:      Backstore Type
    lun_name:     LUN name
    Returns:
    String: LUN id. eg: lun0
    None if something went wrong.
    """
    if not lio_dict:
        lio_dict = lio_query()

    t_luns_dict = lio_get_fc_target_luns(tgt_wwn, lio_dict)
    if not t_luns_dict:
        return None

    for lun_id in list(t_luns_dict.keys()):
        if t_luns_dict[lun_id]['bs_type'] == bs_type and t_luns_dict[lun_id]['lun_name'] == lun_name:
            return lun_id
    return None


#    cmd = "targetcli /tcm_fc/%s/luns ls | grep %s/%s | awk '{print$2}'" % (_wwn_2_tgt_wwn(tgt_wwn), bs_type, lun_name)
#    retcode, output = run_ret_out(cmd, return_output=True)
#    if (retcode != 0):
#        print ("FAIL: Could not get lun %s for FC target %s" % (lun_name, tgt_wwn))
#        return None
#
#    if output == "":
#        return None
#    return output


# ## FC LUNs mapping ###
def lio_fc_lun_map(lun_name, bs_type, tgt_wwn, init_wwn, init_lun_id):  # noqa: ANN001, ANN201
    """Map a LUN to a t_wwpn and h_wwpn."""
    if not lun_name or not bs_type or not tgt_wwn or not init_wwn or not init_lun_id:
        logging.error('lio_fc_lun_map() - requires lun_name, bs_type, tgt_wwn, init_wwn, init_lun_id parameters')
        return False

    logging.info(f'Mapping LUN {bs_type}/{lun_name} to {tgt_wwn}/{init_wwn}...')
    lio_dict = lio_query()
    if tgt_wwn not in lio_get_fc_target(lio_dict=lio_dict):
        lio_create_fc_target(tgt_wwn)
        # update lio_dict with new fc target
        lio_dict = lio_query()

    if not lio_get_fc_target_lun_id(tgt_wwn, bs_type, lun_name, lio_dict=lio_dict):
        lio_create_fc_target_lun(tgt_wwn, bs_type, lun_name)
        # update lio_dict with new fc target
        lio_dict = lio_query()

    # Do not pass lio_dict as parameter as we need to query it again to get updated info
    lun_id = lio_get_fc_target_lun_id(tgt_wwn, bs_type, lun_name, lio_dict=lio_dict)
    if not lun_id:
        logging.error(f'lio_fc_lun_map() - Could not find lun {bs_type}/{lun_name} on target {tgt_wwn}')
        lio_show()
        return False

    if not lio_create_fc_target_acl(tgt_wwn, init_wwn, lio_dict=lio_dict):
        logging.error(f'Could not create ACL to host {init_wwn}')
        lio_show()
        return False

    if not lio_create_fc_target_map_lun(tgt_wwn, init_wwn, init_lun_id, lun_id, lio_dict=lio_dict):
        logging.error(f'Could not map LUN {lun_name} to host {init_wwn}')
        return False

    logging.info(f'LUN {lun_name} mapped successfully')
    return True


def lio_create_fc_target_map_lun(tgt_wwn, init_wwn, init_lun_id, tgt_lun_id, lio_dict=None):  # noqa: ANN001, ANN201
    """Map a LUN to target WWN / Initiator port
    The arguments are:
    tgt_wwn:      Target WWN
    init_wwn:     Host WWN
    init_lun_id   LUN id for the initiator
    tgt_lun_id:   LUN id on target
    Returns:
    True: If LUN is mapped
    False: If some problem happened.
    """
    print('BRUNO lio_create_fc_target_map_lun')
    # print lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id)

    if lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id, lio_dict=lio_dict):
        logging.info(f'lun {tgt_lun_id} is already mapped to FC target {tgt_wwn}/{init_wwn}')
        return True

    cmd = (
        f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/acls/{_wwn_2_tgt_wwn(init_wwn)} create {init_lun_id} {tgt_lun_id}'
    )

    if run(cmd).rc != 0:
        logging.error(f'Could not map lun to FC target {tgt_wwn}/{init_wwn}')
        return False

    if not lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id):
        logging.error(f'It seems to have mapped lun {tgt_lun_id}, but it did not')
        return False

    return True


def lio_fc_target_get_mapped_luns(tgt_wwn, init_wwn, lio_dict=None):  # noqa: ANN001, ANN201
    """Get LUN mapping from tgt_wwn/init_wwn
    The arguments are:
    tgt_wwn:      Target WWN
    init_wwn:     Host WWN
    Returns:
    Dict:         Dictionary with tgt_lunid : init_lun_id
    None:         No mapping was found.
    """
    if not lio_dict:
        lio_dict = lio_query()

    if init_wwn not in lio_get_fc_target_acl(tgt_wwn, lio_dict=lio_dict):
        return None

    mapped_luns_dict = lio_dict['tcm_fc'][tgt_wwn]['acls'][init_wwn]
    if not mapped_luns_dict:
        return None
    return mapped_luns_dict


def lio_fc_target_unmap_lun(tgt_wwn, init_wwn, init_lun_id):  # noqa: ANN001, ANN201
    """Un map LUN from tgt_wwn/init_wwn
    The arguments are:
    tgt_wwn:      Target WWN
    init_wwn:     Host WWN
    init_lun_id   LUN id for the initiator
    Returns:
    True: If LUN is unmapped
    False: If some problem happened.
    """
    cmd = f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/acls/{_wwn_2_tgt_wwn(init_wwn)} delete {init_lun_id}'

    if run(cmd).rc != 0:
        logging.error(f'Could not unmap LUN from target {tgt_wwn}/{init_wwn}')
        return False

    if lio_get_fc_target_map_lun(tgt_wwn, init_wwn, init_lun_id):
        logging.error(f'It seems to have unmapped lun {init_lun_id}, but it did not')
        return False
    return True


def lio_get_fc_target_map_lun(tgt_wwn, init_wwn, tgt_lun_id, lio_dict=None):  # noqa: ANN001, ANN201
    """Get initator LUN ID if a LUN is mapped to target WWN / Initiator port
    The arguments are:
    tgt_wwn:      Target WWN
    init_wwn:     Host WWN
    tgt_lun_id:   LUN id on target
    Returns:
    init_lun_id: If LUN is mapped
    None: If LUN is not mapped.
    """
    # If lio dict is given as parameter we do not need to query lio output again
    if not lio_dict:
        lio_dict = lio_query()

    if init_wwn not in lio_get_fc_target_acl(tgt_wwn, lio_dict=lio_dict):
        return None

    # print "DEBUG lio_get_fc_target_map_lunt t: %s" % tgt_wwn
    # print "DEBUG lio_get_fc_target_map_lunt i: %s" % init_wwn
    # print "DEBUG lio_get_fc_target_map_lunt tgt_id: %s" % tgt_lun_id
    init_acls_dict = lio_dict['tcm_fc'][tgt_wwn]['acls'][init_wwn]
    if tgt_lun_id not in list(init_acls_dict.keys()):
        # print ("FAIL: Could not get mapping for lun %s on FC target %s/%s" % (tgt_lun_id, tgt_wwn, init_wwn))
        return None

    return init_acls_dict[tgt_lun_id]


def lio_get_fc_target_lun_mapping(bs_type, lun_name, lio_dict=None):  # noqa: ANN001, ANN201
    """Get the mapping information for a specifc LUN
    The arguments are:
    bs_type:      Backstore Type
    lun_name:     LUN name
    Returns:
    List:         A list with a dictionary for each mapping found
    None:         If no mapping was found.
    """
    if not lio_dict:
        lio_dict = lio_query()

    bs_details_dict = lio_get_backstore_details(bs_type, lun_name, lio_dict=lio_dict)
    if not bs_details_dict:
        # It does not exist
        return None

    if 'mapping' not in list(bs_details_dict.keys()):
        return None

    return bs_details_dict['mapping']


# ## FC tag ###
def lio_tag_fc_initiator(tgt_wwn, init_wwn, tag):  # noqa: ANN001, ANN201
    """Create a tag for initiator wwn
    The arguments are:
    tgt_wwn:     Host wwn
    init_wwn:    Initiator wwn
    tag:          tag for the initiator wwn
    Returns:
    True: If tag is created
    False: If some problem happened.
    """
    cmd = f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/acls tag {_wwn_2_tgt_wwn(init_wwn)} {tag}'

    if run(cmd).rc != 0:
        logging.error(f'Could not tag FC initiator {init_wwn}')
        return False

    return True


def lio_untag_fc_initiator(tgt_wwn, tag):  # noqa: ANN001, ANN201
    """Remove tag from initiator wwn
    The arguments are:
    tgt_wwn:     Host wwn
    tag:          tag for the initiator wwn
    Returns:
    True: If tag is created
    False: If some problem happened.
    """
    cmd = f'targetcli /tcm_fc/{_wwn_2_tgt_wwn(tgt_wwn)}/acls untag {tag}'

    if run(cmd).rc != 0:
        logging.error(f'Could not untag FC tag {tag}')
        return False

    return True


def lio_is_fc_tag(tgt_wwn, tag):  # noqa: ANN001, ANN201
    """Check if a tag is an FC initiator tag
    The arguments are:
    wwn:     Host wwn
    Returns:
    True: If target is added
    False: If some problem happened.
    """
    cmd = f'targetcli /tcm_fc/{tgt_wwn}/acls/{tag}'
    return run(cmd).rc == 0


##################################################
# ################ LIO General ####################
##################################################
def lio_install():  # noqa: ANN201
    """Install targetcli tool
    The arguments are:
    None
    Returns:
    True: If targetcli is installed correctly
    False: If some problem happened.
    """
    targetcli_pack = 'targetcli'

    if not linux.install_package(targetcli_pack):
        logging.error(f'Could not install {targetcli_pack}')
        return False

    return True


def lio_get_service_name():  # noqa: ANN201
    return 'target'


def lio_restart():  # noqa: ANN201
    """Restart LIO service
    The arguments are:
    None
    Returns:
    True: Service started
    False: If some problem happened.
    """
    targetcli_service = lio_get_service_name()
    if not targetcli_service:
        logging.error('lio_restart() - Could not get LIO service name')
        return False

    if not linux.service_restart(targetcli_service):
        logging.error('Could not restart LIO service')
        return False
    # sleep 5s to avoid service to not be restarted
    # target.service start request repeated too quickly, refusing to start.
    linux.sleep(5)
    return True


def lio_show():  # noqa: ANN201
    """List LIO configuration
    The arguments are:
    None
    Returns:
    True: If listed config
    False: If some problem happened.
    """
    cmd = 'targetcli ls'

    if run(cmd).rc != 0:
        logging.error('Could not show LIO config')
        return False
    return True


def lio_saveconfig():  # noqa: ANN201
    """Save LIO configuration
    The arguments are:
    None
    Returns:
    True: If config is saved
    False: If some problem happened.
    """
    cmd = 'targetcli saveconfig'

    if run(cmd).rc != 0:
        logging.error('Could not save LIO config')
        return False
    return True


def lio_clearconfig(delete_fileio_files: bool = False) -> bool:
    """Clear LIO configuration
    The arguments are:
    None
    Returns:
    True: If config is deleted
    False: If some problem happened.
    """
    logging.info('Cleaning up LIO configuration')

    if not linux.is_installed('targetcli'):
        return True

    if delete_fileio_files:
        fileio_dict = lio_get_backstores('fileio')
        if fileio_dict:
            # Delete all files before cleaning configuration
            for lun in list(fileio_dict.keys()):
                lio_delete_backstore(bs_type='fileio', lun_name=lun)

    cmd = 'targetcli clearconfig true'

    if run(cmd).rc != 0:
        logging.error('Could not delete LIO config')
        return False

    return True


def log_versions() -> None:
    # Package targetcli and all its dependencies
    packages = [
        'targetcli',
        'python3-rtslib',
        'python3-configshell',
        'target-restore',
        'python3-urwid',
        'python3-pyparsing',
        'python3-kmod',
    ]
    for pack in packages:
        linux.log_package_version(pack)


def lio_version():  # noqa: ANN201
    """Get targetcli version
    The arguments are:
    None
    Returns:
    String: TargetCli version
    None: If some problem happened.
    """
    cmd = 'targetcli version'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error('Could not get targetcli version')
        return None

    m = re.compile('.* version (.*)$').search(output)
    if m:
        return m.group(1)
    logging.error(f'Could not parse targetcli version output ({output})')
    return None


def lio_clean_up_targets(lio_dict=None):  # noqa: ANN001, ANN201
    """Removing backstore might leave targets with empty mapping
    They should be removed.
    """
    lio_dict = lio_query(lio_dict)
    fc_targets = lio_get_fc_target(lio_dict=lio_dict)
    if not fc_targets:
        # nothing to clean up
        return True
    # First we checked for initiators without mapping
    need_to_query_lio = False
    success = True
    for tgt in fc_targets:
        initiators = lio_get_fc_target_acl(tgt, lio_dict=lio_dict)
        if initiators:
            for init in initiators:
                if not lio_fc_target_get_mapped_luns(tgt, init, lio_dict=lio_dict):
                    print(f'DEBUG: Should remove initiator {init} from tgt {tgt}')
                    if not lio_delete_fc_target_acl(tgt, init):
                        success = False
                    need_to_query_lio = True

    # Check again for targets without any initiator
    if need_to_query_lio:
        lio_dict = lio_query()
    fc_targets = lio_get_fc_target(lio_dict=lio_dict)
    for tgt in fc_targets:
        initiators = lio_get_fc_target_acl(tgt, lio_dict=lio_dict)
        if not initiators:
            print(f'DEBUG: Should remove target {tgt}')
            if not lio_delete_fc_target(tgt):
                success = False

    return success


class TargetCLI:
    def __init__(self, path='', disable_check=False) -> None:  # noqa: ANN001
        self.disable_check = disable_check
        self.path = path

        if not linux.install_package('targetcli'):
            logging.critical('Could not install targetcli package')

    @staticmethod
    def remove_nones(kwargs):  # noqa: ANN001, ANN205
        return {k: v for k, v in kwargs.items() if v is not None}

    @staticmethod
    def _extract_args(kwargs, keys=None):  # noqa: ANN001, ANN205
        keys = keys or ['return_output', 'verbosity', 'path']
        arguments = {}
        for key in keys:
            if key not in kwargs:
                continue
            arguments[key] = kwargs.pop(key)
        return arguments, kwargs

    def _run(self, cmd, return_output=False, path=None):  # noqa: ANN001, ANN202
        # Constructs the command to run and runs it

        if path is not None:
            self.path = path

        cmd = 'targetcli cd' if cmd == 'cd' and self.path is None else 'targetcli ' + self.path + ' ' + cmd

        if return_output:
            ret, data = run_ret_out(cmd, return_output=True)
            if ret != 0:
                logging.warning(f"Running command: '{cmd}' failed. Return with output.")
            return ret, data

        ret = run(cmd).rc
        if ret != 0:
            logging.warning(f"Running command: '{cmd}' failed.")
        return ret

    def ls(self, depth='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'ls {depth}', **kwargs)

    def cd(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('cd', **kwargs)

    def pwd(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('pwd', **kwargs)

    def create(self, **kwargs):  # noqa: ANN003, ANN201
        keys = None
        cmd = 'create '
        arguments, kwargs = self._extract_args(kwargs)
        # the following ensures the ordering is correct in correct paths
        # True means it is required, False it is optional
        if 'backstores/block' in self.path:
            keys = {'name': True, 'dev': True, 'readonly': False, 'wwn': False}
        elif 'backstores/fileio' in self.path:
            keys = {
                'name': True,
                'file_or_dev': True,
                'size': True,
                'write_back': False,
                'sparse': False,
                'wwn': False,
            }
        elif 'backstores/pscsi' in self.path:
            keys = {'name': True, 'dev': True}
        elif 'backstores/ramdisk' in self.path:
            keys = {'name': True, 'size': True, 'nullio': False, 'wwn': False}
        elif 'backstores/user:qcow' in self.path:  # noqa: SIM114
            keys = {
                'name': True,
                'size': True,
                'cfgstring': True,
                'wwn': False,
                'hw_max_sectors': False,
                'control': False,
            }
        elif 'backstores/user:rbd' in self.path:  # noqa: SIM114
            keys = {
                'name': True,
                'size': True,
                'cfgstring': True,
                'wwn': False,
                'hw_max_sectors': False,
                'control': False,
            }
        elif 'backstores/user:zbc' in self.path:
            keys = {
                'name': True,
                'size': True,
                'cfgstring': True,
                'wwn': False,
                'hw_max_sectors': False,
                'control': False,
            }
        elif self.path.startswith('/iscsi/'):
            if 'iqn' in self.path:
                if 'acls' in self.path:
                    keys = {'wwn': True, 'add_mapped_luns': False}
                elif 'luns' in self.path:
                    keys = {
                        'storage_object': True,
                        'lun': False,
                        'add_mapped_luns': False,
                    }
                elif 'portals' in self.path:
                    keys = {'ip_address': False, 'ip_port': False}
                else:
                    keys = {'tag': False}
            else:
                keys = {'wwn': False}
        elif self.path.startswith('/loopback'):
            if 'naa' in self.path:
                if 'luns' in self.path:
                    keys = {
                        'storage_object': True,
                        'lun': False,
                        'add_mapped_luns': False,
                    }
            else:
                keys = {'wwn': False}
        else:
            keys = {'wwn': False}
        try:
            for key in keys:
                cmd += f'{key}={kwargs[key]} '
        except KeyError:
            if not self.disable_check and keys[key]:
                logging.exception(f"Create on path '{self.path}' requires argument {key}.")
                return 1
        return self._run(cmd, **arguments)

    def delete(self, **kwargs):  # noqa: ANN003, ANN201
        keys = None
        cmd = 'delete '
        arguments, kwargs = self._extract_args(kwargs)
        # the following ensures the ordering is correct in correct paths
        # True means it is required, False it is optional
        if 'backstores/block' in self.path:  # noqa: SIM114
            keys = {'name': True}
        elif 'backstores/fileio' in self.path:  # noqa: SIM114
            keys = {'name': True}
        elif 'backstores/pscsi' in self.path:  # noqa: SIM114
            keys = {'name': True}
        elif 'backstores/ramdisk' in self.path:  # noqa: SIM114
            keys = {'name': True}
        elif 'backstores/user:qcow' in self.path:  # noqa: SIM114
            keys = {'name': True}
        elif 'backstores/user:rbd' in self.path:  # noqa: SIM114
            keys = {'name': True}
        elif 'backstores/user:zbc' in self.path:
            keys = {'name': True}
        elif self.path.startswith('/iscsi/'):
            if 'iqn' in self.path:
                if 'acls' in self.path:
                    keys = {'wwn': True}
                elif 'luns' in self.path:
                    keys = {'lun': True}
                elif 'portals' in self.path:
                    keys = {'ip_address': True, 'ip_port': True}
                else:
                    keys = {'tag': True}
            else:
                keys = {'wwn': True}
        elif self.path.startswith('/loopback'):
            if 'naa' in self.path:
                if 'luns' in self.path:
                    keys = {'lun': True}
            else:
                keys = {'wwn': False}
        else:
            keys = {'wwn': True}

        try:
            for key in keys:
                cmd += f'{key}={kwargs[key]} '
        except KeyError:
            if not self.disable_check and keys[key]:
                logging.exception(f"Delete on path '{self.path}' requires argument {key}.")
                return 1

        return self._run(cmd, **arguments)

    def help(self, topic='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'help {topic}', **kwargs)

    def saveconfig(self, savefile=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        cmd = 'saveconfig'
        if savefile:
            cmd += f' {savefile}'
        return self._run(cmd, **kwargs)

    def restoreconfig(  # noqa: ANN201
        self,
        savefile='/etc/target/saveconfig.json',  # noqa: ANN001
        clearexisting=False,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        return self._run(f'restoreconfig {savefile} {clearexisting}', **kwargs)

    def clearconfig(self, confirm=True, **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'clearconfig {confirm}', **kwargs)

    def sessions(self, action='', sid='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'sessions {action} {sid}', **kwargs)

    def exit(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('exit', **kwargs)

    def get(self, group='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        arguments, kwargs = self._extract_args(kwargs)
        cmd = f"get {group} {' '.join(kwargs.keys())}"
        return self._run(cmd, **arguments)

    def set(self, group='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        arguments, kwargs = self._extract_args(kwargs)
        params = [f"{kwarg}='{kwargs[kwarg]}'" if kwargs[kwarg] else f"{kwarg}='{kwargs[kwarg]}'" for kwarg in kwargs]
        cmd = f"set {group} {' '.join(params)}"
        return self._run(cmd, **arguments)

    def info(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('info', **kwargs)

    def version(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('version', **kwargs)

    def status(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('status', **kwargs)

    def refresh(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('refresh', **kwargs)

    def disable(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('disable', **kwargs)

    def enable(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('enable', **kwargs)

    def bookmarks(self, **kwargs):  # noqa: ANN003, ANN201
        # How to use this?
        return self._run('bookmarks', **kwargs)

    def enable_iser(self, boolean='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'enable_iser {boolean}', **kwargs)

    def enable_offload(self, boolean='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'enable_offload {boolean}', **kwargs)

    def tag(self, wwn_or_tag='', new_tag='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'tag {wwn_or_tag} {new_tag}', **kwargs)

    def untag(self, wwn_or_tag='', **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run(f'untag {wwn_or_tag}', **kwargs)
