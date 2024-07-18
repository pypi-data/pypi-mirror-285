#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest
from unittest.mock import call, patch

import sts.utils.logchecker as log_checker
from sts.utils.cmdline import run

# found segfault
segfault_msg = (
    ' segfault at 10 ip 00007f9bebcca90d sp 00007fffb62705f0 error 4 in libQtWebKit.so.4.5.2[7f9beb83a000+f6f000]'
)
calltrace_msg = ' Call Trace: '


def _run_dmesg_segfault(cmd, **kwargs):
    if cmd.startswith('dmesg | grep'):
        cmd = cmd.replace('dmesg', f"echo '{segfault_msg}'")
        return run(cmd, **kwargs)

    return 0, ''


def _run_dmesg_calltrace(cmd, **kwargs):
    if cmd.startswith('dmesg | grep'):
        cmd = cmd.replace('dmesg', f"echo '{calltrace_msg}'")
        return run(cmd, **kwargs)

    return 0, ''


class Testlogchecker(unittest.TestCase):
    @patch('sts.utils.logchecker.run')
    def test_kernel_check(self, run_func):
        run_func.return_value.rc = 0
        run_func.return_value.stdout = '0'
        assert log_checker.kernel_check() is True
        # already handled taint
        run_func.return_value.rc = 0
        run_func.return_value.stdout = '1'
        assert log_checker.kernel_check() is True

    @patch('sts.utils.logchecker.run')
    def test_dmesg_check(self, run_func):
        run_func.return_value.rc = 0
        run_func.return_value.stdout = ''
        assert log_checker.dmesg_check() is True
        run_func.reset_mock()

        run_func.side_effect = _run_dmesg_segfault
        assert log_checker.dmesg_check() is False
        run_calls = [
            call("dmesg | grep -i ' segfault '"),
            call("echo '\nINFO found  segfault   Saving it\n'>> dmesg.log"),
            call('dmesg >> ./dmesg.log'),
            call("dmesg | grep -i 'Call Trace:'"),
        ]
        # print(run_func.call_args_list)
        run_func.assert_has_calls(run_calls)
        run_func.reset_mock()

        run_func.side_effect = _run_dmesg_calltrace
        assert log_checker.dmesg_check() is False
        run_calls = [
            call("dmesg | grep -i ' segfault '"),
            call("dmesg | grep -i 'Call Trace:'"),
            call("echo '\nINFO found Call Trace:  Saving it\n'>> dmesg.log"),
            call('dmesg >> ./dmesg.log'),
        ]
        # print(run_func.call_args_list)
        run_func.assert_has_calls(run_calls)
        run_func.reset_mock()

    @patch('sts.utils.logchecker.kernel_check')
    def test_check_all(self, check_func):
        check_func.return_value = False
        assert log_checker.check_all() is False
