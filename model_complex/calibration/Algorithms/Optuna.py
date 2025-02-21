import numpy as np
import optuna
from sklearn.metrics import r2_score

from ...models import Model
from ...utils import ModelParams


class Optuna:

    @classmethod
    def calibrate(
        self,
        model: Model,
        data: np.array,
        time_step: str,
        model_params: ModelParams,
        n_trials=1000,
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

        def OptunaModel(trial):

            alpha = [trial.suggest_float(f"alpha_{i}", 0, 1) for i in range(alpha_dim)]
            beta = [trial.suggest_float(f"beta_{i}", 0, 1) for i in range(beta_dim)]

            simulate_params.alpha = alpha
            simulate_params.beta = beta

            model.simulate(
                params=simulate_params,
                modeling_duration=duration,
            )

            return r2_score(data, get_newly_infected_base_on_time_step())

        study = optuna.create_study(direction="maximize")
        study.optimize(OptunaModel, n_trials=n_trials)

        simulate_params.alpha = [
            study.best_params[f"alpha_{i}"] for i in range(alpha_dim)
        ]
        simulate_params.beta = [study.best_params[f"beta_{i}"] for i in range(beta_dim)]

        model.set_ci_params([])
        model.set_best_params(simulate_params)
