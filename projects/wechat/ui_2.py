import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
from pathlib import Path
import threading
from _utils import *


class WeChatMultiLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("微信多开启动器")
        self.root.geometry("500x400")

        # 存储微信路径
        self.wechat_exe_path = None
        self.wechat_dll_path = None

        # 记录已创建的实例
        self.created_instances = set()

        self.setup_ui()
        self.auto_detect_wechat()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="微信多开启动器",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 微信路径设置
        path_frame = ttk.LabelFrame(main_frame, text="微信路径设置", padding="10")
        path_frame.grid(row=1, column=0, columnspan=3,
                        sticky=(tk.W, tk.E), pady=(0, 20))

        # Weixin.exe 路径
        ttk.Label(path_frame, text="Weixin.exe:").grid(
            row=0, column=0, sticky=tk.W)
        self.exe_path_var = tk.StringVar()
        self.exe_path_entry = ttk.Entry(
            path_frame, textvariable=self.exe_path_var, width=40)
        self.exe_path_entry.grid(row=0, column=1, padx=(10, 5))
        ttk.Button(path_frame, text="浏览",
                   command=self.browse_exe).grid(row=0, column=2)

        # Weixin.dll 路径
        ttk.Label(path_frame, text="Weixin.dll:").grid(
            row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.dll_path_var = tk.StringVar()
        self.dll_path_entry = ttk.Entry(
            path_frame, textvariable=self.dll_path_var, width=40)
        self.dll_path_entry.grid(row=1, column=1, padx=(10, 5), pady=(10, 0))
        ttk.Button(path_frame, text="浏览",
                   command=self.browse_dll).grid(row=1, column=2, pady=(10, 0))

        # 快速启动区域
        launch_frame = ttk.LabelFrame(main_frame, text="快速启动", padding="10")
        launch_frame.grid(row=2, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=(0, 20))

        # 创建10个启动按钮（0-9）
        self.launch_buttons = {}
        for i in range(10):
            row = i // 5
            col = i % 5
            btn = ttk.Button(launch_frame, text=f"微信 {i}", width=12,
                             command=lambda n=i: self.launch_wechat(n))
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.launch_buttons[i] = btn

        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3,
                          sticky=(tk.W, tk.E, tk.N, tk.S))

        # 状态文本框
        self.status_text = tk.Text(status_frame, height=8, width=60)
        scrollbar = ttk.Scrollbar(
            status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)

        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 控制按钮
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))

        ttk.Button(control_frame, text="清空日志",
                   command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="关闭所有微信",
                   command=self.close_all_wechat).pack(side=tk.LEFT)

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        self.log("微信多开启动器已启动")

    def auto_detect_wechat(self):
        """自动检测微信路径"""
        try:
            # 常见微信安装路径
            common_paths = [
                r"C:\Program Files\Tencent\WeChat\Weixin.exe",
                r"C:\Program Files (x86)\Tencent\WeChat\Weixin.exe",
                r"D:\Program Files\Tencent\WeChat\Weixin.exe",
                r"D:\Program Files (x86)\Tencent\WeChat\Weixin.exe"
            ]

            for path in common_paths:
                if os.path.exists(path):
                    exe_path = Path(path)
                    dll_path = exe_path.parent / "Weixin.dll"

                    if dll_path.exists():
                        self.exe_path_var.set(str(exe_path))
                        self.dll_path_var.set(str(dll_path))
                        self.wechat_exe_path = exe_path
                        self.wechat_dll_path = dll_path
                        self.log(f"自动检测到微信路径: {exe_path.parent}")
                        return

            self.log("未能自动检测到微信路径，请手动选择")

        except Exception as e:
            self.log(f"自动检测失败: {str(e)}")

    def browse_exe(self):
        """浏览选择 Weixin.exe"""
        filename = filedialog.askopenfilename(
            title="选择 Weixin.exe",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.exe_path_var.set(filename)
            self.wechat_exe_path = Path(filename)

            # 尝试自动找到对应的 dll
            dll_path = self.wechat_exe_path.parent / "Weixin.dll"
            if dll_path.exists():
                self.dll_path_var.set(str(dll_path))
                self.wechat_dll_path = dll_path

    def browse_dll(self):
        """浏览选择 Weixin.dll"""
        filename = filedialog.askopenfilename(
            title="选择 Weixin.dll",
            filetypes=[("动态链接库", "*.dll"), ("所有文件", "*.*")]
        )
        if filename:
            self.dll_path_var.set(filename)
            self.wechat_dll_path = Path(filename)

    def log(self, message):
        """添加日志信息"""
        self.status_text.insert(
            tk.END, f"[{self.get_current_time()}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()

    def get_current_time(self):
        """获取当前时间字符串"""
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")

    def clear_log(self):
        """清空日志"""
        self.status_text.delete(1.0, tk.END)

    def create_wechat_instance(self, n):
        """创建微信实例（基于原代码逻辑）"""
        try:
            if not self.wechat_exe_path or not self.wechat_dll_path:
                raise Exception("请先设置微信路径")

            if not self.wechat_exe_path.exists():
                raise Exception("Weixin.exe 文件不存在")

            if not self.wechat_dll_path.exists():
                raise Exception("Weixin.dll 文件不存在")

            # 检查是否已经创建过
            new_exe = self.wechat_exe_path.with_name(f"Weixin{n}.exe")
            new_dll = self.wechat_dll_path.with_name(f"Weixin.dl{n}")

            if new_exe.exists() and new_dll.exists():
                self.log(f"微信实例 {n} 已存在，跳过创建")
                return True

            self.log(f"正在创建微信实例 {n}...")

            # 处理 EXE 文件
            self.log(f"处理 Weixin{n}.exe...")
            exe_data = load(self.wechat_exe_path)
            EXE_PATTERN = "\x00".join("Weixin.dll")
            EXE_REPLACE = "\x00".join(f"Weixin.dl{n}")
            exe_data = replace(exe_data, EXE_PATTERN, EXE_REPLACE)
            save(new_exe, exe_data)

            # 处理 DLL 文件
            self.log(f"处理 Weixin.dl{n}...")
            dll_data = load(self.wechat_dll_path)

            # 重定向配置文件
            COEXIST_CONFIG_PATTERN = """
            48 B8 67 6C 6F 62 61 6C 5F 63
            48 89 05 ?? ?? ?? ??
            C7 05 ?? ?? ?? ?? 6F 6E 66 69
            66 C7 05 ?? ?? ?? ?? 67 00
            """
            COEXIST_CONFIG_REPLACE = f"""
            ...
            C7 05 ?? ?? ?? ?? 6F 6E 66 {ord(str(n)):02X}
            66 C7 05 ?? ?? ?? ?? 67 00
            """
            dll_data = wildcard_replace(
                dll_data, COEXIST_CONFIG_PATTERN, COEXIST_CONFIG_REPLACE)

            # 重定向自动登录文件
            AUTOLOGIN_PATTERN = "host-redirect.xml"
            AUTOLOGIN_REPLACE = f"host-redirect.xm{n}"
            dll_data = replace(dll_data, AUTOLOGIN_PATTERN, AUTOLOGIN_REPLACE)

            # 修改互斥锁
            MUTEX_PATTERN = "\0".join(
                "XWeChat_App_Instance_Identity_Mutex_Name")
            MUTEX_REPLACE = "\0".join(
                f"XWeChat_App_Instance_Identity_Mutex_Nam{n}")
            dll_data = replace(dll_data, MUTEX_PATTERN, MUTEX_REPLACE)

            save(new_dll, dll_data)

            self.created_instances.add(n)
            self.log(f"微信实例 {n} 创建成功")
            return True

        except Exception as e:
            self.log(f"创建微信实例 {n} 失败: {str(e)}")
            return False

    def launch_wechat(self, n):
        """启动微信实例"""
        def launch_thread():
            try:
                # 先创建实例（如果不存在）
                if n not in self.created_instances:
                    if not self.create_wechat_instance(n):
                        return

                # 启动微信
                exe_path = self.wechat_exe_path.with_name(f"Weixin{n}.exe")
                if not exe_path.exists():
                    self.log(f"微信实例 {n} 不存在，正在创建...")
                    if not self.create_wechat_instance(n):
                        return

                self.log(f"正在启动微信实例 {n}...")

                # 启动进程
                process = subprocess.Popen([str(exe_path)],
                                           cwd=str(exe_path.parent))

                self.log(f"微信实例 {n} 启动成功 (PID: {process.pid})")

            except Exception as e:
                self.log(f"启动微信实例 {n} 失败: {str(e)}")

        # 在新线程中执行，避免阻塞UI
        threading.Thread(target=launch_thread, daemon=True).start()

    def close_all_wechat(self):
        """关闭所有微信进程"""
        try:
            import psutil
            closed_count = 0

            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if proc.info['name'] and 'Weixin' in proc.info['name']:
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if closed_count > 0:
                self.log(f"已关闭 {closed_count} 个微信进程")
            else:
                self.log("没有找到运行中的微信进程")

        except ImportError:
            self.log("需要安装 psutil 库才能使用此功能: pip install psutil")
        except Exception as e:
            self.log(f"关闭微信进程失败: {str(e)}")


def main():
    root = tk.Tk()
    app = WeChatMultiLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
