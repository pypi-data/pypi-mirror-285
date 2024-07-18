"""rdma.py: Module for rdma networking."""

from __future__ import annotations

#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from pathlib import Path

RDMA_SYSFS_BASE = '/sys/class/infiniband/'


def exists_rdma() -> bool:
    """Check whether it contains RDMA device.
    For each InfiniBand device, the InfiniBand drivers create the
    following files under /sys/class/infiniband/<device name>,
    https://www.landley.net/kdocs/Documentation/infiniband/sysfs.txt.

    Returns:
        True if it contains RDMA device, otherwise False.
    """
    return Path(RDMA_SYSFS_BASE).is_dir()


def exists_specific_rdma(ibdev: str) -> bool:
    """Check whether it contains certain RDMA device.

    Args:
        ibdev: The RDMA device ID

    Returns: True if it contains this RDMA device, otherwise False.
    """
    return Path(f'{RDMA_SYSFS_BASE}{ibdev}').is_dir()


# TODO add attributes
class Device:
    """RDMA HCA."""

    def __init__(self, ibdev: str) -> None:
        self.ports = None
        self.ibdev = ibdev

        self.path = Path(f'{RDMA_SYSFS_BASE}{self.ibdev}')
        for param in self.path.iterdir():
            if param.is_file():
                setattr(self, param.stem, param.read_text().strip())

        self.ports_path = self.path / 'ports/'
        self.ports = [port for port in self.ports_path.iterdir() if self.ports_path.is_dir()]
        self.port_numbers = [port.name for port in self.ports]
        self.device_path = Path(f'{RDMA_SYSFS_BASE}{self.ibdev}/device/').resolve()
        self.net_path = self.device_path / 'net/'

        self.is_sriov_capable = (self.device_path / 'sriov_numvfs').is_file()

    def get_netdevs(self) -> list[NetDev]:
        return [NetDev(eth) for eth in self.net_path.iterdir() if self.net_path.is_dir()]

    def get_netdev(self, port_id: str) -> NetDev | None:
        netdevs = self.get_netdevs()
        for dev in netdevs:
            if dev.dev_port == str(int(port_id) - 1):
                return dev
        return None

    def get_ports(self) -> list[Port] | None:
        return [Port(port) for port in self.ports] if self.ports else None

    def get_port(self, port: str) -> Port | None:
        path = self.ports_path / port
        return Port(path) if path.is_dir() else None

    def get_power(self) -> Power:
        return Power(self.path)

    def get_sriov(self) -> Sriov | None:
        return Sriov(self.device_path) if self.is_sriov_capable else None


class Port:
    """The port of an HCA."""

    def __init__(self, path: Path) -> None:
        self.name = path.name
        self.rate = None
        self.state: str | None = None
        self.phys_state: str | None = None
        for param in path.iterdir():
            if param.is_file():
                setattr(self, param.stem, param.read_text().strip())

        if self.rate:
            rate_split = self.rate.split()
            self.rate_speed = rate_split[0]
            self.rate_unit = rate_split[1]
            self.rate_info = f'{rate_split[2]} {rate_split[3]}'

        if self.state:
            self.state_num = self.state.split(':')[0]
            self.state_str = self.state.split(': ')[1]

        if self.phys_state:
            self.phys_state_num = self.phys_state.split(':')[0]
            self.phys_state_str = self.phys_state.split(': ')[1]


class Power:
    """The power of an HCA."""

    def __init__(self, path: Path) -> None:
        power_path = path / 'power'
        if power_path.is_dir():
            for param in power_path.iterdir():
                if param.is_file():
                    try:
                        value = param.read_text()
                    except OSError:
                        continue
                    setattr(self, param.stem, value.strip())


class NetDev:
    """The Netdev of an HCA."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.dev_port: str | None
        for param in self.path.iterdir():
            if param.is_file():
                try:
                    value = param.read_text()
                except OSError:
                    continue
                setattr(self, param.stem, value.strip())


class Sriov:
    """The sriov device info of an HCA.

    Single Root I/O Virtualization (SR-IOV) is a PCI Express Extended capability which makes one physical device
    appear as multiple virtual devices. The physical device is referred to as Physical Function (PF) while the
    virtual devices are referred to as Virtual Functions (VF). Allocation of the VF can be dynamically controlled by
    the PF via registers encapsulated in the capability. By default, this feature is not enabled and the PF behaves
    as traditional PCIe device. Once it is turned on, each VFs PCI configuration space can be accessed by its own
    Bus, Device and Function Number (Routing ID).

    https://docs.kernel.org/PCI/pci-iov-howto.html
    """

    def __init__(self, path: Path) -> None:
        """Initializes the instance based on the sysfs files.

        Args:
            path: Defines the sysfs device path.
        """
        self.sriov_numvfs_path = path / 'sriov_numvfs'
        self.sriov_numvfs: str | None = None
        self.sriov_totalvfs: str | None = None
        if path.is_dir():
            for param in path.iterdir():
                if param.is_file():
                    try:
                        value = param.read_text()
                    except (OSError, UnicodeDecodeError):
                        continue
                    setattr(self, param.stem, value.strip())

    def set_sriov_numvfs(self, num: str = '1') -> None:
        """Sets the number of VF devices for a SR-IOV PF.

        Args:
            num: Defines the number of vfs.
        """
        if self.sriov_numvfs and num != self.sriov_numvfs:
            self.sriov_numvfs_path.write_text('0')
            self.sriov_numvfs_path.write_text(num)
            self.sriov_numvfs = self.read_sriov_numvfs()

    def read_sriov_numvfs(self) -> str | None:
        """Read the sysfs file to get the real vf number.

        Returns:
            The real vf number.
        """
        return self.sriov_numvfs_path.read_text().strip() if self.sriov_numvfs_path.is_file() else None
