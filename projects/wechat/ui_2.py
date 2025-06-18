import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
from pathlib import Path
import threading
import winreg
import tempfile
import json


class WeChatMultiLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("微信多开启动器 v3.0")
        self.root.geometry("600x500")

        # 存储微信路径
        self.wechat_exe_path = None

        # 配置文件路径
        self.config_file = Path.home() / "Documents" / "wechat_multi_config.json"

        # 运行中的进程
        self.running_processes = {}

        self.setup_ui()
        self.load_config()
        self.auto_detect_wechat()

    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 标题
        title_label = ttk.Label(main_frame, text="微信多开启动器 v3.0",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 微信路径设置
        path_frame = ttk.LabelFrame(main_frame, text="微信路径设置", padding="10")
        path_frame.grid(row=1, column=0, columnspan=3,
                        sticky=(tk.W, tk.E), pady=(0, 20))

        # Weixin.exe 路径
        ttk.Label(path_frame, text="微信路径:").grid(row=0, column=0, sticky=tk.W)
        self.exe_path_var = tk.StringVar()
        self.exe_path_entry = ttk.Entry(
            path_frame, textvariable=self.exe_path_var, width=60)
        self.exe_path_entry.grid(row=0, column=1, padx=(10, 5))
        ttk.Button(path_frame, text="浏览",
                   command=self.browse_exe).grid(row=0, column=2)

        # 多开方式选择
        method_frame = ttk.LabelFrame(main_frame, text="多开方式", padding="10")
        method_frame.grid(row=2, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=(0, 20))

        self.method_var = tk.StringVar(value="sandbox")
        ttk.Radiobutton(method_frame, text="沙盒模式（推荐）",
                        variable=self.method_var, value="sandbox").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(method_frame, text="注册表模式",
                        variable=self.method_var, value="registry").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(method_frame, text="命令行模式",
                        variable=self.method_var, value="cmdline").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))

        # 快速启动区域
        launch_frame = ttk.LabelFrame(main_frame, text="快速启动", padding="10")
        launch_frame.grid(row=3, column=0, columnspan=3,
                          sticky=(tk.W, tk.E), pady=(0, 20))

        # 创建10个启动按钮
        self.launch_buttons = {}
        self.status_labels = {}

        for i in range(10):
            row = i // 5
            col = i % 5

            # 按钮框架
            btn_frame = ttk.Frame(launch_frame)
            btn_frame.grid(row=row*2, column=col, padx=5, pady=5)

            # 启动按钮
            btn = ttk.Button(btn_frame, text=f"微信 {i}", width=12,
                             command=lambda n=i: self.launch_wechat(n))
            btn.pack()
            self.launch_buttons[i] = btn

            # 状态标签
            status_label = ttk.Label(btn_frame, text="未运行", foreground="gray")
            status_label.pack()
            self.status_labels[i] = status_label

        # 控制按钮
        control_frame = ttk.Frame(launch_frame)
        control_frame.grid(row=2, column=0, columnspan=5, pady=(10, 0))

        ttk.Button(control_frame, text="关闭所有微信",
                   command=self.close_all_wechat).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="刷新状态",
                   command=self.refresh_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="清理缓存",
                   command=self.clean_cache).pack(side=tk.LEFT)

        # 状态显示
        status_frame = ttk.LabelFrame(main_frame, text="状态信息", padding="10")
        status_frame.grid(row=4, column=0, columnspan=3,
                          sticky=(tk.W, tk.E, tk.N, tk.S))

        # 状态文本框
        self.status_text = tk.Text(status_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(
            status_frame, orient="vertical", command=self.status_text.yview)
        self.status_text.configure(yscrollcommand=scrollbar.set)

        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        # 配置网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)

        self.log("微信多开启动器已启动")

        # 启动状态刷新定时器
        self.refresh_status()
        self.root.after(5000, self.auto_refresh_status)

    def auto_detect_wechat(self):
        """自动检测微信路径"""
        try:
            # 从注册表获取
            wechat_path = self.get_wechat_path_from_registry()
            if wechat_path:
                exe_path = Path(wechat_path) / "WeChat.exe"
                if not exe_path.exists():
                    exe_path = Path(wechat_path) / "Weixin.exe"

                if exe_path.exists():
                    self.exe_path_var.set(str(exe_path))
                    self.wechat_exe_path = exe_path
                    self.log(f"自动检测到微信路径: {exe_path}")
                    self.save_config()
                    return

            # 常见路径检测
            common_paths = [
                r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files\Tencent\WeChat\Weixin.exe",
                r"C:\Program Files (x86)\Tencent\WeChat\Weixin.exe",
                r"D:\Program Files\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
            ]

            for path in common_paths:
                if os.path.exists(path):
                    self.exe_path_var.set(path)
                    self.wechat_exe_path = Path(path)
                    self.log(f"自动检测到微信路径: {path}")
                    self.save_config()
                    return

            self.log("未能自动检测到微信路径，请手动选择")

        except Exception as e:
            self.log(f"自动检测失败: {str(e)}")

    def get_wechat_path_from_registry(self):
        """从注册表获取微信安装路径"""
        try:
            registry_paths = [
                (winreg.HKEY_CURRENT_USER, r"Software\Tencent\WeChat"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Tencent\WeChat"),
                (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Tencent\WeChat"),
                (winreg.HKEY_CURRENT_USER,
                 r"Software\Microsoft\Windows\CurrentVersion\Uninstall\WeChat"),
                (winreg.HKEY_LOCAL_MACHINE,
                 r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\WeChat"),
            ]

            for hkey, subkey in registry_paths:
                try:
                    with winreg.OpenKey(hkey, subkey) as key:
                        try:
                            install_path, _ = winreg.QueryValueEx(
                                key, "InstallPath")
                        except FileNotFoundError:
                            try:
                                install_path, _ = winreg.QueryValueEx(
                                    key, "InstallLocation")
                            except FileNotFoundError:
                                install_path, _ = winreg.QueryValueEx(
                                    key, "DisplayIcon")
                                install_path = str(Path(install_path).parent)

                        if install_path and os.path.exists(install_path):
                            return install_path
                except (FileNotFoundError, OSError):
                    continue

            return None
        except Exception:
            return None

    def launch_wechat(self, n):
        """启动微信实例"""
        def launch_thread():
            try:
                if not self.wechat_exe_path or not self.wechat_exe_path.exists():
                    self.log("请先设置正确的微信路径")
                    return

                # 检查是否已经在运行
                if n in self.running_processes:
                    if self.running_processes[n].poll() is None:
                        self.log(f"微信实例 {n} 已在运行")
                        return
                    else:
                        del self.running_processes[n]

                self.log(f"正在启动微信实例 {n}...")

                method = self.method_var.get()

                if method == "sandbox":
                    process = self.launch_with_sandbox(n)
                elif method == "registry":
                    process = self.launch_with_registry(n)
                else:
                    process = self.launch_with_cmdline(n)

                if process:
                    self.running_processes[n] = process
                    self.log(f"微信实例 {n} 启动成功 (PID: {process.pid})")
                    self.update_button_status(n, "运行中", "green")
                else:
                    self.log(f"微信实例 {n} 启动失败")

            except Exception as e:
                self.log(f"启动微信实例 {n} 失败: {str(e)}")

        threading.Thread(target=launch_thread, daemon=True).start()

    def launch_with_sandbox(self, n):
        """使用沙盒模式启动（推荐方式）"""
        try:
            # 创建临时目录作为沙盒
            sandbox_dir = Path(tempfile.gettempdir()) / f"WeChat_Sandbox_{n}"
            sandbox_dir.mkdir(exist_ok=True)

            # 设置环境变量
            env = os.environ.copy()
            env['APPDATA'] = str(sandbox_dir / "AppData")
            env['LOCALAPPDATA'] = str(sandbox_dir / "LocalAppData")
            env['TEMP'] = str(sandbox_dir / "Temp")
            env['TMP'] = str(sandbox_dir / "Temp")
            env['USERPROFILE'] = str(sandbox_dir / "Profile")

            # 创建必要的目录
            for dir_name in ['AppData', 'LocalAppData', 'Temp', 'Profile']:
                (sandbox_dir / dir_name).mkdir(exist_ok=True)

            # 启动微信
            process = subprocess.Popen(
                [str(self.wechat_exe_path)],
                env=env,
                cwd=str(self.wechat_exe_path.parent)
            )

            return process

        except Exception as e:
            self.log(f"沙盒模式启动失败: {str(e)}")
            return None

    def launch_with_registry(self, n):
        """使用注册表模式启动"""
        try:
            # 创建临时注册表项
            reg_key = f"Software\\Tencent\\WeChat_{n}"

            # 启动微信并传递实例标识
            process = subprocess.Popen(
                [str(self.wechat_exe_path), f"--multi-instance={n}"],
                cwd=str(self.wechat_exe_path.parent)
            )

            return process

        except Exception as e:
            self.log(f"注册表模式启动失败: {str(e)}")
            return None

    def launch_with_cmdline(self, n):
        """使用命令行模式启动"""
        try:
            # 使用不同的命令行参数
            args = [
                str(self.wechat_exe_path),
                f"--user-data-dir={Path.home() / 'Documents' / f'WeChat_User_{n}'}",
                f"--instance-id={n}"
            ]

            process = subprocess.Popen(
                args,
                cwd=str(self.wechat_exe_path.parent)
            )

            return process

        except Exception as e:
            self.log(f"命令行模式启动失败: {str(e)}")
            return None

    def close_all_wechat(self):
        """关闭所有微信进程"""
        try:
            import psutil
            closed_count = 0

            # 关闭记录的进程
            for n, process in list(self.running_processes.items()):
                try:
                    if process.poll() is None:
                        process.terminate()
                        closed_count += 1
                        self.update_button_status(n, "未运行", "gray")
                except:
                    pass

            self.running_processes.clear()

            # 关闭所有微信相关进程
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'] and any(name in proc.info['name'].lower() for name in ['wechat', 'weixin']):
                        proc.terminate()
                        closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            if closed_count > 0:
                self.log(f"已关闭 {closed_count} 个微信进程")
                import time
                time.sleep(1)
                self.refresh_status()
            else:
                self.log("没有找到运行中的微信进程")

        except ImportError:
            self.log("需要安装 psutil 库: pip install psutil")
            # 尝试使用 taskkill 命令
            try:
                subprocess.run(['taskkill', '/f', '/im', 'WeChat.exe'],
                               capture_output=True, check=False)
                subprocess.run(['taskkill', '/f', '/im', 'Weixin.exe'],
                               capture_output=True, check=False)
                self.log("已尝试关闭微信进程")
                self.running_processes.clear()
                self.refresh_status()
            except:
                pass
        except Exception as e:
            self.log(f"关闭微信进程失败: {str(e)}")

    def refresh_status(self):
        """刷新运行状态"""
        try:
            # 检查记录的进程状态
            for n in list(self.running_processes.keys()):
                process = self.running_processes[n]
                if process.poll() is not None:
                    # 进程已结束
                    del self.running_processes[n]
                    self.update_button_status(n, "未运行", "gray")
                else:
                    self.update_button_status(n, "运行中", "green")

            # 检查未记录的进程
            for i in range(10):
                if i not in self.running_processes:
                    self.update_button_status(i, "未运行", "gray")

        except Exception as e:
            self.log(f"刷新状态失败: {str(e)}")

    def auto_refresh_status(self):
        """自动刷新状态"""
        self.refresh_status()
        self.root.after(5000, self.auto_refresh_status)

    def update_button_status(self, n, status, color):
        """更新按钮状态"""
        if n in self.status_labels:
            self.status_labels[n].config(text=status, foreground=color)

    def clean_cache(self):
        """清理缓存"""
        try:
            # 清理沙盒目录
            temp_dir = Path(tempfile.gettempdir())
            for i in range(10):
                sandbox_dir = temp_dir / f"WeChat_Sandbox_{i}"
                if sandbox_dir.exists():
                    import shutil
                    shutil.rmtree(sandbox_dir, ignore_errors=True)

            self.log("缓存清理完成")

        except Exception as e:
            self.log(f"清理缓存失败: {str(e)}")

    def browse_exe(self):
        """浏览选择微信程序"""
        filename = filedialog.askopenfilename(
            title="选择微信程序",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.exe_path_var.set(filename)
            self.wechat_exe_path = Path(filename)
            self.save_config()
            self.log(f"已设置微信路径: {filename}")

    def load_config(self):
        """加载配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    if 'wechat_path' in config:
                        self.exe_path_var.set(config['wechat_path'])
                        self.wechat_exe_path = Path(config['wechat_path'])
        except Exception as e:
            self.log(f"加载配置失败: {str(e)}")

    def save_config(self):
        """保存配置"""
        try:
            config = {
                'wechat_path': str(self.wechat_exe_path) if self.wechat_exe_path else ""
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"保存配置失败: {str(e)}")

    def log(self, message):
        """添加日志信息"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()


def main():
    root = tk.Tk()
    app = WeChatMultiLauncher(root)
    root.mainloop()


if __name__ == "__main__":
    main()
