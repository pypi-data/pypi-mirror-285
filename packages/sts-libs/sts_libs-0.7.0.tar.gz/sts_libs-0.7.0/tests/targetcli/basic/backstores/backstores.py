#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import lio

# Test parameters
fileio_args = [
    {'name': 'bs_fileio_1g', 'size': '1g', 'file_or_dev': 'fileio_testfile_1g', 'size_in_byte': '1073741824'},
    {'name': 'bs_fileio_1b', 'size': '1b', 'file_or_dev': 'fileio_testfile_1b', 'size_in_byte': '1'},
    {'name': 'bs_fileio_10m', 'size': '10m', 'file_or_dev': 'fileio_testfile_10m', 'size_in_byte': '10485760'},
]
unsupported_attributes = [
    'alua_support',
    'block_size',
    'emulate_rest_reord',
    'emulate_dpo',
    'emulate_fua_read',
    'pi_prot_verify',
    'emulate_tpws',
    'unmap_zeroes_data',
    'pi_prot_format',
    'pgr_support',
    'emulate_write_cache',  # Unable to set for block
    'pi_prot_type',  # Unable to set for block
    'emulate_tpu',  # Cannot set for ramdisk
]
sub_table = {'0': '1', '1': '0'}

loopdev_args = [{'name': 'loop1', 'size': '100'}]
block_args = [{'name': 'bs_block_1'}]

ramdisk_args = [
    {'name': 'bs_ramdisk_1', 'size': '6M'},
]


def compare_attributes(dict1: dict, dict2: dict) -> bool:
    for attribute in dict1:
        if int(dict1[attribute]) != int(dict2[attribute]):
            logging.error(f'FAIL: {attribute}  {dict1[attribute]!s} != {dict2[attribute]}')
            return False
    return True


def get_attributes(all_attr: dict) -> dict:
    attr = {}
    for _k, _v in all_attr.items():
        if '[ro]' not in _v:
            if _k in unsupported_attributes:
                continue
            attr[_k] = _v

    return attr


def set_attributes(bs: lio.Backstore) -> None:
    default_attr = get_attributes(bs.get_attributes())

    for attribute in default_attr:
        if int(default_attr[attribute]) == 0 or int(default_attr[attribute]) == 1:
            default_attr[attribute] = sub_table[default_attr[attribute]]
        else:
            default_attr[attribute] = int(int(default_attr[attribute]) / 2)

    result = bs.set_attributes(**default_attr)
    assert result.succeeded

    changed_attr = get_attributes(bs.get_attributes())

    assert compare_attributes(default_attr, changed_attr)


@pytest.mark.parametrize('loopdev_setup', loopdev_args, indirect=True)
@pytest.mark.parametrize('backstore_block_setup', block_args, indirect=True)
def test_backstore_block(backstore_block_setup) -> None:  # noqa: ANN001
    """Sets/gets block backstore attributes."""
    bs = backstore_block_setup
    set_attributes(bs)


@pytest.mark.parametrize('backstore_fileio_setup', fileio_args, indirect=True)
@pytest.mark.usefixtures('backstore_fileio_setup')
def test_backstore_fileio() -> None:
    """Creates fileio backstores with different size."""
    assert True


@pytest.mark.parametrize('backstore_fileio_setup', [fileio_args[1]], indirect=True)
def test_fileio_attributes(backstore_fileio_setup) -> None:  # noqa: ANN001
    """Sets/gets fileio backstore attributes."""
    bs = backstore_fileio_setup
    set_attributes(bs)


@pytest.mark.parametrize('backstore_ramdisk_setup', ramdisk_args, indirect=True)
def test_backstore_ramdisk(backstore_ramdisk_setup) -> None:  # noqa: ANN001
    """Sets/gets ramdisk backstore attributes."""
    bs = backstore_ramdisk_setup
    set_attributes(bs)
