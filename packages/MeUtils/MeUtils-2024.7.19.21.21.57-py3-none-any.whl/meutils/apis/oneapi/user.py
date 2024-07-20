#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : user
# @Time         : 2024/7/19 14:58
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import json

from meutils.pipe import *
from meutils.schemas.oneapi_types import BASE_URL

# https://api.chatfire.cn/api/user/814

token = os.environ.get("CHATFIRE_ONEAPI_TOKEN")

headers = {
    "Authorization": f"Bearer {token}",
}


# https://api.chatfire.cn/api/user/token 刷新token
# https://api.chatfire.cn/api/user/1
# async def get_user(user_id):
#     async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
#         response = await client.get(f"/api/user/{user_id}")
#         logger.debug(response.text)
#
#         if response.is_success:
#             data = response.json()
#             return data

async def get_one_log(api_key: str):
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        response = await client.get("/api/user", params={"key": api_key})

        if response.is_success:
            data = response.json()['data']
            return data


async def get_user(user_id):
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        response = await client.get(f"/api/user/{user_id}")
        logger.debug(response.text)

        if response.is_success:
            data = response.json()
            return data


async def put_user(payload, add_money: float = 0):
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        payload['quota'] = max(payload['quota'] + add_money * 500000, 0)  # 1块钱对应50万

        response = await client.put("/api/user/", json=payload)
        # logger.debug(response.text)
        # logger.debug(response.status_code)

        return response.json()


if __name__ == '__main__':
    # api-key => get_one_log => get_user => put_user
    # arun(get_user(814))
    payload = arun(get_user(814))['data']
    print(payload)
    arun(put_user(payload, -1))
