import os
from dotenv import load_dotenv
from pathlib import Path

def get_env(env_key):
    return os.getenv(env_key)

# 获取环境名称
env = get_env('APPLICATION_STANDARD_ENV') or 'qa'
print(f'=== 环境配置加载 ===')
print(f'当前环境: {env}')

# 构建配置文件路径
# 获取当前文件所在目录，然后向上两级到达 service 目录
current_file = Path(__file__).resolve()
service_dir = current_file.parent.parent.parent  # service/app/utils -> service/app -> service


env_file = f'config/application-{env}.properties'
if env == 'qa':
    # qa 环境使用绝对路径
    env_file = service_dir / 'config' / f'application-qa.properties'

env_file_path = Path(env_file)
print(f'配置文件路径: {env_file_path}')

load_dotenv(env_file)

