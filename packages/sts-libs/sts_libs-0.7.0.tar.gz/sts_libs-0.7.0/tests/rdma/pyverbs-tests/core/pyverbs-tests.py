from os import getenv
from pathlib import Path

from sts.linux import install_package
from sts.utils.cmdline import run

hca_id = getenv('RDMA_HCA_ID', 'mlx5_0')
port_id = getenv('RDMA_PORT', '1')


def test_pyverbs() -> None:
    """Run RDMA pyverbs tests."""
    assert install_package('python3-pyverbs')
    test_bin = Path('/usr/share/doc/rdma-core/tests/run_tests.py')
    assert test_bin.is_file(), f'{test_bin} does not exist.'
    assert run(
        f'python {test_bin} --dev {hca_id} --port {port_id} -v',
    ).succeeded, f'{test_bin} test(s) have failed'
