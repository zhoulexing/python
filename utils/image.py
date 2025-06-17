import cv2
import numpy as np
from PIL import Image


class ImageUtils:
    def __init__(self):
        pass

    def concat_images_vertical(self, image_paths: list, output_path: str):
        """
        将多张图片生成一张垂直图片

        参数：
        image_paths: 图片路径列表
        output_path: 输出路径
        """
        if not image_paths:
            print("未找到任何图片，无法拼接。请检查图片路径是否正确。")
            return
        images = [Image.open(path) for path in image_paths]
        # 宽度以第一张图片的宽度为准
        img_width = images[0].width
        total_height = sum(img.height for img in images)
        new_im = Image.new('RGB', (img_width, total_height))
        y_offset = 0
        for img in images:
            new_im.paste(img, (0, y_offset))
            y_offset += img.height
        new_im.save(output_path)

    def image_matcher(self, source_image_path, template_image_path, threshold=0.7):
        img = cv2.imread(source_image_path)
        if img is None:
            raise FileNotFoundError(
                f"Could not load source image from {source_image_path}")
        template = cv2.imread(template_image_path)
        if template is None:
            raise FileNotFoundError(
                f"Could not load template image from {template_image_path}")
        h, w = template.shape[:2]
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        matches = []
        min_dist = min(w, h) // 2
        for pt in zip(*loc[::-1]):
            if all(np.linalg.norm(np.array(pt) - np.array(m)) > min_dist for m in matches):
                matches.append(pt)
        # 返回所有匹配点的 x, y 以及模板的宽高
        return [{"x": int(x), "y": int(y), "width": int(w), "height": int(h)} for (x, y) in matches]

    def compare_bottom_area(self, img1_path, img2_path, threshold=0.1):
        # 读取图片（带 alpha 通道，如果有的话）
        img1 = cv2.imread(img1_path, cv2.IMREAD_UNCHANGED)
        img2 = cv2.imread(img2_path, cv2.IMREAD_UNCHANGED)

        if img1 is None or img2 is None:
            raise FileNotFoundError("One of the images could not be loaded.")

        # 获取尺寸
        h1, w1 = img1.shape[:2]
        h2, w2 = img2.shape[:2]

        # 取底部区域
        bottom_height = int(h1 * 0.3)
        y = h1 - bottom_height

        # 裁剪底部区域
        img1_crop = img1[y:y+bottom_height, 0:w1]
        img2_crop = img2[y:y+bottom_height, 0:w2]

        # 确保尺寸一致
        if img1_crop.shape != img2_crop.shape:
            raise ValueError("Cropped areas have different shapes!")

        # 如果有 alpha 通道，先转为 4 通道，否则转为 3 通道
        if img1_crop.shape[2] == 3:
            img1_crop = cv2.cvtColor(img1_crop, cv2.COLOR_BGR2BGRA)
        if img2_crop.shape[2] == 3:
            img2_crop = cv2.cvtColor(img2_crop, cv2.COLOR_BGR2BGRA)

        # 计算像素差异
        diff = np.abs(img1_crop.astype(np.int16) - img2_crop.astype(np.int16))
        diff_gray = np.mean(diff, axis=2)  # RGBA -> 灰度差异

        # 阈值映射
        pixel_threshold = threshold * 255
        diff_pixels = np.sum(diff_gray > pixel_threshold)

        total_pixels = diff_gray.shape[0] * diff_gray.shape[1]
        diff_percentage = (diff_pixels / total_pixels) * 100

        return {
            "hasDifference": bool(diff_pixels > 0),
            "diffPixels": int(diff_pixels),
            "diffPercentage": float(diff_percentage),
            "totalPixels": int(total_pixels)
        }
