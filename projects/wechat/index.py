from .gui import WeChatGui
import time
from .ai import WeChatAi
import requests
from .decrypt import WeChatDecrypt
from utils.config import Config
import uuid
import sys


class WeChatType:
    WECHAT = "wechat"
    MULTI_CHAT = "multi_chat"


class WeChat:
    def __init__(self):
        self.wechat_gui = WeChatGui()
        self.wechat_ai = WeChatAi()
        self.wechat_decrypt = WeChatDecrypt()
        self.config = Config()

        self.ip = "172.18.232.82:5001"
        self.record = {}

    def listen_public(self):
        while True:
            material_item = requests.get(
                f"http://{self.ip}/wechat/listen_new_msgs")
            material_item = material_item.json()
            print(f"wechat listen_material_item: {material_item}")
            if material_item and material_item["id"] not in self.record:
                self.record[material_item["id"]] = True

                self.wechat_gui.set_text(material_item["text"])
                self.wechat_gui.download_image_urls(
                    material_item["image_urls"])
                self.wechat_gui.send_moment()
                # requests.post(f"http://{self.ip}/wechat/set_msg_ineffective", json={
                #     "id": material_item["id"]
                # })
            time.sleep(2)

    def decrypt_generate(self):
        """
        这个需要在解密的电脑上运行，需要启动定时解密任务和启动http接口服务
        轮询解密数据库，如果解密到新的消息，则调用ai来判定是否需要发布朋友圈，并生成朋友圈文案
        """
        while True:
            msg_text_list = self.wechat_decrypt.find_new_msgs_of_robot(
                "测试2号13282127")
            print(f"wechat decrypt msg_text_list: {msg_text_list}")
            if len(msg_text_list) > 0:
                for msg_text in msg_text_list:
                    self.wechat_ai.add_message("user", msg_text["content"])
                sussess, text, image_urls = self.wechat_ai.step()
                print(f"wechat ai step: {sussess}, {text}, {image_urls}")
                if text and image_urls and not sussess:
                    self.wechat_gui.set_text(text)
                    self.wechat_gui.download_image_urls(image_urls)
                    self.wechat_gui.send_msg()
                if sussess:
                    friends_circle_material = self.config.get(
                        "friends_circle_material")
                    friends_circle_material.append({
                        "id": str(uuid.uuid4()),
                        "text": text,
                        "image_urls": image_urls,
                        "ineffective": False
                    })
                    self.config.set("friends_circle_material",
                                    friends_circle_material)
                    self.wechat_ai.clear_messages()
            time.sleep(2)

    def test_decrypt_generate(self):
        self.wechat_gui.set_text("123")
        self.wechat_gui.download_image_urls([])
        self.wechat_gui.send_msg()


if __name__ == "__main__":
    wechat = WeChat()
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "decrypt":
            wechat.decrypt_generate()
        elif mode == "listen":
            wechat.listen_public()
        elif mode == "test":
            wechat.test_decrypt_generate()
        else:
            print("Usage: python index.py [decrypt|listen]")
            print("  decrypt: 运行解密生成模式")
            print("  listen: 运行监听公开模式")
    else:
        print("Usage: python index.py [decrypt|listen]")
        print("  decrypt: 运行解密生成模式")
        print("  listen: 运行监听公开模式")
