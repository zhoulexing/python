from .gui import WeChatGui
import time
import pyautogui
import os
from utils.image import ImageUtils

image_utils = ImageUtils()


class WeChatType:
    WECHAT = "wechat"
    MULTI_CHAT = "multi_chat"


class WeChat:
    def __init__(self):
        self.type = WeChatType.MULTI_CHAT
        self.wechat_gui = WeChatGui()
        self.multi_chat_index = 0

    def start(self):
        if self.type == WeChatType.MULTI_CHAT:
            print("正在打开多聊...")
            # 1. 打开多聊
            if not self.wechat_gui.open_multi_chat():
                print("打开多聊失败")
                return

            # 2. 查找多聊窗口
            print("正在查找多聊窗口...")
            if not self.wechat_gui.find_multi_chat_window():
                print("未找到微信窗口，请确保微信已启动")
                return
            if self.multi_chat_index >= len(self.wechat_gui.multi_chat_children_windows):
                print("多聊子窗口索引超出范围")
                return

            # 3. 将多聊窗口置于前台，并等待加载
            if not self.wechat_gui.bring_multi_chat_window_to_front():
                print("将多聊窗口置于前台失败")
                return

            # 4. 截取多聊截图
            screenshot = self.wechat_gui.screenshot_by_rect(
                "assets/images/wechat/current_multi_chat_screenshot.png",
                self.wechat_gui.multi_chat_rect
            )
            if not screenshot:
                print("截图失败")
                return

            self.wechat_gui.click_multi_chat_by_index(self.multi_chat_index)

            # 5. 进入朋友圈
            if not self.wechat_gui.click_by_image("assets/images/wechat/current_multi_chat_screenshot.png",
                                                  "assets/images/wechat/moment_step_1.png", 0.7, relative=True, rect=self.wechat_gui.multi_chat_rect):
                print("进入朋友圈失败")
                return
        else:
            # 1. 打开微信
            print("正在打开微信...")
            if not self.wechat_gui.open_wechat():
                print("打开微信失败")
                return

            # 2. 查找微信窗口
            print("正在查找微信/多聊窗口...")
            if not self.wechat_gui.find_wechat_window():
                print("未找到微信窗口，请确保微信已启动")
                return

            # 3. 显示微信窗口信息
            info = self.wechat_gui.get_wechat_info()
            if info:
                print(f"微信窗口信息: {info}")
            else:
                print("未找到微信窗口")
                return

            # 4. 截取微信截图
            print("正在截取微信截图...")
            screenshot = self.wechat_gui.screenshot_wechat(
                "assets/images/wechat/current_wechat_screenshot.png"
            )
            if not screenshot:
                print("截图失败")
                return
            # 5. 进入朋友圈
            if not self.wechat_gui.click_by_image("assets/images/wechat/current_wechat_screenshot.png",
                                                  "assets/images/wechat/moment_step_1.png", 0.7, relative=True, rect=self.wechat_gui.wechat_rect):
                print("进入朋友圈失败")
                return

        # 6. 查找朋友圈窗口
        self.wechat_gui.find_moment_window()
        # 7. 将朋友圈窗口置于前台，并等待加载
        self.wechat_gui.bring_moment_window_to_front()
        # 8. 截取朋友圈截图
        self.wechat_gui.screenshot_moment(
            "assets/images/wechat/current_moment_screenshot.png"
        )
        # 9. 点击发朋友圈的弹窗按钮
        self.wechat_gui.click_by_image("assets/images/wechat/current_moment_screenshot.png",
                                       "assets/images/wechat/moment_step_2.png", 0.7, relative=True, rect=self.wechat_gui.moment_rect)

        # 10. 点击弹窗中的写文字输入框
        self.wechat_gui.screenshot_moment(
            "assets/images/wechat/current_moment_screenshot.png"
        )
        self.wechat_gui.click_by_image("assets/images/wechat/current_moment_screenshot.png",
                                       "assets/images/wechat/moment_step_text.png", 0.7, relative=True, rect=self.wechat_gui.moment_rect)
        time.sleep(0.5)
        # 11. 输入文字 TODO: 后面换AI来生成
        pyautogui.typewrite("Hello, World!")
        time.sleep(1)
        # 12. 输入图片 TODO: 后面换AI来生成
        self.wechat_gui.screenshot_moment(
            "assets/images/wechat/current_moment_screenshot.png"
        )
        self.wechat_gui.click_by_image("assets/images/wechat/current_moment_screenshot.png",
                                       "assets/images/wechat/moment_step_image.png", 0.7, relative=True, rect=self.wechat_gui.moment_rect)
        time.sleep(1)
        image_dir = os.path.join(os.path.dirname(
            __file__), "../../assets/images/wechat")
        self.wechat_gui.select_images_from_dialog(
            image_dir, ["moment_step_3.png", "current_screenshot_blank.png"])

        # 13. 点击发送按钮
        self.wechat_gui.screenshot_moment(
            "assets/images/wechat/current_moment_screenshot.png"
        )
        self.wechat_gui.click_by_image("assets/images/wechat/current_moment_screenshot.png",
                                       "assets/images/wechat/moment_step_3.png", 0.7, relative=True, rect=self.wechat_gui.moment_rect)

        if self.type == WeChatType.MULTI_CHAT:
            self.multi_chat_index += 1
            self.start()

if (__name__ == "__main__"):
    wechat = WeChat()
    wechat.start()
