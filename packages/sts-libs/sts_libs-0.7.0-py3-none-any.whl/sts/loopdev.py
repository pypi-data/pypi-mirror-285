"""loopdev.py: Module to manipulate loop devices using losetup."""

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
from pathlib import Path

from sts import linux
from sts.utils.cmdline import run, run_ret_out
from sts.utils.size import size_bytes_2_size_human, size_human_2_size_bytes


def _get_loop_path(name):  # noqa: ANN001, ANN202
    loop_path = name
    if '/dev/' not in name:
        loop_path = '/dev/' + name

    return loop_path


def _get_image_file(name, image_path):  # noqa: ANN001, ANN202
    return f'{image_path}/{name}.img'


def _standardize_name(name):  # noqa: ANN001, ANN202
    """Make sure use same standard for name, for example remove /dev/ from it if exists."""
    if not name:
        logging.error('_standardize_name() - requires name as parameter')
        return None
    return name.replace('/dev/', '')


def create_loopdev(name=None, size=1024, image_path='/var/tmp', reuse_file=False):  # noqa: ANN001, ANN201
    """Create a loop device
    Parameters:
    name:         eg. loop0 (optional)
    size:         Size in MB (default: 1024MB)
    image_path:   Path to store the image (default: /var/tmp)
    reuse_file:   Reuse a previous image file (default: False).
    """
    #    name = args['name']
    #    if name is None:
    #        name = "loop0"

    #    size = args['size']
    #    if size is None:
    #        size = 1024

    if not name:
        cmd = 'losetup -f'
        retcode, output = run_ret_out(cmd, return_output=True)
        if retcode != 0:
            logging.error('Could not find free loop device')
            print(output)
            return None
        name = output
    name = _standardize_name(name)

    fname = _get_image_file(name, image_path)
    logging.info(f'Creating loop device {fname} with size {size}')

    if not reuse_file and Path(fname).is_file():
        logging.info(f'Deleting file {fname}')
        # If for some reason the file exist, and we don't want reuse, delete it.
        run(f'rm -f {fname}')

    # make sure we have enough space to create the file
    free_space_bytes = linux.get_free_space(image_path)
    # Convert the size given in megabytes to bytes
    size_bytes = int(size_human_2_size_bytes(f'{size}MiB'))
    if free_space_bytes <= size_bytes:
        print(
            f'FAIL: Not enough space to create loop device with size {size_bytes_2_size_human(size_bytes)}',
        )
        print(f'available space: {size_bytes_2_size_human(free_space_bytes)}')
        return None
    logging.info(f'Creating file {fname}')
    # cmd = "dd if=/dev/zero of=%s seek=%d bs=1M count=0" % (fname, size)
    cmd = f'fallocate -l {size}M {fname}'
    try:
        # We are just creating the file, not writting zeros to it
        if run(cmd).rc != 0:
            print(f'command failed with code {retcode}')
            logging.error('Could not create loop device image file')
            return None
    except OSError as e:
        print('command failed: ', e, file=sys.stderr)
        return None

    loop_path = _get_loop_path(name)
    # detach loop device if it exists
    detach_loopdev(loop_path)

    # Going to associate the file to the loopdevice
    cmd = f'losetup {loop_path} {fname}'
    if run(cmd).rc != 0:
        logging.error('Could not create loop device')
        return None

    return loop_path


def delete_loopdev(name):  # noqa: ANN001, ANN201
    """Delete a loop device
    Parameters:
    name:     eg. loop0 or /dev/loop0.
    """
    if not name:
        logging.error('delete_loopdev() - requires name parameter')
        return False

    logging.info(f'Deleting loop device {name}')
    name = _standardize_name(name)

    loop_path = _get_loop_path(name)

    # find image file
    fname = get_loopdev_file(loop_path)
    if fname is None:
        logging.warning(f'could not find loopdev named {name}')
        # loopdev does not exist, nothing to do
        return True

    # detach loop device if it exists
    if not detach_loopdev(name):
        logging.error(f'could not detach {loop_path}')
        return False

    if Path(fname).is_file():
        cmd = f'rm -f {fname}'
        if run(cmd).rc != 0:
            logging.error(f'Could not delete loop device file {fname}')
            return False

    # check if loopdev file is deleted as it sometimes remains
    if Path(fname).is_file():
        logging.error(f'Deleted loop device file {fname} but it is still there')
        return False

    return True


# show loop devices
def list_loopdev():  # noqa: ANN201
    retcode, output = run_ret_out('losetup -a', return_output=True)
    return retcode, output


# Return all loop devices
def get_loopdev():  # noqa: ANN201
    # example of output on rhel-6.7
    # /dev/loop0: [fd00]:396428 (/var/tmp/loop0.img)
    retcode, output = run_ret_out("losetup -a | awk '{print$1}'", return_output=True)
    # retcode, output = run_ret_out("losetup -l | tail -n +2", return_output=True)
    if retcode != 0:
        logging.error('get_loopdev failed to execute')
        print(output)
        return None

    devs = None
    if output:
        devs = output.split('\n')
        # remove the ":" character from all devices
        devs = [d.replace(':', '') for d in devs]

    return devs


# Return loop device file for given path
def get_loopdev_file(loop_path):  # noqa: ANN001, ANN201
    # example of output on rhel-6.7
    # /dev/loop0: [fd00]:396428 (/var/tmp/loop0.img)
    retcode, output = run_ret_out(
        "losetup -a | grep '%s:' | awk '{print$3}'" % loop_path,  # noqa: UP031
        return_output=True,
    )
    if retcode != 0:
        logging.error('get_loopdev_file failed to execute')
        print(output)
        return None

    if output:
        # remove the "(" and ")" character from device
        dev = output[1:-1]
    else:
        logging.warning('get_loopdev_file failed to requested loopdev')
        return None

    return dev


def detach_loopdev(name=None):  # noqa: ANN001, ANN201
    cmd = 'losetup -D'
    if name:
        devs = get_loopdev()
        if not devs:
            # No device was found
            return False

        name = _standardize_name(name)

        # Just try to detach if device is connected, otherwise ignore
        # print "INFO: Checking if ", loop_path, " exists, to be detached"
        dev_path = _get_loop_path(name)
        if dev_path in devs:
            cmd = f'losetup -d {dev_path}'
        else:
            # if loop device does not exist just ignore it
            return True

    # run losetup -D or -d <device>
    if run(cmd).rc != 0:
        logging.error('Could not detach loop device')
        return False

    return True
