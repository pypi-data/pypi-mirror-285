#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : json标准化
# @Time         : 2024/5/17 15:32
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : pip install json-repair

# https://github.com/josdejong/jsonrepair

from meutils.pipe import *
import json_repair

print(json_repair.repair_json("""你们是{'a': 1, "b": 2, "c": 3}"""))





