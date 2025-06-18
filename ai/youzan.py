import requests


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

    def chat(self, messages):
        params = [{
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
        }]
        result = self.invoke(
            "com.youzan.aigc.common.service.api.service.CommonService", "executeWithNativeParams", params)
        if result.get("code") != 200:
            raise Exception(result.get("message"))

        return result.get("data").get("contents")[0].get("content")

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
