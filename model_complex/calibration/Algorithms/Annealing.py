import numpy as np
from scipy.optimize import dual_annealing
from sklearn.metrics import r2_score

from ...models import Model
from ...utils import ModelParams


class Annealing:

    @classmethod
    def calibrate(
        self,
        model: Model,
        data: np.array,
        time_step: str,
        model_params: ModelParams,
    ):
        alpha_dim, beta_dim = model.params()
        duration = len(data) // alpha_dim
        get_newly_infected_base_on_time_step = model.get_daily_newly_infected

        if time_step == "week":
            duration *= 7
            get_newly_infected_base_on_time_step = model.get_weekly_newly_infected

        simulate_params = ModelParams(
            alpha=[0],
            beta=[0],
            population_size=model_params.population_size,
            initial_infectious=model_params.initial_infectious,
        )

        lw = [0] * (alpha_dim + beta_dim)
        up = [1] * (alpha_dim + beta_dim)

        def AnnealingModel(x):

            alpha = x[:alpha_dim]
            beta = x[alpha_dim:]

            simulate_params.alpha = alpha
            simulate_params.beta = beta

            model.simulate(params=simulate_params, modeling_duration=duration)

            return -r2_score(data, get_newly_infected_base_on_time_step())

        ret = dual_annealing(AnnealingModel, bounds=list(zip(lw, up)))

        simulate_params.alpha = ret.x[:alpha_dim]
        simulate_params.beta = ret.x[alpha_dim:]

        model.set_ci_params([])
        model.set_best_params(simulate_params)
