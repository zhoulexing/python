# YZ-Dubbo

有赞 Dubbo SDK - 基于 Tether 网关的 Dubbo RPC 调用封装

## 功能特性

- 🚀 **简单易用**: 提供简洁的函数式 API
- ⏱️ **超时控制**: 支持自定义超时时间,默认3秒

## 安装

```bash
pip install yz-dubbo
```

## 快速开始

### 基础调用

```python
from yz_dubbo import invoke

# 调用 Dubbo 服务
result = invoke(
    service_name="com.youzan.service.UserService",
    method_name="getUserInfo",
    args=[{"userId": 123}]
)

print(result)  # 直接返回响应数据
```

### 自定义 Headers

```python
result = invoke(
    service_name="com.youzan.service.OrderService",
    method_name="createOrder",
    args=[{"productId": 456, "quantity": 1}],
    headers={
        "X-Request-Id": "req-123",
        "X-Tenant-Id": "tenant-456"
    }
)
```

### 设置超时时间

```python
result = invoke(
    service_name="com.youzan.service.PaymentService",
    method_name="pay",
    args=[payment_data],
    timeout=10000  # 10秒超时
)
```

## 错误处理

### 错误码对照表

| 错误码 | 说明 | 错误信息 |
|--------|------|----------|
| `10000001` | 网络超时 | NETWORK_TIMEOUT |
| `10000002` | 网络错误 | NETWORK_ERROR |
| `10000003` | 参数不能为空 | PARAMS_EMPTY_ERROR |
| `10000004` | 服务接口错误 | SERVICE_INTERFACE_ERROR |

### 异常处理示例

```python
from yz_dubbo import invoke, YzDubboException, YzDubboErrorCode

try:
    result = invoke(
        service_name="com.youzan.service.UserService",
        method_name="getUser",
        args=[{"userId": 123}]
    )
    print(f"成功: {result}")

except YzDubboException as e:
    print(f"错误码: {e.code}")
    print(f"错误信息: {e.message}")
    print(f"上下文: {e.context}")

    # 根据错误码处理
    if e.code == YzDubboErrorCode.NETWORK_TIMEOUT.code:
        print("请求超时,请稍后重试")
    elif e.code == YzDubboErrorCode.NETWORK_ERROR.code:
        print("网络错误")
    else:
        print("其他错误")
```

## 许可证

MIT License

## 联系方式

- 项目地址: `/packages/yz_dubbo`
- 测试目录: `/tests/yz_dubbo`

---

**YZ-Dubbo - 让 Dubbo 调用更简单** 🚀
