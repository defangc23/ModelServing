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

    def base64_to_img(self, base64_str):
        import cv2, base64
        img_bytes = base64.b64decode(base64_str)
        img_list = np.frombuffer(img_bytes, dtype=np.uint8)
        np_img = cv2.imdecode(img_list, cv2.IMREAD_UNCHANGED)
        return np_img

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


