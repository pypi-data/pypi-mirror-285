#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : klingai
# @Time         : 2024/7/9 13:23
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
import jsonpath

from meutils.pipe import *
from meutils.decorators.retry import retrying
from meutils.schemas.kuaishou_types import BASE_URL, KlingaiVideoRequest
from meutils.schemas.task_types import Task

from meutils.notice.feishu import send_message as _send_message
from meutils.config_utils.lark_utils import get_next_token_for_polling

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=PoBI7G"

send_message = partial(
    _send_message,
    title=__name__,
    url="https://open.feishu.cn/open-apis/bot/v2/hook/dc1eda96-348e-4cb5-9c7c-2d87d584ca18"
)


# 自动延长
# {"type":"m2v_extend_video","inputs":[{"name":"input","inputType":"URL","url":"https://h1.inkwai.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_29545092/8992112608804666920/output_ffmpeg.mp4","fromWorkId":29545092}],"arguments":[{"name":"prompt","value":""},{"name":"biz","value":"klingai"},{"name":"__initialType","value":"m2v_img2video"},{"name":"__initialPrompt","value":"母亲对着镜头挥手"}]}
# 自定义创意延长
# {"type":"m2v_extend_video","inputs":[{"name":"input","inputType":"URL","url":"https://h2.inkwai.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_29542959/396308539942414182/output_ffmpeg.mp4","fromWorkId":29542959}],"arguments":[{"name":"prompt","value":"加点字"},{"name":"biz","value":"klingai"},{"name":"__initialType","value":"m2v_txt2video"},{"name":"__initialPrompt","value":"让佛祖说话，嘴巴要动，像真人一样"}]}
@retrying(max_retries=5, predicate=lambda r: not r)
async def submit_task(request: KlingaiVideoRequest, cookie: Optional[str] = None):
    cookie = cookie or await get_next_token_for_polling(FEISHU_URL)

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json;charset=UTF-8'
    }

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        response = await client.post("/api/task/submit", json=request.payload)
        if response.is_success:
            data = response.json()  # metadata
            send_message(bjson(data))

            # 触发重试
            if any(i in str(data) for i in {"页面未找到", "请求超限"}):
                send_message(f"{data}\n\n{cookie}")
                return  # 404 429 触发重试

            try:
                task_ids = jsonpath.jsonpath(data, "$..task.id")  # $..task..[id,arguments]
                if task_ids:
                    return Task(id=task_ids[0], data=data, system_fingerprint=cookie)
                else:
                    return Task(status=0, data=data, system_fingerprint=cookie)

            except Exception as e:
                logger.error(e)
                send_message(f"未知错误：{e}")


@retrying(predicate=lambda r: not r)  # 触发重试
async def get_task(task_id, cookie: str):
    task_id = isinstance(task_id, str) and task_id.split("-", 1)[-1]

    headers = {
        'Cookie': cookie,
        'Content-Type': 'application/json;charset=UTF-8'
    }

    async with httpx.AsyncClient(base_url=BASE_URL, headers=headers) as client:
        response = await client.get("/api/task/status", params={"taskId": task_id})

        logger.debug(response.text)

        if response.is_success:
            data = response.json()
            return data  # "message": "task 29040731 failed, message is ",

            # logger.debug(data)
            #
            # if not task_id or "failed," in str(data): return "TASK_FAILED"  # 跳出条件
            #
            # urls = jsonpath.jsonpath(data, '$..resource.resource')
            # if urls and all(urls):
            #     images = [{"url": url} for url in urls]
            #     return images
            # else:
            #     return "RETRYING"  # 重试


if __name__ == '__main__':
    # https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=v8vcZY

    cookie = "_did=web_78482872453A739A;did=web_ccbac71acd43378cacb0d942986178c35efe;kuaishou.ai.portal_ph=647333d3e07801801dbf36ffec6c912d4140;kuaishou.ai.portal_st=ChVrdWFpc2hvdS5haS5wb3J0YWwuc3QSoAEIENU9DyeRoCoTRRJr4euDO3VXUwx6BPW6Lw8tlbgJERy8OvC6YjXMr_AH-SBMSDKvUwiYmkLOr2O5ct1px4O-pUCFY0W1d7H9DiCyU4F4ZtWOWSZcB_S3tfZUdj8BcA-Ua7iIPsqe9FffzzBo1B51_Lz30pBcSFR9lLctgXs1aEIGOkAmWEMTpK6kUASOUETKXGgWdtesz4kl5RTCv473GhLGi0v_iyPMOr2JVXM8LPzBvxQiIAp84Uu2XvSFjvxOZoYfi0wQdQ06MJwnRKZ62s_cOvq9KAUwAQ;userId=1326278356;weblogger_did=web_27626346807D71EF"
    # request = KlingaiVideoRequest(prompt="一条可爱的小狗", duration=10)  # 27638649

    # pprint(arun(submit_task(request, cookie)))
    # pprint(arun(get_task(28098891, cookie)))

    # pprint(arun(create_image(rquest)))

    # request
    # request = KlingaiVideoRequest(
    #     prompt="一条可爱的小狗",
    #     url="https://p2.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_30135907/1706269798026373672/output_ffmpeg.mp4"
    # )
    # pprint(arun(submit_task(request, cookie)))
    # pprint(arun(get_task(28106800, cookie)))  # 拓展的id 28106800  可能依赖账号 跨账号失败: 单账号测试成功

    # url = "http://p2.a.kwimgs.com/bs2/upload-ylab-stunt/ai_portal/1720681052/LZcEugmjm4/whqrbrlhpjcfofjfywqqp9.png"
    # request = KlingaiVideoRequest(prompt="狗狗跳起来", url=url)  # 28110824
    # pprint(arun(submit_task(request, cookie)))

    # pprint(arun(get_task(28110824, cookie)))

    url = "http://p2.a.kwimgs.com/bs2/upload-ylab-stunt/ai_portal/1720681052/LZcEugmjm4/whqrbrlhpjcfofjfywqqp9.png"
    # request = KlingaiVideoRequest(prompt="狗狗跳起来", url=url)  # 28110824
    # pprint(arun(submit_task(request, cookie)))

    # pprint(arun(get_task(28112984, cookie)))
    # pprint(arun(get_task(28377631, cookie)))
    pprint(arun(get_task(28383134, cookie)))
