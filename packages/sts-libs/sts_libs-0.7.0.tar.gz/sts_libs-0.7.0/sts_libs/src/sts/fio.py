"""fio.py: Module to run FIO util."""

from __future__ import annotations

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
import logging

from sts.linux import install_package
from sts.utils.cmdline import run

DEFAULT_PARAMS = {
    'name': 'sts fio default',
    'ioengine': 'libaio',  # Use Linux native asynchronous I/O
    'direct': '1',  # Use direct I/O (O_DIRECT)
    'rw': 'randrw',  # Perform random read and write operations
    'bs': '4k',  # Block size
    'numjobs': '1',  # Run a single job (thread)
    'iodepth': '32',  # Number of I/O units to keep in flight against the file
    'runtime': '60',  # Run the test for 1 minute (60 seconds)
    'group_reporting': '1',  # Report statistics for the job group, when numjobs > 1
    'do_verify': '1',  # Verify data after write phase
    'verify_fatal': '1',  # Exit on the first observed verification failure
    'verify': 'crc32',  # Use CRC32 for data verification
    'verify_backlog': '1024',  # Verify data continuously after every 1024 blocks
}

FILE_SYSTEM_PARAMS = {
    'name': 'sts fio filesystem',
    'ioengine': 'sync',  # Use basic read(2) or write(2) I/O
    'rw': 'write',  # Perform sequential write operations
    'bs': '1M',  # Set the block size to 1 MiB for large sequential I/O
    'numjobs': '1',  # Run a single job (thread)
    'size': '10G',  # Write 10 GiB of data for the test
    'direct': '1',  # Use direct I/O (O_DIRECT)
    'end_fsync': '1',  # Sync file contents when the write stage has completed
}

BLOCK_DEVICE_PARAMS = {
    'name': 'sts fio block',
    'ioengine': 'libaio',  # Use Linux native asynchronous I/O
    'rw': 'randread',  # Perform random read operations
    'bs': '512',  # Set the block size to 512 bytes (typical block size for disks)
    'numjobs': '4',  # Run 4 parallel jobs (threads)
    'iodepth': '32',  # Number of I/O units to keep in flight against the file
    'runtime': '1800',  # Run the test for 30 minutes (1800 seconds)
    'direct': '1',  # Use direct I/O (O_DIRECT)
    'group_reporting': '',  # Report statistics for the job group
}

STRESS_PARAMS = {
    'name': 'sts fio stress',
    'ioengine': 'libaio',  # Use Linux native asynchronous I/O
    'direct': '1',  # Use direct I/O (O_DIRECT)
    'rw': 'randrw',  # Perform random read and write operations
    'bs': '4k',  # Set the block size to 4 KiB
    'numjobs': '64',  # Run 64 parallel jobs to simulate heavy concurrent load
    'iodepth': '64',  # Use an I/O depth of 64 for each job
    'runtime': '3600',  # Run the test for 1 hour (3600 seconds)
    'group_reporting': '',  # Report statistics for the job group
    'norandommap': '',  # Use sequential mapping for tests
}


class FIO:
    def __init__(
        self,
        filename: str,
        parameters: dict[str, str] | None = None,
        options: list[str] | None = None,
    ) -> None:
        self.filename = filename
        self.parameters = parameters or {}
        if not self.parameters:
            self.load_default_params()
        self.options = options or []

        install_package('fio')

    def update_parameters(self, param_dict: dict[str, str]) -> None:
        # update_parameters({'runtime': '600', 'size': '20%'})
        self.parameters.update(param_dict)

    def update_options(self, option_list: list[str]) -> None:
        # update_options(['minimal', 'readonly'])
        self.options = list(set(self.options + option_list))

    def load_default_params(self) -> None:
        self.update_parameters(DEFAULT_PARAMS)

    def load_stress_params(self) -> None:
        self.update_parameters(STRESS_PARAMS)

    def load_fs_params(self) -> None:
        self.update_parameters(FILE_SYSTEM_PARAMS)

    def load_block_params(self) -> None:
        self.update_parameters(BLOCK_DEVICE_PARAMS)

    def _create_fio_command(self) -> str:
        command_parameters = ' '.join(f'--{k}="{v}"' for k, v in self.parameters.items() if v)
        command = f'fio --filename "{self.filename}" {command_parameters}'
        if self.options:
            command_options = ' '.join(f'--{option}' for option in self.options)
            command = f'{command} {command_options}'
        return command

    def run(self) -> bool:
        """Runs the FIO command with the provided parameters.

        If no parameters are provided, it loads the default parameters.

        Returns:
            True if the FIO command executed successfully, False otherwise.
        """
        command = self._create_fio_command()

        result = run(command)
        if not result.succeeded:
            logging.error(f'FIO run failed:\n{result.stderr}')
            return False
        logging.info('FIO executed successfully')
        return True
