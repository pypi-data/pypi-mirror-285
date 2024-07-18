#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : __init__.py
# @Time         : 2024/7/5 12:05
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.schemas.openai_types import TTSRequest

from openai.types.file_object import FileObject
from fastapi import UploadFile

BASE_URL = "https://api.fish.audio"

url = "https://api.fish.audio/model"


async def get_model_list(token, **kwargs):
    params = {
        'self': True,
        'title': None,

        'page_size': 10,
        'page_number': 1,
        **kwargs
    }
    headers = {
        "authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        response = await client.get("/model", params=params)
        return response.is_success and response.json()


async def create_tts_model(token, file, **kwargs):
    """
    {'_id': '9d10cdbea3954aa9b8fd992fd24b92a7',
     'author': {'_id': 'd71d7c63c52e4d70be72e3afdb7952ab',
                'avatar': '',
                'nickname': '313303303'},
     'cover_image': 'coverimage/9d10cdbea3954aa9b8fd992fd24b92a7',
     'created_at': '2024-07-05T05:30:32.020433Z',
     'description': '',
     'languages': ['zh'],
     'like_count': 0,
     'liked': False,
     'mark_count': 0,
     'marked': False,
     'samples_text': [],
     'shared_count': 0,
     'state': 'trained',
     'tags': [],
     'task_count': 0,
     'title': 'chatfire',
     'train_mode': 'fast',
     'type': 'tts',
     'updated_at': '2024-07-05T05:30:32.020407Z',
     'visibility': 'public'}
    """
    payload = {
        **kwargs
    }

    logger.debug(file)

    files = {
        'title': (None, 'chatfire-tts'),
        'description': (None, ''),
        'type': (None, 'tts'),
        'train_mode': (None, 'fast'),
        'visibility': (None, 'public'),  # private

        'voices': file,  # ('audio_name.mp3', file)
        'cover_image': open(get_resolve_path('cowboy-hat-face.webp', __file__), 'rb')

    }

    headers = {
        "authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=100) as client:
        response = await client.post("/model", json=payload, files=files)
        # logger.debug(response.text)
        if response.is_success:
            _ = response.json()
            _['model_id'] = _['_id']
            return _
        else:
            return response.text


async def create_tts_task(token, model_id, text, return_task_info: bool = True):
    model_id = model_id.split('-', maxsplit=1)[-1]  # 去掉任务前缀

    payload = {
        "type": "tts",
        "channel": "free",
        "stream": True,  # 区别？
        "model": model_id,
        "parameters": {
            "text": text
        }
    }
    headers = {
        "authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=100) as client:
        response = await client.post("/task", json=payload)

        if response.is_success:
            if return_task_info:
                task_id = response.headers.get("task-id")
                task_response = await client.get(f"/task/{task_id}")
                _ = task_response.json()
                _['file_view'] = url2view(_['result'])
                return _

            return response.text
        else:
            return response.text


async def get_tts_task(token, task_id):
    headers = {
        "authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers, timeout=100) as client:
        response = await client.get(f"/task/{task_id}")

        if response.is_success:

            _ = response.json()
            _['file_view'] = url2view(_['result'])
            return _
        else:
            return response.json()


async def create_file_for_openai(file: UploadFile, purpose="tts"):  # todo: 存储 redis
    feishu_url = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=ysSMA2"
    token = await get_next_token_for_polling(feishu_url=feishu_url)

    filename = file.filename or file.file.name
    model_info = await create_tts_model(token, file=(filename, file.file))

    if isinstance(model_info, dict):
        model_id = model_info.get("_id")
        file_id = f"{purpose}-{model_id}"
        status = "processed"
    else:
        file_id = shortuuid.random()
        status = "error"

    file_object = FileObject.construct(

        filename=filename,  # result.get("file_name")
        bytes=file.size,

        id=file_id,
        created_at=int(time.time()),
        object='file',

        purpose=purpose,
        status=status,
        status_details=model_info
    )
    return file_object


async def create_speech_for_openai(request: TTSRequest):  # todo: 存储 redis
    feishu_url = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=ysSMA2"
    token = await get_next_token_for_polling(feishu_url=feishu_url)

    model_id = request.model

    stream = await create_tts_task(token, model_id, request.input, False)
    return stream


if __name__ == '__main__':
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiZDcxZDdjNjNjNTJlNGQ3MGJlNzJlM2FmZGI3OTUyYWIifQ.ZTuBX-l3HdxULqg7CvlYOSnMRvT8CCFKJBjmU4s_Q-s"
    # print(bjson(arun(get_model_list(token))))
    file = open('/Users/betterme/Downloads/whisper-1719913495729-54f08dde5.wav.mp3.mp3', 'rb')

    # pprint(arun(get_model_list(token)))
    # file = UploadFile(file)
    # pprint(arun(create_tts_model(token, file=(file.file.name, file.file))))
    model = "9d10cdbea3954aa9b8fd992fd24b92a7"
    # task_id = "f5a94a3fb78646b8ab1c3606413ca9e0"
    with timer():
        text = "文本转语音\n文本转语音\n文本转语音\n文本转语音\n"
        _ = arun(create_tts_task(token, model, text, return_task_info=False))
        pprint(_)

    # pprint(arun(get_tts_task(token, task_id)))

    #
    # file = open('/Users/betterme/Downloads/whisper-1719913495729-54f08dde5.wav.mp3.mp3', 'rb')
    #
    # file = UploadFile(file)
    #
    # print(arun(upload_audio_for_tts_model(file=file)))
