#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : openai_asr
# @Time         : 2023/11/23 13:10
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description
import io
import os

import requests

from meutils.pipe import *
from openai import OpenAI

# response_format: Literal["json", "text", "srt", "verbose_json", "vtt"]
file = open(
    "/Users/betterme/PycharmProjects/AI/MeUtils/meutils/ai_audio/asr/whisper-1719913495729-54f08dde5.wav.mp3.mp3",
    'rb')  # 正确
# file=open("2022112519张健涛29.mp3", 'rb')
# file = httpx.get("https://oss.chatfire.cn/data/demo.mp3").content

client = OpenAI()

with timer():
    _ = client.audio.transcriptions.create(
        file=file,
        model="whisper-1",
        # model="whisper-large-v3",
        # response_format="text",  # ["json", "text", "srt", "verbose_json", "vtt"]
        # response_format="srt",  # ["json", "text", "srt", "verbose_json", "vtt"]
        # response_format="verbose_json",  # ["json", "text", "srt", "verbose_json", "vtt"]
        # response_format="vtt",  # ["json", "text", "srt", "verbose_json", "vtt"]

    )
    print(_)
    #
    # _ = client.audio.translations.create(
    #     file=file,
    #     # model="whisper-1",
    #     model="whisper-large-v3",
    #     # response_format="text",  # ["json", "text", "srt", "verbose_json", "vtt"]
    #     # response_format="srt",  # ["json", "text", "srt", "verbose_json", "vtt"]
    #     # response_format="verbose_json",  # ["json", "text", "srt", "verbose_json", "vtt"]
    #     # response_format="vtt",  # ["json", "text", "srt", "verbose_json", "vtt"]
    #
    # )
    # print(_)

# Transcription(text='健身需要注意适度和平衡 过度的锻炼可能会导致身体受伤 因此 进行健身活动前 最好先咨询医生 或专业的健身教练 制定一个适合自己的健身计划 一般来说 一周内进行150分钟的适度强度的有氧运动 或者75分钟的高强度有氧运动 加上每周两天的肌肉锻炼就能达到保持健康的目标')
