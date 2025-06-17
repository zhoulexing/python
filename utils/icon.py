from PIL import Image
import os
from enum import Enum

class IconFormat(Enum):
    ICO = 'ICO'
    ICNS = 'ICNS'

class IconUtils:
    def __init__(self):
        pass

    def generate_app_icon(self, image_path: str, output_path: str, format: IconFormat = IconFormat.ICO):
        original_img = Image.open(image_path)
        # 需要的尺寸
        ico_sizes = [(64, 64), (128, 128), (256, 256)]
        ico_images = []

        # 为每个尺寸创建调整后的图像
        for size in ico_sizes:
            img_resized = original_img.resize(size, Image.Resampling.LANCZOS)
            ico_images.append(img_resized)

        # 遍历ico_images, 保存.ico文件
        for i, img in enumerate(ico_images):
            ico_path = os.path.join(
                output_path, f'wechat_rpa_icon_{i+1}.{format.value.lower()}')
            img.save(ico_path, format.value, sizes=[
                     (s[0], s[1]) for s in ico_sizes], append_images=ico_images[i+1:])

        print(f"图标已保存到 {ico_path}")
