#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import patch

import pytest
from testinfra.backend.base import CommandResult

from sts import iscsi

target = 'localhost'


def test_install_initiator() -> None:
    if not iscsi.install():
        pytest.fail('FAIL: Could not install iSCSI initiator package')
    assert 1


def test_query_discovery(monkeypatch) -> None:
    discovery_output = (
        'SENDTARGETS:\nDiscoveryAddress: 172.16.0.10,3260\nTarget: '
        'iqn.2002-03.com.compellent:test-0\n\tPortal: 172.16.0.10:3260,0\n\t\tIface Name: '
        'qedi.00:0e:1e:f1:9c:f0\nTarget: iqn.2002-03.com.compellent:test-1\n\tPortal: '
        '172.16.0.10:3260,0\n\t\tIface Name: qedi.00:0e:1e:f1:9c:f0\niSNS:\nNo targets '
        'found.\nSTATIC:\nNo targets found.\nFIRMWARE:\nNo targets found.\n'
    )
    monkeypatch.setattr(CommandResult, 'failed', False)
    monkeypatch.setattr(CommandResult, 'stdout', discovery_output)

    expected_ret = {
        'SENDTARGETS': {
            '172.16.0.10,3260': {
                'disc_addr': '172.16.0.10',
                'disc_port': '3260',
                'mode': 'sendtargets',
                'targets': {
                    'iqn.2002-03.com.compellent:test-0': {
                        'portal': {
                            'address': '172.16.0.10',
                            'port': '3260',
                        },
                        'iface': ['qedi.00:0e:1e:f1:9c:f0'],
                    },
                    'iqn.2002-03.com.compellent:test-1': {
                        'portal': {'address': '172.16.0.10', 'port': '3260'},
                        'iface': ['qedi.00:0e:1e:f1:9c:f0'],
                    },
                },
            },
        },
        'iSNS': {},
        'STATIC': {},
        'FIRMWARE': {},
    }

    assert iscsi.query_discovery() == expected_ret


def test_discovery(monkeypatch) -> None:
    discovery_output = '[::1]:3260,1 iqn.2009-10.com.redhat:storage-0'
    monkeypatch.setattr(CommandResult, 'failed', False)
    monkeypatch.setattr(CommandResult, 'stdout', discovery_output)

    if not iscsi.discovery_st(target):
        pytest.fail('FAIL: Could not discover iSCSI target')
    assert 1


@patch('sts.linux.service_restart')
def test_set_iscsid_parameter(service_restart_func) -> None:
    service_restart_func.return_value = True
    iscsi.set_iscsid_parameter({'node.session.cmds_max': '4096', 'node.session.queue_depth': '128'})
