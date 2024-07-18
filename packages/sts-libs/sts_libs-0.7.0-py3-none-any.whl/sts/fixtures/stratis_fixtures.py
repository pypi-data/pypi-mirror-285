from collections.abc import Generator
from os import getenv
from pathlib import Path

import pytest

from sts import stratis


@pytest.fixture()
def setup_stratis_key() -> Generator:
    stratis_key = stratis.Key()
    keydesc = getenv('STRATIS_KEY_DESC', 'stratis-test-key')
    keypath = getenv('STRATIS_KEY_PATH', '/tmp/stratis_key_file')
    key = getenv('STRATIS_KEY', 'Stra123tisKey45')
    keyp = Path(keypath)
    keyp.write_text(key, encoding='utf-8')
    assert keyp.is_file()
    assert stratis_key.set(keydesc=keydesc, keyfile_path=keypath).succeeded
    yield keydesc
    assert stratis_key.unset(keydesc).succeeded
    keyp.unlink()
    assert not keyp.is_file()
