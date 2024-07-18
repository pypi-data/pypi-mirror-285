"""lsm.py: Module with test specific method for libstoragemgmt."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
import os
import re
import sys
from contextlib import suppress
from time import sleep

from sts import linux
from sts.utils.cli_tools import (
    FailedCheckExceptionError,
    Wrapper,
    WrongArgumentExceptionError,
    WrongCommandExceptionError,
)
from sts.utils.cmdline import run, run_ret_out


def check_ssl(protocol) -> bool:  # noqa: ANN001
    """Checks if fmf_protocol is ssl/no_ssl and limits the protocol by this."""
    try:
        ssl = os.getenv('STS_LSM_PROTOCOL')
    except KeyError:
        # Protocol not limited
        return True
    if (ssl == 'ssl' and 'ssl' in protocol) or (ssl == 'no_ssl' and 'ssl' not in protocol):  # noqa: SIM103
        return True
    return False


def yield_lsm_config():  # noqa: ANN201
    config = {'protocols': [], 'username': None, 'password': None, 'target': None}

    for conf in config:
        with suppress(OSError):
            config[conf] = os.getenv('LSM_' + conf.upper())

    try:
        if not isinstance(config['protocols'], list):
            raise TypeError  # noqa: TRY301
    except TypeError:
        print(
            f"ERROR: Protocols must be list, got {config['protocols']}, type '{type(config['protocols'])}'.",
        )
        sys.exit(1)

    protocols = config.pop('protocols')
    for protocol in protocols:
        if not check_ssl(protocol):
            continue
        config['protocol'] = protocol
        yield config


def get_data_from_script_output(data, id='id'):  # noqa: ANN001, ANN201
    split_string = re.match('(-*)', data).group()
    try:
        items = [x for x in data.split(split_string) if id in x]
    except ValueError as e:
        print(repr(e))
        return None
    data = {}
    for item in items:
        for line in item.splitlines():
            if len(line) < 2:
                continue
            if line.startswith(id):
                # luckily id is always first
                item_id = line.split('|').pop().strip()
                data[item_id] = {}
            else:
                line_data = line.split('|')
                data[item_id][line_data[0].strip()] = line_data[1].strip()
    return data


def get_local_disk_data(data):  # noqa: ANN001, ANN201
    return get_data_from_script_output(data, id='Path')


def get_id_from_name(data, name, field='Name', item_id='id'):  # noqa: ANN001, ANN201
    data = get_data_from_script_output(data, id=item_id)
    for line in data:
        if data[line][field] == name:
            return line
    logging.error(f"Could not find item named '{name}'.")
    return None


def get_data_from_id(data, name, field='Name', item_id='id'):  # noqa: ANN001, ANN201
    data = get_data_from_script_output(data, id=item_id)
    for line in data:
        if line != name:
            continue
        return data[line][field]
    logging.error(f"Could not find item named '{name}'.")
    return None


def get_ag_id_from_name(data, name):  # noqa: ANN001, ANN201
    return get_id_from_name(data, name)


def get_fs_id_from_name(data, name):  # noqa: ANN001, ANN201
    return get_id_from_name(data, name)


def get_vol_id_from_name(data, name):  # noqa: ANN001, ANN201
    return get_id_from_name(data, name)


def get_export_id_from_export_path(data, export_path):  # noqa: ANN001, ANN201
    # policy is 'disabled' but cli takes 'disable'
    return get_id_from_name(data, export_path, field='Export Path')


def get_system_read_pct_of_sys(data, sys):  # noqa: ANN001, ANN201
    return get_data_from_script_output(data)[sys]['Read Cache Percentage']


def get_cache_policy_from_id(data, vol_id, field):  # noqa: ANN001, ANN201
    return translate_cache_policy(get_data_from_id(data, vol_id, field=field, item_id='Volume id'))


def translate_cache_policy(policy):  # noqa: ANN001, ANN201
    dictionary = {
        'Write Back': 'WB',
        'Write Through': 'WT',
        'Auto': 'AUTO',
        'Enabled': 'enable',
        'Disabled': 'disable',
    }
    try:
        return dictionary[policy]
    except KeyError:
        return policy


def get_replace_dict():  # noqa: ANN201
    """Returns dict of keys to replace from fmf to sts.lsm.LibStorageMgmt.

    Returns:
      dict.
    """
    return {
        'ag_name': 'name',
        'vol_name': 'name',
        'fs_name': 'name',
        'snap_name': 'name',
        'rep_name': 'name',
    }


def _cli(func):  # noqa: ANN001, ANN202
    # This is a decorator to mark functions callable by 'lsmcli'
    func.cli = True
    return func


class LibStorageMgmt(Wrapper):
    def __init__(
        self,
        username=None,  # noqa: ANN001
        password=None,  # noqa: ANN001
        target=None,  # noqa: ANN001
        protocol=None,  # noqa: ANN001
        disable_check=False,  # noqa: ANN001
    ) -> None:
        self.disable_check = disable_check
        self.username = None
        self.password = None
        self.target = None
        self.protocol = None
        self.port = None
        self.query_params = None
        self.timeout = None

        # persistent previous values
        self.previous_sys_read_pct: dict = {}
        self.previous_phy_disk_cache_policy: dict = {}
        self.previous_read_cache_policy: dict = {}
        self.previous_write_cache_policy: dict = {}
        self.previous_local_disk_ident_led: dict = {}
        self.previous_local_disk_fault_led: dict = {}

        # local target does not require anything of this and megaraid/sim needs only protocol
        if username and password and target and protocol:
            self.username = username
            self.password = password
            self.target = target
            self.protocol = protocol
        elif (protocol and 'megaraid' in protocol) or 'sim' in protocol:
            self.protocol = protocol

        if self.password:
            os.environ['LSMCLI_PASSWORD'] = self.password
            logging.info('Password set')
        elif os.environ.get('LSMCLI_PASSWORD'):
            del os.environ['LSMCLI_PASSWORD']
            logging.info('Password cleaned')

        requires_restart = False
        # stop if lsm package cannot be installed
        if not linux.is_installed('libstoragemgmt'):
            if not linux.install_package('libstoragemgmt'):
                logging.critical('Could not install libstoragemgmt package')
            else:
                requires_restart = True

        if self.protocol == 'smispy':
            self.port = '5988'
            self.query_params = '?namespace=root/emc'
        if self.protocol == 'smispy+ssl':
            # ssl uses different port
            self.port = '5989'
            # ignore missing ssl certificate
            self.query_params = '?namespace=root/emc&no_ssl_verify=yes'

        # install protocol specific packages
        if self.protocol:
            if 'ontap' in self.protocol:
                if not linux.is_installed('libstoragemgmt-netapp-plugin'):
                    if not linux.install_package('libstoragemgmt-netapp-plugin'):
                        logging.critical('Could not install LSM NetApp plugin')
                    else:
                        requires_restart = True
            elif 'smispy' in self.protocol:
                if not linux.is_installed('libstoragemgmt-smis-plugin'):
                    if not linux.install_package('libstoragemgmt-smis-plugin'):
                        logging.critical('Could not install LSM SMIS plugin')
                    else:
                        requires_restart = True
            elif 'targetd' in self.protocol:
                if not linux.is_installed('libstoragemgmt-targetd-plugin'):
                    if not linux.install_package('libstoragemgmt-targetd-plugin'):
                        logging.critical('Could not install LSM targetd plugin')
                    else:
                        requires_restart = True
            elif 'megaraid' in self.protocol:
                if not linux.is_installed('libstoragemgmt-megaraid-plugin'):
                    if not linux.install_package('libstoragemgmt-megaraid-plugin'):
                        logging.critical('Could not install LSM megaraid plugin')
                    else:
                        requires_restart = True
                # needs to install 3rd party tool
                if not linux.install_package('storcli'):
                    logging.critical('Could not install storcli')

        if requires_restart:
            if run('service libstoragemgmt restart').rc != 0:
                logging.critical('Could not restart libstoragemgmt service')
            else:
                logging.info('Waiting for service to restart.')
                sleep(5)
        elif not linux.is_service_running('libstoragemgmt'):  # noqa: SIM102
            if linux.service_start('libstoragemgmt'):
                logging.info('Waiting for service to start.')
                sleep(5)

        self.commands: dict[str, str | list[str]] = {
            'list': 'list',
            'job_status': 'job-status',
            'capabilities': 'capabilities',
            'plugin_info': 'plugin-info',
            'volume_create': 'volume-create',
            'volume_raid_create': 'volume-raid-create',
            'volume_raid_create_cap': 'volume-raid-create-cap',
            'volume_delete': 'volume-delete',
            'volume_resize': 'volume-resize',
            'volume_replicate': 'volume-replicate',
            'volume_replicate_range': 'volume-replicate-range',
            'volume_replicate_range_block_size': 'volume-replicate-range-block-size',
            'volume_dependants': 'volume-dependants',
            'volume_dependants_rm': 'volume-dependants-rm',
            'volume_access_group': 'volume-access-group',
            'volume_mask': 'volume-mask',
            'volume_unmask': 'volume-unmask',
            'volume_enable': 'volume-enable',
            'volume_disable': 'volume-disable',
            'volume_raid_info': 'volume-raid-info',
            'volume_ident_led_on': 'volume-ident-led-on',
            'volume_ident_led_off': 'volume-ident-led-off',
            'system_read_cache_pct_update': 'system-read-cache-pct-update',
            'pool_member_info': 'pool-member-info',
            'access_group_create': 'access-group-create',
            'access_group_add': 'access-group-add',
            'access_group_remove': 'access-group-remove',
            'access_group_delete': 'access-group-delete',
            'access_group_volumes': 'access-group-volumes',
            'iscsi_chap': 'iscsi-chap',
            'fs_create': 'fs-create',
            'fs_delete': 'fs-delete',
            'fs_resize': 'fs-resize',
            'fs_export': 'fs-export',
            'fs_unexport': 'fs-unexport',
            'fs_clone': 'fs-clone',
            'fs_snap_create': 'fs-snap-create',
            'fs_snap_delete': 'fs-snap-delete',
            'fs_snap_restore': 'fs-snap-restore',
            'fs_dependants': 'fs-dependants',
            'fs_dependants_rm': 'fs-dependants-rm',
            'file_clone': 'file-clone',
            'local_disk_list': 'local-disk-list',
            'volume_cache_info': 'volume-cache-info',
            'volume_phy_disk_cache_update': 'volume-phy-disk-cache-update',
            'volume_read_cache_policy_update': 'volume-read-cache-policy-update',
            'volume_write_cache_policy_update': 'volume-write-cache-policy-update',
            'local_disk_ident_led_on': 'local-disk-ident-led-on',
            'local_disk_ident_led_off': 'local-disk-ident-led-off',
            'local_disk_fault_led_on': 'local-disk-fault-led-on',
            'local_disk_fault_led_off': 'local-disk-fault-led-off',
        }
        self.commands['all'] = list(self.commands.keys())

        self.arguments = {
            'human': [self.commands['all'], ' --human'],
            'terse': [self.commands['all'], ' --terse='],
            'enum': [self.commands['all'], ' --enum'],
            'force': [self.commands['all'], ' --force'],
            'wait': [self.commands['all'], ' --wait='],
            'header': [self.commands['all'], ' --header'],
            'async': [self.commands['all'], ' --b'],
            'script': [self.commands['all'], ' --script'],
            'lsm_type': [['list'], ' --type='],
            'sys': [
                [
                    'list',
                    'capabilities',
                    'volume_raid_create_cap',
                    'volume_replicate_range_block_size',
                    'system_read_cache_pct_update',
                    'access_group_create',
                ],
                ' --sys=',
            ],
            'pool': [
                [
                    'list',
                    'volume_create',
                    'volume_replicate',
                    'pool_member_info',
                    'fs_create',
                ],
                ' --pool=',
            ],
            'vol': [
                [
                    'list',
                    'volume_delete',
                    'volume_resize',
                    'volume_replicate',
                    'volume_dependants',
                    'volume_dependants_rm',
                    'volume_access_group',
                    'volume_mask',
                    'volume_unmask',
                    'volume_enable',
                    'volume_disable',
                    'volume_raid_info',
                    'volume_ident_led_on',
                    'volume_ident_led_off',
                    'volume_cache_info',
                    'volume_phy_disk_cache_update',
                    'volume_read_cache_policy_update',
                    'volume_read_cache_policy_update',
                ],
                ' --vol=',
            ],
            'disk': [['list', 'volume_raid_create'], ' --disk='],
            'ag': [
                [
                    'list',
                    'volume_mask',
                    'volume_unmask',
                    'access_group_add',
                    'access_group_remove',
                    'access_group_delete',
                    'access_group_volumes',
                ],
                ' --ag=',
            ],
            'fs': [
                [
                    'list',
                    'fs_delete',
                    'fs_resize',
                    'fs_export',
                    'fs_snap_create',
                    'fs_snap_delete',
                    'fs_snap_restore',
                    'fs_dependants',
                    'fs_dependants_rm',
                    'file_clone',
                ],
                ' --fs=',
            ],
            'nfs_export': [['list'], ' --nfs-export='],
            'tgt': [['list'], ' --tgt='],
            'job': [['job_status'], ' --job='],
            'name': [
                [
                    'volume_create',
                    'volume_raid_create',
                    'volume_replicate',
                    'access_group_create',
                    'fs_create',
                    'fs_snap_create',
                ],
                ' --name=',
            ],
            'size': [
                ['volume_create', 'volume_resize', 'fs_create', 'fs_resize'],
                ' --size=',
            ],
            'provisioning': [['volume_create'], ' --provisioning='],
            'raid_type': [['volume_raid_create'], ' --raid-type='],
            'strip_size': [['volume_raid_create'], ' --strip-size='],
            'rep_type': [
                ['volume_replicate', 'volume_replicate_range'],
                ' --rep-type=',
            ],
            'src_vol': [['volume_replicate_range'], ' --src-vol='],
            'dst_vol': [['volume_replicate_range'], ' --dst-vol='],
            'src_start': [['volume_replicate_range'], ' --src-start='],
            'dst_start': [['volume_replicate_range'], ' --dst-start='],
            'count': [['volume_replicate_range'], ' --count='],
            'read_pct': [['system_read_cache_pct_update'], ' --read-pct='],
            'init': [
                [
                    'access_group_create',
                    'access_group_add',
                    'access_group_remove',
                    'iscsi_chap',
                ],
                ' --init=',
            ],
            'in_user': [['iscsi_chap'], ' --in-user='],
            'in_pass': [['iscsi_chap'], ' --in-pass='],
            'out_user': [['iscsi_chap'], ' --out-user='],
            'out_pass': [['iscsi_chap'], ' --out-pass='],
            'export_path': [['iscsi_chap'], ' --exportpath='],
            'anonuid': [['fs_export'], ' --anonuid='],
            'anongid': [['fs_export'], ' --anongid='],
            'auth_type': [['fs_export'], ' --auth-type='],
            'root_host': [['fs_export'], ' --root-host='],
            'ro_host': [['fs_export'], ' --ro-host='],
            'rw_host': [['fs_export'], ' --rw-host='],
            'export': [['fs_unexport'], ' --export='],
            'src_fs': [['fs_clone'], ' --src-fs='],
            'dst_name': [['fs_clone'], ' --dst-name='],
            'backing_snapshot': [['fs_clone', 'file_clone'], ' --backing-snapshot='],
            'snap': [['fs_snap_delete', 'fs_snap_restore'], ' --snap='],
            'lsm_file': [
                ['fs_snap_restore', 'fs_dependants', 'fs_dependants_rm'],
                ' --file=',
            ],
            'fileas': [['fs_snap_restore'], ' --fileas='],
            'src': [['file_clone'], ' --src'],
            'dst': [['file_clone'], ' --dst'],
            'policy': [
                [
                    'volume_phy_disk_cache_update',
                    'volume_read_cache_policy_update',
                    'volume_read_cache_policy_update',
                ],
                ' --policy=',
            ],
            'path': [
                [
                    'local_disk_ident_led_on',
                    'local_disk_ident_led_off',
                    'local_disk_fault_led_on',
                    'local_disk_fault_led_on',
                ],
                ' --path=',
            ],
        }

        Wrapper.__init__(self, self.commands, self.arguments, self.disable_check)

        logging.info('LSM configured')

    def _check(self, cmd):  # noqa: ANN001, ANN202
        if self.disable_check or cmd:
            # Do not check if checking is disabled
            return True

        return True

    def _run(self, cmd, return_output=False, **kwargs):  # noqa: ANN001, ANN003, ANN202
        # Constructs the command to run and runs it

        ret_fail = False
        if return_output:
            ret_fail = (False, None)

        try:
            command = self._add_command(cmd)
            command = self._add_arguments(command, **kwargs)

        except WrongCommandExceptionError as e:
            logging.warning(f"Given command '{e.command}' is not allowed in this version.")
            return ret_fail
        except WrongArgumentExceptionError as e:
            message = f"WARN: Given argument '{e.argument}' is not allowed for given command."
            if e.command:
                message = message[:-1] + " '" + e.command + "'."
            if e.arguments:
                message += f"\nPlease use only these: {', '.join(e.arguments)}."
            print(message)
            return ret_fail

        cmd = 'lsmcli '
        if self.timeout:
            cmd += f'-w {self.timeout} '
        if self.protocol:
            cmd += f'-u "{self.protocol}://'
            if self.username and self.target:
                cmd += f'{self.username}@{self.target}'
            if self.port:
                cmd += f':{self.port}'
            if self.query_params:
                cmd += self.query_params
            cmd += '" '
        cmd += command

        try:
            self._check(cmd)
        except WrongArgumentExceptionError:
            pass
        except FailedCheckExceptionError as e:
            logging.warning(f'Failed checking on argument {e.argument}')
            return ret_fail

        if return_output:
            ret, data = run_ret_out(cmd, return_output=True)
            if ret != 0:
                logging.warning(f"Running command: '{cmd}' failed. Return with output.")
            return ret, data

        ret = run(cmd).rc
        if ret != 0:
            logging.warning(f"Running command: '{cmd}' failed.")
        return ret

    @staticmethod
    def _remove_nones(kwargs):  # noqa: ANN001, ANN205
        return {k: v for k, v in kwargs.items() if v is not None}

    @_cli
    def list(  # noqa: ANN201
        self,
        lsm_type=None,  # noqa: ANN001
        fs=None,  # noqa: ANN001
        sys=None,  # noqa: ANN001
        pool=None,  # noqa: ANN001
        vol=None,  # noqa: ANN001
        disk=None,  # noqa: ANN001
        ag=None,  # noqa: ANN001
        nfs_export=None,  # noqa: ANN001
        tgt=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        kwargs.update(
            {
                'lsm_type': lsm_type,
                'fs': fs,
                'sys': sys,
                'pool': pool,
                'vol': vol,
                'disk': disk,
                'ag': ag,
                'nfs_export': nfs_export,
                'tgt': tgt,
            },
        )
        return self._run('list', **self._remove_nones(kwargs))

    @_cli
    def job_status(self, job=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'job': job})
        return self._run('job_status', **self._remove_nones(kwargs))

    @_cli
    def capabilities(self, sys=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'sys': sys})
        return self._run('capabilities', **self._remove_nones(kwargs))

    @_cli
    def plugin_info(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('plugin_info', **self._remove_nones(kwargs))

    @_cli
    def volume_create(  # noqa: ANN201
        self,
        name=None,  # noqa: ANN001
        size=None,  # noqa: ANN001
        pool=None,  # noqa: ANN001
        provisioning=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        kwargs.update({'name': name, 'size': size, 'pool': pool, 'provisioning': provisioning})
        return self._run('volume_create', **self._remove_nones(kwargs))

    @_cli
    def volume_raid_create(  # noqa: ANN201
        self,
        name=None,  # noqa: ANN001
        raid_type=None,  # noqa: ANN001
        disk=None,  # noqa: ANN001
        strip_size=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        kwargs.update(
            {
                'name': name,
                'raid_type': raid_type,
                'disk': disk,
                'strip_size': strip_size,
            },
        )
        return self._run('volume_raid_create', **self._remove_nones(kwargs))

    @_cli
    def volume_raid_create_cap(self, sys=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'sys': sys})
        return self._run('volume_raid_create_cap', **self._remove_nones(kwargs))

    @_cli
    def volume_ident_led_on(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_ident_led_on', **self._remove_nones(kwargs))

    @_cli
    def volume_ident_led_off(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_ident_led_off', **self._remove_nones(kwargs))

    @_cli
    def volume_delete(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_delete', **self._remove_nones(kwargs))

    @_cli
    def volume_resize(self, vol=None, size=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'size': size})
        return self._run('volume_resize', **self._remove_nones(kwargs))

    @_cli
    def volume_replicate(self, vol=None, name=None, rep_type=None, pool=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'name': name, 'rep_type': rep_type, 'pool': pool})
        return self._run('volume_replicate', **self._remove_nones(kwargs))

    @_cli
    def volume_replicate_range(  # noqa: ANN201
        self,
        src_vol=None,  # noqa: ANN001
        dst_vol=None,  # noqa: ANN001
        rep_type=None,  # noqa: ANN001
        src_start=None,  # noqa: ANN001
        dst_start=None,  # noqa: ANN001
        count=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        kwargs.update(
            {
                'src_vol': src_vol,
                'dst_vol': dst_vol,
                'rep_type': rep_type,
                'src_start': src_start,
                'dst_start': dst_start,
                'count': count,
            },
        )
        return self._run('volume_replicate_range', **self._remove_nones(kwargs))

    @_cli
    def volume_replicate_range_block_size(self, sys=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'sys': sys})
        return self._run('volume_replicate_range_block_size', **self._remove_nones(kwargs))

    @_cli
    def volume_dependants(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_dependants', **self._remove_nones(kwargs))

    @_cli
    def volume_dependants_rm(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_dependants_rm', **self._remove_nones(kwargs))

    @_cli
    def volume_access_group(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_access_group', **self._remove_nones(kwargs))

    @_cli
    def volume_mask(self, vol=None, ag=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'ag': ag})
        return self._run('volume_mask', **self._remove_nones(kwargs))

    @_cli
    def volume_unmask(self, vol=None, ag=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'ag': ag})
        return self._run('volume_unmask', **self._remove_nones(kwargs))

    @_cli
    def volume_enable(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_enable', **self._remove_nones(kwargs))

    @_cli
    def volume_disable(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_disable', **self._remove_nones(kwargs))

    @_cli
    def volume_raid_info(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_raid_info', **self._remove_nones(kwargs))

    @_cli
    def pool_member_info(self, pool=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'pool': pool})
        return self._run('pool_member_info', **self._remove_nones(kwargs))

    @_cli
    def access_group_create(self, name=None, init=None, sys=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'name': name, 'init': init, 'sys': sys})
        return self._run('access_group_create', **self._remove_nones(kwargs))

    @_cli
    def access_group_add(self, ag=None, init=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'ag': ag, 'init': init})
        return self._run('access_group_add', **self._remove_nones(kwargs))

    @_cli
    def access_group_remove(self, ag=None, init=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'ag': ag, 'init': init})
        return self._run('access_group_remove', **self._remove_nones(kwargs))

    @_cli
    def access_group_delete(self, ag=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'ag': ag})
        return self._run('access_group_delete', **self._remove_nones(kwargs))

    @_cli
    def access_group_volumes(self, ag=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'ag': ag})
        return self._run('access_group_volumes', **self._remove_nones(kwargs))

    @_cli
    def iscsi_chap(  # noqa: ANN201
        self,
        init=None,  # noqa: ANN001
        in_user=None,  # noqa: ANN001
        in_pass=None,  # noqa: ANN001
        out_user=None,  # noqa: ANN001
        out_pass=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        kwargs.update(
            {
                'init': init,
                'in_user': in_user,
                'in_pass': in_pass,
                'out_user': out_user,
                'out_pass': out_pass,
            },
        )
        return self._run('iscsi_chap', **self._remove_nones(kwargs))

    @_cli
    def fs_create(self, fs=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs})
        return self._run('fs_create', **self._remove_nones(kwargs))

    @_cli
    def fs_delete(self, fs=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs})
        return self._run('fs_delete', **self._remove_nones(kwargs))

    @_cli
    def fs_resize(self, fs=None, size=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs, 'size': size})
        return self._run('fs_resize', **self._remove_nones(kwargs))

    @_cli
    def fs_export(  # noqa: ANN201
        self,
        fs=None,  # noqa: ANN001
        exportpath=None,  # noqa: ANN001
        anonguid=None,  # noqa: ANN001
        anongid=None,  # noqa: ANN001
        auth_type=None,  # noqa: ANN001
        root_host=None,  # noqa: ANN001
        ro_host=None,  # noqa: ANN001
        rw_host=None,  # noqa: ANN001
        **kwargs,  # noqa: ANN003
    ):
        kwargs.update(
            {
                'fs': fs,
                'exportpath': exportpath,
                'anonguid': anonguid,
                'anongid': anongid,
                'auth_type': auth_type,
                'root_host': root_host,
                'ro_host': ro_host,
                'rw_host': rw_host,
            },
        )
        return self._run('fs_export', **self._remove_nones(kwargs))

    @_cli
    def fs_unexport(self, export=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'export': export})
        return self._run('fs_unexport', **self._remove_nones(kwargs))

    @_cli
    def fs_clone(self, src_fs=None, dst_name=None, backing_snapshot=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update(
            {
                'src_fs': src_fs,
                'dst_name': dst_name,
                'backing_snapshot': backing_snapshot,
            },
        )
        return self._run('fs_clone', **self._remove_nones(kwargs))

    @_cli
    def fs_snap_create(self, name=None, fs=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'name': name, 'fs': fs})
        return self._run('fs_snap_create', **self._remove_nones(kwargs))

    @_cli
    def fs_snap_delete(self, snap=None, fs=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'snap': snap, 'fs': fs})
        return self._run('fs_snap_delete', **self._remove_nones(kwargs))

    @_cli
    def fs_snap_restore(self, fs=None, snap=None, lsm_file=None, fileas=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs, 'snap': snap, 'lsm_file': lsm_file, 'fileas': fileas})
        return self._run('fs_snap_restore', **self._remove_nones(kwargs))

    @_cli
    def fs_dependants(self, fs=None, lsm_file=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs, 'lsm_file': lsm_file})
        return self._run('fs_dependants', **self._remove_nones(kwargs))

    @_cli
    def fs_dependants_rm(self, fs=None, lsm_file=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs, 'lsm_file': lsm_file})
        return self._run('fs_dependants_rm', **self._remove_nones(kwargs))

    @_cli
    def file_clone(self, fs=None, src=None, dst=None, backing_snapshot=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'fs': fs, 'src': src, 'dst': dst, 'backing_snapshot': backing_snapshot})
        return self._run('file_clone', **self._remove_nones(kwargs))

    @_cli
    def system_read_cache_pct_update(self, sys=None, read_pct=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'sys': sys, 'read_pct': read_pct})
        return self._run('system_read_cache_pct_update', **self._remove_nones(kwargs))

    @_cli
    def local_disk_list(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('local_disk_list', **self._remove_nones(kwargs))

    @_cli
    def volume_cache_info(self, vol=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol})
        return self._run('volume_cache_info', **self._remove_nones(kwargs))

    @_cli
    def volume_phy_disk_cache_update(self, vol=None, policy=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'policy': policy})
        return self._run('volume_phy_disk_cache_update', **self._remove_nones(kwargs))

    @_cli
    def volume_read_cache_policy_update(self, vol=None, policy=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'policy': policy})
        return self._run('volume_read_cache_policy_update', **self._remove_nones(kwargs))

    @_cli
    def volume_write_cache_policy_update(self, vol=None, policy=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'vol': vol, 'policy': policy})
        return self._run('volume_write_cache_policy_update', **self._remove_nones(kwargs))

    @_cli
    def local_disk_ident_led_on(self, path=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'path': path})
        return self._run('local_disk_ident_led_on', **self._remove_nones(kwargs))

    @_cli
    def local_disk_ident_led_off(self, path=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'path': path})
        return self._run('local_disk_ident_led_off', **self._remove_nones(kwargs))

    @_cli
    def local_disk_fault_led_on(self, path=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'path': path})
        return self._run('local_disk_fault_led_on', **self._remove_nones(kwargs))

    @_cli
    def local_disk_fault_led_off(self, path=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        kwargs.update({'path': path})
        return self._run('local_disk_fault_led_off', **self._remove_nones(kwargs))

    def help(self, cmd=''):  # noqa: ANN001, ANN201
        """Retrieve help.
        The arguments are:
        cmd - optional | get help on this command
        Returns:
        Boolean:
        True if success
        False in case of failure.
        """
        if cmd and cmd not in list(self.commands.keys()):
            logging.error(f'Unknown command {cmd}.')
            return False

        command = f"{cmd.replace('_', '-')} -h"
        return run(command)

    def version(self, cmd=''):  # noqa: ANN001, ANN201
        """Retrieve plugin version.
        The arguments are:
        cmd - optional | get version of this command
        Returns:
        Boolean:
        True if success
        False in case of failure.
        """
        if cmd and cmd not in list(self.commands.keys()):
            logging.error(f'Unknown command {cmd}.')
            return False

        command = f"{cmd.replace('_', '-')} -v"
        return run(command)
