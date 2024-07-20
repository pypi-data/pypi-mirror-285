#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : textin
# @Time         : 2024/6/26 08:22
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *


@alru_cache(ttl=3600 * 24)
async def textin_fileparser(data: bytes, page_count: int = 1000, service: str = "pdf_to_markdown"):
    # params = {
    #     "service": service,
    #     "page_count": page_count,
    #     # "get_image": "objects"
    # }

    base_url = f"https://api.textin.com/home/user_trial_ocr?service={service}&page_count={page_count}"
    async with httpx.AsyncClient(base_url=base_url, timeout=120) as client:
        response = await client.post('/', content=data)

        if response.is_success:
            return response.json()
        return response.text


if __name__ == '__main__':
    data = open("/Users/betterme/PycharmProjects/AI/11.jpg", 'rb').read()
    # data = open("/Users/betterme/PycharmProjects/AI/蚂蚁集团招股书.pdf", 'rb').read()

    with timer("解析"):
        # arun(textin_fileparser(data))
        print(arun(textin_fileparser(data)))

    # response = requests.request("POST", url, data=data)
