#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Tests iSCSI parameters negotiation with iscsiadm, targetcli."""

import logging
from itertools import product

import pytest

from sts import fio, iscsi, linux, lio, mp, scsi

t_iqn = 'iqn.2017-11.com.redhat:params-target'
i_iqn = 'iqn.2017-11.com.redhat:params-client'
parameters = [
    'HeaderDigest',  # digest_pool
    'MaxRecvDataSegmentLength',  # byte_pool
    'MaxXmitDataSegmentLength',  # byte_pool
    'MaxBurstLength',  # byte_pool
    'FirstBurstLength',  # byte_pool
    'ImmediateData',  # yesno_pool
    'InitialR2T',  # yesno_pool
]  # Parameters to be changed.


def do_io(device: str) -> bool:
    """Running randwrite using FIO until the 256M device is full, then verifying written data using CRC32C."""
    f = fio.FIO(filename=device)
    f.update_parameters({'runtime': '120'})  # adding runtime cap of 2 minutes

    if not f.run():
        logging.error('FIO I/O failed')
        return False

    return True


@pytest.mark.usefixtures('_iscsi_localhost_test')
def test_parameters() -> None:
    iscsi.set_initiatorname(i_iqn)

    digest_pool = [
        'None',
        'CRC32C',
        'None,CRC32C',
        'CRC32C,None',
    ]
    yesno_pool = ['Yes', 'No']
    byte_pool = [
        '512',
        '16777212',
    ]

    # Make pool (list) of 14+ 'permutations'
    r = 2  # repeat - initiator, target = 2
    digest_cartesian = list(product(digest_pool, repeat=r))
    # Prevent 'CRC32C'+'None'
    digest_cartesian = [p for p in digest_cartesian if p not in {('None', 'CRC32C'), ('CRC32C', 'None')}]  # 14
    yesno_cartesian = list(product(yesno_pool, repeat=r)) * 4  # 16 permutations
    byte_cartesian = list(product(byte_pool, repeat=r)) * 4  # 16 permutations

    _mbl = 'MaxBurstLength'

    assert lio.create_basic_iscsi_target(
        target_wwn=t_iqn,
        initiator_wwn=i_iqn,
        size='256M',
    )

    target = lio.Iscsi(target_wwn=t_iqn)

    iterations = 14
    for i in range(iterations):
        logging.info(f'Iteration {i}')
        tgt_params_values = {
            'HeaderDigest': digest_cartesian[i][0],
            'MaxRecvDataSegmentLength': byte_cartesian[i][0],
            'MaxXmitDataSegmentLength': byte_cartesian[-i][0],
            'MaxBurstLength': byte_cartesian[-i][0],
            'FirstBurstLength': byte_cartesian[i][0],
            'ImmediateData': yesno_cartesian[i][0],
            'InitialR2T': yesno_cartesian[-i][0],
        }

        in_params_values = {
            'node.conn[0].iscsi.HeaderDigest': digest_cartesian[i][1],
            'node.conn[0].iscsi.MaxRecvDataSegmentLength': byte_cartesian[i][1],
            'node.conn[0].iscsi.MaxXmitDataSegmentLength': byte_cartesian[~i][1],
            'node.session.iscsi.MaxBurstLength': byte_cartesian[~i][1],
            'node.session.iscsi.FirstBurstLength': byte_cartesian[i][1],
            'node.session.iscsi.ImmediateData': yesno_cartesian[i][1],
            'node.session.iscsi.InitialR2T': yesno_cartesian[~i][1],
        }

        iscsi.cleanup()

        # Setting parameter values with targetcli.
        for param in tgt_params_values:
            if not target.set_parameter(parameter=param, value=tgt_params_values[param]):
                pytest.fail('Unable to set target parameters')

        iscsi.set_iscsid_parameter(in_params_values)  # Setting parameter values in /etc/iscsid.conf.

        iscsi.discovery_st('127.0.0.1', disc_db=True, ifaces='default')
        assert iscsi.node_login(portal='127.0.0.1', udev_wait_time=5)

        # How to check params manually:
        # iscsiadm -m session -P2 | grep HeaderDigest | cut -d " " -f 2
        # cat /sys/class/iscsi_connection/connection*/header_digest
        # cat /sys/class/iscsi_session/session*/first_burst_len

        # Printing negotiated values.
        test_session = iscsi.Session
        sessions = iscsi.get_sessions()
        for s in sessions:
            if s.target_name == t_iqn:
                test_session = s
                break

        if not test_session:
            pytest.fail('Unable to find the correct iSCSI session')

        negotiated = test_session.get_data_p2()

        # Same parameters in /etc/iscsid.conf
        iscsid_params_dict = {
            'HeaderDigest': 'node.conn[0].iscsi.HeaderDigest',
            'MaxRecvDataSegmentLength': 'node.conn[0].iscsi.MaxRecvDataSegmentLength',
            'MaxXmitDataSegmentLength': 'node.conn[0].iscsi.MaxXmitDataSegmentLength',
            'MaxBurstLength': 'node.session.iscsi.MaxBurstLength',
            'FirstBurstLength': 'node.session.iscsi.FirstBurstLength',
            'ImmediateData': 'node.session.iscsi.ImmediateData',
            'InitialR2T': 'node.session.iscsi.InitialR2T',
        }

        for p in parameters:
            t_value = tgt_params_values[p]
            i_value = in_params_values[iscsid_params_dict[p]]
            n_value = negotiated[p]
            n_expected = None
            logging.info(f'{p}: Target: {t_value} | Initiator: {i_value} | Negotiated: {n_value}')

            # Check if negotiated values are correct
            if p == 'HeaderDigest':
                n_expected = 'CRC32C' if 'None' not in i_value or 'None' not in t_value else 'None'

                if 'CRC32C' not in i_value or 'CRC32C' not in t_value:
                    n_expected = 'None'

                if i_value == 'CRC32C,None' and t_value == 'None,CRC32C':
                    n_expected = 'CRC32C'

                if i_value == 'CRC32C,None' and t_value == 'CRC32C,None':
                    n_expected = 'CRC32C'

                if i_value == 'None,CRC32C' and t_value == 'CRC32C,None':
                    n_expected = 'None'

                if i_value == 'None,CRC32C' and t_value == 'None,CRC32C':
                    n_expected = 'None'

            elif p == 'MaxRecvDataSegmentLength':
                n_expected = i_value

            elif p in {'MaxXmitDataSegmentLength', 'MaxBurstLength'}:
                n_expected = t_value if int(t_value) < int(i_value) else i_value

            elif p == 'ImmediateData':
                n_expected = 'Yes' if t_value == 'Yes' and i_value == 'Yes' else 'No'

            elif p == 'InitialR2T':
                n_expected = 'No' if t_value == 'No' and i_value == 'No' else 'Yes'

            elif p == 'FirstBurstLength':
                n_expected = t_value if int(t_value) < int(i_value) else i_value
                # FirstBurstLength cannot be higher than MaxBurstLength
                if int(tgt_params_values[_mbl]) < int(in_params_values[iscsid_params_dict[_mbl]]):
                    exp_max_burst = tgt_params_values[_mbl]
                else:
                    exp_max_burst = in_params_values[iscsid_params_dict[_mbl]]

                if int(n_expected) > int(exp_max_burst):
                    n_expected = exp_max_burst

            assert n_expected == n_value, f'Negotiated parameter {p} has unexpected value'

        # Choosing a device to run IO on.
        test_dev = None
        if linux.is_service_running(mp.mp_service_name()):
            mpaths = mp.get_free_mpaths()
            if mpaths:
                test_dev = '/dev/mapper/' + next(iter(mpaths.keys()))
        if not test_dev:
            dev = scsi.get_free_disks(filter_only={'model': 'params-client'})
            if not dev:
                pytest.fail('Could not find device to use...')
            test_dev = '/dev/' + next(iter(dev.keys()))

        assert do_io(test_dev)
