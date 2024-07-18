#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)
from os import getenv

import pytest

from sts import stratis
from sts.utils.logchecker import check_all


@pytest.mark.usefixtures('setup_stratis_key')
def test_pool_create(setup_stratis_key: str) -> None:
    key_desc = setup_stratis_key
    pool = stratis.Pool()
    pool_name = getenv('STRATIS_POOL_NAME', 'pool1')
    blockdevs = pool.setup_blockdevices()
    assert pool.create(pool_name=pool_name, blockdevs=blockdevs).succeeded
    assert ', Op' in pool.list_pools().stdout
    assert 'Allows Overprovisioning: Yes' in pool.list_pools(pool_name=pool_name).stdout
    assert pool.stop(pool_name=pool_name).succeeded
    assert pool.start(pool_name=pool_name).succeeded
    pool_uuid = pool.get_pool_uuid(pool_name=pool_name)
    assert pool_uuid is not None
    assert pool.stop(pool_uuid=pool_uuid).succeeded
    assert pool.start(pool_uuid=pool_uuid).succeeded
    assert pool.destroy(pool_name=pool_name).succeeded

    assert pool.create(pool_name=pool_name, blockdevs=blockdevs, no_overprovision=True)
    assert '~Op' in pool.list_pools().stdout
    assert 'Allows Overprovisioning: No' in pool.list_pools(pool_name=pool_name).stdout
    assert pool.stop(pool_name=pool_name).succeeded
    assert pool.start(pool_name=pool_name).succeeded
    assert '~Op' in pool.list_pools().stdout
    assert 'Allows Overprovisioning: No' in pool.list_pools(pool_name=pool_name).stdout
    pool_uuid = pool.get_pool_uuid(pool_name=pool_name)
    assert pool_uuid is not None
    assert pool.stop(pool_uuid=pool_uuid).succeeded
    assert pool.start(pool_uuid=pool_uuid).succeeded
    assert '~Op' in pool.list_pools().stdout
    assert 'Allows Overprovisioning: No' in pool.list_pools(pool_name=pool_name).stdout
    assert pool.destroy(pool_name=pool_name).succeeded

    assert pool.create(pool_name=pool_name, blockdevs=blockdevs, key_desc=key_desc).succeeded
    assert pool.destroy(pool_name=pool_name).succeeded
    assert pool.create(pool_name=pool_name, blockdevs=blockdevs, key_desc=key_desc, no_overprovision=True).succeeded
    assert pool.destroy(pool_name=pool_name).succeeded

    assert check_all()
