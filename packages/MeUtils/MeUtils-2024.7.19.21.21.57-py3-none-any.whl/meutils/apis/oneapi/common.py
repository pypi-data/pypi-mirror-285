#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : oneapi
# @Time         : 2024/6/28 09:23
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://github.com/Thekers/Get_OpenaiKey/blob/9d174669d7778ea32d1132bedd5167597912dcfb/Add_01AI_Token.py
import jsonpath
from meutils.pipe import *
from meutils.schemas.oneapi_types import REDIRECT_MODEL
from meutils.schemas.oneapi_types import MODEL_PRICE, MODEL_RATIO, COMPLETION_RATIO, GROUP_RATIO

import requests
import json


# 500000对应1块
def option(token: Optional[str] = None):
    token = token or os.environ.get("CHATFIRE_ONEAPI_TOKEN")

    url = "https://api.chatfire.cn/api/option/"
    headers = {
        "Authorization": f"Bearer {token}",
    }

    payloads = [
        {
            "key": "ModelPrice",
            "value": json.dumps(MODEL_PRICE)
        },
        {
            "key": "ModelRatio",
            "value": json.dumps(MODEL_RATIO)
        },
        {
            "key": "CompletionRatio",
            "value": json.dumps(COMPLETION_RATIO)
        },
        {
            "key": "GroupRatio",
            "value": json.dumps(GROUP_RATIO)
        },

    ]
    for payload in payloads:
        response = requests.request("PUT", url, headers=headers, json=payload)
        logger.debug(response.json())


def add_channel(
        base_url,
        api_keys: list,
        models: list,
        url: Optional[str] = None,
        token: Optional[str] = None,
):
    token = token or os.environ.get("CHATFIRE_ONEAPI_TOKEN")

    url = url or "https://api.chatfire.cn/api/channel"
    headers = {
        "Authorization": f"Bearer {token}",
    }
    payload = {

        "name": base_url,  # 渠道名

        "type": 1,
        "base_url": base_url,
        "key": '\n'.join(api_keys),
        "models": ','.join(models),

        "openai_organization": "",
        "max_input_tokens": 0,
        "other": "",
        "model_mapping": "",
        "status_code_mapping": "",
        "auto_ban": 1,
        "test_model": "",
        "groups": [
            "default"
        ],
        "group": "default"
    }
    response = requests.request("POST", url, headers=headers, json=payload)
    logger.debug(response.text)

    return response.json()


# todo: 同一个任务补偿一次【加个缓存】，再想想【redis加个标识，判断吧】
# def compensate_user_money(callback_fn):
#     if set(jsonpath.jsonpath(data, "$.status")) == {"error"}:  # 触发补偿，如何去重【剔除id？】
#         pass

# https://api.chatfire.cn/api/log/token?key=sk-
if __name__ == '__main__':
    # option()
    # print(json.dumps(MODEL_RATIO, indent='\n'))
    print(add_channel(
        base_url="xx",
        api_keys=['xx'],
        models=['xx'],
        token=""
    ))
