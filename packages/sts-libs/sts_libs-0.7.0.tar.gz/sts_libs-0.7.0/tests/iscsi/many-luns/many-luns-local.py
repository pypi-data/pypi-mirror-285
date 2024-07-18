import pytest

from sts import iscsi, lio
from sts.linux import package_info, wait_udev
from sts.utils.cmdline import run


@pytest.mark.usefixtures('_iscsi_localhost_test')
def test_many_luns_local() -> None:
    n_luns = 256
    back_size = '1M'
    t_iqn = 'iqn.1994-05.com.redhat:manylunstarget'
    i_iqn = 'iqn.1994-05.com.redhat:manylunsinitiator'

    assert lio.Iscsi(target_wwn=t_iqn).create_target().succeeded
    assert lio.ACL(target_wwn=t_iqn, initiator_wwn=i_iqn).create_acl().succeeded

    for n in range(n_luns):
        backstore = lio.BackstoreFileio(name=f'backstore{n}')
        assert backstore.create_backstore(size=back_size, file_or_dev=f'backstore_file{n}').succeeded
        assert lio.LUNs(target_wwn=t_iqn).create_lun(storage_object=backstore.path).succeeded

    iscsi.set_initiatorname(i_iqn)
    iscsi.discovery_st('127.0.0.1', disc_db=True, ifaces='default')
    iscsiadm = iscsi.IscsiAdm()
    for _ in range(3):
        assert iscsiadm.node_login()
        wait_udev(sleeptime=1)
        test_session = iscsi.get_session_by_target(target_wwn=t_iqn)
        disks = test_session.get_disks()
        expected_disks = 255 if package_info('targetcli').version < '2.1.54' else n_luns
        assert len(disks) == expected_disks
        for disk in disks:
            assert disk.is_running
        assert iscsiadm.node_logoutall()
    # Running clearconfig manually to avoid individually deleting backstores
    run('targetcli clearconfig confirm=true')
    run('rm -rf ./backstore_file*')
