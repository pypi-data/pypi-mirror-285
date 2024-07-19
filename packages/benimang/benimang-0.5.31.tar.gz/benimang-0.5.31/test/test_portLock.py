import asyncio

import pytest

from beni.block import portLock


@pytest.mark.asyncio
async def test():
    port = 60000
    await asyncio.gather(funcA(port), funcB(port))


async def funcA(port: int):
    with portLock(port):
        await asyncio.sleep(0.2)


async def funcB(port: int):
    await asyncio.sleep(0.1)
    try:
        with portLock(port):
            pass
    except Exception as e:
        assert str(e) == '程序禁止多开'
        return
    assert False, '未被阻止多开'
