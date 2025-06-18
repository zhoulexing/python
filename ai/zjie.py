import requests
from dotenv import load_dotenv
import os

load_dotenv()


class ZjieModel:
    def __init__(self):
        self.api_key = os.getenv("ZJIE_API_KEY")

    def text_2_image(self, prompt):
        url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "doubao-seedream-3-0-t2i-250415",
            "prompt": prompt,
            "response_format": "url",
            "size": "1024x1024",
            "seed": 12,
            "guidance_scale": 2.5,
            "num_inference_steps": 20,
            "num_images": 1,
            "watermark": True,
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()


if __name__ == "__main__":
    zjie = ZjieModel()
    result = zjie.text_2_image("鱼眼镜头，一只猫咪的头部，画面呈现出猫咪的五官因为拍摄方式扭曲的效果。")
    print(result)