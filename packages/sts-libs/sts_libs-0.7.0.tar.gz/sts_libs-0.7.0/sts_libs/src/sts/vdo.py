"""vdo.py: Module with test specific method for VDO."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import logging
import stat
from contextlib import suppress
from difflib import context_diff
from pathlib import Path

from sts import linux
from sts.utils.cli_tools import (
    FailedCheckExceptionError,
    Wrapper,
    WrongArgumentExceptionError,
    WrongCommandExceptionError,
)
from sts.utils.cmdline import run, run_ret_out


def report_modify_difference(errors, status_old, status_new, changed_var, changed_argument):  # noqa: ANN001, ANN201
    status_old = [x for x in status_old.splitlines() if changed_var in x]
    status_new = [x for x in status_new.splitlines() if changed_var in x]
    print(f"Before: {', '.join(status_old)}")
    print(f"After:  {', '.join(status_new)}")
    diff = list(context_diff(status_old, status_new))
    difference = '\n'.join([x for x in diff if x.startswith('!')])

    if not difference:
        error = f'WARN: Modifying VDO to {changed_argument} did nothing.'
        print(error)
        errors.append(error)


def minimum_slab_size(device, default_to_2g=True):  # noqa: ANN001, ANN201
    def _get_raid_device(device):  # noqa: ANN001, ANN202
        device_name = device.split('/').pop()
        ret, device_link = run_ret_out(cmd=f'ls -al /dev/md | grep {device_name}', return_output=True)
        if ret or device_link is None:
            logging.warning(f'Device {device_name} not found in /dev/md.')
            return None
        return device_link.split('../').pop()  # raid device

    device_name = _get_raid_device(device) if device.startswith('/dev/md') else device.split('/').pop()
    ret, device_size = run_ret_out(cmd=f"lsblk | grep '{device_name} ' ", return_output=True)
    if ret or device_size is None:
        logging.warning(f'Device {device_name} not found using lsblk. Using default 2G size.')
        return '2G'
    size = device_size.split()[3]
    multipliers = ['M', 'G', 'T', 'P', 'E']
    device_size = int(float(size[:-1]) * (1024 ** multipliers.index(size[-1:])))
    max_number_of_slabs = 8192
    minimum_size = 2 ** int(device_size / max_number_of_slabs).bit_length()
    minimum_size = max(minimum_size, 128)
    if default_to_2g and minimum_size < 2048:
        return '2G'
    return str(minimum_size) + 'M'


def maximum_logical_size():  # noqa: ANN201
    """Returns maximum logical size based on memory.

    Returns:
      string max_size.
    """
    good_size = 4096
    memory = linux.get_memory()['mem']['free']
    size = f'{good_size}T'
    if memory < 10000:
        size = 2 ** (int((4096.0 / 10000) * float(memory)).bit_length() - 1)
        size = min(size, good_size)
    return size


def is_block_device(device):  # noqa: ANN001, ANN201
    try:
        mode = Path(device).stat().st_mode
    except OSError:
        return f'Device {device} does not exist.'

    if not stat.S_ISBLK(mode):
        msg = f'Device {device} is not block device, aborting.'
        print(msg)
        return msg
    return True


def get_underlying_device(name, conf_file='/etc/vdoconf.yml'):  # noqa: ANN001, ANN201
    vdo = VDO(disable_check=True)
    ret, data = vdo.status(name=name, return_output=True, verbosity=False, conf_file=conf_file)
    if ret != 0:
        msg = f"FAIL: Could not get status of VDO device '{name}'."
        print(msg)
        return None
    device = None
    for line in data.splitlines():
        if 'Storage device' in line:
            device = f"/dev/{line.split('/dev/').pop().split().pop(0).strip()}"
    if device is None:
        # The device is probably crashed and needs to be force removed
        logging.warning("Could not find 'Device mapper status' in vdo status output.")
        # Let's try alternative way of getting the device by checking vdo config file
        # First get the config file
        conf_file = None
        for line in data.splitlines():
            if 'File:' in line:
                conf_file = line.split('File:').pop().strip()
        if not conf_file:
            logging.error('Could not find vdo conf file in vdo status, something is really wrong!')
            return None
        # Read the file contents
        with Path(conf_file).open() as f:
            lines = f.readlines()
        correct_vdo_device = False
        for line in lines:
            if f'{name}:' in line:
                # Get the correct VDO device in the config, there might be more
                correct_vdo_device = True
            if correct_vdo_device and 'device:' in line:
                # Now we have the device, just need to follow the link
                device = line.split('device:').pop().strip()
                break

    # now we might have /dev/disk/by-id/UUID, need to get something reasonable
    device = run(f'ls -la {device}').stdout.rstrip().split('/').pop().strip()

    # format dm-X causes issues later on, where the device cannot be found using lsblk to check for size
    if device.startswith('dm-'):
        with Path(f'/sys/block/{device}/dm/name').open() as f:
            dev_name = f.readline().rstrip('\n')
        device = f'/dev/mapper/{dev_name}'
    else:
        device = f'/dev/{device}'

    return device


def get_replace_dict():  # noqa: ANN201
    """Returns dict of keys to replace from fmf to sts.vdo.VDO.

    Returns:
      dict.
    """
    return {'vdo_name': 'name'}


class VDO(Wrapper):
    def __init__(self, disable_check=False) -> None:  # noqa: ANN001
        self.disable_check = disable_check

        self.commands: dict[str, str | list[str]] = {
            'create': 'create',
            'remove': 'remove',
            'start': 'start',
            'stop': 'stop',
            'activate': 'activate',
            'deactivate': 'deactivate',
            'status': 'status',
            'list': 'list',
            'modify': 'modify',
            'change_write_policy': 'changeWritePolicy',
            'enable_deduplication': 'enableDeduplication',
            'disable_deduplication': 'disableDeduplication',
            'enable_compression': 'enableCompression',
            'disable_compression': 'disableCompression',
            'grow_logical': 'growLogical',
            'grow_physical': 'growPhysical',
            'print_config_file': 'printConfigFile',
        }
        self.commands['all'] = list(self.commands.keys())

        self.arguments = {
            'all': [self.commands['all'], ' --all'],
            'conf_file': [self.commands['all'], ' --confFile='],
            'log_file': [self.commands['all'], ' --logfile='],
            'name': [self.commands['all'], ' --name='],
            'no_run': [self.commands['all'], ' --noRun'],
            'verbose': [self.commands['all'], ' --verbose'],
            'activate': [['create'], ' --activate='],
            'compression': [['create'], ' --compression='],
            'deduplication': [['create'], ' --deduplication='],
            'device': [['create'], ' --device='],
            'emulate512': [['create'], ' --emulate512='],
            'index_mem': [['create'], ' --indexMem='],
            'sparse_index': [['create'], ' --sparseIndex='],
            'logical_size': [['create', 'grow_logical'], ' --vdoLogicalSize='],
            'log_level': [['create'], ' --vdoLogLevel='],
            'slab_size': [['create'], ' --vdoSlabSize='],
            'block_map_cache_size': [['create', 'modify'], ' --blockMapCacheSize='],
            'block_map_period': [['create', 'modify'], ' --blockMapPeriod='],
            'max_discard_size': [['create', 'modify'], ' --maxDiscardSize='],
            'ack_threads': [['create', 'modify'], ' --vdoAckThreads='],
            'bio_rotation_interval': [
                ['create', 'modify'],
                ' --vdoBioRotationInterval=',
            ],
            'bio_threads': [['create', 'modify'], ' --vdoBioThreads='],
            'cpu_threads': [['create', 'modify'], ' --vdoCpuThreads='],
            'hash_zone_threads': [['create', 'modify'], ' --vdoHashZoneThreads='],
            'logical_threads': [['create', 'modify'], ' --vdoLogicalThreads='],
            'physical_threads': [['create', 'modify'], ' --vdoPhysicalThreads='],
            'write_policy': [
                ['create', 'modify', 'change_write_policy'],
                ' --writePolicy=',
            ],
            'force_rebuild': [['start'], ' --forceRebuild'],
            'force': [['stop', 'remove', 'create'], ' --force'],
        }

        Wrapper.__init__(self, self.commands, self.arguments, self.disable_check)

    @staticmethod
    def _check_size_format(size, return_size=False):  # noqa: ANN001, ANN205
        # check if requested size format is in supported formats and the rest is numbers
        # FIXME: Is KiB and KB valid too?
        size = size.strip("'")
        with suppress(ValueError):
            if size[-3:] in {'KiB', 'MiB', 'GiB', 'TiB'} and isinstance(int(size[:-3]), int):
                if return_size:
                    return True, [size[:-3], size[-3:-2]]
                return True
            if size[-2:] in {'KB', 'MB', 'GB', 'TB'} and isinstance(int(size[:-2]), int):
                if return_size:
                    return True, [size[:-2], size[-2:-1]]
                return True
            if size[-1:].upper() in {'K', 'M', 'G', 'T'} and isinstance(int(size[:-1]), int):
                if return_size:
                    return True, [size[:-1], size[-1:]]
                return True
            if int(size):
                if return_size:
                    # default size is megabytes
                    return True, [size, 'M']
                return True
        return False, []

    @staticmethod
    def _is_positive_int(value):  # noqa: ANN001, ANN205
        try:
            port = int(value)
            if port < 1:
                raise ValueError  # noqa: TRY301
        except ValueError:
            return False
        return True

    def _check(self, cmd):  # noqa: ANN001, ANN202
        if self.disable_check:
            # Do not check if checking is disabled
            return True

        if self._get_arg('all') in cmd and self._get_arg('name') in cmd:
            logging.warning("Use either 'name' or 'all', not both.")
            raise FailedCheckExceptionError

        if self._get_arg('conf_file') in cmd:
            _file = self._get_value(cmd, self._get_arg('conf_file'))
            if not Path(_file).is_file():
                logging.warning(f'Config file {_file} is not a regular file.')
                raise FailedCheckExceptionError(self._get_arg('conf_file'))

        if self._get_arg('log_file') in cmd:
            _file = self._get_value(cmd, self._get_arg('log_file'))
            f = Path(_file)
            if not f.is_file() and stat.S_ISBLK(f.stat().st_mode):
                logging.warning(f'Path {_file} exists and is not a regular file.')
                raise FailedCheckExceptionError(self._get_arg('log_file'))

        if self._get_arg('name') in cmd:
            # FIXME: Check if VDO already exists
            pass

        for arg in (
            'activate',
            'compression',
            'deduplication',
            'emulate512',
            'sparse_index',
        ):
            if self._get_arg(arg) in cmd:
                _value = self._get_value(cmd, self._get_arg(arg))
                if _value not in {'enabled', 'disabled'}:
                    logging.warning(f"{arg} value must be either 'enabled' or 'disabled'.")
                    raise FailedCheckExceptionError(self._get_arg(arg))

        for arg in (
            'logical_size',
            'slab_size',
            'block_map_cache_size',
            'max_discard_size',
        ):
            if self._get_arg(arg) in cmd:
                _value = self._get_value(cmd, self._get_arg(arg))
                ret, _ = self._check_size_format(_value, return_size=True)
                if not ret:
                    logging.warning(f"VDO {' '.join(arg.split('_'))} value {_value} is in unknown format.")
                    raise FailedCheckExceptionError(self._get_arg(arg))
                if arg == 'slab_size':  # noqa: SIM114
                    pass
                    # FIXME: Check if size is power of 2 between 128M and 32G
                elif arg == 'block_map_cache_size':
                    pass
                    # FIXME: Check if size is multiple of 4096

        if self._get_arg('index_mem') in cmd:
            _value = self._get_value(cmd, self._get_arg('index_mem'), return_type=float)
            if not (_value in {0, 0.25, 0.5, 0.75} or self._is_positive_int(_value)):
                logging.warning(f'Albireo mem value {_value} is not a 0, 0.25, 0.5, 0.75 or positive int.')
                raise FailedCheckExceptionError(self._get_arg('index_mem'))

        if self._get_arg('log_level') in cmd:
            _value = self._get_value(cmd, self._get_arg('log_level'))
            possible_values = [
                'critical',
                'error',
                'warning',
                'notice',
                'info',
                'debug',
            ]
            if _value not in possible_values:
                logging.warning(f'Unknown vdo log level value, must be one of {possible_values}.')
                raise FailedCheckExceptionError(self._get_arg('log_level'))

        if self._get_arg('device') in cmd:
            _value = self._get_value(cmd, self._get_arg('device'))
            # FIXME: Check if device exists

        if self._get_arg('block_map_period') in cmd:
            _value = self._get_value(cmd, self._get_arg('block_map_period'))
            if not self._is_positive_int(_value):
                logging.warning('Block map period value must be a positive integer.')
                raise FailedCheckExceptionError(self._get_arg('block_map_period'))
            # FIXME: Can this be higher than 16380?

        for arg in (
            'ack_threads',
            'bio_rotation_interval',
            'bio_threads',
            'cpu_threads',
            'hash_zone_threads',
            'logical_threads',
            'physical_threads',
        ):
            if self._get_arg(arg) in cmd:
                _value = self._get_value(cmd, self._get_arg(arg))
                if not self._is_positive_int(_value):
                    logging.warning(f"VDO {' '.join(arg.split('_'))} value must be a positive integer.")
                    raise FailedCheckExceptionError(self._get_arg(arg))
                    # FIXME: Is 0 valid?

        if self._get_arg('write_policy') in cmd:
            _value = self._get_value(cmd, self._get_arg('write_policy'))
            if _value not in {'sync', 'async'}:
                logging.warning("VDO read cache value must be either 'sync' or 'async'.")
                raise FailedCheckExceptionError(self._get_arg('write_policy'))

        if self._get_arg('force_rebuild') in cmd and self._get_arg('upgrade') in cmd:
            logging.warning('Cannot use both force_rebuild and upgrade when starting VDO volume.')
            raise FailedCheckExceptionError

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
            logging.warning(f"Given command '{e.command}' is not allowed in this VDO version.")
            return ret_fail
        except WrongArgumentExceptionError as e:
            message = f"WARN: Given argument '{e.argument}' is not allowed for given command."
            if e.command:
                message = message[:-1] + " '" + e.command + "'."
            if e.arguments:
                message += f"\nPlease use only these: {', '.join(e.arguments)}."
            print(message)
            return ret_fail

        cmd = 'vdo ' + command

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
    def help():  # noqa: ANN205
        if run('vdo --help') != 0:
            logging.warning("Running command: 'vdo --help' failed.")
            return False
        return True

    def create(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('create', **kwargs)

    def remove(self, force=True, **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run('remove', force=force, **kwargs)

    def start(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('start', **kwargs)

    def stop(self, force=True, **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run('stop', force=force, **kwargs)

    def restart(self) -> None:
        self.stop()
        self.start()

    def activate(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('activate', **kwargs)

    def deactivate(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('deactivate', **kwargs)

    def status(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('status', **kwargs)

    def list(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('list', **kwargs)

    def modify(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('modify', **kwargs)

    def change_write_policy(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('change_write_policy', **kwargs)

    def deduplication(self, enable=True, **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run('enable_deduplication', **kwargs) if enable else self._run('disable_deduplication', **kwargs)

    def compression(self, enable=True, **kwargs):  # noqa: ANN001, ANN003, ANN201
        return self._run('enable_compression', **kwargs) if enable else self._run('disable_compression', **kwargs)

    def grow(self, grow_type=None, **kwargs):  # noqa: ANN001, ANN003, ANN201
        if grow_type.upper() not in {'LOGICAL', 'PHYSICAL'}:
            logging.warning("Please specify either 'logical' or 'physical' type for growing VDO.")
            if kwargs['return_output']:
                return False, None
            return False

        if grow_type.upper() == 'LOGICAL':
            ret = self._run('grow_logical', **kwargs)
        else:
            ret = self._run('grow_physical', **kwargs)
        return ret

    def print_config_file(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run('print_config_file', **kwargs)


class VDOStats:
    def __init__(self, disable_check=False) -> None:  # noqa: ANN001
        self.disable_check = disable_check
        self.command = 'vdostats'
        self.arguments = {
            'help': ' --help',
            'all': ' --all',
            'human_readable': ' --human-readable',
            'si': ' --si',
            'verbose': ' --verbose',
            'version': ' --version',
        }

    def _get_arg(self, name):  # noqa: ANN001, ANN202
        return self.arguments[name]

    def _get_possible_arguments(self):  # noqa: ANN202
        # Returns possible arguments
        return list(self.arguments.keys())

    def _add_argument(self, arg, command):  # noqa: ANN001, ANN202
        # Checks if given argument is allowed and adds it to cmd string
        if arg not in self.arguments:
            return None
        argument = self._get_arg(arg)
        command += argument
        return command

    def _add_arguments(self, cmd, **kwargs):  # noqa: ANN001, ANN003, ANN202
        command = cmd
        for kwarg in kwargs:
            command = self._add_argument(kwarg, command)
            if command is None:
                args = self._get_possible_arguments()
                logging.warning(f"Unknown argument '{kwarg}', please use only these: {args}.")
                return None
        return command

    def _check(self, cmd):  # noqa: ANN001, ANN202
        if self.disable_check:
            # Do not check if checking is disabled
            return True

        # check if specified devices are block devices
        for block in cmd.split():
            file = Path(block)
            if (
                (block not in list(self.arguments.values()) and block != self.command)
                and file.exists()
                and not stat.S_ISBLK(file.stat().st_mode)
            ):
                logging.warning(f'Device {block} is not a block device.')
                return False

        return True

    def _run(self, **kwargs):  # noqa: ANN003, ANN202
        # Constructs the command to run and runs it
        cmd = self.command

        if 'devices' in kwargs:
            devices = kwargs.pop('devices')
            if isinstance(devices, list):
                for device in devices:
                    cmd += ' ' + str(device)
            else:
                cmd += ' ' + str(devices)

        cmd = self._add_arguments(cmd, **kwargs)
        if cmd is None:
            return False

        if not self._check(cmd):
            # Requested command did not pass checking, reason was already written by _check()
            return False

        if run(cmd).rc != 0:
            logging.warning(f"Running command: '{cmd}' failed.")
            return False
        return True

    def help(self):  # noqa: ANN201
        return self._run(help=True)

    def version(self):  # noqa: ANN201
        return self._run(version=True)

    def stats(self, **kwargs):  # noqa: ANN003, ANN201
        return self._run(**kwargs)
