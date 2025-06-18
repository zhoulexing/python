import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import win32gui
import win32con
import win32process
import psutil
import json
import os
from threading import Thread
import time


class WeChatManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("金舟多聊 - 微信管理器")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')

        # 存储微信窗口信息
        self.wechat_windows = {}
        self.wechat_processes = []

        # 话术数据
        self.scripts_file = "scripts.json"
        self.scripts_data = self.load_scripts()

        self.setup_ui()
        self.start_window_monitor()

    def setup_ui(self):
        # 主框架
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左侧微信管理区域
        left_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # 微信控制按钮
        control_frame = tk.Frame(left_frame, bg='white')
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(control_frame, text="启动新微信", command=self.launch_wechat,
                  bg='#07c160', fg='white', font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=5)

        tk.Button(control_frame, text="刷新窗口", command=self.refresh_windows,
                  bg='#1aad19', fg='white', font=('微软雅黑', 10)).pack(side=tk.LEFT, padx=5)

        # 微信窗口列表
        list_frame = tk.Frame(left_frame, bg='white')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        tk.Label(list_frame, text="微信窗口列表", font=('微软雅黑', 12, 'bold'),
                 bg='white').pack(anchor=tk.W, pady=(0, 10))

        # 创建Treeview显示微信窗口
        self.tree = ttk.Treeview(list_frame, columns=(
            'pid', 'title'), show='tree headings')
        self.tree.heading('#0', text='序号')
        self.tree.heading('pid', text='进程ID')
        self.tree.heading('title', text='窗口标题')

        self.tree.column('#0', width=60)
        self.tree.column('pid', width=80)
        self.tree.column('title', width=200)

        scrollbar = ttk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 右侧话术区域
        right_frame = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_frame.configure(width=300)

        # 话术标题
        tk.Label(right_frame, text="话术列表", font=('微软雅黑', 12, 'bold'),
                 bg='white').pack(pady=10)

        # 话术分类
        category_frame = tk.Frame(right_frame, bg='white')
        category_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(category_frame, text="分类:", bg='white').pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="默认分类")
        self.category_combo = ttk.Combobox(category_frame, textvariable=self.category_var,
                                           values=list(self.scripts_data.keys()))
        self.category_combo.pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.category_combo.bind(
            '<<ComboboxSelected>>', self.on_category_change)

        # 话术列表
        script_list_frame = tk.Frame(right_frame, bg='white')
        script_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.script_listbox = tk.Listbox(script_list_frame, font=('微软雅黑', 9))
        script_scrollbar = ttk.Scrollbar(script_list_frame, orient=tk.VERTICAL,
                                         command=self.script_listbox.yview)
        self.script_listbox.configure(yscrollcommand=script_scrollbar.set)

        self.script_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        script_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.script_listbox.bind('<Double-Button-1>', self.on_script_select)

        # 话术内容显示
        content_frame = tk.Frame(right_frame, bg='white')
        content_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(content_frame, text="话术内容:", bg='white').pack(anchor=tk.W)
        self.content_text = scrolledtext.ScrolledText(content_frame, height=8,
                                                      font=('微软雅黑', 9))
        self.content_text.pack(fill=tk.X, pady=(5, 0))

        # 操作按钮
        button_frame = tk.Frame(right_frame, bg='white')
        button_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(button_frame, text="复制话术", command=self.copy_script,
                  bg='#576b95', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="新增话术", command=self.add_script,
                  bg='#07c160', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="编辑话术", command=self.edit_script,
                  bg='#fa9d3b', fg='white').pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="删除话术", command=self.delete_script,
                  bg='#f56c6c', fg='white').pack(side=tk.LEFT, padx=2)

        # 初始化话术列表
        self.refresh_script_list()

    def launch_wechat(self):
        """启动新的微信实例"""
        try:
            # 微信安装路径，需要根据实际情况修改
            wechat_paths = [
                r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"C:\Program Files\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
                r"D:\Program Files\Tencent\WeChat\WeChat.exe"
            ]

            wechat_path = None
            for path in wechat_paths:
                if os.path.exists(path):
                    wechat_path = path
                    break

            if not wechat_path:
                messagebox.showerror("错误", "未找到微信安装路径，请手动指定")
                return

            # 启动微信
            process = subprocess.Popen([wechat_path])
            self.wechat_processes.append(process)

            messagebox.showinfo("成功", "微信启动中，请稍等...")

            # 延迟刷新窗口列表
            self.root.after(3000, self.refresh_windows)

        except Exception as e:
            messagebox.showerror("错误", f"启动微信失败: {str(e)}")

    def refresh_windows(self):
        """刷新微信窗口列表"""
        self.tree.delete(*self.tree.get_children())
        self.wechat_windows.clear()

        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if "微信" in window_title and window_title != "":
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        windows[hwnd] = {
                            'title': window_title,
                            'pid': pid,
                            'hwnd': hwnd
                        }
                    except:
                        pass

        win32gui.EnumWindows(enum_windows_callback, self.wechat_windows)

        # 更新树形控件
        for i, (hwnd, info) in enumerate(self.wechat_windows.items(), 1):
            self.tree.insert('', 'end', text=str(i),
                             values=(info['pid'], info['title']))

    def start_window_monitor(self):
        """启动窗口监控线程"""
        def monitor():
            while True:
                time.sleep(5)
                self.root.after(0, self.refresh_windows)

        monitor_thread = Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def load_scripts(self):
        """加载话术数据"""
        if os.path.exists(self.scripts_file):
            try:
                with open(self.scripts_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass

        # 默认话术数据
        return {
            "默认分类": [
                {"title": "问候语", "content": "您好！很高兴为您服务，有什么可以帮助您的吗？"},
                {"title": "感谢语", "content": "感谢您的信任和支持！"},
            ],
            "问候语": [
                {"title": "早上好", "content": "早上好！新的一天开始了，祝您工作顺利！"},
                {"title": "下午好", "content": "下午好！希望您今天过得愉快！"},
                {"title": "晚上好", "content": "晚上好！辛苦了一天，注意休息哦！"},
            ]
        }

    def save_scripts(self):
        """保存话术数据"""
        try:
            with open(self.scripts_file, 'w', encoding='utf-8') as f:
                json.dump(self.scripts_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存话术失败: {str(e)}")

    def on_category_change(self, event=None):
        """分类改变事件"""
        self.refresh_script_list()

    def refresh_script_list(self):
        """刷新话术列表"""
        self.script_listbox.delete(0, tk.END)
        category = self.category_var.get()

        if category in self.scripts_data:
            for script in self.scripts_data[category]:
                self.script_listbox.insert(tk.END, script['title'])

    def on_script_select(self, event=None):
        """选择话术事件"""
        selection = self.script_listbox.curselection()
        if selection:
            index = selection[0]
            category = self.category_var.get()
            if category in self.scripts_data and index < len(self.scripts_data[category]):
                script = self.scripts_data[category][index]
                self.content_text.delete(1.0, tk.END)
                self.content_text.insert(1.0, script['content'])

    def copy_script(self):
        """复制话术到剪贴板"""
        content = self.content_text.get(1.0, tk.END).strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            messagebox.showinfo("成功", "话术已复制到剪贴板")
        else:
            messagebox.showwarning("提示", "请先选择一个话术")

    def add_script(self):
        """添加新话术"""
        self.script_dialog("添加话术")

    def edit_script(self):
        """编辑话术"""
        selection = self.script_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个话术")
            return

        index = selection[0]
        category = self.category_var.get()
        script = self.scripts_data[category][index]
        self.script_dialog("编辑话术", script, index)

    def delete_script(self):
        """删除话术"""
        selection = self.script_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择一个话术")
            return

        if messagebox.askyesno("确认", "确定要删除这个话术吗？"):
            index = selection[0]
            category = self.category_var.get()
            del self.scripts_data[category][index]
            self.save_scripts()
            self.refresh_script_list()
            self.content_text.delete(1.0, tk.END)

    def script_dialog(self, title, script=None, index=None):
        """话术编辑对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # 话术标题
        tk.Label(dialog, text="话术标题:").pack(anchor=tk.W, padx=10, pady=(10, 5))
        title_entry = tk.Entry(dialog, font=('微软雅黑', 10))
        title_entry.pack(fill=tk.X, padx=10, pady=(0, 10))

        # 话术内容
        tk.Label(dialog, text="话术内容:").pack(anchor=tk.W, padx=10, pady=(0, 5))
        content_text = scrolledtext.ScrolledText(
            dialog, height=10, font=('微软雅黑', 10))
        content_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # 如果是编辑模式，填入现有内容
        if script:
            title_entry.insert(0, script['title'])
            content_text.insert(1.0, script['content'])

        # 按钮
        button_frame = tk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        def save_script():
            script_title = title_entry.get().strip()
            script_content = content_text.get(1.0, tk.END).strip()

            if not script_title or not script_content:
                messagebox.showwarning("提示", "标题和内容不能为空")
                return

            category = self.category_var.get()
            new_script = {'title': script_title, 'content': script_content}

            if index is not None:  # 编辑模式
                self.scripts_data[category][index] = new_script
            else:  # 添加模式
                if category not in self.scripts_data:
                    self.scripts_data[category] = []
                self.scripts_data[category].append(new_script)

            self.save_scripts()
            self.refresh_script_list()
            dialog.destroy()
            messagebox.showinfo("成功", "话术保存成功")

        tk.Button(button_frame, text="保存", command=save_script,
                  bg='#07c160', fg='white').pack(side=tk.RIGHT, padx=(5, 0))
        tk.Button(button_frame, text="取消", command=dialog.destroy,
                  bg='#f56c6c', fg='white').pack(side=tk.RIGHT)

    def run(self):
        """运行主程序"""
        self.root.mainloop()


if __name__ == "__main__":
    app = WeChatManager()
    app.run()
