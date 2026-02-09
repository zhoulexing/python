import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from app.exceptions.exceptions import BusinessException

logger = logging.getLogger(__name__)


async def business_exception_handler(request: Request, exc: BusinessException):
    """业务异常"""
    logger.warning(
        f"业务异常: msg={exc.message}, 请求路径: {request.url}")

    return JSONResponse(status_code=200, content={
        "success": False,
        "code": exc.code or 500,
        "msg": f"业务异常: msg={exc.message}",
        "data": None
    })


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """参数验证异常"""
    errMsg = ""
    for error in exc.errors():
        errMsg += ".".join(str(loc) for loc in error.get("loc")
                           ) + ":" + error.get("msg") + ";"

    logger.warning(f"参数验证失败: {errMsg}, 请求路径: {request.url}")

    return JSONResponse(status_code=200, content={
        "success": False,
        "code": 400,
        "msg": errMsg,
        "data": None
    })


async def global_exception_handler(request: Request, exc: Exception):
    """
    全局异常处理器 - 捕获所有未处理的异常
    这是最后的兜底异常处理器
    """
    # 构建错误详情
    error_detail = {
        "exception_type": type(exc).__name__,
        "exception_message": str(exc),
        "request_url": str(request.url),
        "request_method": request.method,
    }

    # 记录详细错误日志（包含堆栈信息）
    logger.error(f"系统级异常: {error_detail}", exc_info=True)

    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "code": 500,
            "msg": f"{type(exc).__name__}: {str(exc)}",
            "data": None
        }
    )
