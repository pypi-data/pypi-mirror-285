"""scsi_debug.py: Module to manipulate devices created by scsi_debug module."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

from sts import linux, mp
from sts.scsi import get_scsi_name_by_vendor
from sts.utils.cmdline import run


def scsi_debug_load_module(options=None):  # noqa: ANN001, ANN201
    module_cmd = 'scsi_debug'
    if linux.is_module_loaded(module_cmd):
        logging.warning('scsi_debug_load_module() - Module is already loaded')
        return True

    if options:
        module_cmd += f' {options}'

    if not linux.load_module(module_cmd):
        logging.error(f'scsi_debug_load_module() - Could not load {module_cmd}')
        return False
    # Wait a bit, for example for multipath to create the device
    linux.sleep(2)
    return True


def scsi_debug_unload_module():  # noqa: ANN201
    module_name = 'scsi_debug'
    if not linux.is_module_loaded(module_name):
        # Module is not loaded, return success
        return True

    if mp.is_multipathd_running():
        mpaths = mp.mpath_names_of_vendor('Linux')
        for mpath in mpaths:
            mp.remove_mpath(mpath)
            # Wait a bit, for example for multipath to remove the device
            linux.sleep(2)

    if not linux.unload_module(module_name):
        logging.error(f'scsi_debug_load_module() - Could not unload {module_name}')
        return False
    return True


def get_scsi_debug_devices():  # noqa: ANN201
    """Return a list of scsi_debug devices."""
    module_name = 'scsi_debug'
    vendor = 'Linux'
    if not linux.is_module_loaded(module_name):
        return None

    mpaths = mp.mpath_names_of_vendor(vendor)
    if mpaths:
        return mpaths

    scsi_devices = get_scsi_name_by_vendor(vendor)
    if scsi_devices:
        return scsi_devices

    return None


def scsi_debug_set_param(param, value):  # noqa: ANN001, ANN201
    """Set specific value to scsi debug parameter."""
    if param is None or value is None:
        logging.error('scsi_debug_set_param() - requires param_name and value')
        return False

    if (
        run(
            f"echo '{value}' > /sys/bus/pseudo/drivers/scsi_debug/{param}",
        )
        != 0
    ):
        logging.error(f'scsi_debug_set_param() - Could not set {param} with value {value}')
        return False
    return True


def scsi_debug_insert_failure(every_nth, opts):  # noqa: ANN001, ANN201
    """Purpose:
    Enable/Disable failure on scsi_debug device
    Parameter:
    A dictionary with all option to be set
    The supported parameters are defined at: http://sg.danny.cz/sg/sdebug26.html
    opts: 1 - "noisy"
    2-"medium error"
    4 - ignore "nth"
    8 - cause "nth" read or write command to yield a RECOVERED_ERROR
    16 -  cause "nth" read or write command to yield a ABORTED_COMMAND
    every_nth: how often the failure is inserted
    Return:
    True: if success
    False: if some problem occurred.
    """
    if not every_nth:
        every_nth = 0
    if not opts:
        opts = 0

    if not scsi_debug_set_param('every_nth', every_nth):
        logging.error(f'scsi_debug_insert_failure() - Could not set every_nth with value: {every_nth}')
        return False
    if not scsi_debug_set_param('opts', opts):
        logging.error(f'scsi_debug_insert_failure() - Could not set opts with value: {opts}')
        return False
    return True


def self_test():  # noqa: ANN201
    if not scsi_debug_load_module():
        logging.error('self_test() - Could not load the module')
        return False

    if not get_scsi_debug_devices():
        logging.error('self_test() - Could not find any scsi debug device')
        scsi_debug_unload_module()
        return False

    if not scsi_debug_insert_failure(0, 0):
        logging.error('self_test() - Could not set parameters')
        scsi_debug_unload_module()
        return False

    if not scsi_debug_unload_module():
        logging.error('self_test() - Could not unload the module')
        return False

    return True
