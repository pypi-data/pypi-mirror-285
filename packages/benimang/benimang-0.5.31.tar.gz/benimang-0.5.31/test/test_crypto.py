import pytest
from beni import bcrypto


@pytest.mark.asyncio
async def testCrypto():
    password = 'ceshimima'
    content = '这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密这是一个秘密'
    secret = bcrypto.encryptText(content, password)
    secretContent = bcrypto.decryptText(secret, password)
    assert content == secretContent