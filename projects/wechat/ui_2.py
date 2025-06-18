import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import psutil
import threading
import time
from pathlib import Path

class WeChatMultiOpener:
    def __init__(self):
        self.root = tk.Tk()
        self.wechat_processes = []
        self.wechat_path = ""
        self.setup_ui()
        self.find_wechat_path()
        self.start_monitor_thread()

    def setup_ui(self):
        """设置用户界面"""
        self.root.title("微信多开工具")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="微信路径: 检测中...", foreground="blue")
        self.status_label.grid(row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 添加微信按钮
        self.add_button = ttk.Button(button_frame, text="添加新微信窗口", command=self.add_wechat)
        self.add_button.grid(row=0, column=0, padx=(0, 5))
        
        # 关闭所有按钮
        self.close_all_button = ttk.Button(button_frame, text="关闭所有微信", command=self.close_all_wechat)
        self.close_all_button.grid(row=0, column=1, padx=5)
        
        # 刷新按钮
        self.refresh_button = ttk.Button(button_frame, text="刷新列表", command=self.refresh_process_list)
        self.refresh_button.grid(row=0, column=2, padx=(5, 0))
        
        # 选择路径按钮
        self.select_path_button = ttk.Button(button_frame, text="选择微信路径", command=self.select_wechat_path)
        self.select_path_button.grid(row=1, column=0, columnspan=3, pady=(5, 0))
        
        # 进程列表标签
        ttk.Label(main_frame, text="当前微信进程:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        # 进程列表框架
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 创建Treeview显示进程信息
        columns = ('PID', '状态', '启动时间', '内存使用')
        self.process_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=12)
        
        # 设置列标题
        self.process_tree.heading('PID', text='进程ID')
        self.process_tree.heading('状态', text='状态')
        self.process_tree.heading('启动时间', text='启动时间')
        self.process_tree.heading('内存使用', text='内存使用(MB)')
        
        # 设置列宽
        self.process_tree.column('PID', width=80)
        self.process_tree.column('状态', width=80)
        self.process_tree.column('启动时间', width=150)
        self.process_tree.column('内存使用', width=100)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 绑定双击事件
        self.process_tree.bind('<Double-1>', self.on_process_double_click)
        
        # 右键菜单
        self.create_context_menu()
        
        # 统计信息
        self.stats_label = ttk.Label(main_frame, text="运行中的微信进程: 0")
        self.stats_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(5, 0))
        
        # 说明文本
        info_text = """使用说明:
1. 点击"添加新微信窗口"来启动新的微信实例
2. 双击列表中的进程可以关闭对应的微信
3. 右键点击进程可以查看更多操作
4. 程序会自动监控微信进程状态

注意: 微信多开可能存在封号风险，请谨慎使用！"""
        
        info_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="5")
        info_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        info_label = ttk.Label(info_frame, text=info_text, foreground="red", font=("Arial", 8))
        info_label.grid(row=0, column=0, sticky=tk.W)
        
        # 设置窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_context_menu(self):
        """创建右键菜单"""
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="关闭此进程", command=self.close_selected_process)
        self.context_menu.add_command(label="查看进程详情", command=self.show_process_details)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="刷新", command=self.refresh_process_list)
        
        self.process_tree.bind('<Button-3>', self.show_context_menu)

    def show_context_menu(self, event):
        """显示右键菜单"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def find_wechat_path(self):
        """查找微信安装路径"""
        possible_paths = [
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"D:\Program Files\Tencent\WeChat\WeChat.exe",
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                self.wechat_path = path
                self.status_label.config(text=f"微信路径: {path}", foreground="green")
                self.add_button.config(state="normal")
                return
        
        self.status_label.config(text="未找到微信，请手动选择路径", foreground="red")
        self.add_button.config(state="disabled")

    def select_wechat_path(self):
        """手动选择微信路径"""
        file_path = filedialog.askopenfilename(
            title="选择微信程序",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")],
            initialfile="WeChat.exe"
        )
        
        if file_path:
            self.wechat_path = file_path
            self.status_label.config(text=f"微信路径: {file_path}", foreground="green")
            self.add_button.config(state="normal")

    def add_wechat(self):
        """添加新的微信实例"""
        if not self.wechat_path or not os.path.exists(self.wechat_path):
            messagebox.showerror("错误", "微信路径无效，请重新选择！")
            self.select_wechat_path()
            return
        
        try:
            # 启动微信进程
            process = subprocess.Popen([self.wechat_path], 
                                     cwd=os.path.dirname(self.wechat_path))
            
            # 等待进程启动
            time.sleep(1)
            
            # 验证进程是否成功启动
            if process.poll() is None:  # 进程仍在运行
                self.wechat_processes.append(process)
                messagebox.showinfo("成功", f"微信进程已启动！PID: {process.pid}")
                self.refresh_process_list()
            else:
                messagebox.showerror("错误", "微信进程启动失败！")
                
        except Exception as e:
            messagebox.showerror("错误", f"启动微信失败: {str(e)}")

    def get_all_wechat_processes(self):
        """获取所有微信进程"""
        wechat_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'create_time', 'memory_info', 'status']):
                if proc.info['name'] and 'wechat' in proc.info['name'].lower():
                    wechat_processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        return wechat_processes

    def refresh_process_list(self):
        """刷新进程列表"""
        # 清空当前列表
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        # 获取所有微信进程
        processes = self.get_all_wechat_processes()
        
        for proc in processes:
            try:
                pid = proc.info['pid']
                status = proc.info['status']
                create_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                          time.localtime(proc.info['create_time']))
                memory_mb = round(proc.info['memory_info'].rss / 1024 / 1024, 1)
                
                self.process_tree.insert('', 'end', values=(pid, status, create_time, memory_mb))
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 更新统计信息
        self.stats_label.config(text=f"运行中的微信进程: {len(processes)}")

    def on_process_double_click(self, event):
        """双击进程项时关闭进程"""
        self.close_selected_process()

    def close_selected_process(self):
        """关闭选中的进程"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个进程！")
            return
        
        item = selection[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        
        try:
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            if messagebox.askyesno("确认", f"确定要关闭进程 {proc_name} (PID: {pid}) 吗？"):
                proc.terminate()
                time.sleep(0.5)
                
                if proc.is_running():
                    proc.kill()  # 强制关闭
                
                messagebox.showinfo("成功", f"进程 {pid} 已关闭")
                self.refresh_process_list()
                
        except psutil.NoSuchProcess:
            messagebox.showinfo("信息", "进程已经不存在了")
            self.refresh_process_list()
        except psutil.AccessDenied:
            messagebox.showerror("错误", "没有权限关闭此进程")
        except Exception as e:
            messagebox.showerror("错误", f"关闭进程失败: {str(e)}")

    def show_process_details(self):
        """显示进程详细信息"""
        selection = self.process_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择一个进程！")
            return
        
        item = selection[0]
        pid = int(self.process_tree.item(item, 'values')[0])
        
        try:
            proc = psutil.Process(pid)
            
            details = f"""进程详细信息:
PID: {proc.pid}
名称: {proc.name()}
状态: {proc.status()}
CPU使用率: {proc.cpu_percent()}%
内存使用: {round(proc.memory_info().rss / 1024 / 1024, 1)} MB
创建时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(proc.create_time()))}
可执行文件: {proc.exe()}
命令行: {' '.join(proc.cmdline())}"""
            
            messagebox.showinfo("进程详情", details)
            
        except psutil.NoSuchProcess:
            messagebox.showinfo("信息", "进程已经不存在了")
        except psutil.AccessDenied:
            messagebox.showerror("错误", "没有权限访问此进程信息")
        except Exception as e:
            messagebox.showerror("错误", f"获取进程信息失败: {str(e)}")

    def close_all_wechat(self):
        """关闭所有微信进程"""
        processes = self.get_all_wechat_processes()
        
        if not processes:
            messagebox.showinfo("信息", "没有找到运行中的微信进程")
            return
        
        if messagebox.askyesno("确认", f"确定要关闭所有 {len(processes)} 个微信进程吗？"):
            closed_count = 0
            for proc in processes:
                try:
                    proc.terminate()
                    closed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            time.sleep(1)
            
            # 强制关闭仍在运行的进程
            for proc in processes:
                try:
                    if proc.is_running():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            messagebox.showinfo("完成", f"已关闭 {closed_count} 个微信进程")
            self.refresh_process_list()

    def start_monitor_thread(self):
        """启动监控线程"""
        def monitor():
            while True:
                try:
                    self.root.after(0, self.refresh_process_list)
                    time.sleep(3)  # 每3秒刷新一次
                except:
                    break
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出微信多开工具吗？"):
            self.root.destroy()

    def run(self):
        """运行程序"""
        self.root.mainloop()

if __name__ == "__main__":
    # 检查是否安装了必要的库
    try:
        import psutil
    except ImportError:
        print("请先安装 psutil 库: pip install psutil")
        exit(1)
    
    app = WeChatMultiOpener()
    app.run()
