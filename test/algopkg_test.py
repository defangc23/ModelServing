import os, sys
import unittest
import importlib
import numpy as np
MODELZOO = os.path.abspath(os.path.join(os.path.dirname(__file__),'..','Model_ZOO'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import algopkg


''' Change by user '''
ALGO_PKG_NAME = 'AlgoExample'
BACKEND_CLS_NAME = 'algo_backend'
MODEL_NAME = 'algoexample_model_v1.pb'
PARAM_DICT = {}


class TestAlgopkg(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        backend_py = importlib.import_module(f"algopkg.{ALGO_PKG_NAME}.backend")
        cls.backend_cls = getattr(backend_py, f"{BACKEND_CLS_NAME}")

    def test_algo(self):
        algobck = self.backend_cls(model_path=MODELZOO + ',' +MODEL_NAME)
        res = algobck._model_inference(PARAM_DICT)
        print(res)

if __name__ == '__main__':
    unittest.main()