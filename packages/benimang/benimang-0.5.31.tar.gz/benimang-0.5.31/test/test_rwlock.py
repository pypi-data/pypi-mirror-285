import asyncio

import pytest

from beni.block import RWLock

_result = ''
_lock = RWLock()


@pytest.mark.asyncio
async def test():
    await asyncio.gather(_read(), _read(), _write())
    assert _result == 'rrw'


async def _read():
    async with _lock.useRead():
        await asyncio.sleep(0.2)
        global _result
        _result += 'r'


async def _write():
    async with _lock.useWrite():
        global _result
        _result += 'w'
