import requests
import json

class YouzanModel:
    def __init__(self):
        self.model = "azure4o"

    def invoke(self, service, method, data):
        url = f"http://tether-qa.s.qima-inc.com:8680/soa/{service}/{method}"
        headers = {
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'x-request-protocol': 'dubbo'
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    def chat(self, messages, tools = None):
        param = {
            "source": "shared_front",
            "scene": "wechat_helper",
            "n": 1,
            "tempPromptModel": {
                "settings": {
                    "presencePenalty": 0.2,
                    "frequencyPenalty": 0.2,
                    "stop": [],
                    "topP": 1.0,
                    "bestOf": 3,
                    "user": "openai-sdk",
                    "stream": False,
                    "modelKey": self.model,
                }
            },
            "messages": messages,
        }
        if tools:
            param["tools"] = tools
            
        result = self.invoke(
            "com.youzan.aigc.common.service.api.service.CommonService", "executeWithNativeParams", [param])
        if result.get("code") != 200:
            raise Exception(result.get("message"))

        contentItem = result.get("data").get("contents")[0]
        toolCalls = json.loads(contentItem.get("toolCalls")) if contentItem.get("toolCalls") else None
        return {
            "role": contentItem.get("role"),
            "content": contentItem.get("content"),
            "toolCalls": toolCalls
        }

    def generate(self, prompt):
        messages = [{
            "role": "user",
            "content": prompt
        }]
        return self.chat(messages)


if __name__ == "__main__":
    youzan = YouzanModel()
    result = youzan.chat([{"role": "user", "content": "你是谁"}])
    print(result)
