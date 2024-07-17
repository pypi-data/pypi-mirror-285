#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : common
# @Time         : 2024/5/6 08:52
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : httpx重试 transport = httpx.AsyncHTTPTransport(retries=3) # response.raise_for_status()
import json

from meutils.pipe import *
from meutils.decorators.retry import retrying
from urllib.parse import urlparse, parse_qs

FEISHU_BASE_URL = "https://open.feishu.cn/open-apis/"


def get_app_access_token():
    payload = {
        "app_id": os.getenv("FEISHU_APP_ID"),
        "app_secret": os.getenv("FEISHU_APP_SECRET")
    }
    response = httpx.post(
        "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal",
        json=payload,
        timeout=30,
    )

    # logger.debug(response.json())

    return response.json().get("app_access_token")


@retrying(max_retries=3, predicate=lambda x: not x)
async def aget_app_access_token():
    """不加缓存，access_token会提前失效
    该报错是因为开发者本次调用过程中使用的 Tenant Access Token 已经失效或有误，飞书开放平台无法判断当前请求是否来自一个可信的用户，因此拦截了情况。
    :return:
    """
    payload = {
        "app_id": os.getenv("FEISHU_APP_ID"),
        "app_secret": os.getenv("FEISHU_APP_SECRET")
    }
    async with httpx.AsyncClient(base_url=FEISHU_BASE_URL, timeout=30) as client:
        response = await client.post("/auth/v3/app_access_token/internal", json=payload)

        return response.is_success and response.json().get("app_access_token")  # False / None


def get_spreadsheet_values(
        spreadsheet_token: Optional[str] = None,
        sheet_id: Optional[str] = None,
        feishu_url=None,
        to_dataframe: Optional[bool] = False
):
    if feishu_url and feishu_url.startswith("http"):
        parsed_url = urlparse(feishu_url)
        spreadsheet_token = parsed_url.path.split('/')[-1]
        sheet_id = parsed_url.query.split('=')[-1]

    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}"

    headers = {
        "Authorization": f"Bearer {get_app_access_token()}"
    }
    response = httpx.get(url, headers=headers, timeout=30)
    _ = response.json()
    return _ if not to_dataframe else pd.DataFrame(_.get('data').get('valueRange').get('values'))


@alru_cache(ttl=600)
async def aget_spreadsheet_values(
        spreadsheet_token: Optional[str] = None,
        sheet_id: Optional[str] = None,
        feishu_url=None,
        to_dataframe: Optional[bool] = False
):
    if feishu_url and feishu_url.startswith("http"):
        parsed_url = urlparse(feishu_url)
        spreadsheet_token = parsed_url.path.split('/')[-1]
        sheet_id = parsed_url.query.split('=')[-1]

    access_token = await aget_app_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    async with httpx.AsyncClient(base_url=FEISHU_BASE_URL, timeout=30, headers=headers) as client:
        response = await client.get(f"/sheets/v2/spreadsheets/{spreadsheet_token}/values/{sheet_id}")
        if response.is_success:
            _ = response.json()
            if to_dataframe:
                return pd.DataFrame(_.get('data').get('valueRange').get('values'))
            return _
        else:
            from meutils.notice.feishu import send_message
            send_message(
                f"{response.status_code}\n\n{access_token}\n\n{response.text}",
                '飞书为啥为none: 已经去掉缓存了'
            )
            return get_spreadsheet_values(spreadsheet_token, sheet_id, feishu_url, to_dataframe)


async def spreadsheet_values_append(
        spreadsheet_token: Optional[str] = None,
        sheet_id: Optional[str] = None,
        feishu_url=None,
        range: Optional[str] = None,
        values: Optional[list] = None
):
    """ https://open.feishu.cn/document/server-docs/docs/sheets-v3/data-operation/append-data

        https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values_prepend
        https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values_append
        https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/:spreadsheetToken/values_image

    :param spreadsheet_token:
    :param sheet_id:
    :param feishu_url:
    :param values:
    :return:
    """

    if feishu_url and feishu_url.startswith("http"):
        parsed_url = urlparse(feishu_url)
        spreadsheet_token = parsed_url.path.split('/')[-1]
        sheet_id = parsed_url.query.split('=')[-1]

    access_token = await aget_app_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",

    }
    payload = {
        "valueRange": {
            # https://open.feishu.cn/document/server-docs/docs/sheets-v3/overview
            # "range": f"{sheet_id}!A:B",  # <sheetId>!<开始列>:<结束列>
            # "range": f"{sheet_id}!A1:E3",  # <sheetId>!<开始单元格>:<结束列>
            # "range": f"{sheet_id}",  # 非空的最大行列范围内的数据

            "range": f"{sheet_id}!{range}" if range else sheet_id,
            "values": values
        }
    }

    async with httpx.AsyncClient(base_url=FEISHU_BASE_URL, timeout=30, headers=headers) as client:
        # 默认覆盖 ?insertDataOption=OVERWRITE
        response = await client.post(f"/sheets/v2/spreadsheets/{spreadsheet_token}/values_append", json=payload)
        return response.is_success and response.json() or response.text


def create_document(title: str = "一篇新文档🔥", folder_token: Optional[str] = None):
    payload = {
        "title": title,
        "folder_token": folder_token,
    }

    url = "https://open.feishu.cn/open-apis/docx/v1/documents"
    headers = {
        "Authorization": f"Bearer {get_app_access_token()}"
    }
    response = httpx.post(url, headers=headers, timeout=30, json=payload)
    return response.json()


def get_doc_raw_content(document_id: str = "BxlwdZhbyoyftZx7xFbcGCZ8nah"):
    url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content"
    headers = {
        "Authorization": f"Bearer {get_app_access_token()}"
    }
    response = httpx.get(url, headers=headers, timeout=30)
    return response.json()


async def get_next_token_for_polling(feishu_url):  # 轮询
    df = await aget_spreadsheet_values(feishu_url=feishu_url, to_dataframe=True)
    api_keys = df[0]
    api_keys = [k for k in api_keys if k]  # 过滤空值
    return np.random.choice(api_keys)


if __name__ == '__main__':
    print(get_app_access_token())
    # print(get_spreadsheet_values("Qy6OszlkIhwjRatkaOecdZhOnmh", "0f8eb3"))
    # pprint(get_spreadsheet_values("Bmjtst2f6hfMqFttbhLcdfRJnNf", "Y9oalh"))
    # pd.DataFrame(
    #     get_spreadsheet_values("Bmjtst2f6hfMqFttbhLcdfRJnNf", "79272d").get('data').get('valueRange').get('values'))

    # print(get_doc_raw_content("TAEFdXmzyobvgUxKM3lcLfc2nxe"))
    # print(create_document())
    # "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=79272d"

    # r = get_spreadsheet_values(feishu_url="https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=79272d",
    #                            to_dataframe=True)
    # print(list(filter(None, r[0])))
    # print(get_spreadsheet_values("Bmjtst2f6hfMqFttbhLcdfRJnNf", "79272d"))

    # print(arun(aget_app_access_token()))
    # df = arun(aget_spreadsheet_values(
    #     feishu_url="https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=5i64gO",
    #     to_dataframe=True
    #
    # ))
    # print(df)

    from inspect import iscoroutinefunction

    # print(filter(lambda x: x and x.strip(), df[0]) | xlist)

    # func = aget_app_access_token()

    # print(alru_cache(ttl=300)(sync_to_async(aget_app_access_token))())

    # for i in tqdm(range(10)):
    #     # print(aget_app_access_token())
    #     print(arun(aget_app_access_token()))
    #     # print(get_app_access_token())

    values = [
        [
            "2023/12/25",
            "收入",
            "微信",
            "100",
            "帐号 老表max"
        ],
        [
            "2023/12/25",
            "支出",
            "支付宝",
            "10",
            "买东西 老表max"
        ],
        [
            "2023/12/26",
            "支出",
            "支付宝",
            "19.9",
            "买东西 老表max"
        ],
    ]

    _ = spreadsheet_values_append(
        feishu_url="https://xchatllm.feishu.cn/sheets/BPxjsmNj7hZr7Ytwk9uccvOKn6Z?sheet=7ce4e3",

        range="A1:E3",
        values=values

    )

    print(arun(_))

    print(create_document())
