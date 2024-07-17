#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : suno
# @Time         : 2024/3/27 20:37
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :


import jsonpath

from meutils.pipe import *
from meutils.schemas.task_types import Task
from meutils.schemas.suno_types import SunoAIRequest
from meutils.schemas.suno_types import MODELS, BASE_URL, CLIENT_BASE_URL, UPLOAD_BASE_UR
from meutils.schemas.suno_types import API_SESSION, API_FEED, API_BILLING_INFO, API_GENERATE_LYRICS, API_GENERATE_V2

from meutils.decorators.retry import retrying
from meutils.notice.feishu import send_message as _send_message
from meutils.config_utils.lark_utils import get_next_token_for_polling

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=Jxlglo"

send_message = partial(
    _send_message,
    title=__name__,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/dc1eda96-348e-4cb5-9c7c-2d87d584ca18"
)


@alru_cache(ttl=3600)
# @retrying(max_retries=5, predicate=lambda r: not r)
async def get_refresh_token(token: str):  # 定时更新一次就行
    headers = {
        "Cookie": f"__client={token}"
    }
    async with httpx.AsyncClient(base_url=CLIENT_BASE_URL, headers=headers, timeout=60) as client:
        response = await client.get('')

        # logger.debug(response.status_code)
        # logger.debug(response.text)

        if response.is_success:
            data = response.json()
            if ids := jsonpath.jsonpath(data, "$..last_active_session_id"):
                return token, ids[0]  # last_active_session_id

        send_message(f"未知错误：{response.text}")


@alru_cache(ttl=30 - 3)
async def get_access_token(token: str):
    token, last_active_session_id = await get_refresh_token(token)  # last_active_token 没啥用

    headers = {
        "Cookie": f"__client={token}"
    }
    async with httpx.AsyncClient(base_url=CLIENT_BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post(f"/sessions/{last_active_session_id}/tokens")
        if response.is_success:
            return response.json().get('jwt')


@retrying(max_retries=5, predicate=lambda r: not r)
async def create_task(request: SunoAIRequest, token: Optional[str] = None):
    token = token or await get_next_token_for_polling(FEISHU_URL)

    access_token = await get_access_token(token)

    headers = {
        "Authorization": f"Bearer {access_token}",
    }
    payload = request.model_dump()
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post(API_GENERATE_V2, json=payload)
        if response.is_success:
            data = response.json()
            task_id, *clip_ids = jsonpath.jsonpath(data, "$..id")
            task_id = f"suno-{','.join(clip_ids)}"  # 需要返回的任务id
            return Task(id=task_id, data=data, system_fingerprint=token)

        send_message(f"未知错误：{response.text}")


@retrying(predicate=lambda r: not r)  # 触发重试
async def get_task(task_id, token: str):  # task_id 实际是 clip_ids， 必须指定token获取任务
    task_id = task_id.split("suno-", 1)[-1]

    access_token = await get_access_token(token)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    params = {"ids": task_id}
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.get(API_FEED, params=params)
        if response.is_success:
            return response.json()


@alru_cache(ttl=15)
async def generate_lyrics(prompt: str = '', token: Optional[str] = None):
    token = token or await get_next_token_for_polling(FEISHU_URL)

    access_token = await get_access_token(token)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    payload = {"prompt": prompt}

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=60) as client:
        response = await client.post(API_GENERATE_LYRICS, json=payload)
        if response.is_success:
            task_id = response.json().get("id")

            for i in range(100):
                await asyncio.sleep(1)
                response = await client.get(API_GENERATE_LYRICS + task_id)

                logger.debug(response.text)

                if response.is_success and response.json().get("text"):
                    return response.json()
                    # break


async def upload(file: bytes, title: str = '文件名', token: Optional[str] = None):  # 必须指定token获取任务
    token = token or await get_next_token_for_polling(FEISHU_URL)

    access_token = await get_access_token(token)
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    async with httpx.AsyncClient(timeout=100) as client:
        # payload = {"extension": "wav"} # "{\"extension\":\"wav\"}"
        payload = "{\"extension\":\"mp3\"}"
        response = await client.post(f"{BASE_URL}/api/uploads/audio/", content=payload, headers=headers)

        # logger.debug(response.text)

        if response.is_success:
            data = response.json()
            logger.debug(data)

            file_id = Path(data.get("fields").get('key')).stem

            payload = data.get("fields")
            files = {
                'file': file
                # 'file': ("xx", file, 'audio/mpeg')

            }

            response = await client.post(url=UPLOAD_BASE_UR, data=payload, files=files)
            if response.is_success:
                payload = {"upload_type": "file_upload", "upload_filename": "audio.wav"}
                response = await client.post(f"{BASE_URL}/api/uploads/audio/{file_id}/upload-finish/", headers=headers,
                                             json=payload)

                for i in range(30):
                    response = await client.get(f"{BASE_URL}/api/uploads/audio/{file_id}/", headers=headers)
                    if response.is_success and response.json().get("s3_id"):
                        logger.debug(response.json())

                        # {
                        #     "id": "557f349e-2ce5-45f0-806c-efba18286599",
                        #     "status": "complete",
                        #     "error_message": null,
                        #     "s3_id": "m_476a2e21-a0aa-4e33-92ff-2b5ddd587661",
                        #     "title": "audio",
                        #     "image_url": "https://cdn1.suno.ai/image_476a2e21-a0aa-4e33-92ff-2b5ddd587661.png"
                        # }
                        break
                    await asyncio.sleep(0.5 if i > 0 else 3)

                response = await client.post(
                    f"{BASE_URL}/api/uploads/audio/{file_id}/initialize-clip/",
                    headers=headers
                )
                clip_id = response.json().get("clip_id")  # m_{clip_id} image_{clip_id}.png

                payload = {"id": clip_id, "title": title}  # 好像不要也行，前端展示  title 传入文件名
                resp = await client.post(f"{BASE_URL}/api/gen/{clip_id}/set_metadata/", json=payload, headers=headers)

                data = await get_task(task_id=clip_id, token=token)  # 绑定token才能获取
                return data, token  # clip_id: token 存一下


if __name__ == '__main__':
    pass
    token = os.getenv("SUNO_API_KEY")
    # token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6ImNsaWVudF8yaGlHSTlCZFVwOUdZcUlGM3ZmTU1IT25SNFAiLCJyb3RhdGluZ190b2tlbiI6ImltOWMzOGJ4bnV2OThiZXplMW8yOG1zd2Y2c3lrdzd6YnM2ejJubHkifQ.SnC8-G2LVQztTiA2davFS413mQIaBmRFDzIw1JmvHg4UOMXq95z0CgbfK8Gx8Zv-FXdpKVqkamiNTzZP9qsLOSgREqCSSq5bmA6SPIWx-R6dj1PMDFRX-qv5qGyyPe4sadF6wnr45MS9859148gRmr_Go8rAT_7Hu0DKySextl-Xbs6ClDaYYUyyV3HudWQh4F8jwvxkyer05AgN6smQH5eZI-NRKVgZn_i6Mtl8IJz8R1fzD2YNIcvH4QC4qGhrg9n74ljIeORCMsoJzW2SBZa4QWWDx_0VYs-tA_Z43bqwN_2ojMGM63fm2hLOZmwf6S1LQy9_O6UdcUQiEs__OA"

    # print(arun(get_refresh_token(token)))
    # print(arun(get_access_token(token)))

    # arun(generate_lyrics(prompt=''))

    # ids = "ee6d4369-3c75-4526-b6f1-b5f2f271cf30"
    # print(api_feed(api_key, ids))

    # for i in range(100):  # 测试过期时间
    #     print(api_billing_info(api_key))
    #     time.sleep(60)

    # print(arun(get_api_key()))
    # task_id = music_ids = 1
    # send_message(f"""
    #     https://api.chatfire.cn/task/suno/v1/tasks/{task_id}
    #     https://api.chatfire.cn/task/suno/v1/music/{music_ids}
    #     """)
    # file = open("/Users/betterme/PycharmProjects/AI/test.mp3", 'rb').read()
    # arun(upload(file=file))

    arun(generate_lyrics())
