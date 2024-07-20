#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : redis
# @Time         : 2024/3/26 11:21
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
# from meutils.pipe import *

import os
from redis import Redis
from redis.asyncio import Redis as AsyncRedis

if REDIS_URL := os.getenv("REDIS_URL"):
    redis_client = Redis.from_url(REDIS_URL)
    redis_aclient = AsyncRedis.from_url(REDIS_URL)
else:
    redis_client = Redis()  # decode_responses=True
    redis_aclient = AsyncRedis()

if __name__ == '__main__':
    from meutils.pipe import *

    # print(arun(redis_aclient.get("")))
    # print(redis_client.lrange("https://api.moonshot.cn/v1",0, -1))

    # print(redis_client.lrange("https://api.deepseek.com/v1",0, -1))
    # print(redis_client.exists("https://api.deepseek.com/v1"))

    # print(type(redis_aclient.get("test")))

    # print(redis_client.delete("https://api.deepseek.com/v1"))

    _ = redis_client.get("https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=79272d")
    print(len(eval(_)))
