"""
七牛云上传测试

测试两个核心功能:
1. 上传本地路径的图片
2. 上传网络图片地址
"""
from pathlib import Path

import httpx

from yz_doc.utils.qiniu_utils import upload_image


def download_image(url: str, save_path: Path) -> None:
    """
    从网络下载图片到本地

    Args:
        url: 图片URL
        save_path: 保存路径
    """
    with httpx.Client(timeout=30.0) as client:
        response = client.get(url)
        if response.status_code != 200:
            raise Exception(f"下载图片失败 [HTTP {response.status_code}]: {url}")

        save_path.write_bytes(response.content)
        print(f"✅ 图片已下载: {save_path}")


def test_upload_local_image():
    """
    测试1: 上传本地路径的图片

    创建一个临时测试图片文件，然后上传到七牛云
    """
    print("=" * 60)
    print("测试1: 上传本地路径的图片")
    print("=" * 60)

    # 创建测试图片文件
    test_image = Path("/tmp/test_local_image.png")
    test_image.write_bytes(b"PNG fake image content for testing")

    print(f"✅ 测试图片已创建: {test_image}")

    try:
        # 上传图片 - 需要提供实际的proxy_domain
        result = upload_image(
            image_path=test_image,
            operator_id=16595,
            operator_type=1,
            channel="ai_sales",
            from_app="ai-platform",
            max_size=102400,  # 100KB
            proxy_domain="YOUR_PROXY_DOMAIN_HERE",  # 需要替换为实际的代理域名
        )

        print(f"✅ 上传成功!")
        print(f"   图片Key: {result.get('key', 'N/A')}")
        print(f"   图片Hash: {result.get('hash', 'N/A')}")
        print(f"   完整结果: {result}")

    except Exception as e:
        print(f"❌ 上传失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理测试文件
        if test_image.exists():
            test_image.unlink()
            print(f"✅ 测试文件已删除")

    print()


def test_upload_network_image():
    """
    测试2: 上传网络图片地址

    从网络下载图片，保存到本地临时文件，然后上传到七牛云
    """
    print("=" * 60)
    print("测试2: 上传网络图片地址")
    print("=" * 60)

    # 网络图片URL - 使用一个公开的测试图片
    image_url = "https://img01.yzcdn.cn/upload_files/2025/07/10/Fl2hWyiFKKRFqDA7gaXfM6FpHyGh.jpg"
    temp_image = Path("/tmp/test_network_image.png")

    try:
        # 1. 从网络下载图片
        print(f"正在下载图片: {image_url}")
        download_image(image_url, temp_image)

        # 2. 上传到七牛云 - 需要提供实际的proxy_domain
        print(f"正在上传图片到七牛云...")
        result = upload_image(
            image_path=temp_image,
            operator_id=16595,
            operator_type=1,
            channel="ai_sales",
            from_app="ai-platform",
            max_size=1048576,  # 1MB
            proxy_domain="http://proxy-static-qa.s.qima-inc.com",  # 需要替换为实际的代理域名
        )

        print(f"✅ 上传成功!")
        print(f"   图片Key: {result.get('key', 'N/A')}")
        print(f"   图片Hash: {result.get('hash', 'N/A')}")
        print(f"   完整结果: {result}")

    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # 清理临时文件
        if temp_image.exists():
            temp_image.unlink()
            print(f"✅ 临时文件已删除")

    print()

if __name__ == "__main__":
    print("\n" + "🚀 七牛云图片上传功能测试".center(60, "="))
    print("\n⚠️  注意: 运行测试前需要替换 'YOUR_PROXY_DOMAIN_HERE' 为实际的代理域名\n")

    # 运行所有测试
    # test_upload_local_image()
    test_upload_network_image()

    print("=" * 60)
    print("✅ 所有测试完成!")
    print("=" * 60)
