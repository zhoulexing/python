import pyautogui
import subprocess
import time
import win32gui
import win32con
from utils.image import ImageUtils
import os
import pyperclip

image_utils = ImageUtils()


class WeChatGui:
    def __init__(self):
        self.wechat_window = None
        self.wechat_rect = None
        self.moment_window = None
        self.moment_rect = None
        self.multi_chat_window = None
        self.multi_chat_rect = None

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
        
    def open_multi_chat(self):
        """启动多聊"""
        try:
            # 尝试通过常见路径启动
            multi_chat_paths = [
                r"C:\Users\zhoulexing\AppData\Roaming\jinzhousoft\JZWeChatTool\JZWeChatTool.exe"
            ]

            for path in multi_chat_paths:
                try:
                    subprocess.Popen(path)
                    print(f"多聊启动成功: {path}")
                    time.sleep(3)  # 等待多聊启动
                    return True
                except FileNotFoundError:
                    continue

            return True

        except Exception as e:
            print(f"启动多聊失败: {e}")
            return False

    def click_by_image(self, image_path, template_image_path, threshold=0.7, relative=True, rect=None):
        """根据图片点击"""
        result = image_utils.image_matcher(
            image_path, template_image_path, threshold)
        if len(result) == 0:
            raise Exception("未找到图片")
        else:
            x = result[0]['x']
            y = result[0]['y']
            width = result[0]['width']
            height = result[0]['height']
            print(f"图片的坐标: ({x}, {y}, {width}, {height})")
            self.click_at_coordinate(
                int(x + width / 2), int(y + height / 2), relative, rect=rect)

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
    
    def find_multi_chat_window(self):
        """查找多聊窗口"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "金舟多聊" in window_title or "金舟多聊子窗体" not in window_title:
                    windows.append((hwnd, window_title))

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        if windows:
            self.multi_chat_window = windows[0][0]  # 取第一个多聊窗口
            self.multi_chat_rect = win32gui.GetWindowRect(self.multi_chat_window)
            print(f"找到多聊窗口: {windows[0][1]}")
            print(f"窗口位置: {self.multi_chat_rect}")
            return True
        else:
            print("未找到多聊窗口")
            return False
        
    def find_wechat_window(self):
        """查找微信窗口"""
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWin
                dowText(hwnd)
                if "微信" in window_title or "WeChat" in window_title:
                    windows.append((hwnd, window_title))

        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)

        if windows:
            self.wechat_window = windows[0][0]  # 取第一个微信窗口
            self.wechat_rect = win32gui.GetWindowRect(self.wechat_window)
            print(f"找到微信窗口: {windows[0][0]}")
            print(f"窗口位置: {self.wechat_rect}")
            return True
        else:
            print("未找到微信窗口")
            return False
        
    def bring_multi_chat_window_to_front(self):
        """将多聊窗口置于前台"""
        if self.multi_chat_window:
            try:
                win32gui.ShowWindow(self.multi_chat_window, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(self.multi_chat_window)
                time.sleep(0.5)
                return True
            except Exception as e:
                print(f"置于前台失败: {e}")
                return False
        else:
            print("未找到多聊窗口，无法置于前台")
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
            return self.screenshot_by_rect(save_path, self.wechat_rect)
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def screenshot_by_rect(self, save_path, rect):
        """截取指定区域的截图"""
        if not rect:
            print("未指定窗口 rect")
            return None
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top
        screenshot = pyautogui.screenshot(
            region=(left, top, width, height))
        screenshot.save(save_path)
        print(f"截图已保存: {save_path}")
        return screenshot

    def screenshot_moment(self, save_path):
        """截取朋友圈截图"""
        if not self.moment_window or not self.moment_rect:
            print("请先找到朋友圈窗口")
            return None

        try:
            # 将朋友圈窗口置于前台
            self.bring_moment_window_to_front()
            time.sleep(2)

            return self.screenshot_by_rect(save_path, self.moment_rect)
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def click_at_coordinate(self, x, y, relative=True, rect=None):
        """
        在指定坐标点击

        Args:
            x (int): X坐标
            y (int): Y坐标
            relative (bool): True表示相对于窗口的坐标，False表示屏幕绝对坐标
            rect (tuple or None): 指定窗口的 (left, top, right, bottom)，relative=True 时用来计算绝对坐标，未传则默认用微信主窗口
        """
        try:
            if relative:
                # 使用传入的 rect 或默认的 self.wechat_rect
                use_rect = rect if rect is not None else self.wechat_rect
                if not use_rect:
                    print("未指定窗口 rect，且未找到默认窗口 rect")
                    return False
                left, top, right, bottom = use_rect
                abs_x = left + x
                abs_y = top + y

                # 检查坐标是否在窗口范围内
                if abs_x < left or abs_x > right or abs_y < top or abs_y > bottom:
                    print(f"坐标({x}, {y})超出窗口范围")
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
        
    def get_multi_chat_info(self):
        """获取多聊窗口信息"""
        if self.multi_chat_window and self.multi_chat_rect:
            left, top, right, bottom = self.multi_chat_rect
            return {
                "window_handle": self.multi_chat_window,
                "position": (left, top),
                "size": (right - left, bottom - top),
                "rect": self.multi_chat_rect
            }
        return None

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

    def select_images_from_dialog(self, image_folder, image_names):
        """
        在文件选择对话框中选择多张图片（调用方传入图片目录和文件名列表）
        Args:
            image_folder (str): 图片所在文件夹路径
            image_names (list): 图片文件名列表（不含路径）
        """
        try:
            if not image_names:
                print("未提供图片文件名")
                return False
            if not os.path.isdir(image_folder):
                print(f"图片文件夹不存在: {image_folder}")
                return False

            # 检查所有图片是否存在
            # for name in image_names:
            #     full_path = os.path.join(image_folder, name)
            #     if not os.path.exists(full_path):
            #         print(f"图片文件不存在: {full_path}")
            #         return False

            filenames_str = ' '.join(f'"{name}"' for name in image_names)

            # 1. 进入目标文件夹
            pyperclip.copy(image_folder)
            pyautogui.hotkey('ctrl', 'l')  # 激活地址栏
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')  # 全选
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')  # 粘贴文件夹路径
            time.sleep(0.5)
            pyautogui.press('enter')
            time.sleep(1)

            # 2. 粘贴所有文件名到文件名输入框
            pyperclip.copy(filenames_str)
            pyautogui.hotkey('alt', 'n')  # 激活文件名输入框
            pyautogui.hotkey('ctrl', 'a')  # 全选
            time.sleep(0.2)
            pyautogui.press('delete')
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'v')  # 粘贴文件名
            time.sleep(0.5)
            pyautogui.press('enter')  # 确认选择
            print(f"已选择 {len(image_names)} 张图片")
            time.sleep(2)  # 等待图片加载
            return True
        except Exception as e:
            print(f"选择图片失败: {e}")
            return False