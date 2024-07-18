"""beaker.py: Module to manage beaker."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import os
import re

from sts.utils.cmdline import run, run_ret_out
from sts.utils.restraint import is_restraint_job, log_submit


def get_task_timeout(task_id):  # noqa: ANN001, ANN201
    """Get how much time the task still has
    Parameter:
    task_id:          Beaker Task id
    Return:
    None:             In case of some problem
    or
    int(value):       The remaining time in seconds.
    """
    if not is_restraint_job():
        return None

    if task_id is None:
        logging.error('beaker get_task_timeout() - requires task_id as parameter')
        return None

    cmd = f'bkr watchdog-show {task_id}'
    ret, output = run_ret_out(cmd, return_output=True)
    if ret != 0:
        logging.error('beaker get_task_timeout() - Could not get beaker kill time')
        print(output)
        return None

    m = re.compile(r'%s: (\d+)' % task_id).match(output)  # noqa: UP031
    if m:
        return int(m.group(1))
    logging.error('beaker get_task_timeout() - Could not parse output:')
    print(output)
    return None


def get_task_status(task_id):  # noqa: ANN001, ANN201
    """Requires beaker-client package installed and configured."""
    if not is_restraint_job():
        return None

    if not task_id:
        logging.error('get_task_status() - requires task id')
        return None

    cmd = f'bkr job-results --prettyxml T:{task_id}'
    ret, output = run_ret_out(cmd, return_output=True)
    if ret != 0:
        logging.error(f'get_task_status() - Could not get beaker task result for T:{task_id}')
        print(output)
        return None

    lines = output.split('\n')
    status_regex = re.compile(r'<task.*status=\"(\S+)\"')
    for line in lines:
        m = status_regex.match(line)
        if m:
            return m.group(1)
    return None


def console_log_check(error_mgs):  # noqa: ANN001, ANN201
    """Checks for error messages on console log ("Call Trace and segfault")."""
    error = 0
    console_log_file = '/root/console.log'
    prev_console_log_file = '/root/console.log.prev'
    new_console_log_file = '/root/console.log.new'

    if not is_beaker_job():
        logging.warning("skip console_log_check as it doesn't seem to be a beaker job")
        return True

    lab_controller = os.environ['LAB_CONTROLLER']
    recipe_id = os.environ['BEAKER_RECIPE_ID']

    # get current console log
    url = f'http://{lab_controller}:8000/recipes/{recipe_id}/logs/console.log'

    if run(f'curl -s {url} -O {new_console_log_file}') != 0:
        logging.info('Could not get console log')
        # return success when could not get console.log
        return True

    # if there was previous console log, we just check the new part
    run(
        f'diff -N -n --unidirectional-new-file {prev_console_log_file} {new_console_log_file} > {console_log_file}',
    )

    # backup the current full console.log
    # next time we run the test we will compare just
    # what has been appended to console.log
    run(f'mv -f {new_console_log_file} {prev_console_log_file}')

    logging.info(f'Checking for errors on {console_log_file}')
    for msg in error_mgs:
        output = run(f"cat {console_log_file} | grep -i '{msg}'").stdout.rstrip()
        if output:
            print(f'INFO found {msg} on {console_log_file}')
            log_submit(console_log_file)
            error = +1

    if error:
        return False

    print(f'PASS: No errors on {console_log_file} have been found.')
    return True


def is_beaker_job():  # noqa: ANN201
    """Checks if it is beaker job."""
    need_env = ['BEAKER', 'BEAKER_RECIPE_ID', 'LAB_CONTROLLER']
    return all(not var not in os.environ for var in need_env)
