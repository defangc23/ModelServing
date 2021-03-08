import os, sys
import unittest
import importlib
import numpy as np


ALGO_PKG_NAME = 'AlgoExample'
BACKEND_CLS_NAME = 'algo_backend'
MODEL_ABS_PATH = '/mnt/media/users/fangcheng/remote_deploy/ModelServing/Model_ZOO/algoexample_model_v1.pb'
PARAM_DICT = {}



class TestAlgopkg(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
        import algopkg
        backend_py = importlib.import_module(f"algopkg.{ALGO_PKG_NAME}.backend")
        cls.backend_cls = getattr(backend_py, f"{BACKEND_CLS_NAME}")

    def test_algo(self):
        # '''add by user'''
        algobck = self.backend_cls(model_path=MODEL_ABS_PATH)
        algobck._model_inference(PARAM_DICT)

if __name__ == '__main__':
    unittest.main()