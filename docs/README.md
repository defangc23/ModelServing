

# Model Serving 分布式模型服务

This model serving framework is built on top of the powerful distributed library Ray and providing further simplified configurations to parallelize and accelerate machine learning workloads.



## Getting Started



### Prerequisites

Project-ready docker image with:

- python >= 3.6
- ray[serve] == 1.2.0

### Installation

1. Clone the repo

2. Create your project as a python package (e.g. *AlgoExample*) under `algopkg` directory with this layout:

   ```bash
   algopkg/
   ├── AlgoExample
   │   ├── backend.py
   │   └── __init__.py
   └── setup.py
   ```

   `AlgoExample` is the name of your package directory. This name is free to modify and suggesting naming by the core algorithm name in your project.  (FaceDetection e.g.)  In addition,  your full project dependency modules should under this package directory.

   `backend.py`   This python file is the main entry of your model processing backend in project and the filename should not be altered.  There are a few class methods down below you need to add and modify referring to your own model processing workflow: 

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
               print("[Request Processed Successfully] Input request: {}   Output Result: {}".format(param_dict, self.res))
               return {'status': 1, 'result': self.res, 'info':self.info_msg}
           except Exception:
               print("[Request Failed]:")
               traceback.print_exc()
               return {'status': 0, 'info':self.info_msg}
   ```

   <u>*def _model_init(self, model_path)*</u> : Initialize your backend model for long running .

   <u>*def _model_inference(self, param_dict)*</u> : grab all parameters you need from `param_dict` and run your model.  When finish, return your model results. (but it's ok to leave it empty ) 

   <u>*class algo_backend(object)*</u> : The class name should be considered to change by your own.

3. Test your package

   check out `./test/algopkg_test.py`  This module can help you check the two methods adding by you and make sure your package can work properly when it is imported by others. 

4. Deployment

   After making sure your package works, put your model file into `Model_ZOO` folder. Then open `conf.ini` file and edit it:
   
   ```ini
   # fixed section name, don't change
   [MODEL SERVE] 
   # port for model serve REST API
   port = 666         
   
   # AlgoExample should be changed by user according to the project dir under algopkg folder
   [algopkg.AlgoExample]
   # algo_backend is your class name in ./algopkg/AlgoExample/backend.py
   backend = algo_backend
   # algoexample_model_v1.pb is your model filename in Model_ZOO
   model = algoexample_model_v1.pb
   # numbers of your specified model paralleled running in backend 
   replicas = 1
   # the gpu fraction of usage for one single model
   gpu_cost = 1
   # route for model serve REST API
   route = extract
   # request method for model serve REST API
   method = POST
   ```
   
   You can add more different sections in this config file which sets different types of models running simultaneously.

5. Run

   Everytime you add or modify `conf.ini`, simply run `controller.py` . It will set all for you.

   The request REST API URL should be like http://host_ip_address:port/route  with JSON parameters in the body of your request by default. 

   Dashboard: http://host_ip_address:8265

   Before running `controller.py`, please make sure your Ray serve has been all set. 

   

   **Docker Setups:**

   ```bash
   # Host
   docker run --shm-size=4G -d \
              -v your-modelserve-path:/opt/modelserve/ \
              --net=host --name=modelserve_host \
              your-docker-image \
              ray start --head --port=6370 --dashboard-host 0.0.0.0 --block
   # Worker
   docker run --shm-size=4G -d --gpus all\
              -v your-modelserve-path:/opt/modelserve/ \
              --net=host --name=modelserve_worker_1 \
              your-docker-image \
              ray start --address='hostIP:6370' --block
            
   ```

   use `docker exec` to run controller.py



## Debug



1. screen -S modelserving

2. docker run --shm-size=4G -it --rm --gpus all -v /:/mnt --net host --name fang_modelserving -e TZ="Asia/Shanghai" deep_env:v1 bash

3. vim /etc/ssh/sshd_config 修改docker的22端口, 因为docker直接使用了系统网络模式

4. pip install ray[serve]==1.2.0 -i https://mirrors.aliyun.com/pypi/simple/

5. /etc/init.d/ssh restart

   

### host 
ray start --head --port=6370 --dashboard-host 0.0.0.0
### join worker
ray start --address='hostIP:6370'


