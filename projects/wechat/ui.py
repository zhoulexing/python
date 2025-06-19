#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信多开启动器
功能：支持同时运行多个微信实例，每个实例使用独立的数据目录
作者：MiniMax Agent
创建时间：2025-06-19
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import json
import time
from pathlib import Path
import psutil
import winreg


class WeChatMultiLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("微信多开启动器")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 配置文件路径
        self.config_file = Path("wechat_config.json")
        self.instances = []
        self.processes = {}  # 存储进程信息
        
        # 微信可执行文件路径
        self.wechat_path = self.find_wechat_path()
        
        # 加载配置
        self.load_config()
        
        # 创建界面
        self.create_gui()
        
        # 启动监控线程
        self.start_monitoring()
    
    def find_wechat_path(self):
        """自动查找微信安装路径"""
        possible_paths = [
            r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"C:\Program Files\Tencent\WeChat\WeChat.exe",
            r"D:\Program Files (x86)\Tencent\WeChat\WeChat.exe",
            r"D:\Program Files\Tencent\WeChat\WeChat.exe",
        ]
        
        # 尝试从注册表获取
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              r"SOFTWARE\Tencent\WeChat") as key:
                install_path, _ = winreg.QueryValueEx(key, "InstallPath")
                wechat_exe = os.path.join(install_path, "WeChat.exe")
                if os.path.exists(wechat_exe):
                    return wechat_exe
        except:
            pass
        
        # 尝试预定义路径
        for path in possible_paths:
            if os.path.exists(path):
                return path
        
        return ""
    
    def load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.instances = config.get('instances', [])
                    self.wechat_path = config.get('wechat_path', self.wechat_path)
            except Exception as e:
                print(f"加载配置失败: {e}")
                self.instances = []
    
    def save_config(self):
        """保存配置文件"""
        config = {
            'wechat_path': self.wechat_path,
            'instances': self.instances
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def create_gui(self):
        """创建图形用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 微信路径设置
        ttk.Label(main_frame, text="微信路径:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        path_frame = ttk.Frame(main_frame)
        path_frame.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        path_frame.columnconfigure(0, weight=1)
        
        self.path_var = tk.StringVar(value=self.wechat_path)
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var)
        path_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(path_frame, text="浏览", 
                  command=self.browse_wechat_path).grid(row=0, column=1)
        
        # 控制按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        ttk.Button(button_frame, text="添加微信实例", 
                  command=self.add_instance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="删除选中实例", 
                  command=self.remove_instance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="启动选中实例", 
                  command=self.start_selected_instance).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭选中实例", 
                  command=self.stop_selected_instance).pack(side=tk.LEFT, padx=5)
        
        # 实例列表
        list_frame = ttk.LabelFrame(main_frame, text="微信实例列表", padding="5")
        list_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 创建Treeview
        columns = ("名称", "状态", "PID", "数据目录")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 设置列标题
        self.tree.heading("#0", text="序号")
        self.tree.column("#0", width=50)
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "数据目录":
                self.tree.column(col, width=200)
            else:
                self.tree.column(col, width=100)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # 刷新列表
        self.refresh_instance_list()
    
    def browse_wechat_path(self):
        """浏览选择微信路径"""
        filename = filedialog.askopenfilename(
            title="选择微信程序",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.path_var.set(filename)
            self.wechat_path = filename
            self.save_config()
    
    def add_instance(self):
        """添加新的微信实例"""
        if not self.wechat_path or not os.path.exists(self.wechat_path):
            messagebox.showerror("错误", "请先设置正确的微信路径")
            return
        
        # 创建添加实例的对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("添加微信实例")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="实例名称:").grid(row=0, column=0, sticky=tk.W, pady=5)
        name_var = tk.StringVar(value=f"微信实例{len(self.instances) + 1}")
        ttk.Entry(frame, textvariable=name_var, width=30).grid(row=0, column=1, pady=5)
        
        ttk.Label(frame, text="数据目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        data_dir_var = tk.StringVar(value=f"./wechat_data/instance_{len(self.instances) + 1}")
        
        dir_frame = ttk.Frame(frame)
        dir_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dir_frame, textvariable=data_dir_var, width=25).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(dir_frame, text="浏览", 
                  command=lambda: self.browse_data_dir(data_dir_var)).grid(row=0, column=1, padx=(5, 0))
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        def confirm_add():
            name = name_var.get().strip()
            data_dir = data_dir_var.get().strip()
            
            if not name:
                messagebox.showerror("错误", "请输入实例名称")
                return
            
            if not data_dir:
                messagebox.showerror("错误", "请设置数据目录")
                return
            
            # 检查名称是否重复
            if any(inst['name'] == name for inst in self.instances):
                messagebox.showerror("错误", "实例名称已存在")
                return
            
            # 创建数据目录
            try:
                os.makedirs(data_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror("错误", f"创建数据目录失败: {e}")
                return
            
            # 添加实例
            instance = {
                'name': name,
                'data_dir': data_dir,
                'created_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            self.instances.append(instance)
            self.save_config()
            self.refresh_instance_list()
            dialog.destroy()
            self.status_var.set(f"已添加实例: {name}")
        
        ttk.Button(button_frame, text="确认", command=confirm_add).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def browse_data_dir(self, var):
        """浏览选择数据目录"""
        directory = filedialog.askdirectory(title="选择数据目录")
        if directory:
            var.set(directory)
    
    def remove_instance(self):
        """删除选中的实例"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要删除的实例")
            return
        
        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1
        
        if index < 0 or index >= len(self.instances):
            messagebox.showerror("错误", "无效的选择")
            return
        
        instance = self.instances[index]
        
        # 检查是否正在运行
        if instance['name'] in self.processes:
            if messagebox.askyesno("确认", f"实例 '{instance['name']}' 正在运行，是否先关闭后删除？"):
                self.stop_instance(instance['name'])
            else:
                return
        
        if messagebox.askyesno("确认删除", f"确定要删除实例 '{instance['name']}' 吗？\n注意：数据目录不会被删除。"):
            self.instances.pop(index)
            self.save_config()
            self.refresh_instance_list()
            self.status_var.set(f"已删除实例: {instance['name']}")
    
    def start_selected_instance(self):
        """启动选中的实例"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要启动的实例")
            return
        
        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1
        
        if index < 0 or index >= len(self.instances):
            messagebox.showerror("错误", "无效的选择")
            return
        
        instance = self.instances[index]
        self.start_instance(instance['name'])
    
    def stop_selected_instance(self):
        """关闭选中的实例"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("提示", "请选择要关闭的实例")
            return
        
        item = selection[0]
        index = int(self.tree.item(item, "text")) - 1
        
        if index < 0 or index >= len(self.instances):
            messagebox.showerror("错误", "无效的选择")
            return
        
        instance = self.instances[index]
        self.stop_instance(instance['name'])
    
    def start_instance(self, instance_name):
        """启动指定的微信实例"""
        instance = next((inst for inst in self.instances if inst['name'] == instance_name), None)
        if not instance:
            messagebox.showerror("错误", f"未找到实例: {instance_name}")
            return
        
        # 检查是否已经在运行
        if instance_name in self.processes:
            messagebox.showinfo("提示", f"实例 '{instance_name}' 已经在运行")
            return
        
        if not os.path.exists(self.wechat_path):
            messagebox.showerror("错误", "微信程序路径不存在")
            return
        
        try:
            # 确保数据目录存在
            os.makedirs(instance['data_dir'], exist_ok=True)
            
            # 构建启动命令
            # 使用不同的数据目录启动微信
            cmd = [self.wechat_path]
            
            # 设置环境变量来指定数据目录
            env = os.environ.copy()
            env['APPDATA'] = os.path.abspath(instance['data_dir'])
            
            # 启动进程
            process = subprocess.Popen(
                cmd,
                env=env,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == 'win32' else 0
            )
            
            self.processes[instance_name] = {
                'process': process,
                'pid': process.pid,
                'start_time': time.time()
            }
            
            self.status_var.set(f"已启动实例: {instance_name} (PID: {process.pid})")
            self.refresh_instance_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"启动实例失败: {e}")
    
    def stop_instance(self, instance_name):
        """关闭指定的微信实例"""
        if instance_name not in self.processes:
            messagebox.showinfo("提示", f"实例 '{instance_name}' 未在运行")
            return
        
        try:
            process_info = self.processes[instance_name]
            process = process_info['process']
            
            # 尝试优雅关闭
            process.terminate()
            
            # 等待进程结束
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # 强制结束
                process.kill()
                process.wait()
            
            del self.processes[instance_name]
            self.status_var.set(f"已关闭实例: {instance_name}")
            self.refresh_instance_list()
            
        except Exception as e:
            messagebox.showerror("错误", f"关闭实例失败: {e}")
    
    def refresh_instance_list(self):
        """刷新实例列表"""
        # 清空当前列表
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 添加实例到列表
        for i, instance in enumerate(self.instances):
            status = "运行中" if instance['name'] in self.processes else "未运行"
            pid = self.processes[instance['name']]['pid'] if instance['name'] in self.processes else ""
            
            self.tree.insert("", "end", text=str(i + 1), values=(
                instance['name'],
                status,
                pid,
                instance['data_dir']
            ))
    
    def start_monitoring(self):
        """启动进程监控线程"""
        def monitor():
            while True:
                try:
                    # 检查进程是否还在运行
                    to_remove = []
                    for instance_name, process_info in self.processes.items():
                        try:
                            process = process_info['process']
                            if process.poll() is not None:  # 进程已结束
                                to_remove.append(instance_name)
                        except:
                            to_remove.append(instance_name)
                    
                    # 移除已结束的进程
                    for instance_name in to_remove:
                        del self.processes[instance_name]
                        self.root.after(0, lambda name=instance_name: self.status_var.set(f"实例 {name} 已退出"))
                    
                    if to_remove:
                        self.root.after(0, self.refresh_instance_list)
                    
                except Exception as e:
                    print(f"监控线程错误: {e}")
                
                time.sleep(2)
        
        # 启动监控线程
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def run(self):
        """运行程序"""
        try:
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
            self.root.mainloop()
        except Exception as e:
            print(f"程序运行错误: {e}")
    
    def on_closing(self):
        """程序关闭时的处理"""
        # 询问是否关闭所有微信实例
        if self.processes:
            if messagebox.askyesno("确认退出", "是否关闭所有运行中的微信实例？"):
                for instance_name in list(self.processes.keys()):
                    self.stop_instance(instance_name)
        
        self.root.destroy()


def main():
    """主函数"""
    # 检查系统
    if sys.platform != 'win32':
        print("此程序仅支持Windows系统")
        return
    
    try:
        app = WeChatMultiLauncher()
        app.run()
    except Exception as e:
        print(f"程序启动失败: {e}")
        messagebox.showerror("错误", f"程序启动失败: {e}")


if __name__ == "__main__":
    main()
