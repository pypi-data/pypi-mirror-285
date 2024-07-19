import pytest

from beni.bfunc import deobfuscate, obfuscate, shuffleSequence


@pytest.mark.asyncio
async def test_obfuscate():
    data = '(故意地)混淆，使困惑，使模糊不清to make sth less clear and more difficult to understand, usually deliberately'.encode()
    magicContent = obfuscate(data)
    assert deobfuscate(magicContent) == data


@pytest.mark.asyncio
async def test_shuffleSequence():
    msg = 'asdlfjkasjlasdf..xxaa@#$@#aasdfasdczvzcxva'
    value = shuffleSequence(msg)
    assert msg != value
    value = shuffleSequence(value)
    assert msg == value
