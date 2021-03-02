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
        # Add by user
        pass

    def _model_inference(self, param_dict):
        # Add by user
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


