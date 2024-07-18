#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : oneapi
# @Time         : 2024/6/28 09:23
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://github.com/Thekers/Get_OpenaiKey/blob/9d174669d7778ea32d1132bedd5167597912dcfb/Add_01AI_Token.py
import os

from meutils.pipe import *
from meutils.schemas.oneapi_types import REDIRECT_MODEL
from meutils.schemas.oneapi_types import MODEL_PRICE, MODEL_RATIO, COMPLETION_RATIO, GROUP_RATIO

import requests
import json


def option():
    url = "https://api.chatfire.cn/api/option/"
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
        headers = {
            'priority': 'u=1, i',
            'Cookie': os.getenv("CHATFIRE_ONEAPI_COOKIE"),
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'content-type': 'application/json'
        }
        response = requests.request("PUT", url, headers=headers, json=payload)
        logger.debug(response.json())


def add_channel(base_url, api_keys: list, models: list, cookie: Optional[str] = None,
                url: Optional[str] = None,
                api_key: Optional[str] = None,
                ):
    url = url or "https://api.chatfire.cn/api/channel"
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
    headers = {
        'priority': 'u=1, i',
        'Cookie': cookie or os.getenv("CHATFIRE_ONEAPI_COOKIE"),
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'content-type': 'application/json',
        "Authorization": f"Bearer {api_key}",

    }

    response = requests.request("POST", url, headers=headers, json=payload)
    logger.debug(response.text)

    return response.json()


if __name__ == '__main__':
    option()
    # print(json.dumps(MODEL_RATIO, indent='\n'))
