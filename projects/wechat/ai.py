from ai.youzan import YouzanModel
from ai.zjie import ZjieModel
import json
import requests
import uuid


class WeChatAi:
    def __init__(self):
        self.youzanModel = YouzanModel()
        self.zjieModel = ZjieModel()

    def execute(self, msg_list):
        messages = [
            {
                "role": "system",
                "content": """
                你是一名朋友圈助手，需要根据用户的输入来判定是否需要发朋友圈，
                如果需要发的话，请根据消息内容判定是否要选择朋友圈文案生成工具（text_generator），
                和朋友圈图片生成工具（image_generator）来生成素材内容, 如果不需要发则返回空。
                """
            },
            {
                "role": "user",
                "content": f"{json.dumps(msg_list)}"
            }
        ]
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "text_generator",
                    "description": "朋友圈文案生成工具",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "朋友圈文案",
                            }
                        },
                        "required": ["content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "image_generator",
                    "description": "朋友圈图片生成工具",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "图片描述",
                            },
                            "num": {
                                "type": "number",
                                "description": "图片数量",
                            }
                        },
                        "required": ["description", "num"]
                    }
                }
            }
        ]

        return self.youzanModel.chat(messages, tools)

    def text_generator(self, content):
        print(f"text_generator: {content}")
        return content

    def image_generator(self, description, num):
        file_names = []
        for i in range(num):
            url = self.zjieModel.text_2_image(description)
            # 下载图片
            response = requests.get(url)
            file_name = f"{uuid.uuid4()}.png"
            with open(f"assets/images/wechat/{file_name}", "wb") as f:
                f.write(response.content)
            file_names.append(file_name)
        return file_names

    def start(self, msg_list):
        content, toolCalls = self.execute(msg_list)
        toolCalls = json.loads(toolCalls)
        for toolCall in toolCalls:
            if toolCall["function"]["name"] == "text_generator":
                arguments = json.loads(toolCall["function"]["arguments"])
                text = self.text_generator(arguments["content"])
            elif toolCall["function"]["name"] == "image_generator":
                arguments = json.loads(toolCall["function"]["arguments"])
                file_names = self.image_generator(
                    arguments["description"], arguments["num"])
                print(f"image_generator: {file_names}")
        return text, file_names


if __name__ == "__main__":
    wechat_ai = WeChatAi()
    msg_list = [
        {
            "id": 126,
            "content": "帮我发条朋友圈，具体内容如下：\n文案：拉布布蛋糕|这阵风还在吹,三款快入手\n图片：基于最火的labubu生成2张蛋糕图片",
            "createTime": "2025-06-24 10:29:53"
        }
    ]
    wechat_ai.start(msg_list)
