"""stratis.py: Module with test specific method for Stratis."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from sts import linux
from sts.blockdevice import LinuxBlockDeviceExtended
from sts.utils.cmdline import run

if TYPE_CHECKING:
    from testinfra.backend.base import CommandResult

CLI_NAME = 'stratis'
PACKAGE_NAME = 'stratis-cli stratisd'


class Stratis:
    """_summary_."""

    def __init__(
        self,
        propagate: bool = False,
        unhyphenated_uuids: bool = False,
    ) -> None:
        self.propagate = propagate
        self.unhyphenated_uuids = unhyphenated_uuids
        self.available_blockdevs: list[str] = []

        if not linux.install_package(PACKAGE_NAME):
            logging.critical(f'Could not install {PACKAGE_NAME}')
        if not linux.service_start('stratisd'):
            logging.critical('Could not start stratisd.service!')

    def _run(
        self,
        subcommand: str | None = None,
        action: str | None = None,
        options: dict[str, str] | dict[str, str | None] | None = None,
        positional_args: list[str] | None = None,
    ) -> CommandResult:
        command_list: list[str] = [CLI_NAME]
        if self.propagate:
            command_list.append('--propagate')
        if self.unhyphenated_uuids:
            command_list.append('--unhyphenated_uuids')
        if subcommand is not None:
            command_list.append(subcommand)
        if action is not None:
            command_list.append(action)
        if options is not None:
            command_list = command_list + [k if v is None else f'{k} {v}' for k, v in options.items()]
        if positional_args:
            command_list.extend(positional_args)
        command: str = ' '.join(command_list)
        return run(command)

    @staticmethod
    def setup_blockdevices() -> list[str]:
        blockdevices = LinuxBlockDeviceExtended.get_free_disks()

        filtered_disks_by_block_sizes: dict[tuple[str, str], list[str]] = {}
        for disk in blockdevices:
            block_sizes_tuple = (str(disk.sector_size), str(disk.block_size))
            if block_sizes_tuple in filtered_disks_by_block_sizes:
                filtered_disks_by_block_sizes[block_sizes_tuple].append(disk.device)
            else:
                filtered_disks_by_block_sizes[block_sizes_tuple] = [disk.device]

        logging.info('Find devices with the most common logical block sizes and physical block sizes')
        most_common_block_sizes: list[str] = []
        block_size_of_chosen_disks: tuple[str, str] = ('0', '0')
        for block_size in filtered_disks_by_block_sizes:
            logging.info(
                f"Found following disks with block "
                f"sizes {', '.join(block_size)}: {','.join(filtered_disks_by_block_sizes[block_size])}",
            )
            if len(filtered_disks_by_block_sizes[block_size]) > len(most_common_block_sizes):
                most_common_block_sizes = filtered_disks_by_block_sizes[block_size]
                block_size_of_chosen_disks = block_size
        logging.info(
            f"Using following disks: {', '.join(block_size_of_chosen_disks)}"
            f" with block sizes: {', '.join(block_size_of_chosen_disks)}",
        )
        disks = most_common_block_sizes

        disk_paths = []
        for disk in disks:
            if '/dev' not in disk:
                disk_paths.append(f'/dev/{disk}')
                continue
            disk_paths.append(disk)

        logging.info(f"Using blockdevs: {' '.join(disk_paths)}")
        for disk in disk_paths:
            run(f'dd if=/dev/zero of={disk} bs=1M count=10')
        return disk_paths

    def version(self) -> CommandResult:
        return self._run(action='--version')


class Pool(Stratis):
    """_summary_."""

    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'pool'

    def create(
        self,
        pool_name: str,
        blockdevs: list[str],
        key_desc: str | None = None,
        tang_url: str | None = None,
        thumbprint: str | None = None,
        clevis: str | None = None,
        trust_url: bool = False,
        no_overprovision: bool = False,
    ) -> CommandResult:
        options = {}
        if key_desc:
            options['--key-desc'] = key_desc
        if clevis:
            options['--clevis'] = clevis
        if tang_url:
            options['--tang-url'] = tang_url
        if thumbprint:
            options['--thumbprint'] = thumbprint
        if trust_url:
            options['--trust-url'] = ''
        if no_overprovision:
            options['--no-overprovision'] = ''
        return self._run(
            subcommand=self.subcommand,
            action='create',
            options=options,
            positional_args=[pool_name, ' '.join(blockdevs)],
        )

    def stop(self, pool_uuid: str | None = None, pool_name: str | None = None) -> CommandResult:
        options = {}
        if pool_uuid:
            options['--uuid'] = pool_uuid
        if pool_name:
            options['--name'] = pool_name
        return self._run(self.subcommand, action='stop', options=options)

    def start(
        self,
        unlock_method: str | None = None,
        pool_uuid: str | None = None,
        pool_name: str | None = None,
    ) -> CommandResult:
        options = {}
        if unlock_method:
            options['--unlock-method'] = unlock_method
        if pool_uuid:
            options['--uuid'] = pool_uuid
        if pool_name:
            options['--name'] = pool_name
        return self._run(self.subcommand, action='start', options=options)

    def init_cache(self, pool_name: str, blockdevs: list[str]) -> CommandResult:
        return self._run(
            subcommand=self.subcommand,
            action='init-cache',
            positional_args=[pool_name, ' '.join(blockdevs)],
        )

    def list_pools(
        self,
        pool_name: str | None = None,
        pool_uuid: str | None = None,
        stopped: bool = False,
    ) -> CommandResult:
        options = {}
        if pool_name:
            options['--name'] = pool_name
        if pool_uuid:
            options['--uuid'] = pool_uuid
        if stopped:
            options['--stopped'] = ''
        return self._run(subcommand=self.subcommand, action='list', options=options)

    def destroy(
        self,
        pool_name: str,
    ) -> CommandResult:
        return self._run(subcommand=self.subcommand, action='destroy', positional_args=[pool_name])

    def rename(
        self,
        current: str,
        new: str,
    ) -> CommandResult:
        return self._run(subcommand=self.subcommand, action='rename', positional_args=[current, new])

    def add_data(
        self,
        pool_name: str,
        blockdevs: list[str],
    ) -> CommandResult:
        return self._run(
            subcommand=self.subcommand,
            action='add-data',
            positional_args=[pool_name, ' '.join(blockdevs)],
        )

    def add_cache(
        self,
        pool_name: str,
        blockdevs: list[str],
    ) -> CommandResult:
        return self._run(
            subcommand=self.subcommand,
            action='add-cache',
            positional_args=[pool_name, ' '.join(blockdevs)],
        )

    def extend_data(self, pool_name: str, device_uuids: list[str] | None = None) -> CommandResult:
        options = {}
        if device_uuids:
            options['--device-uuid'] = ' '.join(device_uuids)
        return self._run(self.subcommand, action='extend-data', options=options, positional_args=[pool_name])

    def bind_tang(
        self,
        pool_name: str,
        tang_url: str,
        trust_url: bool = False,
        thumbprint: str | None = None,
    ) -> CommandResult:
        options = {}
        if trust_url:
            options['--trust-url'] = ''
        if thumbprint:
            options['--thumbprint'] = thumbprint
        return self._run(subcommand=self.subcommand, action='bind tang', positional_args=[pool_name, tang_url])

    def bind_tpm2(self, pool_name: str) -> CommandResult:
        return self._run(subcommand=self.subcommand, action='bind tpm2', positional_args=[pool_name])

    def bind_keyring(self, pool_name: str, keydesc: str) -> CommandResult:
        return self._run(self.subcommand, action='bind keyring', positional_args=[pool_name, keydesc])

    def rebind_clevis(self, pool_name: str) -> CommandResult:
        return self._run(self.subcommand, action='rebind clevis', positional_args=[pool_name])

    def rebind_keyring(self, pool_name: str, keydesc: str) -> CommandResult:
        return self._run(self.subcommand, action='rebind keyring', positional_args=[pool_name, keydesc])

    def unbind_keyring(self, pool_name: str) -> CommandResult:
        return self._run(self.subcommand, action='unbind keyring', positional_args=[pool_name])

    def unbind_clevis(self, pool_name: str) -> CommandResult:
        return self._run(self.subcommand, action='unbind clevis', positional_args=[pool_name])

    def set_fs_limit(
        self,
        pool_name: str,
        amount: str,
    ) -> CommandResult:
        return self._run(self.subcommand, action='set-fs-limit', positional_args=[pool_name, amount])

    def overprovision(
        self,
        pool_name: str,
        decision: str,
    ) -> CommandResult:
        return self._run(self.subcommand, action='overprovision', positional_args=[pool_name, decision])

    def explain(self, error_code: str) -> CommandResult:
        return self._run(self.subcommand, action='explain', positional_args=[error_code])

    def debug_pool(
        self,
        pool_name: str | None = None,
        pool_uuid: str | None = None,
    ) -> CommandResult:
        options = {}
        if pool_name:
            options['--name'] = pool_name
        if pool_uuid:
            options['--uuid'] = pool_uuid
        return self._run(self.subcommand, action='debug get-object-path', options=options)

    def get_pool_uuid(self, pool_name: str) -> str | None:
        result = self._run('report')
        if result.exit_status == 0 and result.stdout:
            try:
                report = json.loads(result.stdout)
            except json.JSONDecodeError:
                return None
            for pool in report['pools']:
                if pool_name == pool['name']:
                    return pool['uuid']
            return None
        return None


class Blockdev(Stratis):
    """Summary."""

    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'blockdev'

    def list_blockdev(self, pool_name: str) -> CommandResult:
        return self._run(self.subcommand, action='list', positional_args=[pool_name])

    def debug(self, uuid: str) -> CommandResult:
        options = {'--uuid': uuid}
        return self._run(self.subcommand, action='debug get-object-path', options=options)


class Filesystem(Stratis):
    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'filesystem'

    def create(
        self,
        pool_name: str,
        fs_name: str,
        size: str | None = None,
        size_limit: str | None = None,
    ) -> CommandResult:
        options = {}
        if size:
            options['--size'] = size
        if size_limit:
            options['--size-limit'] = size_limit
        return self._run(self.subcommand, action='create', options=options, positional_args=[pool_name, fs_name])

    def snapshot(
        self,
        pool_name: str,
        origin_name: str,
        snapshot_name: str,
    ) -> CommandResult:
        return self._run(self.subcommand, action='snapshot', positional_args=[pool_name, origin_name, snapshot_name])

    def list_filesystems(self, pool_name: str | None = None) -> CommandResult:
        args = None
        if pool_name:
            args = [pool_name]
        return self._run(self.subcommand, action='list', positional_args=args)

    def destroy(
        self,
        pool_name: str,
        fs_name: list[str],
    ) -> CommandResult:
        return self._run(self.subcommand, action='destroy', positional_args=[pool_name, ' '.join(fs_name)])

    def rename(self, pool_name: str, fs_name: str, new_name: str) -> CommandResult:
        return self._run(self.subcommand, action='rename', positional_args=[pool_name, fs_name, new_name])

    def set_size_limit(self, pool_name: str, fs_name: str, limit: str) -> CommandResult:
        return self._run(self.subcommand, action='set-size-limit', positional_args=[pool_name, fs_name, limit])

    def unset_size_limit(self, pool_name: str, fs_name: str) -> CommandResult:
        return self._run(self.subcommand, action='unset-size-limit', positional_args=[pool_name, fs_name])

    def debug(self, name: str | None = None, uuid: str | None = None) -> CommandResult:
        options = {}
        if name:
            options['--name'] = name
        if uuid:
            options['--uuid'] = uuid
        return self._run(self.subcommand, action='debug get-object-path', options=options)

    def get_fs_uuid(self, pool_name: str, fs_name: str) -> str | None:
        result = self._run('report')
        if result.exit_status == 0 and result.stdout:
            try:
                report = json.loads(result.stdout)
            except json.JSONDecodeError:
                return None
            for pool in report['pools']:
                if pool_name != pool['name']:
                    continue
                for fs in pool['filesystems']:
                    if fs_name != fs['name']:
                        continue
                    return fs['uuid']
            return None
        return None


class Report(Stratis):
    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'report'

    def engine_state_report(self) -> CommandResult:
        return self._run(self.subcommand, action='engine_state_report')

    def managed_objects_report(self) -> CommandResult:
        return self._run(self.subcommand, action='managed_objects_report')

    def stopped_pools(self) -> CommandResult:
        return self._run(self.subcommand, action='stopped_pools')


class Key(Stratis):
    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'key'

    def set(
        self,
        keydesc: str,
        keyfile_path: str | None = None,
        capture_key: bool = False,
    ) -> CommandResult:
        options = {}
        if keyfile_path:
            options['--keyfile-path'] = keyfile_path
        if capture_key:
            options['--capture-key'] = ''
        return self._run(self.subcommand, action='set', options=options, positional_args=[keydesc])

    def reset(
        self,
        keydesc: str,
        keyfile_path: str | None = None,
        capture_key: bool = False,
    ) -> CommandResult:
        options = {}
        if keyfile_path:
            options['--keyfile-path'] = keyfile_path
        if capture_key:
            options['--capture-key'] = ''
        return self._run(self.subcommand, action='reset', options=options, positional_args=[keydesc])

    def unset(self, keydesc: str) -> CommandResult:
        return self._run(self.subcommand, action='unset', positional_args=[keydesc])

    def list_keys(self) -> CommandResult:
        return self._run(self.subcommand, action='list')


class Debug(Stratis):
    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'debug'

    def refresh(self) -> CommandResult:
        return self._run(self.subcommand, action='refresh')

    def uevent(self, device: str) -> CommandResult:
        return self._run(self.subcommand, action='uevent', positional_args=[device])


class Daemon(Stratis):
    def __init__(self) -> None:
        super().__init__()
        self.subcommand = 'daemon'

    def version(self) -> CommandResult:
        return self._run(self.subcommand, action='version')
