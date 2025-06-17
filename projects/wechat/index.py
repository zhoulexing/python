from .gui import WeChatGui
import time
import pyautogui
import os

class WeChat:
    def __init__(self):
        self.wechat_gui = WeChatGui()

    def start(self):
        # 1. 打开微信
        print("正在打开微信...")
        if not self.wechat_gui.open_wechat():
            print("打开微信失败")
            return

        # 2. 查找微信窗口
        print("正在查找微信窗口...")
        if not self.wechat_gui.find_wechat_window():
            print("未找到微信窗口，请确保微信已启动")
            return

        # 3. 显示微信窗口信息
        info = self.wechat_gui.get_wechat_info()
        if info:
            print(f"微信窗口信息: {info}")

        # 4. 截取微信截图
        print("正在截取微信截图...")
        screenshot = self.wechat_gui.screenshot_wechat(
            "assets/images/wechat/current_wechat_screenshot.png"
        )
        if not screenshot:
            print("截图失败")

        # 5. 进入朋友圈
        self.wechat_gui.click_by_image("assets/images/wechat/current_wechat_screenshot.png",
                                       "assets/images/wechat/moment_step_1.png", 0.7, relative=True, rect=self.wechat_gui.wechat_rect)
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
        image_dir = os.path.join(os.path.dirname(__file__), "../../assets/images")
        self.wechat_gui.select_images_from_dialog([
            os.path.abspath(os.path.normpath(os.path.join(image_dir, "wechat/moment_step_3.png"))),
            os.path.abspath(os.path.normpath(os.path.join(image_dir, "wechat/current_screenshot_blank.png"))),
        ])

        # # 13. 点击发送按钮
        # self.wechat_gui.screenshot_moment(
        #     "assets/images/wechat/current_moment_screenshot.png"
        # )
        # self.wechat_gui.click_by_image("assets/images/wechat/current_moment_screenshot.png",
        #                                "assets/images/wechat/moment_step_4.png", 0.7, relative=True, rect=self.wechat_gui.moment_rect)

if (__name__ == "__main__"):
    wechat = WeChat()
    wechat.start()