from utils.image import ImageUtils

if __name__ == "__main__":
    image_utils = ImageUtils()

    result = image_utils.image_matcher(
        'assets/images/hack/wechat_home.png', 'assets/images/hack/wechat_moment_icon.png')
    print(result)
