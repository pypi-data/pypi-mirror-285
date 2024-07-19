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
from meutils.schemas.translator_types import DeeplxRequest


@alru_cache(ttl=3600)
async def translate(
        request: DeeplxRequest,
        api_key: Optional[str] = None,
):
    """
    https://fakeopen.org/DeepLX/#%E6%8E%A5%E5%8F%A3%E5%9C%B0%E5%9D%80
    https://linux.do/t/topic/111737
    """
    api_key = api_key or "2UvLe4qjo_bGi7BCHltMyRR29ce-rwAJQ4fwUBqLyGI"  # todo

    url = f"https://api.deeplx.org/{api_key}/translate"

    payload = request.model_dump()
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, json=payload)
        if response.is_success:
            return response.json()

        response.raise_for_status()


if __name__ == '__main__':
    request = DeeplxRequest(text='火哥AI是最棒的', source_lang='ZH', target_lang='EN')
    with timer():
        arun(translate(request))
