import pyautogui
import subprocess
import time
import win32gui
import win32con
from utils.image import ImageUtils

image_utils = ImageUtils()


class WeChatGui:
    def __init__(self):
        self.wechat_window = None
        self.wechat_rect = None
        self.moment_window = None
        self.moment_rect = None

    def open_wechat(self):
        """打开微信应用"""
        try:
            # 尝试通过常见路径启动微信
            wechat_paths = [
                r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files (x86)\Tencent\Weixin\Weixin.exe",
                r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files\Tencent\Weixin\Weixin.exe",
            ]

            for path in wechat_paths:
                try:
                    subprocess.Popen(path)
                    print(f"微信启动成功: {path}")
                    time.sleep(3)  # 等待微信启动
                    return True
                except FileNotFoundError:
                    continue

            # 如果路径都不对，尝试通过开始菜单启动
            subprocess.run(['start', 'wechat'], shell=True)
            time.sleep(3)
            return True

        except Exception as e:
            print(f"启动微信失败: {e}")
            return False
    
    def click_moment_popup_button(self):
        """点击朋友圈弹窗按钮"""
        result = image_utils.image_matcher(
            'assets/images/wechat/current_moment_screenshot.png', 'assets/images/wechat/moment_step_2.png')
        if len(result) == 0:
            raise Exception("未找到朋友圈弹窗按钮")
        else:
            x = result[0]['x']
            y = result[0]['y']
            width = result[0]['width']
            height = result[0]['height']
            print(f"朋友圈弹窗按钮的坐标: ({x}, {y}, {width}, {height})")
            self.click_at_coordinate(int(x + width / 2), int(y + height / 2), relative=True)

    def entry_moment(self):
        """进入朋友圈"""
        result = image_utils.image_matcher(
            'assets/images/wechat/current_wechat_screenshot.png', 'assets/images/wechat/moment_step_1.png')
        if len(result) == 0:
            raise Exception("未找到朋友圈的图标")
        else:
            x = result[0]['x']
            y = result[0]['y']
            width = result[0]['width']
            height = result[0]['height']
            print(f"朋友圈的坐标: ({x}, {y}, {width}, {height})")

            # 5. 在指定坐标点击（相对于微信窗口的坐标）
            print("3秒后将在坐标")
            time.sleep(3)
            wechat.click_at_coordinate(
                int(x + width / 2), int(y + height / 2), relative=True)

    def find_moment_window(self):
        """查找朋友圈窗口"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "朋友圈" in window_title or "Moments" in window_title:
                    windows.append((hwnd, window_title))

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        if windows:
            self.moment_window = windows[0][0]  # 取第一个朋友圈窗口
            self.moment_rect = win32gui.GetWindowRect(self.moment_window)
            print(f"找到朋友圈窗口: {windows[0][1]}")
            print(f"窗口位置: {self.moment_rect}")
            return True
        else:
            print("未找到朋友圈窗口")
            return False

    def bring_moment_window_to_front(self):
        """将朋友圈窗口置于前台"""
        if self.moment_window:
            try:
                win32gui.ShowWindow(self.moment_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.moment_window)
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"置于前台失败: {e}")
                return False
        else:
            print("未找到朋友圈窗口，无法置于前台")
            return False

    def find_wechat_window(self):
        """查找微信窗口"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "微信" in window_title or "WeChat" in window_title:
                    windows.append((hwnd, window_title))

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        if windows:
            self.wechat_window = windows[0][0]  # 取第一个微信窗口
            self.wechat_rect = win32gui.GetWindowRect(self.wechat_window)
            print(f"找到微信窗口: {windows[0][1]}")
            print(f"窗口位置: {self.wechat_rect}")
            return True
        else:
            print("未找到微信窗口")
            return False

    def bring_wechat_to_front(self):
        """将微信窗口置于前台"""
        if self.wechat_window:
            try:
                # 恢复窗口（如果是最小化状态）
                win32gui.ShowWindow(self.wechat_window, win32con.SW_RESTORE)
                # 将窗口置于前台
                win32gui.SetForegroundWindow(self.wechat_window)
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"置于前台失败: {e}")
                return False
        return False

    def screenshot_wechat(self, save_path):
        """截取微信窗口截图"""
        if not self.wechat_window or not self.wechat_rect:
            print("请先找到微信窗口")
            return None

        try:
            # 将微信窗口置于前台
            self.bring_wechat_to_front()

            # 获取窗口位置和大小
            left, top, right, bottom = self.wechat_rect
            width = right - left
            height = bottom - top

            # 截取指定区域的截图
            screenshot = pyautogui.screenshot(
                region=(left, top, width, height))

            # 保存截图
            screenshot.save(save_path)
            print(f"截图已保存: {save_path}")

            return screenshot

        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def screenshot_moment(self, save_path):
        """截取朋友圈截图"""
        if not self.moment_window or not self.moment_rect:
            print("请先找到朋友圈窗口")
            return None

        try:
            # 将朋友圈窗口置于前台
            self.bring_moment_window_to_front()
            time.sleep(2)

            # 获取窗口位置和大小
            left, top, right, bottom = self.moment_rect
            width = right - left
            height = bottom - top

            # 截取指定区域的截图
            screenshot = pyautogui.screenshot(
                region=(left, top, width, height))

            # 保存截图
            screenshot.save(save_path)
            print(f"截图已保存: {save_path}")
            return screenshot
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def click_at_coordinate(self, x, y, relative=True):
        """
        在指定坐标点击

        Args:
            x (int): X坐标
            y (int): Y坐标
            relative (bool): True表示相对于微信窗口的坐标，False表示屏幕绝对坐标
        """
        if not self.wechat_window or not self.wechat_rect:
            print("请先找到微信窗口")
            return False

        try:
            # 将微信窗口置于前台
            self.bring_wechat_to_front()

            if relative:
                # 相对坐标转换为绝对坐标
                left, top, right, bottom = self.wechat_rect
                abs_x = left + x
                abs_y = top + y

                # 检查坐标是否在窗口范围内
                if abs_x < left or abs_x > right or abs_y < top or abs_y > bottom:
                    print(f"坐标({x}, {y})超出微信窗口范围")
                    return False
            else:
                abs_x, abs_y = x, y

            # 执行点击
            pyautogui.click(abs_x, abs_y)
            print(f"已点击坐标: ({abs_x}, {abs_y})")
            return True

        except Exception as e:
            print(f"点击失败: {e}")
            return False

    def get_wechat_info(self):
        """获取微信窗口信息"""
        if self.wechat_window and self.wechat_rect:
            left, top, right, bottom = self.wechat_rect
            return {
                "window_handle": self.wechat_window,
                "position": (left, top),
                "size": (right - left, bottom - top),
                "rect": self.wechat_rect
            }
        return None

    def start(self):
        # 1. 打开微信
        print("正在打开微信...")
        if not self.open_wechat():
            print("打开微信失败")
            return

        # 2. 查找微信窗口
        print("正在查找微信窗口...")
        if not self.find_wechat_window():
            print("未找到微信窗口，请确保微信已启动")
            return

        # 3. 显示微信窗口信息
        info = self.get_wechat_info()
        if info:
            print(f"微信窗口信息: {info}")
            return

        # 4. 截取微信截图
        print("正在截取微信截图...")
        screenshot = self.screenshot_wechat(
            "assets/images/wechat/current_wechat_screenshot.png"
        )
        if screenshot:
            print("截图失败")

        # 5. 进入朋友圈
        self.entry_moment()
        # 6. 查找朋友圈窗口
        self.find_moment_window()
        # 7. 将朋友圈窗口置于前台，并等待加载
        self.bring_moment_window_to_front()
        time.sleep(2)
        # 8. 截取朋友圈截图
        self.screenshot_moment(
            "assets/images/wechat/current_moment_screenshot.png"
        )
        # 9. 点击发朋友圈的弹窗按钮
        self.click_moment_popup_button()


if __name__ == "__main__":
    wechat = WeChatGui()
    wechat.start()
