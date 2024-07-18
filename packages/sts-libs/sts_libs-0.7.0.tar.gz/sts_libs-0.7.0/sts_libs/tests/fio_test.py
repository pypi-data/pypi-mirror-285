import pytest

from sts.fio import FIO


@pytest.fixture()
def fio_instance():
    return FIO('testfile')


def test_create_fio_command(fio_instance):
    parameters = {'runtime': '600', 'size': '20%'}
    options = ['readonly']
    options.sort()
    fio_instance.load_fs_params()
    fio_instance.update_parameters(parameters)
    fio_instance.update_options(options)
    command = fio_instance._create_fio_command()
    assert command == (
        'fio --filename "testfile" --name="sts fio filesystem" --ioengine="sync" --direct="1" '
        '--rw="write" --bs="1M" --numjobs="1" --iodepth="32" --runtime="600" --group_reporting="1" '
        '--do_verify="1" --verify_fatal="1" --verify="crc32" --verify_backlog="1024" --size="20%" '
        '--end_fsync="1" --readonly'
    )
