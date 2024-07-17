#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : klingai
# @Time         : 2024/7/9 13:23
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import jsonpath

from meutils.pipe import *
from meutils.decorators.retry import retrying
from meutils.schemas.kuaishou_types import BASE_URL, UPLOAD_BASE_URL, KlingaiImageRequest
from meutils.notice.feishu import send_message as _send_message
from meutils.config_utils.lark_utils import get_next_token_for_polling

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=v8vcZY"

send_message = partial(
    _send_message,
    title=__name__,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/dc1eda96-348e-4cb5-9c7c-2d87d584ca18"
)


@retrying(predicate=lambda r: not isinstance(r, str))  # 触发重试
async def upload(file: bytes, filename: Optional[str] = None, cookie: Optional[str] = None):  # 应该不绑定cookie
    cookie = cookie or await get_next_token_for_polling(FEISHU_URL)

    filename = filename or f"{shortuuid.random()}.png"

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json;charset=UTF-8'
    }

    async with httpx.AsyncClient(base_url=UPLOAD_BASE_URL, headers=headers, timeout=100) as client:
        # 文件名生成token
        response = await client.get(f"{BASE_URL}/api/upload/issue/token", params={"filename": filename})
        # logger.debug(response.json())

        token = jsonpath.jsonpath(response.json(), "$.data.token")[0]

        # 判断是否存在
        response = await client.get("/api/upload/resume", params={"upload_token": token})
        # {"result":1,"existed":true,"fragment_index":-1,"fragment_list":[],"endpoint":[{"protocol":"KTP","host":"103.107.217.16","port":6666},{"protocol":"KTP","host":"103.102.202.156","port":6666},{"protocol":"TCP","host":"103.107.217.16","port":6666}],"fragment_index_bytes":0,"token_id":"d36ce45c09ce9b84","prefer_http":false}
        # logger.debug(response.json())

        # 上传
        response = await client.post(
            "/api/upload/fragment",
            params={"fragment_id": 0, "upload_token": token},
            content=file
        )
        # logger.debug(response.json())

        # 校验
        response = await client.post(
            "api/upload/complete",
            params={"fragment_count": 1, "upload_token": token},
        )
        # logger.debug(response.json())

        # 最终
        response = await client.get(f"{BASE_URL}/api/upload/verify/token", params={"token": token})
        if response.is_success:
            data = response.json()
            send_message(data)

            try:
                urls = jsonpath.jsonpath(response.json(), "$.data.url")  # False
                if urls:
                    return urls[0] or data

            except Exception as e:  # 429
                logger.error(e)

            else:
                return data


@retrying(max_retries=5, predicate=lambda r: not r)
async def create_task(request: KlingaiImageRequest, cookie: str):
    cookie = cookie or await get_next_token_for_polling(FEISHU_URL)

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json;charset=UTF-8'
    }

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post("/api/task/submit", json=request.payload)
        if response.is_success:
            data = response.json()
            send_message(bjson(data))

            if '请求超限' in str(data): return  # 429 重试
            try:
                task_ids = jsonpath.jsonpath(data, "$..task.id")  # $..task..[id,arguments]
                if task_ids:
                    return task_ids[0]

            except Exception as e:
                logger.error(e)

            else:
                return data


@retrying(max_retries=16, exp_base=1.1, predicate=lambda r: r == "RETRYING")  # 触发重试
async def get_task(task_id, cookie: str):
    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json;charset=UTF-8'
    }

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.get("/api/task/status", params={"taskId": task_id, "withWatermark": False})
        if response.is_success:
            data = response.json()

            logger.debug(data)

            if not task_id or "failed," in str(data): return "TASK_FAILED"  # 跳出条件

            urls = jsonpath.jsonpath(data, '$..resource.resource')
            if urls and all(urls):
                images = [{"url": url} for url in urls]
                return images
            else:
                return "RETRYING"  # 重试


@retrying(max_retries=3, predicate=lambda r: r == "TASK_FAILED")
async def create_image(request: KlingaiImageRequest):
    cookie = await get_next_token_for_polling(FEISHU_URL)

    task_id = await create_task(request, cookie)
    if isinstance(task_id, dict):
        return task_id

    data = await get_task(task_id, cookie)

    return data


if __name__ == '__main__':
    # https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=v8vcZY
    rquest = KlingaiImageRequest(prompt="一条狗", imageCount=1)  # 27638649

    cookie = "weblogger_did=web_47164250171DB527; did=web_e022fde52721456f43cb66d90a7d6f14e462; userId=742626779; kuaishou.ai.portal_st=ChVrdWFpc2hvdS5haS5wb3J0YWwuc3QSoAGAEPOivL4BJ2Y8y48CvR-t25o44Sj_5G9LnZI8BJbV_Inkqd4qxPMJy4OqZCf0VHZnr8EcgMHOzuj_fw5-x0OF3UtrXrU2ZBe6G_bnD1umPIAL6DVtv6ERJ9uLpa7asCBgIUvMXk6K345vc5okzhoTPw69b1GsXY777qwuOwGoUrP9eyJc6Z4TeQPYDEW2wdazss7Dn2osIhObsW9izb1yGhJaTSf_z6v_i70Q1ZuLG30vAZsiIGMXZhr3i8pOgOICzAXA0T6fJZZk3hFRsxn3MDQzIeiKKAUwAQ; kuaishou.ai.portal_ph=fe74c1e2fb91142f838c4b3d435d6153ccf3"
    #
    # pprint(arun(create_task(rquest, cookie)))
    # # pprint(arun(get_task(None, cookie)))
    #
    # pprint(arun(create_image(rquest)))

    file = open("/Users/betterme/PycharmProjects/AI/x.jpg", "rb").read()

    pprint(arun(upload(file, cookie)))
