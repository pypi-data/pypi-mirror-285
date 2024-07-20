#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : kuaishou_types
# @Time         : 2024/7/9 13:26
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *

# oss
"https://s2-111386.kwimgs.com/bs2/mmu-kolors-public/5f9c7b42688fe95c4b8d9ebd1dba3431.png?x-oss-process=image/resize,m_mfit,w_305"

BASE_URL = "https://klingai.kuaishou.com"
UPLOAD_BASE_URL = "https://upload.kuaishouzt.com"

ASPECT_RATIOS = {
    "1:1": "1024x1024",

    "16:9": "1344x768",
    "9:16": "768x1344",

    "4:3": "1152x896",
    "3:4": "896x1152",

    "3:2": "1216x832",
    "2:3": "832x1216",

}

STYLES = {
    "默认", "皮克斯", "卡通盲盒", "新海诚", "动漫3D", "怀旧动漫", "电子游戏", "水彩插画", "莫奈油画", "高清写实"
}


class KolorsRequest(BaseModel):
    prompt: str = '多肉植物，带着水珠，潮玩盲盒风格，皮克斯，3D质感，温馨的环境，丰富的场景，最佳画质，超精细，Octane渲染'
    negativePrompt: str = ''  # 不希望出现的内容

    style: str = "默认"
    imageCount: int = 1
    resolution: str = "1024x1024"

    #
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = "1:1"

    # 垫图
    referImage: str = ''
    fidelity: float = 0.5  # 参考度

    cfgScale: float = 7
    strength: float = 0.8

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if self.style not in STYLES:
            self.style = "默认"

        if self.resolution not in set(ASPECT_RATIOS.values()):
            self.resolution = ASPECT_RATIOS.get(self.aspect_ratio, "1024x1024")

        if self.referImage and self.referImage.startswith("http"):
            self.imageCount = 4
            self.referImage = self.referImage.split("/")[-2].split('?')[0]


class KlingaiImageRequest(BaseModel):
    prompt: str = '清凉夏季美少女，微卷短发，运动服，林间石板路，斑驳光影，超级真实，16K'
    style: str = "默认"
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = "1:1"
    imageCount: int = 1
    url: str = ''

    #
    payload: dict = {}

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        inputs = []
        task_type = "mmu_txt2img_aiweb"
        if self.url:
            task_type = "mmu_img2img_aiweb"
            inputs.append({'name': 'input', 'inputType': 'URL', 'url': self.url})
            inputs[-1]["fromWorkId"] = self.url.split('/')[-3].split('_')[-1]

        arguments = [
            {'name': 'prompt', 'value': self.prompt},
            {'name': 'style', 'value': self.style},
            {'name': 'aspect_ratio', 'value': self.aspect_ratio},
            {'name': 'imageCount', 'value': self.imageCount},
            {'name': 'biz', 'value': 'klingai'}
        ]
        self.payload = {
            'arguments': arguments,
            'type': task_type,
            'inputs': inputs
        }


class Camera(BaseModel):
    type: Literal["empty", "horizontal", "vertical", "zoom", "tilt", "pan", "roll", "down_back"] = "empty"
    horizontal: float = 0
    vertical: float = 0
    zoom: float = 0
    tilt: float = 0
    pan: float = 0
    roll: float = 0

    #
    camera_json: str = ""  # 运镜

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        if self.type == "down_back":
            self.vertical = self.vertical or -10
            self.zoom = self.zoom or -10

        # elif hasattr(self, self.type):
        #     self.__setattr__(self.type, self.__getattr__(self.type))

        self.camera_json = json.dumps(self.dict(exclude={'camera_json'}))


class KlingaiVideoRequest(BaseModel):
    prompt: str = ''
    negative_prompt: str = ''  # 不希望出现的内容

    duration: int = 5
    aspect_ratio: Literal["1:1", "2:3", "3:2", "3:4", "4:3", "9:16", "16:9"] = "16:9"
    cfg: float = 0.5  # 创意程度
    camera: Camera = Camera()  # 运镜

    url: str = ''
    # 图生视频
    tail_image_url: str = ''

    #
    payload: dict = {}

    def __init__(self, /, **data: Any):
        super().__init__(**data)
        arguments = [
            {'name': 'prompt', 'value': self.prompt},
            {'name': 'negative_prompt', 'value': self.negative_prompt},
            {'name': 'duration', 'value': self.duration},
            {'name': 'aspect_ratio', 'value': self.aspect_ratio},
            {'name': 'cfg', 'value': self.cfg},
            {'name': 'camera_json', 'value': self.camera.camera_json},

            # 图生视频
            {"name": "tail_image_enabled", "value": "true" if self.tail_image_url else "false"},

            {'name': 'biz', 'value': 'klingai'}
        ]

        inputs = []
        task_type = "m2v_txt2video"
        if self.url:
            task_type = "m2v_img2video"
            inputs.append({'name': 'input', 'inputType': 'URL', 'url': self.url})
            if self.url.endswith(".mp4"):  # 待测试
                inputs[-1]["fromWorkId"] = self.url.split('/')[-3].split('_')[-1]
                task_type = "m2v_extend_video"

        if self.tail_image_url:
            inputs.append({'name': 'tail_image', 'inputType': 'URL', 'url': self.tail_image_url})

        self.payload = {
            'arguments': arguments,
            'type': task_type,
            'inputs': inputs
        }

    # .split('/')[-3].split('_')[-1]
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "prompt": "一只可爱的黑白边境牧羊犬，头伸出车窗，毛发被风吹动，微笑着伸出舌头",

                    "url": "",
                    "tail_image_url": "",

                    "negative_prompt": "",
                    "duration": 5,
                    "aspect_ratio": "16:9",
                    "cfg": 0.5,
                    "camera": {
                        "type": "empty",
                        "horizontal": 0,
                        "vertical": 0,
                        "zoom": 0,
                        "tilt": 0,
                        "pan": 0,
                        "roll": 0
                    }
                },

                {
                    "prompt": "一只可爱的黑白边境牧羊犬，头伸出车窗，毛发被风吹动，微笑着伸出舌头",

                    "url": "https://p2.a.kwimgs.com/bs2/upload-ylab-stunt/ai_portal/1720681052/LZcEugmjm4/whqrbrlhpjcfofjfywqqp9.png",
                    "tail_image_url": "",

                    "negative_prompt": "",
                    "duration": 5,
                    "aspect_ratio": "16:9",
                    "cfg": 0.5,
                    "camera": {
                        "type": "empty",
                        "horizontal": 0,
                        "vertical": 0,
                        "zoom": 0,
                        "tilt": 0,
                        "pan": 0,
                        "roll": 0
                    }
                }

            ]
        }


"https://p2.a.kwimgs.com/bs2/upload-ylab-stunt/special-effect/output/HB1_PROD_ai_web_30121850/8784600431869866912/out.mp4"
if __name__ == '__main__':
    print(Camera().camera_json)
