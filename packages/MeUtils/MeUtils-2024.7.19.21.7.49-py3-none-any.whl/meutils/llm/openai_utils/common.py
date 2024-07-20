#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : commom
# @Time         : 2024/5/30 11:20
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

import tiktoken

from contextlib import asynccontextmanager
from openai import AsyncOpenAI, OpenAI, AsyncStream

from meutils.pipe import *
from meutils.async_utils import achain, async_to_sync

from meutils.schemas.oneapi_types import MODEL_PRICE
from meutils.schemas.openai_types import ChatCompletionRequest, ImageRequest
from meutils.schemas.openai_types import ChatCompletion, ChatCompletionChunk, CompletionUsage
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, chat_completion_chunk_stop  # todo

token_encoder = tiktoken.get_encoding('cl100k_base')
token_encoder_with_cache = lru_cache(maxsize=1024)(token_encoder.encode)

CHAT_COMPLETION_PARAMS = get_function_params()
IMAGES_GENERATE_PARAMS = get_function_params(fn=OpenAI(api_key='').images.generate)


def to_openai_completion_params(
        request: Union[dict, ChatCompletionRequest],
        redirect_model: Optional[str] = None
) -> dict:
    data = copy.deepcopy(request)
    if isinstance(request, ChatCompletionRequest):
        data = request.model_dump()

    extra_body = {}
    for key in list(data):
        if key not in CHAT_COMPLETION_PARAMS:
            extra_body.setdefault(key, data.pop(key))

    data['extra_body'] = extra_body  # 拓展字段
    data['model'] = redirect_model or data['model']

    return data


def to_openai_images_params(
        request: Union[dict, ImageRequest],
        redirect_model: Optional[str] = None
) -> dict:
    data = copy.deepcopy(request)
    if isinstance(request, ImageRequest):
        data = request.model_dump()

    extra_body = {}
    for key in list(data):
        if key not in IMAGES_GENERATE_PARAMS:
            extra_body.setdefault(key, data.pop(key))

    data['extra_body'] = extra_body  # 拓展字段
    data['model'] = redirect_model or data['model']

    return data


def ppu(model='ppu', api_key: Optional[str] = None):
    client = OpenAI(api_key=api_key)
    return client.chat.completions.create(messages=[{'role': 'user', 'content': 'hi'}], model=model)


async def appu(model='ppu', api_key: Optional[str] = None, base_url: Optional[str] = None):
    client = AsyncOpenAI(api_key=api_key, base_url=base_url)
    return await client.chat.completions.create(messages=[{'role': 'user', 'content': 'hi'}], model=model)  # 支持ppu


@asynccontextmanager
async def ppu_flow(api_key: str, base_url: Optional[str] = None, post: str = "ppu-1", pre: str = "ppu-0001"):
    api_key and await appu(pre, api_key=api_key, base_url=base_url)
    logger.debug(f"PREPAY: {pre}")

    yield

    post = post if post in MODEL_PRICE else "ppu-1"
    api_key and await appu(post, api_key=api_key, base_url=base_url)
    logger.debug(f"POSTPAY: {post}")



def create_chat_completion(
        completion: Union[str, ChatCompletion],
        redirect_model: str = '',
        chat_id: Optional[str] = None
):
    if isinstance(completion, str):
        chat_completion.choices[0].message.content = completion

    chat_completion.id = chat_id or shortuuid.random()
    chat_completion_chunk.created = int(time.time())

    chat_completion.model = redirect_model or chat_completion.model
    return chat_completion


async def create_chat_completion_chunk(
        completion_chunks: Union[
            Coroutine,
            AsyncStream[ChatCompletionChunk],
            Iterator[Union[str, ChatCompletionChunk]],
            AsyncIterator[Union[str, ChatCompletionChunk]]
        ],
        redirect_model: str = ' ',
        chat_id: Optional[str] = None
):
    """
        async def main():
            data = {}
            _ = AsyncOpenAI().chat.completions.create(**data)
            async for i in create_chat_completion_chunk(_):
                print(i)
    """

    # logger.debug(type(completion_chunks))
    # logger.debug(isinstance(completion_chunks, Coroutine))

    if isinstance(completion_chunks, Coroutine):  # 咋处理
        completion_chunks = await completion_chunks
        # logger.debug(type(completion_chunks))

    async for completion_chunk in achain(completion_chunks):

        # logger.debug(completion_chunk)

        chat_completion_chunk.id = chat_id or shortuuid.random()
        chat_completion_chunk.created = int(time.time())
        if isinstance(completion_chunk, str):
            chat_completion_chunk.choices[0].delta.content = completion_chunk
            chat_completion_chunk.model = redirect_model or chat_completion_chunk.model
            yield chat_completion_chunk.model_dump_json()
        else:  # todo: AttributeError: 'tuple' object has no attribute 'model'
            try:
                completion_chunk.model = redirect_model or completion_chunk.model
                yield completion_chunk.model_dump_json()
            except Exception as e:
                from meutils.notice.feishu import send_message
                send_message(f"{type(completion_chunks)}\n\n{completion_chunks}\n\n{completion_chunk}", title=str(e))

    yield chat_completion_chunk_stop.model_dump_json()
    yield "[DONE]"  # 兼容标准格式


if __name__ == '__main__':
    # print(ppu())
    # print(appu())
    # print(arun(appu()))

    # print(create_chat_completion('hi'))
    # print(create_chat_completion('hi', redirect_model='@@'))
    #
    #
    # async def main():
    #     async for i in create_chat_completion_chunk(['hi', 'hi'], redirect_model='@@'):
    #         print(i)
    #
    #
    # arun(main())

    # encode = lru_cache()(token_encoder.encode)
    # # encode = token_encoder.encode
    #
    # with timer('xx'):
    #     encode("xxxxxxxxxxxxxxxxx" * 1000)
    #
    # with timer('xx'):
    #     encode("xxxxxxxxxxxxxxxxx" * 1000)
    #
    # with timer('xx'):
    #     encode("xxxxxxxxxxxxxxxxx" * 1000)

    # print(CHAT_COMPLETION_PARAMS)
    print(IMAGES_GENERATE_PARAMS)

    # async def main():
    #     async with ppu_flow('sk-h6A6esZh8jwjaM9W99Af7eB1733c4816936b1498FaF27c26'):
    #         await asyncio.sleep(20)
    #
    #
    # arun(main())
