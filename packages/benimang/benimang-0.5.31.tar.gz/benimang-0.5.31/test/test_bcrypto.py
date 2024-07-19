import pytest

from beni import bcrypto

_PASSWORD = 'test_password'
_DATA = '(故意地)混淆，使困惑，使模糊不清to make sth less clear and more difficult to understand, usually deliberately'.encode()


@pytest.mark.asyncio
async def test_encrypt():
    data = bcrypto.encrypt(_DATA, _PASSWORD)
    assert bcrypto.decrypt(data, _PASSWORD) == _DATA


@pytest.mark.asyncio
async def test_encryptText():
    text = _DATA.decode()
    data = bcrypto.encryptText(text, _PASSWORD)
    assert bcrypto.decryptText(data, _PASSWORD) == text


@pytest.mark.asyncio
async def test_encryptJson():
    data = {'key': _DATA.decode()}
    text = bcrypto.encryptJson(data, _PASSWORD)
    assert bcrypto.decryptJson(text, _PASSWORD) == data
