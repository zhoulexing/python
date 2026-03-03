"""
客户端模块测试 (使用 Mock)
"""
from yz_dubbo import invoke, YzDubboException


def test_client_invoke():
    try:
        resp = invoke("com.youzan.material.materialcenter.api.service.storage.file.StorageQiniuFileWriteService", "getPublicFileUploadToken", [{
            "channel": "ai_sales",
            "maxSize": 1073741824,
            "fromApp": "ai-sales",
            "operatorType": 1,
            "operatorId": 00,
        }])
        print(resp)
    except YzDubboException as e:
        print(f"error: {e.code}, {e.message}")


if __name__ == "__main__":
    test_client_invoke()
