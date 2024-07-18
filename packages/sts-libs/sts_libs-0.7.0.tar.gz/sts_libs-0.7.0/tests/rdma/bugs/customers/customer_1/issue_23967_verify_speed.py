from os import getenv

from sts import rdma


def test_speed() -> None:
    hca_id = getenv('RDMA_HCA_ID', 'mlx5_0')
    port_id = getenv('RDMA_PORT', '1')
    actual_speed = getenv('RDMA_ACTUAL_SPEED', '100')

    device: rdma.Device = rdma.Device(hca_id)
    port: rdma.Port = device.get_port(port_id)
    netdev = device.get_netdev(port_id)

    assert port.rate_speed == actual_speed
    assert int(actual_speed) == int(netdev.speed) / 1000
