import os
import subprocess

def open_multiple_wechat(wechat_path, instances=2):
    """
    根据提供的路径和实例数量打开多个微信客户端。
    
    :param wechat_path: 微信安装路径
    :param instances: 需要打开的微信实例数量，默认为2
    """
    if not os.path.exists(wechat_path):
        print("未找到微信程序，请检查安装路径")
        return
    
    for _ in range(instances):
        # 启动微信实例
        try:
            subprocess.Popen([wechat_path])
            print(f"已启动一个微信实例：{wechat_path}")
        except Exception as e:
            print(f"启动微信实例时出错：{e}")

if __name__ == "__main__":
    # 设置微信安装路径
    wechat_path = r"C:\Program Files (x86)\Tencent\WeChat\WeChat.exe"
    
    # 调用函数并指定需要打开的微信实例数量
    open_multiple_wechat(wechat_path, instances=3)