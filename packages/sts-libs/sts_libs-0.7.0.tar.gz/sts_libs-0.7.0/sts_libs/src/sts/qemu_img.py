"""qemu_img.py: Module to manipulate disk image using QEMU disk image utility."""

import logging
from pathlib import Path

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from sts import linux
from sts.utils.cmdline import run

_QCOW_SUPPORTED_OPTIONS = [
    'compat',
    'backing_file',
    'encryption',
    'cluster_size',
    'preallocation',
    'lazy_refcounts',
]


def _get_package_name():  # noqa: ANN202
    return 'qemu-img'


def _get_image_file(name, image_path):  # noqa: ANN001, ANN202
    return f'{image_path}/{name}.img'


def get_qcow_supported_options():  # noqa: ANN201
    """Return supported options for qcow image.

    Returns:
      List of strings.
    """
    return _QCOW_SUPPORTED_OPTIONS


def install_qemu_img():  # noqa: ANN201
    """Install qemu-img tool.

    Returns:
    True: If qemu-img is installed correctly
    False: If some problem happened
    """
    if not linux.install_package(_get_package_name()):
        logging.error(f'Could not install {_get_package_name()}')
        return False
    return True


def qemu_create(filename, size='1024', fmt=None, img_path='/var/tmp', **options):  # noqa: ANN001, ANN003, ANN201
    """Create the new disk image.

    Args:
      filename: is a disk image filename
      size: is the disk image size in bytes
      fmt: is the disk image format
      img_path: is the full path to output directory
      **options: see supported options for a qcow image

    Returns:
    True: if success
    False: in case of failure
    """
    if not linux.is_installed(_get_package_name()):
        install_qemu_img()
    if not filename:
        logging.error('qemu_create() requires parameter filename')
        return False
    if img_path:
        filename = _get_image_file(filename, img_path)
    cmd = _get_package_name() + ' create '
    if fmt is not None:
        cmd += f'-f {fmt}'
    if fmt == 'qcow2' and options:
        cmd += ' -o '
        option = [str(i) + '=' + str(options[i]) for i in options if i in _QCOW_SUPPORTED_OPTIONS]
        cmd += ','.join(option)
    cmd += f' {filename} {size}'
    if run(cmd).rc != 0:
        logging.error('Could not create disk image.')
        return False
    return True


def delete_image(name, image_path='/var/tmp'):  # noqa: ANN001, ANN201
    """Delete the disk image.

    Args:
      name: is the image filename
      image_path: is the full path to the image directory

    Returns:
    True: if success
    False: in case of failure
    """
    if not name:
        logging.error('delete_image() - requires name parameter')
        return False

    logging.info(f'Deleting image device {name}')
    fname = _get_image_file(name, image_path)
    if Path(fname).is_file():
        cmd = f'rm -f {fname}'
        if run(cmd).rc != 0:
            logging.error(f'Could not delete image disk file {fname}')
            return False
    return True
