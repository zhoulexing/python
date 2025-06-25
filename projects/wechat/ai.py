from ai.youzan import YouzanModel
from ai.zjie import ZjieModel
import json


class WeChatAi:
    def __init__(self):
        self.youzanModel = YouzanModel()
        self.zjieModel = ZjieModel()
        self.messages = [
            {
                "role": "system",
                "content": """
                你是一名朋友圈助手，需要根据用户的输入来判定是否需要发朋友圈，如果不需要发朋友圈，则不用做任何处理，也不需要返回任何内容，
                如果需要发的话，判定系统是否已经将文案和图片生成好了，如果已经生成好了，则不用调用工具生成，
                如果没生成好，请根据消息内容判定是否要选择朋友圈文案生成工具（text_generator），
                和朋友圈图片生成工具（image_generator）来生成素材内容, 生成完的内容会让用户进行确认，
                如果用户最终确认要发，则你需要将最终的文案和图片链接返回即可，以json格式返回，示例如下：
                {
                    "text": "拉布布蛋糕|这阵风还在吹,三款快入手",
                    "image_urls": ["https://example.com/image1.png", "https://example.com/image2.png"]
                }
                如果用户最终确认不发，则什么都不需要返回。
                """
            }
        ]

    def clear_messages(self):
        self.messages = []

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

        return self.youzanModel.chat(self.messages, tools)

    def text_generator(self, content):
        print(f"text_generator params: {content}")
        messages = [
            {
                "role": "system",
                "content": """
                你需要根据用户的输入来判定是用AI生成朋友圈文案还是直接返回用户输入的内容,
                如果用户的输入要求用AI生成，则根据用户要求生成朋友圈文案，文案字数在20字以内，不要超过20字
                如果用户的输入没有要求用AI生成，则返回用户输入的内容。

                示例：
                用户的输入：拉布布蛋糕|这阵风还在吹,三款快入手
                你的输出：拉布布蛋糕|这阵风还在吹,三款快入手

                用户的输入：用ai生成，要形容蛋糕好吃
                你的输出：甜而不腻，入口即化，每一口都是幸福的味道
                """
            },
            {
                "role": "user",
                "content": content
            }
        ]

        try:
            content, toolCalls = self.youzanModel.chat(messages)
            return content
        except Exception as e:
            print(f"text_generator error: {e}")
            return "物美价廉，优惠满满，性价比无敌！"

    def image_generator(self, description, num):
        print(f"image_generator params: {description}, {num}")
        image_urls = []
        try:
            for i in range(num):
                url = self.zjieModel.text_2_image(description)
                image_urls.append(url)
        except Exception as e:
            print(f"image_generator error: {e}")

        return image_urls

    def step(self):
        content, toolCalls = self.execute()
        if content:
            json_content = json.loads(content)
            return True, json_content.get("text"), json_content.get("image_urls")
        if toolCalls:
            toolCalls = json.loads(toolCalls)
            for toolCall in toolCalls:
                if toolCall["function"]["name"] == "text_generator":
                    arguments = json.loads(toolCall["function"]["arguments"])
                    text = self.text_generator(arguments["content"])
                elif toolCall["function"]["name"] == "image_generator":
                    arguments = json.loads(toolCall["function"]["arguments"])
                    image_urls = self.image_generator(
                        arguments["description"], arguments["num"])
            self.add_message(
                "assistant", f"图片和文案都生成好了，如下：\n文案：{text}\n图片：{image_urls}\n是否确认发布？")
            return False, text, image_urls
        return False, "", []

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content
        })

    def test(self, count=0, message=""):
        if not message:
            raise Exception("message is required")
        if count > 5:
            return False, "", []
        self.add_message("user", message)
        sussess, text, image_urls = self.step()
        print(f"test result: {sussess}, {text}, {image_urls}")


if __name__ == "__main__":
    wechat_ai = WeChatAi()
    wechat_ai.test(
        message="帮我发条朋友圈，具体内容如下：\n文案：拉布布蛋糕，快入手\n图片：一条小狗在奔跑")
