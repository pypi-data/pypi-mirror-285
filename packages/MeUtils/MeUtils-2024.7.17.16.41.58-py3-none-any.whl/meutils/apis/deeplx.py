#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : deeplx
# @Time         : 2024/3/1 16:54
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from meutils.async_utils import arequest
from meutils.decorators.retry import retrying

username = password = 'chatfire'


@retrying
@lru_cache
def translate(text: str = "Hello, world!", source_lang: str = "auto", target_lang: str = "ZH"):
    """https://fakeopen.org/DeepLX/#%E6%8E%A5%E5%8F%A3%E5%9C%B0%E5%9D%80"""
    url = "https://api.deeplx.org/translate"
    url = f"https://{username}:{password}@deeplx.chatfire.cn/translate"
    payload = {
        "text": text,
        "source_lang": source_lang,
        "target_lang": target_lang
    }
    # arequest(url, payload=payload, method='post')

    response = httpx.post(url, json=payload, timeout=30)
    return response.json()


if __name__ == '__main__':
    print(translate('火哥AI是最棒的', target_lang='EN'))
