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
    
    def open_wechat(self):
        """打开微信应用"""
        try:
            # 尝试通过常见路径启动微信
            wechat_paths = [
                r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files\Tencent\WeChat\WeChat.exe"
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
    
    def screenshot_wechat(self, save_path="assets/images/wechat/current_screenshot.png"):
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
            screenshot = pyautogui.screenshot(region=(left, top, width, height))
            
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

# 使用示例
def main():
    # 创建微信控制器
    wechat = WeChatGui()
    
    # 1. 打开微信
    print("正在打开微信...")
    if not wechat.open_wechat():
        print("打开微信失败")
        return
    
    # 2. 查找微信窗口
    print("正在查找微信窗口...")
    if not wechat.find_wechat_window():
        print("未找到微信窗口，请确保微信已启动")
        return
    
    # 3. 显示微信窗口信息
    info = wechat.get_wechat_info()
    if info:
        print(f"微信窗口信息: {info}")
    
    # 4. 截取微信截图
    print("正在截取微信截图...")
    screenshot = wechat.screenshot_wechat("assets/images/wechat/current_screenshot.png")
    if screenshot:
        print("截图成功")
    
    # 5. 匹配图片, 获取坐标
    result = image_utils.image_matcher(
        'assets/images/wechat/current_screenshot.png', 'assets/images/wechat/wechat_moment_icon.png')
    if len(result) == 0:
        raise Exception("未找到朋友圈的图标")
    print(result)
    
    x = result[0]['x']
    y = result[0]['y']
    width = result[0]['width']
    height = result[0]['height']
    print(f"朋友圈的坐标: ({x}, {y}, {width}, {height})")
    
    # 5. 在指定坐标点击（相对于微信窗口的坐标）
    print("3秒后将在坐标")
    time.sleep(3)
    wechat.click_at_coordinate(int(x + width / 2), int(y + height / 2), relative=True)
    # 新增：等待朋友圈窗口加载
    time.sleep(2)
    # 朋友圈区域大致在主窗口的右侧，假设主窗口左上角为(left, top)
    left, top, right, bottom = wechat.wechat_rect
    # 朋友圈内容区域大致偏右偏上，具体偏移可根据实际调整
    feed_x = left + (right - left) * 0.7
    feed_y = top + 120  # 距离顶部约120像素，避开顶部栏
    # 移动鼠标到朋友圈内容区域
    pyautogui.moveTo(feed_x, feed_y)
    # 向上滚动多次，确保回到顶部
    for _ in range(5):
        pyautogui.scroll(500)
        time.sleep(0.2)
    # 再次点击顶部区域，进入最新朋友圈
    pyautogui.click(feed_x, feed_y)

if __name__ == "__main__":
    main()
