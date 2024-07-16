#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : demo
# @Time         : 2024/4/30 16:46
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import os

from meutils.pipe import *
import lark_oapi as lark
from lark_oapi.api.sheets.v3 import *


# SDK 使用说明: https://github.com/larksuite/oapi-sdk-python#readme

client = lark.Client.builder() \
        .enable_set_token(True) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()

option = lark.RequestOption.builder().user_access_token(os.getenv("FEISHU_USER_ACCESS_TOKEN")).build()




# 构造请求对象
request: GetSpreadsheetSheetRequest = GetSpreadsheetSheetRequest.builder() \
    .spreadsheet_token("APMRsoxW4hkIzwt693Bc9kWtnSd") \
    .sheet_id("95c9b1") \
    .build()

# 发起请求
response: GetSpreadsheetSheetResponse = client.sheets.v3.spreadsheet_sheet.get(request, option)
#
#
# # 处理业务结果
# lark.logger.info()


if __name__ == "__main__":
    print(lark.JSON.marshal(response.data, indent=4))

