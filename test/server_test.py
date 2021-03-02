import requests, json
from io import BytesIO
from PIL import Image
# IMAGE_PATH = "/mnt/media/users/fangcheng/remote_deploy/ModelServing/test/test.jpg"
# request_url = "http://172.16.124.12:666/extract"
# file = open(IMAGE_PATH, 'rb')
# params = {"file": file}
# response = requests.post(request_url, data=file)
# file.close()
# print(response.json())


IMAGE_PATH = "/mnt/media/users/fangcheng/remote_deploy/ModelServing/test/test.jpg"
request_url = "http://172.16.124.12:666/extract"
params = {"key_1": 123}
response = requests.post(request_url, json=params)
print(response.json())