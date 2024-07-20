#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : text_to_image
# @Time         : 2024/7/8 12:19
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : https://docs.siliconflow.cn/reference/stabilityaistable-diffusion-3-medium_text-to-image

from meutils.pipe import *
from meutils.pipe import storage_to_cookie
from meutils.config_utils.lark_utils import get_spreadsheet_values, get_next_token_for_polling
from meutils.schemas.openai_types import ImageRequest

BASE_URL = "https://cloud.siliconflow.cn"


async def create_image(request: ImageRequest):
    cookie = await get_next_token_for_polling(
        feishu_url="https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=xlvlrH")

    cookie = storage_to_cookie(cookie)

    params = {
        "modelName": request.model,  # stabilityai/stable-diffusion-3-medium
        "modelSubType": "text-to-image"
    }

    data = f'{{"image_size":"{request.size}","batch_size":{request.n},' \
           f'"num_inference_steps":{request.num_inference_steps},"guidance_scale":{request.guidance_scale},'

    if request.negative_prompt:
        data += f'"negative_prompt":"{request.negative_prompt}",'

    if request.seed:
        data += f'"seed":{request.seed},'

    data += f'"prompt":"{request.prompt}"}}'

    headers = {
        'Cookie': cookie,
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=100, follow_redirects=True) as client:
        response = await client.post("/api/model/text2img", params=params, content=data)
        return response.is_success and response.json()


if __name__ == '__main__':
    # cookie = await get_next_token_for_polling(feishu_url="https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=xlvlrH")
    # api_key = storage_to_cookie(cookie)

    storage_state = \
        get_spreadsheet_values(feishu_url="https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=xlvlrH",
                               to_dataframe=True)[0]

    cookie = storage_to_cookie(storage_state[0])

    request = ImageRequest(
        model="stabilityai/stable-diffusion-3-medium",
        prompt="Man snowboarding on the mars, ultra high resolution 8k"
    )
    print(arun(create_image(request)))
