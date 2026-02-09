"""
FastAPI 应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.exceptions import RequestValidationError

from app.exceptions.exception_handel import validation_exception_handler, global_exception_handler
from app.controllers import example_controller

load_dotenv()
app = FastAPI()

# 添加中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有源（包括file://协议），生产环境应该改为 cors_origins_list
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]  # 暴露所有响应头
)

# 添加异常处理
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# 注册路由
app.include_router(example_controller.router, prefix="/example")
