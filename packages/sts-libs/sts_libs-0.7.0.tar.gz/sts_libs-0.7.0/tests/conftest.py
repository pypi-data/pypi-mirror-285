#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
import logging
from collections.abc import Generator
from os import getenv

import pytest

from sts import iscsi
from sts.iscsi import ConfVars, IfaceVars, TargetVars

pytest_plugins = [
    'sts.fixtures.iscsi_fixtures',
    'sts.fixtures.rdma_fixtures',
    'sts.fixtures.stratis_fixtures',
    'sts.fixtures.common_fixtures',
    'sts.fixtures.lvm_fixtures',
    'sts.fixtures.target_fixtures',
]


@pytest.fixture(scope='class')
def _iscsi_offload_setup(_iscsi_test: Generator) -> None:
    iscsi_env = getenv('ISCSI_SETUP_VARS')

    be2iscsi_vars: ConfVars = {
        'initiatorname': 'iqn.1994-05.com.redhat:storageqe-84',
        'ifaces': [IfaceVars(iscsi_ifacename='be2iscsi.00:90:fa:d6:bc:ed.ipv4.0', ipaddress='172.16.1.84')],
        'targets': [TargetVars(portal='172.16.1.10', interface='be2iscsi.00:90:fa:d6:bc:ed.ipv4.0')],
    }

    bnx2i_vars: ConfVars = {
        'initiatorname': 'iqn.1994-05.com.redhat:storageqe-83',
        'ifaces': [IfaceVars(iscsi_ifacename='bnx2i.ac:16:2d:85:64:bd', ipaddress='172.16.1.83')],
        'targets': [TargetVars(interface='bnx2i.ac:16:2d:85:64:bd', portal='172.16.1.10')],
    }

    cxgb4i_vars: ConfVars = {
        'initiatorname': 'iqn.1994-05.com.redhat:storageqe-87',
        'ifaces': [IfaceVars(iscsi_ifacename='cxgb4i.00:07:43:73:04:b8.ipv4.0', ipaddress='172.16.1.87')],
        'targets': [TargetVars(interface='cxgb4i.00:07:43:73:04:b8.ipv4.0', portal='172.16.1.10')],
    }

    intel_vars: ConfVars = {
        'initiatorname': 'iqn.1994-05.com.redhat:storageqe-82',
        'ifaces': [IfaceVars(hwaddress='b4:96:91:a0:68:8b', iscsi_ifacename='intel-e810-p1', ipaddress='172.16.1.82')],
        'targets': [TargetVars(interface='intel-e810-p1', portal='172.16.1.10')],
    }

    qedi_vars: ConfVars = {
        'initiatorname': 'iqn.1994-05.com.redhat:storageqe-86',
        'ifaces': [IfaceVars(iscsi_ifacename='qedi.00:0e:1e:f1:9c:f1', ipaddress='172.16.1.86')],
        'targets': [TargetVars(interface='qedi.00:0e:1e:f1:9c:f1', portal='172.16.1.10')],
    }
    vars_mapping = {
        'intel': intel_vars,
        'qedi': qedi_vars,
        'cxgb4i': cxgb4i_vars,
        'cxgb4i_noipv4': cxgb4i_vars,
        'be2iscsi': be2iscsi_vars,
        'bnx2i': bnx2i_vars,
    }

    if not iscsi_env:
        logging.error('_iscsi_offload_setup requires ISCSI_SETUP_VARS')
        return
    try:
        vars_to_set = vars_mapping[iscsi_env]
    except KeyError as err:
        raise ValueError(f'Unsupported ISCSI_SETUP_VARS value: {iscsi_env}') from err

    if iscsi_env == 'cxgb4i_noipv4':
        vars_to_set['ifaces'][0]['iscsi_ifacename'] = 'cxgb4i.00:07:43:73:04:b8'

    iscsi.setup(vars_to_set)
