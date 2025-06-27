from ai.youzan import YouzanModel
from ai.zjie import ZjieModel
import json
import random
import string


class WeChatAi:
    def __init__(self):
        self.youzanModel = YouzanModel()
        self.zjieModel = ZjieModel()
        self.messages = [
            {
                "role": "system",
                "content": """
                你是一名朋友圈助手，能轻松创建和发送朋友圈内容。

                任务：
                1. 你需要根据用户的需求，判定是否是发朋友圈的任务，如果不是，则不用处理；
                2. 如果用户需要发朋友圈，你需要根据用户的需求，判定是否使用文案生成工具（text_generator）、图片生成工具（image_generator）或者同时使用两者来创建朋友圈内容；
                3. 用户在确认内容并同意发送后，你需要使用发送朋友圈消息工具（send_friends_circle）将内容发送到朋友圈；
                4. 如果用户最终确认不发，则不需要发送；
                5. 其他输入：跟朋友圈不相关的请求，将不予处理。

                要求：
                - 你不需要思考，直接根据用户的需求，使用工具来完成任务；
                - 在使用发送朋友圈消息工具时，需要用户确认文案和/或图片后，再使用， 且使用时一定是有文案或图片或者两者都有；
                """
            }
        ]
        self.image_url_map = {}

    def clear_messages(self):
        self.messages = []
        self.image_url_map = {}

    def execute(self):
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
                                "description": "朋友圈文案要求，比如：用ai生成，要形容蛋糕好吃",
                            },
                            "use_ai": {
                                "type": "boolean",
                                "description": "是否使用AI生成文案，true表示使用AI生成文案，false表示直接返回用户输入的内容",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "send_friends_circle",
                    "description": "发送朋友圈消息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "朋友圈文案",
                            },
                            "image_ids": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "朋友圈图片id"
                                },
                                "description": "朋友圈图片id列表",
                            }
                        }
                    }
                }
            }
        ]

        return self.youzanModel.chat(self.messages, tools)

    def text_generator(self, content, use_ai=False):
        print(f"text_generator params: {content}, {use_ai}")
        if not use_ai:
            return f"文案生成好了：{content}", content

        messages = [
            {
                "role": "system",
                "content": "根据用户的要求生成朋友圈文案，文案字数在50字以内"
                # "content": """
                # 你需要根据用户的输入来判定是用AI生成朋友圈文案还是直接返回用户输入的内容,
                # 如果用户的输入要求用AI生成，则根据用户要求生成朋友圈文案，文案字数在20字以内，不要超过20字
                # 如果用户的输入没有要求用AI生成，则返回用户输入的内容。

                # 示例：
                # 用户的输入：拉布布蛋糕|这阵风还在吹,三款快入手
                # 你的输出：拉布布蛋糕|这阵风还在吹,三款快入手

                # 用户的输入：用ai生成，要形容蛋糕好吃
                # 你的输出：甜而不腻，入口即化，每一口都是幸福的味道
                # """
            },
            {
                "role": "user",
                "content": content
            }
        ]

        try:
            result = self.youzanModel.chat(messages)
            return f"文案生成好了：{result.get('content')}", result.get('content')
        except Exception as e:
            print(f"text_generator error: {e}")
            return "文案生成失败，需要重新生成吗？", ""

    def send_msg(self, text="", image_ids=[]):
        print(f"send_msg params: {text}, {image_ids}")
        image_urls = []
        for image_id in image_ids:
            image_urls.append(self.image_url_map.get(image_id))
        return text, image_urls

    def image_generator(self, description, num):
        print(f"image_generator params: {description}, {num}")
        image_urls = []
        image_ids = []
        try:
            
            for i in range(num):
                random_str = ''.join(random.sample(
                    string.ascii_letters + string.digits, 5))
                # url = f"https://test.com/{random_str}.png"
                url = self.zjieModel.text_2_image(description)
                self.image_url_map[random_str] = url
                image_ids.append(random_str)
                image_urls.append(url)
        except Exception as e:
            print(f"image_generator error: {e}")

        return f"图片生成好了, 图片的id是：{image_ids}", image_urls

    def step(self):
        step_result = self.execute()
        print(f"wechat ai step: {step_result}")
        self.messages.append({
            "role": "assistant",
            "content": step_result.get("content"),
            "toolCalls": step_result.get("toolCalls"),
            "class": "com.youzan.aigc.common.service.api.model.AssistantMessage"
        })
        text = step_result.get("content")
        image_urls = []

        if step_result.get("toolCalls"):
            toolCalls = step_result.get("toolCalls")
            for toolCall in toolCalls:
                if toolCall["function"]["name"] == "text_generator":
                    arguments = json.loads(toolCall["function"]["arguments"])
                    text_desc, text_result = self.text_generator(
                        arguments.get("content"), arguments.get("use_ai"))
                    self.messages.append({
                        "role": "tool",
                        "content": text_desc,
                        "toolCallId": toolCall["id"],
                        "class": "com.youzan.aigc.common.service.api.model.ToolMessage"
                    })
                    text = text_result
                elif toolCall["function"]["name"] == "image_generator":
                    arguments = json.loads(toolCall["function"]["arguments"])
                    image_desc, image_result = self.image_generator(
                        arguments.get("description"), arguments.get("num"))

                    self.messages.append({
                        "role": "tool",
                        "content": image_desc,
                        "toolCallId": toolCall["id"],
                        "class": "com.youzan.aigc.common.service.api.model.ToolMessage"
                    })
                    image_urls = image_result
                elif toolCall["function"]["name"] == "send_friends_circle":
                    arguments = json.loads(toolCall["function"]["arguments"])
                    text, image_urls = self.send_msg(
                        arguments.get("text"), arguments.get("image_ids"))
                    return True, text, image_urls

        return False, text, image_urls

    def add_message(self, content):
        self.messages.append({
            "role": "user",
            "content": content
        })

    def run(self, message):
        if not message:
            raise Exception("message is required")
        self.add_message(message)
        return self.step()