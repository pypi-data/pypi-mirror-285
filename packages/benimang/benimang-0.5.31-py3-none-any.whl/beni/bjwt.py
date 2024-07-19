# 即将丢弃

import uuid
from typing import Any

import jwt

from beni import bfile
from beni.bfunc import shuffleSequence
from beni.btype import XPath

_KEY_SALT = '_salt_@#%@#xafDGAz.nq'
_KEY_TEXT = '_text_A!@$,FJ@#adsfkl'


def encodeJson(data: dict[str, Any], secret: str, tips: str = '') -> str:
    tips = tips.strip()
    data[_KEY_SALT] = uuid.uuid4().hex
    result = jwt.encode(data, secret, algorithm='HS256')
    result = shuffleSequence(result)
    if tips:
        result = f'{tips} {result}'
    return result


def encodeText(text: str, secret: str, tips: str = '') -> str:
    tips = tips.strip()
    data = {
        _KEY_TEXT: text,
    }
    return encodeJson(data, secret, tips)


async def encodeFile(file: XPath, secret: str, tips: str = '') -> None:
    content = await bfile.readText(file)
    result = encodeText(content, secret, tips)
    await bfile.writeText(file, result)


def decodeJson(content: str, secret: str) -> dict[str, Any]:
    content = content.split(' ')[-1]
    content = shuffleSequence(content)
    data = jwt.decode(content, secret, algorithms=['HS256'])
    if _KEY_SALT in data:
        del data[_KEY_SALT]
    return data


def decodeText(content: str, secret: str) -> str:
    data = decodeJson(content, secret)
    return data[_KEY_TEXT]


async def decodeFile(file: XPath, secret: str) -> None:
    content = await bfile.readText(file)
    result = decodeText(content, secret)
    await bfile.writeText(file, result)
