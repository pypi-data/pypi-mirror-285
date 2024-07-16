#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : task_types
# @Time         : 2024/5/31 15:47
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
from enum import Enum

from meutils.pipe import *


class TaskType(str, Enum):
    kling = "kling"
    suno = "suno"


class Task(BaseModel):
    id: Union[str, int] = Field(default_factory=lambda: shortuuid.random())
    status: Union[str, int] = "success"  # pending, running, success, failed

    data: Optional[dict] = None
    metadata: Optional[dict] = None
    # metadata: Optional[Dict[str, str]] = None
    description: Optional[str] = None

    system_fingerprint: Optional[str] = None  # api-key token cookie 加密

    created_at: int = Field(default_factory=lambda: int(time.time()))


class TaskRequest(BaseModel):
    task_type: str  # 任务类型: suno、tts
    purpose: str  # 任务用途: 翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译、总结、问答、写作、总结、翻译
    task_id: Optional[str] = None
    task_name: Optional[str] = None

    task_status: str  # 任务状态: pending、running、finished、failed
    task_result: str  # 任务结果

    task_params: dict = {}

    # task_log: str  # 任务日志

    extra_body: dict = {}

    # 自动生成task_id?提交的时候就生成

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        self.task_id = self.task_id or f"{self.task_type}-{shortuuid.random()}"


# pass

if __name__ == '__main__':
    # print(TaskType("kling").name)
    #
    # print(TaskType("kling") == 'kling')

    print(Task(id=1, status='failed', system_fingerprint='xxx').model_dump(exclude={"system_fingerprint"}))
