import os
import sys
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algopkg.AlgoExample import backend
backend_cls = backend.algo_backend



algobck = backend_cls(model_path="/mnt/media/users/fangcheng/remote_deploy/ModelServing/Model_ZOO/algoexample_model_v1.pb")
