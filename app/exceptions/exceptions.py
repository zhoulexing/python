from app.exceptions.error_codes import BusinessErrorCode

class BusinessException(Exception):
    """业务异常"""

    def __init__(self, error_code: BusinessErrorCode, message: str = None):
        self.message = message or error_code.message
        self.code = error_code.code
        super().__init__(self.message)

