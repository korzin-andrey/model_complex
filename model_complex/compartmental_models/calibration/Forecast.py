import numpy as np

from ..models import BRModel


class Forecast:
    def __init__(self, available_data: list,
                 model: BRModel,
                 forecast_duration: int) -> None:
        self.available_data = available_data
        self.model = model
        self.forecast_duration = forecast_duration
        params_dict = self.model.get_params_if_calibrated()
        self.alpha = params_dict['alpha']
        self.beta = params_dict['beta']
        self.initial_infectious = params_dict['initial_infectious']
        self.population_size = params_dict['population_size']

    def forecast(self):
        data_size = len(self.available_data)//len(self.init_infectious) + \
            self.forecast_duration
        res = np.array(
            [[[float('inf'), float('-inf')] for _ in range(data_size)]
             for j in range(len(self.init_infectious))])

        for alpha, beta in zip(zip(*self.alpha), zip(*self.beta)):
            self.model.simulate(
                alpha=alpha,
                beta=beta,
                initial_infectious=self.init_infectious,
                population_size=self.population_size,
                modeling_duration=data_size
            )

            new_res = np.array(self.model.get_result())
            res = np.array([np.minimum(res[0], new_res[0]),
                           np.maximum(res[1], new_res[1])])
        return res

    def retrospective(self):
        pass
