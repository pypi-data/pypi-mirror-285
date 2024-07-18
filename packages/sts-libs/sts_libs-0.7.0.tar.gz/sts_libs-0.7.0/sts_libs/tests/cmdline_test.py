#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import unittest

from sts.utils.cmdline import run, run_ret_out


class TestCmdline(unittest.TestCase):
    def test_run_verbose(self) -> None:
        test_msg = 'run test message'
        # write to stderr, the message should be shown in the test
        test_cmd = f'echo {test_msg} >&2'
        verbose_log = f"INFO:root:Running: '{test_cmd}'"

        logger = logging.getLogger()
        with self.assertLogs(logger, level='DEBUG') as cm:
            result = run(test_cmd)

        assert result.rc == 0
        assert verbose_log == cm.output[0]

    def test_run_return_output(self) -> None:
        test_msg = 'run test message'
        test_cmd = f'echo {test_msg}'
        ret_out = run(test_cmd)
        assert ret_out.rc == 0
        assert ret_out.stdout == f'{test_msg}\n'

    def test_run_return_output_legacy(self) -> None:
        test_msg = 'run test message'
        test_cmd = f'echo {test_msg}'
        assert run_ret_out(test_cmd, return_output=True) == (0, test_msg)

    def test_run_fail_return_output(self) -> None:
        failure_msg = "ls: cannot access 'invalid_file': No such file or directory"
        test_cmd = 'ls invalid_file'
        ret_out = run(test_cmd)
        assert ret_out.rc == 2
        assert ret_out.stderr == f'{failure_msg}\n'

    def test_run_fail_return_output_legacy(self) -> None:
        failure_msg = "ls: cannot access 'invalid_file': No such file or directory"
        test_cmd = 'ls invalid_file'
        assert run_ret_out(test_cmd, return_output=True) == (2, failure_msg)
