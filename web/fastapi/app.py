from fastapi import FastAPI, Body
from fastapi.responses import PlainTextResponse
from utils.image import ImageUtils
from utils.config import Config
import copy


config = Config()
app = FastAPI()
image_utils = ImageUtils()


@app.get("/", response_class=PlainTextResponse)
def hello_world():
    return "Hello, World!"


@app.get("/image_matcher")
def image_matcher(source_image_path: str, template_image_path: str, threshold: float = 0.7):
    return image_utils.image_matcher(source_image_path, template_image_path, threshold)


@app.get("/compare_bottom_area")
def compare_bottom_area(img1_path: str, img2_path: str, threshold: float = 0.1):
    return image_utils.compare_bottom_area(img1_path, img2_path, threshold)


@app.get("/wechat/listen_new_msgs")
def listen_new_msgs():
    config.reload_config()
    friends_circle_material = config.get("friends_circle_material")

    material_list = [
        item for item in friends_circle_material if not item["ineffective"]]
    if len(material_list) > 0:
        material_item = copy.deepcopy(material_list[0])
        material_list[0]["ineffective"] = True
        config.set("friends_circle_material", friends_circle_material)
        return material_item
    return {}


@app.post("/wechat/set_msg_ineffective")
def set_msg_ineffective(msg_item: dict = Body(...)):
    print(f"set_ineffective: {msg_item}")
    friends_circle_material = config.get("friends_circle_material")
    for item in friends_circle_material:
        if item.get("id") == msg_item.get("id"):
            item["ineffective"] = True
    config.set("friends_circle_material", friends_circle_material)
    return {"success": True}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)
