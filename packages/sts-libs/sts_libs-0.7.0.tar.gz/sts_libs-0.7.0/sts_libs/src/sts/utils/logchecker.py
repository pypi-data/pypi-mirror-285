"""logchecker.py: Module to Check for errors on the system."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import re
from datetime import datetime
from os import getenv
from pathlib import Path

import sts.linux
from sts.utils import beaker, restraint
from sts.utils.cmdline import run, run_ret_out

segfault_msg = ' segfault '
calltrace_msg = 'Call Trace:'

error_mgs = [segfault_msg, calltrace_msg]

tmt_test_data = getenv('TMT_TEST_DATA')
LOG_PATH = tmt_test_data or './'


def journalctl_timestamp() -> str:
    """Returns current time in journalctl-compatible format.

    Usage example:
        logging_start = journalctl_timestamp()
        failure_logs = run(f"journalctl -S {logging_start}).stdout.rstrip()"
    """
    return datetime.now().isoformat(sep=' ', timespec='minutes')  # noqa: DTZ005 <- We want local timezone.


def check_all():  # noqa: ANN201
    """Check for error on the system
    Returns:
    Boolean:
    True is no error was found
    False if some error was found.
    """
    logging.info('Checking for error on the system')
    error = 0

    if not kernel_check():
        error += 1
    if not abrt_check():
        error += 1
    if not messages_dump_check():
        error += 1
    if not dmesg_check():
        error += 1
    if not console_log_check():
        error += 1
    if not kdump_check():
        error += 1

    if error:
        log_messages = '/var/log/messages'
        log_messages_path = Path(log_messages)
        if log_messages_path.is_file():
            print(f'submit {log_messages}, named messages.log')
            run(f'cp {log_messages} {LOG_PATH}messages.log')
            restraint.log_submit('messages.log')

        if sts.linux.is_installed('sos'):
            sos_file = sts.linux.generate_sosreport()
            if not sos_file:
                return False
            restraint.log_submit(sos_file)
        return False

    return True


def abrt_check():  # noqa: ANN201
    """Check if abrtd found any issue
    Returns:
    Boolean:
    True no error was found
    False some error was found.
    """
    logging.info('Checking abrt for error')

    if run('rpm -q abrt') != 0:
        logging.warning('abrt tool does not seem to be installed')
        logging.warning('skipping abrt check')
        return True

    if run('pidof abrtd') != 0:
        logging.error('abrtd is not running')
        return False

    ret, log = run_ret_out('abrt-cli list', return_output=True)
    if ret != 0:
        logging.error('abrt-cli command failed')
        return False

    # We try to match for "Directory" to check if
    # abrt-cli list is actually listing any issue
    error = False
    if log:
        lines = log.split('\n')
        for line in lines:
            m = re.match(r'Directory:\s+(\S+)', line)
            if m:
                directory = m.group(1)
                filename = directory
                filename = filename.replace(':', '-')
                filename += '.tar.gz'
                run(f'tar cfzP {filename} {directory}')
                restraint.log_submit(filename)
                run(f'mv {filename} {LOG_PATH}')
                # if log is saved on restraint, it can be deleted from server
                # it avoids next test from detecting this failure
                run(f'abrt-cli rm {directory}')
                error = True

    if error:
        logging.error('Found abrt error')
        return False

    print('PASS: no Abrt entry has been found.')
    return True


def kernel_check():  # noqa: ANN201
    """Check if kernel got tainted.
    It checks /proc/sys/kernel/tainted which returns a bitmask.
    The values are defined in the kernel source file include/linux/kernel.h,
    and explained in kernel/panic.c
    cd /usr/src/kernels/`uname -r`/
    Sources are provided by kernel-devel
    Returns:
    Boolean:
    True if did not find any issue
    False if found some issue.
    """
    logging.info('Checking for tainted kernel')

    previous_tainted_file = '/tmp/previous-tainted'

    tainted = run('cat /proc/sys/kernel/tainted').stdout.rstrip()

    tainted_val = int(tainted)
    if tainted_val == 0:
        run('echo %d > %s' % (tainted_val, previous_tainted_file))
        return True

    logging.warning('Kernel is tainted!')

    if not Path(previous_tainted_file).is_file():
        run(f'echo {tainted_val} > {previous_tainted_file}')
    prev_taint = run(f'cat {previous_tainted_file}').stdout.rstrip()
    prev_taint_val = int(prev_taint)
    if prev_taint_val == tainted_val:
        logging.info('Kernel tainted has already been handled')
        return True

    run('echo %d > %s' % (tainted_val, previous_tainted_file))

    # check all bits that are set
    bit = 0
    while tainted_val != 0:
        # need to change back to int because it got changed to float at shifting
        tainted_val = int(tainted_val)
        if tainted_val & 1:
            print('\tTAINT bit %d is set\n' % bit)
        bit += 1
        # shift tainted value
        tainted_val /= 2
    # List all tainted bits that are defined
    print('List bit definition for tainted kernel')
    run('cat /usr/src/kernels/`uname -r`/include/linux/kernel.h | grep TAINT_')

    found_issue = False
    # try to find the module which tainted the kernel, tainted module have a mark between '('')'
    tainted_mods = run("cat /proc/modules | grep -e '(.*)' |  cut -d' ' -f1").stdout.rstrip().split('\n')
    # For example during iscsi async_events scst tool loads an unsigned module
    # just ignores it, so we will ignore this tainted if there is no tainted
    # modules loaded
    if not tainted_mods:
        logging.info('ignoring tainted as the module is not loaded anymore')
    else:
        # ignore ocrdma due BZ#1334675
        # ignore nvme_fc and nvmet_fc due Tech Preview - BZ#1384922
        ignore_modules = ['ocrdma', 'nvme_fc', 'nvmet_fc']
        for tainted_mod in tainted_mods:
            if tainted_mod:
                logging.info(f'The following module got tainted: {tainted_mod}')
                run(f'modinfo {tainted_mod}')
                # due BZ#1334675  we are ignoring ocrdma module
                if tainted_mod in ignore_modules:
                    logging.info(f'ignoring tainted on {tainted_mod}')
                    run(
                        'echo %d > %s' % (tainted_val, previous_tainted_file),
                    )
                    continue
                found_issue = True

    run(f'echo {tainted} > {previous_tainted_file}')
    return not found_issue


def _date2num(date):  # noqa: ANN001, ANN202
    date_map = {
        'Jan': '1',
        'Feb': '2',
        'Mar': '3',
        'Apr': '4',
        'May': '5',
        'Jun': '6',
        'Jul': '7',
        'Aug': '8',
        'Sep': '9',
        'Oct': '10',
        'Nov': '11',
        'Dec': '12',
    }

    date_regex = r'(\S\S\S)\s(\d+)\s(\d\d:\d\d:\d\d)'
    m = re.match(date_regex, date)
    month = date_map[m.group(1)]
    day = str(m.group(2))
    # if day is a single digit, add '0' to begin
    if len(day) == 1:
        day = '0' + day

    hour = m.group(3).replace(':', '')

    return month + day + hour


def messages_dump_check():  # noqa: ANN201
    previous_time_file = '/tmp/previous-dump-check'

    log_msg_file = '/var/log/messages'
    if not Path(log_msg_file).is_file():
        logging.warning(f'Could not open {log_msg_file}')
        return True

    with Path(log_msg_file).open('rb') as log_file:
        log = ''
        try:
            for line in log_file:
                log += line.decode('UTF-8')
        except UnicodeDecodeError:
            log += line.decode('latin-1')

    begin_tag = '\\[ cut here \\]'
    end_tag = '\\[ end trace '

    if not Path(previous_time_file).is_file():
        first_time = 'Jan 01 00:00:00'
        time = _date2num(first_time)
        run(f'echo {time} > {previous_time_file}')

    # Read the last time test ran
    last_run = run(f'cat {previous_time_file}').stdout.rstrip()
    logging.info(f'Checking for stack dump messages after: {last_run}')

    # Going to search the file for text that matches begin_tag until end_tag
    dump_regex = begin_tag + '(.*?)' + end_tag
    m = re.findall(dump_regex, log, re.MULTILINE)
    if m:
        logging.info(f'Checking if it is newer than: {last_run}')
        print(m.group(1))
        # TODO

    print('PASS: No recent dump messages has been found.')
    return True


def dmesg_check():  # noqa: ANN201
    """Check for error messages on dmesg ("Call Trace and segfault")."""
    logging.info('Checking for errors on dmesg.')
    error = 0
    for msg in error_mgs:
        output = run(f"dmesg | grep -i '{msg}'").stdout
        if output:
            logging.error(f'found {msg} on dmesg')
            run(f"echo '\nINFO found {msg}  Saving it\n'>> dmesg.log")
            run(f'dmesg >> {LOG_PATH}dmesg.log')
            restraint.log_submit('dmesg.log')
            error = 1
    sts.linux.clear_dmesg()
    if error:
        return False

    print('PASS: No errors on dmesg have been found.')
    return True


def console_log_check():  # noqa: ANN201
    """Checks for error messages on console log ("Call Trace and segfault")."""
    if not beaker.is_beaker_job():
        # skip check
        return True
    return beaker.console_log_check(error_mgs)


def kdump_check():  # noqa: ANN201
    """Check for kdump error messages.
    It assumes kdump is configured on /var/crash.
    """
    error = 0

    previous_kdump_check_file = '/tmp/previous-kdump-check'
    kdump_dir = '/var/crash'
    ret, hostname = run_ret_out('hostname', return_output=True)

    if not Path(f'{kdump_dir}/{hostname}').exists():
        logging.info('No kdump log found for this server')
        return True

    ret, output = run_ret_out(f"ls -l {kdump_dir}/{hostname} |  awk '{{print$9}}'", return_output=True)
    kdumps = output.split('\n')
    kdump_dates = []
    for kdump in kdumps:
        if not kdump:
            continue
        # parse on the date, remove the ip of the uploader
        m = re.match('.*?-(.*)', kdump)
        if not m:
            logging.warning(f'unexpected format for kdump ({kdump})')
            continue
        date = m.group(1)
        # Old dump were using "."
        date = date.replace(r'\.', '-')
        # replace last "-" with space to format date properly
        index = date.rfind('-')
        date = date[:index] + ' ' + date[index + 1 :]
        logging.info(f'Found kdump from {date}')
        kdump_dates.append(date)

    # checks if a file to store last run exists, if not create it
    if not Path(previous_kdump_check_file).is_file():
        # time in seconds
        ret, time = run_ret_out(r'date +\"\%s\"', return_output=True)
        run(f'echo -n {time} > {previous_kdump_check_file}')
        logging.info('kdump check is executing for the first time.')
        logging.info("doesn't know from which date should check files.")
        print('PASS: Returning success.')
        return True

    # Read the last time test ran
    ret, previous_check_time = run_ret_out(f'cat {previous_kdump_check_file}', return_output=True)
    # just add new line to terminal because the file should not have already new line character
    print()

    for date in kdump_dates:
        # Note %% is escape form to use % in a string
        ret, kdump_time = run_ret_out('date --date="%s" +%%s' % date, return_output=True)  # noqa: UP031
        if ret != 0:
            logging.warning(f'Could not convert date {date}')
            continue

        if not kdump_time:
            continue
        if int(kdump_time) > int(previous_check_time):
            logging.error(f'Found a kdump log from {date} (more recent than {previous_check_time})')
            logging.error(f'Check {kdump_dir}/{hostname}')
            error += 1

    ret, time = run_ret_out(r'date +\"\%s\"', return_output=True)
    run(f'echo -n {time} > {previous_kdump_check_file}')

    if error:
        return False

    print('PASS: No errors on kdump have been found.')
    return True
