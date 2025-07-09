import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

class AliModel:
    def __init__(self):
        self.api_key = os.getenv("ALI_API_KEY")

   

    def generate_image(self, prompt):
        url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        data = {
            "model": "wanx2.1-t2i-turbo",
            "input": {
                "prompt": prompt
            },
            "parameters": {
                "size": "1024*1024",
                "n": 1
            }
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def text_2_image(self, prompt):
        result = self.generate_image(prompt)
        task_id = result.get("output").get("task_id")
        
        url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
        }
        while True:
            response = requests.get(url, headers=headers)
            result = response.json()
            if result.get("output").get("task_status") == "SUCCEEDED":
                return result.get("output").get("results")[0].get("url")
            time.sleep(0.5)

if __name__ == "__main__":
    ali = AliModel()
    result = ali.text_2_image("一间有着精致窗户的花店，漂亮的木质门，摆放着花朵")
    print(result)
