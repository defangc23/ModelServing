import cv2
import base64
import numpy as np

def img_to_base64(image):
    base64_str = base64.b64encode(cv2.imencode('.jpg', image)[1]).decode()
    return base64_str

def base64_to_img(base64_str):
    img_bytes = base64.b64decode(base64_str)
    img_list = np.frombuffer(img_bytes, dtype=np.uint8)
    np_img = cv2.imdecode(img_list, cv2.IMREAD_UNCHANGED)
    return np_img
