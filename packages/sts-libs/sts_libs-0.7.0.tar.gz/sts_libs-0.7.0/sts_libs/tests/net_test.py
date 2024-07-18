#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import unittest
from unittest.mock import patch

from sts import net

MAC = '7E:CD:60:1E:AC:6E'
NOTMAC = '7E:CD:60:1E:AC'
BADMAC = '7ecd.601e.ac6e'
LOWMAC = '7e:cd:60:1e:ac:6e'
NOTVALID = 'ThisIsNotValid'
LOCALHOST = '127.0.0.1'
NETMASK24 = '255.255.255.0'
CIDR24 = '24'
NOTIP = '256.256.256.256'
IPV6 = 'fd6f:60d2:2d9:0:b7e:b6e6:7bf5:c17e'


class TestNet(unittest.TestCase):
    def test_is_mac(self) -> None:
        assert net.is_mac(MAC)
        assert not net.is_mac(NOTMAC)

    def test_get_nics(self) -> None:
        assert net.get_nics() is not None

    def test_get_mac_of_nics(self) -> None:
        assert net.get_mac_of_nic(NOTVALID) is None
        assert net.get_mac_of_nic(net.get_nics()[-1]) is not None

    def test_get_nic_of_mac(self) -> None:
        assert net.get_nic_of_mac(MAC) is None
        assert net.get_nic_of_mac(net.get_mac_of_nic(net.get_nics()[-1])) is not None

    def test_get_ip_address_of_nic(self) -> None:
        assert net.get_ip_addresses_of_nic(NOTVALID) is None
        assert net.get_ip_addresses_of_nic(net.get_nics()[-1]) is not None

    def test_get_nic_of_ip(self) -> None:
        assert net.get_nic_of_ip(NOTIP) is None
        assert net.get_nic_of_ip(LOCALHOST) is not None

    def test_driver_of_nic(self) -> None:
        assert net.driver_of_nic(NOTVALID) is None

    def test_get_ip_version(self) -> None:
        assert net.get_ip_version(LOCALHOST) == 4
        assert net.get_ip_version(IPV6) == 6
        assert net.get_ip_version(NOTIP) is None

    def test_standardize_mac(self) -> None:
        assert net.standardize_mac(BADMAC) == LOWMAC
        assert net.standardize_mac(NOTMAC) is None

    def test_convert_netmask(self) -> None:
        assert int(CIDR24) == net.convert_netmask(NETMASK24)
        assert int(CIDR24) == net.convert_netmask(CIDR24)
        assert net.convert_netmask(NOTVALID) is None

    def test_nm_get_conn(self) -> None:
        assert net.nm_get_conn(MAC) is None
        assert net.nm_get_conn(NOTVALID) is None

    def test_nm_get_conn_iface(self) -> None:
        assert net.nm_get_conn_iface(NOTVALID) is None

    def test_nm_get_conn_uuid(self) -> None:
        assert net.nm_get_conn_uuid(NOTVALID) is None

    def test_nm_get_conn_from_dev(self) -> None:
        assert net.nm_get_conn_from_dev(NOTVALID) is None

    def test_nm_get_dev_from_conn(self) -> None:
        assert net.nm_get_dev_from_conn(NOTVALID) is None

    def test_nm_conn_up(self) -> None:
        assert not net.nm_conn_up(NOTVALID)

    def test_nm_set_ip(self) -> None:
        assert not net.nm_set_ip(NOTVALID, NOTIP)
        assert not net.nm_set_ip(NOTVALID, IPV6)

    def test_nm_dev_mod_success(self) -> None:
        with patch('sts.net.run_ret_out') as run_func:
            run_func.return_value = [0, '']
            assert net.nm_dev_mod('enp17s0f1', 'connection.autoconnect', 'yes')

    def test_nm_dev_mod_failure(self) -> None:
        with patch('sts.net.run_ret_out') as run_func:
            run_func.return_value = [1, 'Mocked failure']
            assert not net.nm_dev_mod('enp17s0f1', 'connection.autoconnect', 'yes')

    def test_nm_set_ip_success(self) -> None:
        with patch('sts.net.run_ret_out') as run_func:
            run_func.return_value = [0, '']
            assert net.nm_set_ip('enp17s0f1', '192.168.10.18', activate=False)

    def test_nm_set_ip_failure(self) -> None:
        with patch('sts.net.run_ret_out') as run_func:
            run_func.return_value = [1, 'Mocked failure']
            assert not net.nm_set_ip('enp17s0f1', '192.168.10.18', activate=False)
