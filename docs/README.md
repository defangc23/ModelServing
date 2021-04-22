

# Model Serving 分布式模型服务

This model serving framework is built on top of the powerful distributed library Ray and providing further simplified configurations to parallelize and accelerate machine learning workloads.



## Getting Started



### Prerequisites

Project-ready docker image already integrated with:

- python == 3.6
- ray[serve] == 2.0.0 dev0

you should do is freezing your algorithm dependencies as requirements.txt

### Installation

1. Clone the repo 

2. To convert your original algorithm with model, create your project as a python package (e.g. *AlgoExample*) under `algopkg` directory with this layout:

   ```bash
   algopkg/
   ├── AlgoExample
       ├── __init__.py
       └── backend.py
   ├── YourAlgoPkgName
       ├── __init__.py
       ├── backend.py
       └── other_denpendency_files_you_need.py
   ```

   `AlgoExample` is the default package example with two vital models (`__init__.py` and `backend.py`)you need to have. You can use it as a template or a reference.

   `YourAlgoPkgName` is the name of the package directory that you should create. This name is free to modify and suggesting naming by the core algorithm in your project.  (FaceDetection e.g.)  In addition,  your full project dependency modules should under this package directory.

   `backend.py`   This python file is the main entry of your model processing backend in project and the filename should not be altered. Please copy it from  `AlgoExample/backend.py` and rewrite. There are only a few methods and names you need to add and modify down below referring to your own model processing workflow: 

   ```python
   import sys, os, socket, time, traceback
   import numpy as np
   
   class algo_backend(object):
   
       def __init__(self, model_path):
           try:
               self.res = None
               self.info_msg = "Result from {}".format(socket.gethostname())
               if len(model_path) == 0:
                   self._model_init()
                   print("[Model Initialized Successfully] No model path specified")
               else:
                   model_info_lst = model_path.split(',')
                   modelzoo_path = model_info_lst.pop(0).strip()
                   model_path_lst = [os.path.join(modelzoo_path, model.strip()) for model in model_info_lst if len(model) != 0]
                   for p in model_path_lst:
                       assert os.path.exists(p) == True, "Model Not Found"
                   self._model_init(model_path_lst)
                   print("[Model Initialized Successfully] load model from : {}".format(model_path_lst))
           except Exception:
               print("[Model Initialized Failed]:")
               traceback.print_exc()
   
       def reconfigure(self, config):
           # Optional method
           # This will be called when the class is created and when
           # the user_config field of BackendConfig is updated.
           pass
   
       def _model_init(self, model_path_lst=None):
           # Add by user
           pass
   
       def _model_inference(self, param_dict):
           # Add by user
           pass
   
       async def __call__(self, starlette_request):
           try:
               param_dict = await starlette_request.json()
               self.res = self._model_inference(param_dict)
               print("[Request Processed Successfully] Input request: {}   Output Result: {}".format(param_dict, self.res))
               return {'status': 1, 'result': self.res, 'info':self.info_msg}
           except Exception:
               error_info = traceback.format_exc()
               print("[Request Failed]: {}".format(error_info))
               return {'status': 0, 'info':self.info_msg + error_info}
   ```

   Add or change by user:

   `def _model_init(self, model_path_lst)` : Initialize and load your backend model for long running. Get your model path from argument `model_path_lst` with index. Considering more than one model is possibly needed in the initialization step, this argument is a list. And it can be set in the next test step in script `algopkg_test.py` with global variable `MODEL_NAME`, don't worry too much right now.

   `def _model_inference(self, param_dict)` : grab all the model inputs and parameters you need from `param_dict` and run your model.  When finish, return your model results. Argument `param_dict` can also be set and tested in next test step.

   `class algo_backend(object)` : The class name should be considered to change by your own.

   ***Caution*: Please import your dependencies within these method functions** 

3. Test your package

   check out `./test/algopkg_test.py`  This module can help you check the two methods adding by you and make sure your package can work properly when it is imported by others. Before running this unitest, you only need to change some global variables in this test script:

   ```python
   ''' Change by user '''
   ALGO_PKG_NAME = 'AlgoExample'
   BACKEND_CLS_NAME = 'algo_backend'
   MODEL_NAME = 'algoexample_model_v1.pb' # put your model in folder named Model_ZOO
   PARAM_DICT = {}
   ```

4. Deployment

   After making sure your package works, put your model file into `Model_ZOO` folder. Then open `conf.ini` file and edit it:

   ```ini
   # fixed section name, don't change
   [MODEL SERVE] 
   # port for model serve REST API
   port = 666         
   
   # AlgoExample should be changed by user according to the project dir under algopkg folder
   [algopkg.AlgoExample]
   # algo_backend is your class name in script: ./algopkg/AlgoExample/backend.py
   backend = algo_backend
   # algoexample_model_v1.pb is your model filename in Model_ZOO, you can add multiple models separate with commas or leave it empty 
   model = algoexample_model_v1.pb
   # numbers of your specified model paralleled running in backend, caution: cpu cores is the upper bound for this setting
   replicas = 1
   # the gpu fraction of usage for one single model
   gpu_cost = 1
   # route for model serve REST API
   route = extract
   # request method for model serve REST API, please use default GET with json params
   method = GET
   ```

   You can add more different sections in this config file which sets different types of models running simultaneously.

   

5. Start your server

   ```bash
   # move your repo in /opt/modelserve/ 
   
   # docker pull eum814/modelserve_env:latest
   # check out the dockerfile: https://hub.docker.com/r/eum814/modelserve_env
   
   # Head node
   docker run --shm-size=8G -d --gpus all \
              -e TZ="Asia/Shanghai" \
              -v /:/mnt \
              -w /mnt/opt/modelserve/ \
              --net=host --name=modelserve_head \
              eum814/modelserve_env:latest \
              conda run -n AlgoExample ray start --head --port=6370 --dashboard-host 0.0.0.0 --block
   
   # Worker node
   docker run --shm-size=4G -d --gpus all \
              -e TZ="Asia/Shanghai" \
              -v /:/mnt \
              -w /mnt/opt/modelserve/ \
              --net=host --name=modelserve_worker_1 \
              eum814/modelserve_env:latest \
              conda run -n AlgoExample ray start --address='HeadNode_IP:6370' --block
   ```

   

6. Build your Conda env

   Each Algo package you created should have its own virtual environment to support algo backends with different (possibly conflicting) python dependencies. Conda env has already been installed in ModelServing docker image with one existing conda env named `AlgoExample`. And conda env `AlgoExample` has two functions : 1. from last step your server has started based on this conda env.   2. To build your conda env, you need to clone this env and rename it with your algo package name. To be more specific, please follow these steps to build your own conda env :

   ```bash
   # after starting your server, enter modelserving container in each node
   docker exec -it modelserve_head bash        # HeadNode
   docker exec -it modelserve_worker_1 bash    # WorkerNode
   
   # create your conda env
   conda create -n YourAlgoPackageName --clone AlgoExample
   
   # enter your env and install your dependencies
   conda activate YourAlgoPackageName
   pip install -r requirements.txt
   ```

   

7. Run your package

   Everytime you modify `conf.ini`, simply run `controller.py`  in your conda env. It will immediately take effect on the running backends with your new settings.

   The request REST API URL should be like http://headnode_IP:port/route  with JSON parameters in the body of your request by default. 

   Dashboard: http://headnode_IP:8265

   Before running `controller.py`, please make sure your Ray serve has been all set. 



6. Test your REST API

   check out `./test/server_test.py` You can send your request and test the response from server. 

> If you need to modify your code in your algopkg and restart your serve, please firstly comment your algo config part in conf.ini and run controller.py to stop your serve.  After finished your code just uncomment your config part and run controller.py again.
>



## Debug



1. docker exec -it 进入container 

3. vim /etc/ssh/sshd_config 修改docker的22端口, 因为docker直接使用了系统网络模式无法通过ssh调试程序

3. /etc/init.d/ssh restart

   



