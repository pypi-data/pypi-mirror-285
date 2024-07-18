#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging

import pytest

from sts import scsi


def test_query_scsi_hosts() -> None:
    hosts = scsi.get_hosts()
    if not hosts:
        logging.info('SKIP: Could not find scsi hosts')
        return

    for host in hosts:
        print(f'Querying info for host {host}')
        info = scsi.query_scsi_host_info(host)
        if not info:
            pytest.fail(f'Could not query info for host: {host}')
        for inf in info:
            print(f'\t{inf}: {info[inf]}')

    assert 1


def test_query_scsi_disks() -> None:
    disks = scsi.query_all_scsi_disks()
    if not disks:
        logging.info('SKIP: Could not find scsi disks')
        return

    for disk in disks:
        logging.info(f'details for scsi id: {disk}')
        disk_info = disks[disk]
        for info in disk_info:
            print(f'\t{info}: {disk_info[info]}')

    assert 1
