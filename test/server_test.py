import requests, json
import cv2
import base64
import numpy as np


def img_to_base64(image):
    base64_str = base64.b64encode(cv2.imencode('.jpg', image)[1]).decode()
    return base64_str

def base64_to_img(base64_str):
    img_bytes = base64.b64decode(base64_str)
    img_np = np.frombuffer(img_bytes, dtype=np.uint8)
    img = cv2.imdecode(img_np, cv2.IMREAD_UNCHANGED)
    return img




IMAGE_PATH = "/mnt/media/users/fangcheng/remote_deploy/ModelServing/test/test.jpg"
img = cv2.imread(IMAGE_PATH)
base64_img = img_to_base64(img)
convert_img = base64_to_img(base64_img)

request_url = "http://172.16.124.12:666/extract"
params = {"key_1": 123, "base64_image":base64_img}
response = requests.post(request_url, json=params)
print(response.json())