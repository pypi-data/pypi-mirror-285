from abc import ABC, abstractmethod
from collections import OrderedDict
from typing import Dict, Union, List, Tuple
from fedimpute.execution_environment.utils.tracker import Tracker
from fedimpute.execution_environment.loaders.load_strategy import load_fed_strategy_server
import numpy as np


class Server:

    """
    Server class to be used in the federated imputation environment

    Attributes:
        fed_strategy: str - name of the federated strategy
        fed_strategy_params: dict - parameters of the federated strategy
        server_config: dict - configuration of the server
        X_test_global: np.ndarray - global test data

    """

    def __init__(
            self,
            fed_strategy_name: str,
            fed_strategy_params: dict,
            global_test: np.ndarray,
            server_config: Dict[str, Union[str, int, float]],
    ):
        self.fed_strategy = load_fed_strategy_server(fed_strategy_name, fed_strategy_params)
        self.server_config = server_config
        self.X_test_global = global_test[:, :-1]
        self.y_test_global = global_test[:, -1]

    def global_evaluation(self, eval_res: dict) -> dict:
        # global evaluation of imputation models
        raise NotImplementedError
