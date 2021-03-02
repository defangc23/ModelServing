

# Model Serving 分布式模型服务

This model serving framework is built on top of the distributed library Ray and providing further simplified configurations to parallelize and accelerate machine learning workloads.



## Getting Started



### Prerequisites

Project-ready docker image with:

- python >= 3.6
- ray[serve] == 1.2.0

### Installation

1. Clone the repo

2. Create your project as a python package with this layout:

   ```bash
   AlgoExample
       ├── backend.py
       └── __init__.py
   
   ```

   *AlgoExample* is the name of your package directory. This name is free to modify and suggesting naming by the core algorithm name in your project.  (FaceDetection e.g.)

   *backend.py*   This python file is the main entry of your model processing backend in project and the filename should not be altered.  There are a few class methods down below your need to add and modify by referring your own model processing workflow: 

   ```python
   import sys, os, socket, time, traceback
   import numpy as np
   
   
   class algo_backend(object):
   
       def __init__(self, model_path):
           try:
               self.res = None
               self.info_msg = "Result from {}".format(socket.gethostname())
               assert os.path.exists(model_path) == True, "Model Not Found"
               self._model_init(model_path)
               print("[Model Initialized Successfully] load model from : {}".format(model_path))
           except Exception:
               print("[Model Initialized Failed]:")
               traceback.print_exc()
   
       def reconfigure(self, config):
           # Optional method
           # This will be called when the class is created and when
           # the user_config field of BackendConfig is updated.
           pass
   
       def _model_init(self, model_path):
           '''Add by user'''
           pass
   
       def _model_inference(self, param_dict):
           '''Add by user'''
           pass
   
       async def __call__(self, flask_request):
           try:
               param_dict = await flask_request.json()
               self.res = self._model_inference(param_dict)
               print("[Request Processed Successfully] Input request: {}   Output Result: {}".format(param_dict, res))
               return {'status': 1, 'result': self.res, 'info':self.info_msg}
           except Exception:
               print("[Request Failed]:")
               traceback.print_exc()
               return {'status': 0, 'info':self.info_msg}
   ```

    

3. 



## Debug



1. docker run --shm-size=4G -it --rm --gpus all -v /:/mnt --net host --name fang_modelserving -e TZ="Asia/Shanghai" eum814/deep_env:latest bash
2. vim /etc/ssh/sshd_config 修改docker的22端口, 因为docker直接使用了系统网络模式
3. pip install "ray[serve]" -i https://mirrors.aliyun.com/pypi/simple/
4. /etc/init.d/ssh restart

### host
ray start --head --port=6370 --dashboard-host 0.0.0.0
### client
ray start --address='172.16.124.76:6370'





## Deployment



### Ray Server

docker run --shm-size=4G -d \
           --net=host --name=ray-server \
           rayproject/ray:1.2.0-gpu \
           ray start --head --port=6370 --dashboard-host 0.0.0.0 --block

### Ray Client
docker run --shm-size=4G -d --gpus all\
           --net=host --name=ray-client2 \
           rayproject/ray:1.2.0-gpu \
           ray start --address='172.16.124.76:6370' --block