from fastapi import FastAPI, Body
from fastapi.responses import PlainTextResponse
from utils.image import ImageUtils
from utils.config import Config


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
    robot_text_msgs_list = config.get("robot_text_msgs_list")
    print(robot_text_msgs_list)

    msgs_list = [
        item for item in robot_text_msgs_list if not item["ineffective"]]
    if len(msgs_list) > 0:
        return msgs_list[0]
    return []


@app.post("/wechat/set_msg_ineffective")
def set_msg_ineffective(msg_item: dict = Body(...)):
    print(f"set_msg_ineffective: {msg_item}")
    robot_text_msgs_list = config.get("robot_text_msgs_list")
    for item in robot_text_msgs_list:
        if item.get("id") == msg_item.get("id"):
            item["ineffective"] = True
    config.set("robot_text_msgs_list", robot_text_msgs_list)
    return {"success": True}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001)
