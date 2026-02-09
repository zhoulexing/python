"""
数据库引擎配置
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from app.utils.env_utils import get_env


def get_database_url() -> str:
    """
    构建数据库连接 URL

    Returns:
        str: 数据库连接 URL
    """
    user = get_env('DB_Service_db_sales_ai_user')
    password = get_env('DB_Service_db_sales_ai_password')
    host = get_env('DB_Service_db_sales_ai_host')
    port = get_env('DB_Service_db_sales_ai_port')
    database = get_env('DB_Service_db_sales_ai_dbname')

    return (
        f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"
        f"?charset=utf8mb4"
    )


# 创建异步引擎
engine: AsyncEngine = create_async_engine(
    get_database_url(),
    echo=True,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)
