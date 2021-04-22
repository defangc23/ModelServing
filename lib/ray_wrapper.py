import ray
from ray import serve
from ray.serve.exceptions import RayServeException

import requests
import traceback
from io import BytesIO
import sys, os, logging

class RAY(object):

    TAG = 'RayServe'

    def __init__(self, port=None, tag=None):

        # log
        if tag is None:
            self.log = logging.getLogger(__name__)
        else:
            self.log = logging.getLogger("%s.%s" % (tag, RAY.TAG))

        ray.init(address="auto")
        nodes_info = ray.nodes()
        try:
            self.client = serve.start(http_options={"location": "EveryNode", "host":"0.0.0.0", "port":port}, detached=True)
            self.log.info("Ray serve initialized, node number: {} \n Nodes Info: {}".format(len(nodes_info), nodes_info))

        except RayServeException:
            self.client = serve.connect()
            self.log.info("Connected existing Ray serve, node number: {} \n Nodes Info: {}".format(len(nodes_info), nodes_info))

    def shutdown(self):
        self.client.shutdown()
        self.log.info("Ray serve shutdown")

    def backend_list(self):
        return self.client.list_backends()

    def backend_create(self, backend_name, backend_func, model_path, replicas, gpu_cost, conda_env):
        if model_path is None:
            self.client.create_backend(backend_name, backend_func, "", config={"num_replicas": replicas}, ray_actor_options={"num_gpus": gpu_cost, "runtime_env": {"conda": conda_env}})
            self.log.info("Backend created, backend_name:{}, func:{}, model:{}, replicas:{}, gpu_cost:{}, conda_env:{}".format(backend_name, backend_func, model_path, replicas, gpu_cost, conda_env))
        else:
            self.client.create_backend(backend_name, backend_func, model_path, config={"num_replicas": replicas}, ray_actor_options={"num_gpus": gpu_cost, "runtime_env": {"conda": conda_env}})
            self.log.info("Backend created, backend_name:{}, func:{}, model:{}, replicas:{}, gpu_cost:{}, conda_env:{}".format(backend_name, backend_func, model_path, replicas, gpu_cost, conda_env))

    def backend_delete(self, backend_name):
        self.client.delete_backend(backend_name)
        self.log.info("Backend deleted, backend_name:{}".format(backend_name))

    def backend_getconf(self, backend_name):
        return self.client.get_backend_config(backend_name)

    def backend_updateconf(self, backend_name, scale_config=None, user_config=None):
        if scale_config:
            self.client.update_backend_config(backend_name, scale_config)
        if user_config:
            from ray.serve import BackendConfig
            backend_config = BackendConfig(user_config=user_config)
            self.client.update_backend_config(backend_name, backend_config)

    def endpoint_list(self):
        return self.client.list_endpoints()

    def endpoint_create(self, endpoint_name, backend, route, methods=["GET"]):
        self.client.create_endpoint(endpoint_name, backend=backend, route=route, methods=methods)
        self.log.info("Endpoint created, endpoint_name:{}, backend:{}, route:{}, methods:{}".format(
            endpoint_name, backend, route, methods
        ))

    def endpoint_delete(self, endpoint_name):
        self.client.delete_endpoint(endpoint_name)
        self.log.info("Endpoint deleted, endpoint_name:{}".format(endpoint_name))




