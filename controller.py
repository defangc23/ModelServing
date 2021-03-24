import os, sys
import importlib
import configparser

from lib.ray_wrapper import RAY
from lib import logger
import algopkg


class Controller(object):

    TAG = "CONTROLLER"
    MODELZOO = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Model_ZOO'))
    CONFIG = os.path.abspath(os.path.join(os.path.dirname(__file__), 'conf.ini'))

    def __init__(self):
        self.log = logger.get_logger(Controller.TAG, level='info')
        self.log.info("[1/5] Controller Start. config file: {}".format(Controller.CONFIG))
        self.Config = configparser.ConfigParser()
        self.Config.read(Controller.CONFIG)
        self.log.info("[2/5] Config file loaded.")
        self.__modelserve_conn()
        self.log.info("[3/5] Model Serve connected.")

        self.AddAlgo, self.DelAlgo, self.ResetAlgo = None, None, None

    def __modelserve_conn(self):
        port = self.Config['MODEL SERVE']['port']
        self.ModelServe = RAY(port, tag=Controller.TAG)

    def __parser_getsections(self, keyword, split_sign="."):
        return [i.split(split_sign)[1] for i in self.Config.sections() if i.split(split_sign)[0] == keyword]

    def __algo_diff(self):
        if not self.AlgoChecklist:
            return None
        AlgoDiff = []
        for AlgoName in self.AlgoChecklist:
            AlgoConf = self.Config["algopkg."+AlgoName]
            Backend = AlgoConf['backend']
            # check backend
            if not self.RunningEndpoint[AlgoName]['traffic'].get(Backend):
                AlgoDiff.append(AlgoName)
                continue
            # check route
            if not self.RunningEndpoint[AlgoName]['route'] == "/" + AlgoConf['route']:
                AlgoDiff.append(AlgoName)
                continue
            # check method
            if not self.RunningEndpoint[AlgoName]['methods'] == [AlgoConf['method']]:
                AlgoDiff.append(AlgoName)
                continue
            # check replicate
            if not self.RunningBackend[Backend].num_replicas == int(AlgoConf['replicas']):
                AlgoDiff.append(AlgoName)
                continue
            # check gpu cost
            if not self.RunningBackend[Backend].user_config.get('gpu_cost') == float(AlgoConf['gpu_cost']):
                AlgoDiff.append(AlgoName)
                continue
            # check model
            if not self.RunningBackend[Backend].user_config.get('model') == AlgoConf['model']:
                AlgoDiff.append(AlgoName)
                continue

        return AlgoDiff

    def __modelserve_add(self):
        if self.AddAlgo:
            self.log.info("===== Add algo to ModelServe =====\n")
            for AlgoName in self.AddAlgo:
                try:
                    AlgoConf = self.Config['algopkg.'+AlgoName]
                    Backend = AlgoConf['backend']
                    backend_py = importlib.import_module(f"algopkg.{AlgoName}.backend")
                    backend_cls = getattr(backend_py, f"{Backend}")

                    if len(AlgoConf['model'].strip()) == 0:
                        self.ModelServe.backend_create(backend_name=Backend,
                                                       backend_func=backend_cls,
                                                       model_path='',
                                                       config={"num_replicas": AlgoConf['replicas']},
                                                       gpu_config={"num_gpus": float(AlgoConf['gpu_cost'])})
                    else:
                        self.ModelServe.backend_create(backend_name=Backend,
                                                       backend_func=backend_cls,
                                                       model_path=Controller.MODELZOO +','+ AlgoConf['model'],
                                                       config={"num_replicas": AlgoConf['replicas']},
                                                       gpu_config={"num_gpus": float(AlgoConf['gpu_cost'])})

                    self.ModelServe.backend_updateconf(backend_name=Backend,
                                                       user_config={'gpu_cost': float(AlgoConf['gpu_cost']),
                                                                    'model': AlgoConf['model']})
                    self.ModelServe.endpoint_create(endpoint_name=AlgoName,
                                                    backend=Backend,
                                                    route="/" + AlgoConf['route'],
                                                    methods=[AlgoConf['method']])
                    self.log.info("Model serve Add endpoint: {} with backend {} succeed".format(
                        AlgoName, Backend
                    ))
                except:
                    self.log.error("Model serve Add endpoint: {} with backend {} failed".format(
                        AlgoName, Backend
                    ), exc_info=True)
                    self.ModelServe.backend_delete(backend_name=Backend)
                    self.ModelServe.endpoint_delete(endpoint_name=AlgoName)
                    self.log.error("As exception occur, Delete endpoint: {} with backend {}".format(AlgoName, Backend))
            self.log.info("===== Add OP finished =====\n")

    def __modelserve_del(self):
        if self.DelAlgo:
            self.log.info("====== Del algo from ModelServe =====\n")
            for AlgoName in self.DelAlgo:
                try:
                    BackendInAlgo = list(self.RunningEndpoint[AlgoName]['traffic'].keys())[0]
                    self.ModelServe.endpoint_delete(endpoint_name=AlgoName)
                    self.ModelServe.backend_delete(backend_name=BackendInAlgo)
                    self.log.info("Model serve Del endpoint: {} with backend {} succeed".format(
                        AlgoName, BackendInAlgo
                    ))
                except:
                    self.log.error("Model serve Del endpoint: {} with backend {} failed".format(
                        AlgoName, BackendInAlgo
                    ))
            self.log.info("===== Del OP finished =====\n")

    def __modelserve_reset(self):
        if self.ResetAlgo:
            self.log.info("========= Reset algo from ModelServe ==========")
            self.DelAlgo = self.ResetAlgo
            self.AddAlgo = self.ResetAlgo
            self.__modelserve_del()
            self.__modelserve_add()
            self.log.info("========= Reset OP finished ==========")


    def gen_tasks(self):
        AlgoObj = self.__parser_getsections("algopkg")
        self.RunningEndpoint = self.ModelServe.endpoint_list()
        self.RunningBackend = self.ModelServe.backend_list()
        self.AddAlgo = list(set(AlgoObj) - set(list(self.RunningEndpoint.keys())))
        self.DelAlgo = list(set(list(self.RunningEndpoint.keys())) - set(AlgoObj))
        self.AlgoChecklist = list(set(list(self.RunningEndpoint.keys())) - set(self.DelAlgo))
        self.ResetAlgo = self.__algo_diff()
        self.log.info("[4/5] Generate new tasks: \n")
        self.log.info("    Add: {} \n".format(self.AddAlgo))
        self.log.info("    Del: {} \n".format(self.DelAlgo))
        self.log.info("    Reset: {} \n\n".format(self.ResetAlgo))


    def exec_tasks(self):
        self.__modelserve_del()
        self.__modelserve_add()
        self.__modelserve_reset()
        self.log.info("[5/5] All tasks finished \n")
        self.log.info("    RunningEndpoint: {} \n".format(self.ModelServe.endpoint_list()))
        self.log.info("    RunningBackend: {}".format(self.ModelServe.backend_list()))

    def run(self):
        self.gen_tasks()
        self.exec_tasks()

if __name__ == "__main__":

    c = Controller()
    c.run()
