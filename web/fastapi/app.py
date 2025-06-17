from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from utils.image import ImageUtils

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

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=5001) 