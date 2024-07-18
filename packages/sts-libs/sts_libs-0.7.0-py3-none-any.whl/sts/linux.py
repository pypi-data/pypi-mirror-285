"""py: Module to get information from servers."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import annotations

import errno
import logging
import os.path
import re
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from sts import host_init, mp, scsi
from sts.utils.cmdline import exists, run, run_ret_out

if TYPE_CHECKING:
    from testinfra.modules.package import Package

host = host_init()


def hostname():  # noqa: ANN201
    ret, name = run_ret_out('hostname', return_output=True)
    if ret != 0:
        logging.error('hostname() - could not run command')
        print(name)
        return None
    return name


def rm_files_containing_str(
    directory: str | os.PathLike,
    string_to_match: str,
    not_containing: bool = False,
) -> None:
    """Deletes files containing (or not containing) specific string.

    Note: does not check subdirectories, or file names
    Args:
        directory: path to dir or Pathlike object
        string_to_match: string to mach in file contents
        not_containing: Delete files not containing specified string
    """
    for file in Path(directory).iterdir():
        logging.warning(file)
        if file.is_file():
            content = file.read_text()
            if not_containing:
                logging.warning(content)
                if string_to_match not in content:
                    file.unlink()
                return
            if string_to_match in content:
                file.unlink()


def is_service_running(service: str) -> bool:
    # Workaround for https://github.com/pytest-dev/pytest-testinfra/issues/748
    try:
        return host.service(service).is_running
    except AssertionError:
        return run(f'systemctl is-active {service}').succeeded


def is_service_enabled(service: str) -> bool:
    return host.service(service).is_enabled


def service_start(service_name: str) -> bool:
    """Start service
    The arguments are:
    None
    Returns:
    True: Service started
    False: There was some problem.
    """
    cmd = f'systemctl start {service_name}'
    has_systemctl = True

    if not exists('systemctl'):
        has_systemctl = False
    if not has_systemctl:
        cmd = f'service {service_name} start'

    if run(cmd).rc != 0:
        logging.error(f'Could not start {service_name}')
        if has_systemctl:
            run(f'systemctl status {service_name}')
            run('journalctl -xn')
        return False
    return True


def service_stop(service_name: str) -> bool:
    """Stop service
    The arguments are:
    Name of the service
    Returns:
    True: Service stopped
    False: There was some problem.
    """
    cmd = f'systemctl stop {service_name}'
    has_systemctl = True

    if not exists('systemctl'):
        has_systemctl = False
    if not has_systemctl:
        cmd = f'service {service_name} stop'

    if run(cmd).rc != 0:
        logging.error(f'Could not stop {service_name}')
        if has_systemctl:
            run(f'systemctl status {service_name}')
            run('journalctl -xn')
        return False
    return True


def service_restart(service_name: str) -> bool:
    """Restart service
    The arguments are:
    Name of the service
    Returns:
    True: Service restarted
    False: There was some problem.
    """
    cmd = f'systemctl restart {service_name}'
    has_systemctl = True

    if not exists('systemctl'):
        has_systemctl = False
    if not has_systemctl:
        cmd = f'service {service_name} restart'
    service_timestamp = get_service_timestamp(service_name)
    if service_timestamp is not None:
        timestamp_struct = time.strptime(service_timestamp, '%a %Y-%m-%d %H:%M:%S %Z')
        actual_time = time.localtime()
        if time.mktime(actual_time) - time.mktime(timestamp_struct) < 5:
            logging.info('Waiting 5 seconds before restart.')
            time.sleep(5)
    if run(cmd).failed:
        logging.error(f'Could not restart {service_name}')
        if has_systemctl:
            run(f'systemctl status {service_name}')
            run('journalctl -xn')
        return False
    return True


def service_enable(service_name: str, now: bool = False) -> bool:
    """Enable service
    The arguments are:
    Name of the service
    Returns:
    True: Service got enabled
    False: There was some problem.
    """
    cmd = f'systemctl enable {service_name}'
    if now:
        cmd += ' --now'

    if run(cmd).rc != 0:
        logging.error(f'Could not enable {service_name}')
        run(f'systemctl status {service_name}')
        run('journalctl -xn')
        return False
    return True


def service_disable(service_name: str, now: bool = False) -> bool:
    """Disable service
    The arguments are:
    Name of the service
    Returns:
    True: Service got disabled.
    False: There was some problem.
    """
    cmd = f'systemctl disable {service_name}'
    if now:
        cmd += ' --now'

    if run(cmd).rc != 0:
        logging.error(f'Could not disable {service_name}')
        run(f'systemctl status {service_name}')
        run('journalctl -xn')
        return False
    return True


def package_info(package: str) -> Package:
    """Returns testinfra package object."""
    return host.package(package)


def log_package_version(package: str) -> None:
    """Logs package version and release as INFO."""
    pack = package_info(package)
    logging.info(f'{package}-{pack.version}{pack.release}')


def log_kernel_version() -> None:
    logging.info(f'kernel-{kernel_version()}')


def is_installed(package: str) -> bool:
    return package_info(package).is_installed


def install_package(package: str) -> bool:
    """Install a package "pack" via `yum|dnf install -y`."""
    # Check if package is already installed
    if is_installed(package):
        return True

    if run(f'dnf install -y {package}').rc != 0:
        logging.error(f'Could not install {package}')
        return False

    logging.info(f'{package} was successfully installed')
    return True


def wait_udev(sleeptime: int = 5) -> None:
    """Wait udev to finish. Often used after scsi rescan."""
    logging.info('Waiting udev to finish storage scan')
    run('udevadm settle')
    sleep(sleeptime)


def get_all_loaded_modules():  # noqa: ANN201
    """Check /proc/modules and return a list of all modules that are loaded."""
    cmd = 'cat /proc/modules | cut -d " " -f 1'
    result = run(cmd)
    if result.rc != 0:
        logging.error(f'get_all_loaded_modules() - Could not execute: {cmd} - {result.stderr}')
        return None

    return result.stdout.split('\n')


def load_module(module):  # noqa: ANN001, ANN201
    """Run modprobe using module with parameters given as input
    Parameters:
    module:       module name and it's parameters.
    """
    if not module:
        logging.error('load_module() - requires module parameter')
        return False
    cmd = f'modprobe {module}'
    if run(cmd).rc != 0:
        logging.error(f'load_module() - Could not execute: {module}')
        return False
    return True


def unload_module(module_name, remove_dependent=False):  # noqa: ANN001, ANN201
    """Run rmmod to unload module
    Parameters:
    module_name:       module name.
    """
    if not module_name:
        logging.error('unload_module() - requires module_name parameter')
        return False
    cmd = f'modprobe -r {module_name}'

    if remove_dependent:
        dep_modules = get_dependent_modules(module_name)
        if dep_modules:  # print info only if there are any modules to remove
            logging.info(f'Removing modules dependent on {module_name}')
            for module in dep_modules:
                if not unload_module(module, remove_dependent=remove_dependent):
                    logging.error('unload_module() - Could not unload dependent modules')
                    return False

    if run(cmd).rc != 0:
        logging.error(f'unload_module() - Could not unload: {module_name}')
        return False

    return True


def get_dependent_modules(module_name):  # noqa: ANN001, ANN201
    """Returns list of modules that loaded this module as a dependency
    Useful when removing parent modules (error "Module is in use by: ")
    Parameters:
    module_name:      module_name.
    """
    if not module_name:
        logging.error('get_dependent_modules() - requires module_name parameter')
        return None
    cmd = f'cat /proc/modules | grep -Ew "^{module_name}" | cut -d \' \' -f 4 | tr "," " "'
    ret, dependent_modules = run_ret_out(cmd, return_output=True)
    if dependent_modules == '-':
        return []  # No dependent modules found
    if ret != 0:
        logging.error('get_dependent_modules() - failed to get a list of modules')
        return None
    return dependent_modules.split()


def is_module_loaded(module_name):  # noqa: ANN001, ANN201
    """Check if given module is loaded
    Parameters:
    module_name:      module_name.
    """
    return module_name in get_all_loaded_modules()


def sleep(duration):  # noqa: ANN001, ANN201
    """It basically calls sys.sleep, but as stdout and stderr can be buffered
    We flush them before sleep.
    """
    sys.stdout.flush()
    sys.stderr.flush()
    time.sleep(duration)


def is_mounted(device=None, mountpoint=None):  # noqa: ANN001, ANN201
    """Check if mountpoint is already mounted."""
    if device:
        return run(f'mount | grep {device}').succeeded
    if mountpoint:
        return run(f'mount | grep {mountpoint}').succeeded
    return False


def mount(device=None, mountpoint=None, fs=None, options=None):  # noqa: ANN001, ANN201
    cmd = 'mount'
    if fs:
        cmd += f' -t {fs}'
    if options:
        cmd += f' -o {options}'
    if device:
        cmd += f' {device}'
    if mountpoint:
        cmd += f' {mountpoint}'
    if run(cmd).rc != 0:
        logging.error('Could not mount partition')
        return False

    return True


def umount(device=None, mountpoint=None):  # noqa: ANN001, ANN201
    cmd = 'umount'
    if device:
        cmd += f' {device}'
        if not is_mounted(device):
            # Device is not mounted
            return True

    if mountpoint:
        cmd += f' {mountpoint}'
        if not is_mounted(mountpoint=mountpoint):
            # Device is not mounted
            return True

    if run(cmd).rc != 0:
        logging.error('Could not umount partition')
        return False

    return True


def run_cmd_background(cmd):  # noqa: ANN001, ANN201
    """Run Command on background
    Returns:
    subprocess.
    PID is on process.pid
    Exit code is on process.rc (after run process.communicate())
    Wait for process to finish
    while process.poll() is None:
    sleep(1)
    Get stdout and stderr
    (stdout, stderr) = process.communicate().
    """
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if not process:
        logging.error(f"Could not run '{cmd}' on background")
        return None
    logging.info(f'running {cmd} on background. PID is {process.pid}')
    return process


def kill_pid(pid):  # noqa: ANN001, ANN201
    os.kill(pid, signal.SIGTERM)
    sleep(1)
    if check_pid(pid):
        os.kill(pid, signal.SIGKILL)
        sleep(1)
        if check_pid(pid):
            return False
    return True


def kill_all(process_name):  # noqa: ANN001, ANN201
    ret = run(f'killall {process_name}').rc
    # Wait few seconds for process to finish
    sleep(3)
    return ret


def check_pid(pid):  # noqa: ANN001, ANN201
    """Check there is a process running with this PID."""
    # try:
    # #0 is the signal, it does not kill the process
    # os.kill(int(pid), 0)
    # except OSError:
    # return False
    # else:
    # return True
    try:
        return os.waitpid(pid, os.WNOHANG) == (0, 0)
    except OSError as e:
        if e.errno != errno.ECHILD:
            raise


def time_stamp(utc: bool = False, in_seconds: bool = False):  # noqa: ANN201
    now = datetime.now(tz=timezone.utc if utc else None)

    # ts = "%s%s%s%s%s%s" % (now.year, now.month, now.day, now.hour, now.minute, now.second)
    ts = now.strftime('%Y%m%d%H%M%S')
    if in_seconds:
        ts = now.strftime('%s')
    return ts


def kernel_command_line():  # noqa: ANN201
    """Return the kernel command line used to boot."""
    retcode, output = run_ret_out('cat /proc/cmdline', return_output=True)
    if retcode != 0:
        logging.error('could not get kernel command line')
        print(output)
        return None
    return output


def kernel_version() -> str:
    """Same as `uname -r` output."""
    return host.sysctl('kernel.osrelease')


def is_debug() -> bool:
    kernel = kernel_version()
    return '+debug' in kernel


def kmem_leak_start():  # noqa: ANN201
    """Usage
        kmem_leak_start()
    Purpose
        Start and clear kernel memory leak detection.
    Parameter
        N/A
    Returns
        True
          or
        False       # not debug kernel or failure found.
    """
    if not is_debug():
        logging.warning('Not debug kernel, will not enable kernel memory leak check')
        return False

    arch = host.system_info.arch
    if arch in {'i386', 'i686'}:
        logging.info('Not enabling kmemleak on 32 bits server.')
        return False

    k_commandline = kernel_command_line()
    if not re.search('kmemleak=on', k_commandline):
        logging.warning("kmem_leak_start(): need 'kmemleak=on' kernel_option to enable kernel memory leak detection")

    check_debugfs_mount_cmd = 'mount | grep "/sys/kernel/debug type debugfs"'
    retcode = run(check_debugfs_mount_cmd).rc
    if retcode != 0:
        # debugfs is not mounted
        mount_debugfs_cli_cmd = 'mount -t debugfs nodev /sys/kernel/debug'
        run(mount_debugfs_cli_cmd)
        check_debugfs_mount_cmd = 'mount | grep "/sys/kernel/debug type debugfs"'
        retcode, output = run_ret_out(check_debugfs_mount_cmd, return_output=True)
        if retcode != 0:
            logging.warning('Failed to mount debugfs to /sys/kernel/debug')
            print(output)
            return False

    # enable kmemleak and clear
    logging.info('Begin kernel memory leak check')
    if run('echo scan=on > /sys/kernel/debug/kmemleak') != 0:
        return False
    if run('echo stack=on > /sys/kernel/debug/kmemleak') != 0:
        return False
    return run('echo clear > /sys/kernel/debug/kmemleak') == 0


def kmem_leak_check():  # noqa: ANN201
    """Usage
        kmem_leak_check()
    Purpose
        Read out kernel memory leak check log and then clear it up.
    Parameter
        N/A
    Returns
        kmemleak_log
          or
        None       # when file '/sys/kernel/debug/kmemleak' not exists
                  # or no leak found.
    """
    sysfs_kmemleak = '/sys/kernel/debug/kmemleak'
    if not Path(sysfs_kmemleak).is_file():
        return None

    with Path(sysfs_kmemleak).open() as f:
        if not f:
            logging.error(f'Could not read {sysfs_kmemleak}')
            return None
        kmemleak_log = f.read()

    if kmemleak_log:
        logging.warning(f'Found kernel memory leak:\n{kmemleak_log}')
        logging.info('Clearing memory leak for next check')
        run(f"echo 'clear' > {sysfs_kmemleak}")
        return kmemleak_log

    logging.info('No kernel memory leak found')
    return None


def kmem_leak_disable():  # noqa: ANN201
    """Usage
        kmem_leak_disable()
    Purpose
        Disable kmemleak by 'scan=off' and 'stack=off' to
        '/sys/kernel/debug/kmemleak'.
    Parameter
        N/A
    Returns
        True           # disabled or not enabled yet
          or
        False       # failed to run 'echo' command.
    """
    sysfs_kmemleak = '/sys/kernel/debug/kmemleak'
    if not Path(sysfs_kmemleak).is_file():
        return True

    logging.info('kmem_leak_disable(): Disabling kernel memory leak detection')
    ok1, ok1_output = run_ret_out(f'echo scan=off > {sysfs_kmemleak}', return_output=True)
    ok2, ok2_output = run_ret_out(f'echo stack=off > {sysfs_kmemleak}', return_output=True)
    if ok1 != 0 or ok2 != 0:
        logging.error('kmem_leak_disable(): Failed to disable kernel memory leak detection')
        print(ok1_output)
        print(ok2_output)
        return False

    logging.info('kmem_leak_disable(): Kernel memory leak detection disabled')
    return True


def get_driver_info(driver: str):  # noqa: ANN201
    if not driver:
        logging.error('get_driver_info() - requires driver parameter')
        return None

    sys_fs_dir = '/sys/module'
    sys_fs_path = Path(sys_fs_dir)
    if not sys_fs_path.is_dir():
        logging.error(f'get_driver_info() - {sys_fs_path} is not a valid directory')
        return None

    sysfs_driver_folder = sys_fs_path / driver
    if not sysfs_driver_folder.is_dir():
        logging.error(f'get_driver_info() - module {driver} is not loaded')
        return None

    driver_info = {}
    infos = ['srcversion', 'version', 'taint']
    for info in infos:
        info_path = sysfs_driver_folder / info
        if not Path(info_path).is_file():
            continue
        output = run(f'cat {info_path}').stdout
        driver_info[info] = output

    sys_driver_parameter = sysfs_driver_folder / 'parameters'
    if sys_driver_parameter.is_dir():
        # Need to add driver parameters
        param_files = list(sys_driver_parameter.iterdir())
        for param in param_files:
            output = run(f'cat {sys_driver_parameter}/{param}').stdout.rstrip()
            if 'parameters' not in driver_info:
                driver_info['parameters'] = {}
            driver_info['parameters'][param] = output
    return driver_info


def mkdir(new_dir):  # noqa: ANN001, ANN201
    if Path(new_dir).is_dir():
        logging.info(f'{new_dir} already exist')
        return True
    cmd = f'mkdir -p {new_dir}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'could create directory {new_dir}')
        print(output)
        return False
    return True


def rmdir(dir_name):  # noqa: ANN001, ANN201
    """Remove directory and all content from it."""
    if not Path(dir_name).is_dir():
        logging.info(f'{dir_name} does not exist')
        return True
    cmd = f'rm -rf {dir_name}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'could remove directory {dir_name}')
        print(output)
        return False
    return True


def mkfs(device_name, fs_type, force=False):  # noqa: ANN001, ANN201
    """Create a Filesystem on device."""
    if not device_name or not fs_type:
        logging.info('mkfs() requires device_name and fs_type')
        return False

    force_option = '-F'
    if fs_type == 'xfs':
        force_option = '-f'

    cmd = f'mkfs.{fs_type} '
    if force:
        cmd += f'{force_option} '
    cmd += device_name
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'could create filesystem {fs_type} on {device_name}')
        print(output)
        return False
    return True


def sync(directory=None):  # noqa: ANN001, ANN201
    cmd = 'sync'
    if directory:
        cmd += f' {directory}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error('could not sync')
        print(output)
        return False
    return True


def get_free_space(path):  # noqa: ANN001, ANN201
    """Get free space of a path.
    Path could be:
    /dev/sda
    /root
    ./.
    """
    if not path:
        return None

    cmd = f'df -B 1 {path}'
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'get_free_space() - could not run {cmd}')
        print(output)
        return None
    fs_list = output.split('\n')
    # delete the header info
    del fs_list[0]

    if len(fs_list) > 1:
        # Could be the information was too long and splited in lines
        tmp_info = ''.join(fs_list)
        fs_list[0] = tmp_info

    # expected order
    # Filesystem    1B-blocks       Used   Available Use% Mounted on
    m = re.compile(r'\S+\s+\d+\s+\d+\s+(\d+)').search(fs_list[0])
    if m:
        return int(m.group(1))
    return None


def get_block_device_name(device: str) -> str:
    """Returns kernel name from block device
    eg. lvm1 from /dev/mapper/lvm1.
    """
    if not device.startswith('/dev/'):
        device = get_full_path(device)

    cp = run(f'lsblk -ndlo NAME {device}')
    if cp.rc != 0:
        logging.error(f'get_full_path() - {cp.stderr.rstrip()}')
    return cp.stdout.rstrip()


def get_full_path(device_name):  # noqa: ANN001, ANN201
    """Returns full block device path, eg. from device: /dev/mapper/device."""
    cmds = [
        f'lsblk -pnalo NAME  | grep {device_name} -m1',  # should be more robust
        f'find /dev/ -name {device_name}',
    ]  # older OS(rhel-6), will fail with partitions

    for cmd in cmds:
        _retcode, output = run_ret_out(cmd, return_output=True)
        if output:
            return output

    logging.error(f'get_full_path() - {device_name}')
    return None


def get_parent_device(child_device, only_direct=False):  # noqa: ANN001, ANN201
    """Returns block device's parent device: eg. sda, nvme0n1
    child_device: eg. /dev/sda2, nvme0n1p1, /dev/mapper/device
    only_direct: returns only the direct parent. eg. lvm -> sda3, not sda.
    """
    if not child_device.startswith('/dev/'):
        child_device = get_full_path(child_device)
    if not child_device:  # get_full_path would return None if device does not exist
        logging.error(f"get_parent_device - unknown child_device '{child_device}'")
    cmd = f'lsblk -nsl {child_device} -o KNAME | tail -n 1'
    if only_direct:
        cmd = f'lsblk -nsl {child_device} -o KNAME | sed -n 2p'  # if no parent, returns nothing
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'run {cmd}')
        print(output)
        return None
    if not output or output == child_device:
        logging.warning('get_parent_device - device has no parent')
        return None
    return output


def get_udev_property(device_name: str, property_key: str) -> str | None:
    """Given an /dev device name, returns specified property using udevadm.

    Args:
      device_name: e.g. 'sda', 'mpatha', 'dm-0', 'nvme0n1', 'sr0', ...
      property_key: eg. 'ID_SERIAL', 'DM_WWN', 'ID_PATH', ...
    :return property_value: eg. for ID_SERIAL: '360fff19abdd9f5fb943525d45126ca27'
    """
    if not device_name:
        logging.warning('get_udev_property() - requires device_name parameter')
        return None

    # Converts for example mpatha to /dev/mapper/mpatha or sda to /dev/sda
    device = get_full_path(device_name)
    if not device:
        logging.error(f"get_udev_property - unknown device_name '{device_name}'")

    # Trying to catch wrong key name when dm-multipath is used.
    if mp.is_mpath_device(device_name):  # noqa: SIM102
        if property_key.startswith('ID_') and not property_key.startswith('ID_FS_'):
            property_key = property_key.replace('ID_', 'DM_')

    ret, property_value = run_ret_out(
        f'udevadm info -q property --name={device} | grep {property_key}= | cut -d = -f 2',
        return_output=True,
    )
    if ret:
        logging.warning(f"Could not get udevadm info of device '{device}'")
        return None
    if not property_value:
        logging.warning(f"Could not find property '{property_key}' in udevadm info of device '{device}'")
        return None

    return property_value


def get_boot_device(parent_device=False, full_path=False):  # noqa: ANN001, ANN201
    """Returns boot device, eg. 'sda1'
    parent_device, eg. 'sda'
    full_path, eg. '/dev/sda1'.
    """
    boot_mount = '/boot'
    root_mount = '/'
    # get boot device
    cmd = f"mount | grep ' {boot_mount} ' | cut -d ' ' -f 1"
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'run {cmd}')
        print(output)
        return None
    boot_device = output
    # get root device
    cmd = f"mount | grep ' {root_mount} ' | cut -d ' ' -f 1"
    retcode, output = run_ret_out(cmd, return_output=True)
    if retcode != 0:
        logging.error(f'run {cmd}')
        print(output)
        return None
    root_device = output

    if not boot_device and not root_device:
        logging.error("Could not find '/boot' and '/' mounted!")
        return None
    if not boot_device:
        # /boot is not mounted on openstack virtual machines
        logging.info('Could not find /boot mounted... Assuming this is a virtual machine')
        boot_device = root_device
    if boot_device == 'overlay':
        logging.info('/ mounted on overlay device. Assuming running in a container')
        return None

    if parent_device:
        boot_device = get_parent_device(boot_device)
    if full_path:
        return get_full_path(boot_device)
    return get_block_device_name(boot_device)


def is_dm_device(device_name: str) -> bool:
    """Checks if device is mapped by device-mapper.

    Args:
      device_name: e.g. 'sda', 'mpatha', ...
    """
    # Converts for example mpatha to /dev/mapper/mpatha or sda to /dev/sda
    device = get_full_path(device_name)
    if not device:
        logging.error(f"is_dm_device - unknown device_name '{device_name}'")
        return False
    ret, name = run_ret_out(f'udevadm info -q name --name={device}', return_output=True)
    if ret:
        logging.error(f"Could not get udevadm info for device '{device}'")
        return False
    if not name:
        logging.error(f"Could not find udev name for '{device}'")
        return False

    return bool(name.startswith('dm'))


def is_nvme_device(device):  # noqa: ANN001, ANN201
    """Checks if device is nvme device."""
    return bool(re.match('^nvme[0-9]n[0-9]$', device))


def get_wwid_of_nvme(device):  # noqa: ANN001, ANN201
    """Reads WWID from udev ID_WWN."""
    return get_udev_property(device, property_key='ID_WWN')


def get_device_wwid(device):  # noqa: ANN001, ANN201
    """Given an SCSI, NVMe or multipath device, returns its WWID."""
    if device.startswith('vd'):
        logging.debug(f'{device}: Presuming virtual disk does not have wwid.')
        return None

    serial = get_udev_property(device_name=device, property_key='ID_SERIAL')
    if not serial and is_dm_device(device):  # RHEL-6 workaround
        dm_uuid = get_udev_property(device_name=device, property_key='DM_UUID')
        serial = dm_uuid.replace('mpath-', '')
    if not serial:
        logging.info(f'get_device_wwid() - Could not find WWID for {device}')
        return None

    return serial


def remove_device_wwid(wwid):  # noqa: ANN001, ANN201
    if not wwid:
        logging.error('remove_device_wwid() - requires wwid as parameter')
        return False

    mpath_wwid = mp.mpath_name_of_wwid(wwid)
    if mpath_wwid:
        mp.remove_mpath(mpath_wwid)

    scsi_ids_wwid = scsi.scsi_ids_of_wwid(wwid)
    if scsi_ids_wwid:
        for scsi_id in scsi_ids_wwid:
            scsi_name = scsi.get_scsi_disk_name(scsi_id)
            if not scsi_name:
                continue
            logging.info(f'detaching SCSI disk {scsi_name}')
            scsi.delete_disk(scsi_name)
    return True


def clear_dmesg() -> None:
    run('dmesg -c')


def get_regex_pci_id():  # noqa: ANN201
    regex_pci_id = r'(?:([0-0a-f]{4}):){0,1}'  # domain id (optional)
    regex_pci_id += r'([0-9a-f]{2})'  # bus id
    regex_pci_id += r':'
    regex_pci_id += r'([0-9a-f]{2})'  # slot id
    regex_pci_id += r'\.'
    regex_pci_id += r'(\d+)'  # function id
    return regex_pci_id


def get_partitions(device):  # noqa: ANN001, ANN201
    """Return a list of all parition numbers from the device."""
    if not device:
        logging.warning('get_partitions() - requires device as parameter')
        return None

    cmd = f'parted -s {device} print'
    ret, output = run_ret_out(cmd, return_output=True)
    if ret != 0:
        # logging.error("get_partitions() - Could not read partition information from %s" % device)
        # print output
        return None

    lines = output.split('\n')
    if not lines:
        return None

    header_regex = re.compile(r'Number  Start   End     Size    Type')
    partition_regex = re.compile(r'\s(\d+)\s+\S+')
    partitions = []
    found_header = False
    for line in lines:
        if header_regex.match(line):
            found_header = True
            continue
        if found_header:
            m = partition_regex.match(line)
            if m:
                partitions.append(m.group(1))

    return partitions


def delete_partition(device, partition):  # noqa: ANN001, ANN201
    """Delete specific partition from the device."""
    if not device or not partition:
        logging.error('delete_partition() - requires device and partition as argument')
        return False

    cmd = f'parted -s {device} rm {partition}'
    ret, output = run_ret_out(cmd, return_output=True)
    if ret != 0:
        logging.error(f'delete_partition() - Could not delete partition {partition} from {device}')
        print(output)
        return False

    return True


def add_repo(name, address, metalink=False):  # noqa: ANN001, ANN201
    """Adds yum repository to /etc/yum.repos.d/NAME.repo."""
    repo = Path(f'/etc/yum.repos.d/{name.lower()}.repo')
    if repo.is_file():
        logging.info(f'Repo {repo} already exists.')
        return True

    url = 'metalink' if metalink else 'baseurl'

    repo_conf_table = {
        'name': name,
        url: address,
        'enabled': '1',
        'gpgcheck': '0',
        'skip_if_unavailable': '1',
    }

    repo_conf = f'[{name}]\n'
    for setting, value in repo_conf_table.items():
        repo_conf += f'{setting}={value}\n'

    with repo.open(mode='w') as f:
        f.write(repo_conf)

    return True


def download_repo_file(url, name=None, overwrite=True):  # noqa: ANN001, ANN201
    """Downloads .repo file to /etc.repos.d/."""
    if not url:
        logging.error('repo file url argument required')
        return False
    if not name:
        name = url.split('/')[-1]
    if name[-5:] != '.repo':
        name = f'{name}.repo'
    path = f'/etc/yum.repos.d/{name}'

    if Path(path).is_file():
        if overwrite is False:
            logging.warning(f'{name} exits, skipping repo file download')
            return True
        logging.warning(f'{name} exits, overwriting .repo file')
    install_package('curl')
    return run(f'curl {url} --output {path}')


def del_repo(name):  # noqa: ANN001, ANN201
    """Removes .repo file."""
    try:
        Path(f'/etc/yum.repos.d/{name}.repo').unlink()
    except FileNotFoundError:
        logging.warning(f'Removing repository {name} failed.')
        return False
    return True


def check_repo(name, check_if_enabled=True):  # noqa: ANN001, ANN201
    """Checks if repository works and is enabled."""
    if not name:
        logging.error('repo name argument required')
        return False

    cmd = f'yum repoinfo {name} | grep Repo-status'  # yum=dnf alias works here
    ret, out = run_ret_out(cmd, return_output=True)
    if ret != 0:
        print(f'{name} repo is not present')
        return False
    if check_if_enabled and 'enabled' not in out:
        print(f'{name} repo is not enabled')
        return False

    return True


def in_container() -> bool:
    """Check if we are running inside container."""
    try:
        proc_current = Path('/proc/1/attr/current').read_text()
        # Check for unconfined, which can be found in gitlab ci
        if 'container_t' in proc_current or 'unconfined' in proc_current:
            return True
        if 'docker' in Path('/proc/self/cgroup').read_text():
            return True
    except PermissionError:
        logging.info('Assuming containerized environment')
        return True
    return False


def get_memory(units='m', total=False):  # noqa: ANN001, ANN201
    """Returns data from 'free' as a dict."""
    possible_units = 'b bytes k kilo m mega  g giga tera peta'.split()
    if units not in possible_units:
        logging.error(f"'units' must be one of {[str(x) for x in possible_units]}")
        return None

    memory = {}
    columns = []

    if len(units) > 1:
        units = '-' + units
    cmd = f'free -{units}'
    if total:
        cmd += ' -t'
    ret, mem = run_ret_out(cmd=cmd, return_output=True)
    if ret != 0:
        logging.error(f"Running '{cmd}' failed.")
        return None

    for row, m in enumerate(mem.splitlines()):
        if row == 0:
            columns = [c.strip() for c in m.split()]
            continue
        m = [x.strip() for x in m.split()]  # noqa: PLW2901
        key = m.pop(0)[:-1].lower()
        memory[key] = {}
        for i, value in enumerate(m):
            memory[key][columns[i]] = int(value)

    return memory


def get_service_timestamp(service_name: str) -> str | None:
    """Returns active enter timestamp of a service.

    Args:
      service_name: Name of the service

    Returns:
    Time in format: a YYYY-MM-DD hh:mm:ss Z
    None: systemctl is not installed or timestamp does not exist
    """
    if not exists('systemctl'):
        cmd = f'systemctl show {service_name} --property=ActiveEnterTimestamp'
        ret, data = run_ret_out(cmd, return_output=True)
        if ret == 0:
            timestamp = data.split('=')
            if timestamp[1]:
                return timestamp[1]
            return None
        logging.warning(f'Could not get active enter timestamp of service: {service_name}')
    return None


def get_system_logs(
    length: int | None = None,
    reverse: bool = False,
    kernel_only: bool = False,
    since: str | None = None,
    grep: str | None = None,
    options: list[str] | None = None,
    return_output: bool = True,
) -> Literal[0, 1] | tuple[Literal[0, 1]] | Any:  # noqa: ANN401
    """Gets system logs using journalctl.

    Args:
      length: Get last $length messages.
      reverse: Get logs in reverse.
      kernel_only: Get only kernel messages.
      since: Get messages since some time, can you '+' and '-' prefix.
      grep: String to test_filter messages using 'grep'.
      options: Any other possible options with its value as a string.
      return_output: Should the function return only retcode or also the output.

    Returns:
      retcode / (retcode, data)
    """
    cmd = 'journalctl'
    if kernel_only:
        cmd += ' -k'
    if length:
        cmd += f' -n {length}'
    if reverse:
        cmd += ' -r'
    if since:
        # since can be used with '+' and '-', see man journalctl
        cmd += f' -S {since}'
    if options:
        cmd += ' ' + ' '.join(options)

    if grep:
        cmd += f" | grep '{grep}'"

    ret, journal = run_ret_out(cmd, return_output=return_output)
    if ret:
        logging.error(f"cmd '{cmd}' failed with retcode {ret}.")
        return None
    if not return_output:
        return ret

    # shorten the hostname to match /var/log/messages format
    data = ''
    for line in journal.splitlines():
        line = line.split()  # noqa: PLW2901
        if len(line) < 4:
            continue
        line[3] = line[3].split('.')[0]
        data += ' '.join(line) + '\n'
    return ret, data


def generate_sosreport(skip_plugins=None, plugin_timeout=300):  # noqa: ANN001, ANN201
    """Generates a sos report.

    Args:
      skip_plugins: (string) comma separated list of plugins to skip (no space after comma)
      plugin_timeout: (int) timeout in seconds to allow each plugin to run for (only applicable to rhel-8+)
    """
    cmd = f'sos report --batch --plugin-timeout {plugin_timeout}'

    if not install_package('sos'):
        logging.error('unable to install sos package')
        return False

    mount_flag = False
    if is_mounted('/var/crash'):
        logging.info('Unmounting /var/crash to avoid sosreport being hang there')
        umount('/var/crash')
        mount_flag = True

    if skip_plugins:
        cmd += f' --skip-plugins {skip_plugins}'

    ret_code, sosreport_ret = run_ret_out(cmd, return_output=True)
    if ret_code != 0:
        logging.error('sosreport command failed')
        if mount_flag:
            mount('/var/crash')
        return False

    sos_report = None
    for line in sosreport_ret.split('\n'):
        if '/tmp/sosreport' in line:
            sos_report = line.strip()
            break

    if mount_flag:
        mount('/var/crash')

    return sos_report
