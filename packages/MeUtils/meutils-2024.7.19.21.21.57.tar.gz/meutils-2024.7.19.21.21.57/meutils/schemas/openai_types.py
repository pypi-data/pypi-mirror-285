#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_types
# @Time         : 2024/6/7 17:30
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

from openai.types.chat import ChatCompletion as _ChatCompletion, ChatCompletionChunk as _ChatCompletionChunk
from openai.types.chat.chat_completion import Choice as _Choice, ChatCompletionMessage as _ChatCompletionMessage, \
    CompletionUsage as _CompletionUsage
from openai.types.chat.chat_completion_chunk import Choice as _ChunkChoice, ChoiceDelta
from openai._types import FileTypes

from fastapi import UploadFile


class CompletionUsage(_CompletionUsage):
    prompt_tokens: int = 1
    completion_tokens: int = 1
    total_tokens: int = 1


class ChatCompletionMessage(_ChatCompletionMessage):
    role: Literal["assistant"] = "assistant"
    """The role of the author of this message."""


class Choice(_Choice):
    index: int = 0
    finish_reason: Literal["stop", "length", "tool_calls", "content_filter", "function_call"] = None


class ChatCompletion(_ChatCompletion):
    id: str = Field(default_factory=shortuuid.random)
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = ""
    object: str = "chat.completion"
    usage: CompletionUsage = CompletionUsage()


class ChunkChoice(_ChunkChoice):
    index: int = 0


class ChatCompletionChunk(_ChatCompletionChunk):
    id: str = Field(default_factory=shortuuid.random)
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = ""
    object: str = "chat.completion.chunk"


chat_completion = ChatCompletion(
    choices=[Choice(message=ChatCompletionMessage(content=""))]
)
chat_completion_chunk = ChatCompletionChunk(
    choices=[ChunkChoice(delta=ChoiceDelta(content=""))]
)
chat_completion_chunk_stop = ChatCompletionChunk(
    choices=[ChunkChoice(delta=ChoiceDelta(content=""), finish_reason="stop")]
)


# chat_completion.choices[0].message.content = "*"
# chat_completion_chunk.choices[0].delta.content = "*"


class ChatCompletionRequest(BaseModel):
    """
    prompt_filter_result.content_filter_results
    choice.content_filter_results

    todo: ['messages', 'model', 'frequency_penalty', 'function_call', 'functions', 'logit_bias', 'logprobs', 'max_tokens', 'n', 'presence_penalty', 'response_format', 'seed', 'stop', 'stream', 'temperature', 'tool_choice', 'tools', 'top_logprobs', 'top_p', 'user']
    """
    model: str = ''  # "gpt-3.5-turbo-file-id"

    # [{'role': 'user', 'content': 'hi'}]
    # [{'role': 'user', 'content':  [{"type": "text", "text": ""}]]
    # [{'role': 'user', 'content':  [{"type": "image_url", "image_url": {"url": ""}}]] # 也兼容文件
    # [{'role': 'user', 'content':  [{"type": "file", "file_url": ""}]]
    messages: List[Dict[str, Any]] = [{'role': 'user', 'content': 'hi'}]

    top_p: Optional[float] = 0.7
    temperature: Optional[float] = 0.7

    n: Optional[int] = 1
    max_tokens: Optional[int] = None
    stop: Optional[Union[str, List[str]]] = None
    stream: Optional[bool] = False
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    user: Optional[str] = None

    # 1106
    response_format: Optional[Any] = None
    function_call: Optional[Any] = None

    # 拓展字段
    last_content: Optional[Any] = None

    payload: Optional[Dict[str, Any]] = Field(default_factory=dict)  # 任意接口转chat api
    return_raw_response: Optional[bool] = None

    additional_kwargs: Optional[Dict[str, Any]] = Field(default_factory=dict)

    refs: List[str] = []
    file_ids: List[str] = []

    search: Optional[bool] = None
    use_search: Optional[bool] = None  # 自动推断联网

    # glm
    assistant_id: str = ""
    conversation_id: str = ""  # kimi、glm4

    # todo：设计apikey入参
    # rag

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # if isinstance((last_content := self.messages[-1].get('content')), list):  # 多模态
        #     self.last_content = last_content
        self.last_content: str = self.messages[-1].get('content')  # 大部分时间等价于user_content

        # 兼容 glm-4
        self.top_p = self.top_p is not None and np.clip(self.top_p, 0.01, 0.99)
        self.temperature = self.temperature is not None and np.clip(self.temperature, 0.01, 0.99)

        # 兼容 没有system
        if self.model.startswith(("gemini", "gemma")) and "system" in str(self.messages[0]):  # 偶数带 system
            self.messages[0]['role'] = 'user'
            self.messages.insert(1, {"role": "assistant", "content": ""})
            logger.debug(self.messages)

        if file_ids := self.file_ids or self.refs:
            self.file_ids = file_ids
            self.refs = file_ids

        if search := self.use_search or self.search:
            self.search = search
            self.use_search = search

        # glm
        self.assistant_id = self.assistant_id or "65940acff94777010aa6b796"

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": "hi"
                        }
                    ],
                    "stream": False
                },

                {
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": "请按照下面标题，写一篇400字的文章\n王志文说，一个不熟的人找你借饯，说明他已经把熟人借遍了。除非你不想要了，否则不要借"
                        }
                    ],
                    "stream": False
                },

                # url
                {
                    "model": "url-gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": "总结一下https://mp.weixin.qq.com/s/Otl45GViytuAYPZw3m7q9w"
                        }
                    ],
                    "stream": False
                },

                # rag
                {
                    "messages": [
                        {
                            "content": "分别总结这两篇文章",
                            "role": "user"
                        }
                    ],
                    "model": "gpt-3.5-turbo",
                    "stream": False,
                    "file_ids": ["cn2a0s83r07am0knkeag", "cn2a3ralnl9crebipv4g"]
                }

            ]
        }
    }


class ImageRequest(BaseModel):
    prompt: str
    model: str = ''
    n: int = 1
    quality: str = 'hd'
    response_format: Literal["url", "b64_json"] = "url"
    size: Literal["256x256", "512x512", "1024x1024", "1792x1024", "1024x1792"] = '1024x1024'  # 测试默认值
    # sd: 768x1024 1024x576
    style: Union[str, Literal["vivid", "natural"]] = "vivid"

    # 拓展参数
    guidance_scale: float = 4.5
    num_inference_steps: int = 25  # https://blog.csdn.net/qq_37508554/article/details/133975130
    seed: Optional[int] = None
    negative_prompt: Optional[str] = None

    class Config:
        # frozen = True

        json_schema_extra = {
            "examples": [
                {
                    "model": "stable-diffusion-3-medium",  # sd3
                    "prompt": "画条狗",
                },
            ]
        }


class TTSRequest(BaseModel):
    input: str
    model: str = 'tts'  # "tts-1", "tts-1-hd" tts-xx 计费2分钱一次
    voice: str = ""
    response_format: Literal["mp3", "opus", "aac", "flac", "wav", "pcm"] = "mp3"
    speed: float = 1
    # extra_query: Optional[dict] = None
    extra_body: dict = {}

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "model": "tts-1",
                    "voice": "7f92f8afb8ec43bf81429cc1c9199cb1",
                    "input": "你好，我是AI助手",
                }
            ]
        }


if __name__ == '__main__':
    pass
    # print(ChatCompletion(choices=[Choice(message=ChatCompletionMessage(content="ChatCompletion"))]))
    # print(ChatCompletionChunk(choices=[ChunkChoice(delta=ChoiceDelta(content="ChatCompletionChunk"))]))
    #
    # print(chat_completion)
    # print(chat_completion_chunk)
    # print(chat_completion_chunk_stop)

    # print(ChatCompletionRequest(temperature=0, top_p=1))
    # print(ChatCompletionRequest(temperature=1, top_p=0))

    file = UploadFile(open("/Users/betterme/PycharmProjects/AI/ChatLLM/chatllm/api/routers/cocopilot.py", "rb"))
    # #
    print(AudioRequest(file=file))
