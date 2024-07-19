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
    lyrics = "lyrics"
    runwayml = "runwayml"
    fish = 'fish'


class Task(BaseModel):
    id: Union[str, int] = Field(default_factory=lambda: shortuuid.random())
    status: Union[str, int] = "success"  # pending, running, success, failed

    data: Optional[Any] = None
    metadata: Optional[Any] = None
    # metadata: Optional[Dict[str, str]] = None
    description: Optional[str] = None

    system_fingerprint: Optional[str] = None  # api-key token cookie 加密

    created_at: int = Field(default_factory=lambda: int(time.time()))


# pass

if __name__ == '__main__':
    # print(TaskType("kling").name)
    #
    # print(TaskType("kling") == 'kling')

    # print(Task(id=1, status='failed', system_fingerprint='xxx').model_dump(exclude={"system_fingerprint"}))

    print("kling" == TaskType.kling)
