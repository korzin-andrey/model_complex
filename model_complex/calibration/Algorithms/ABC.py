import numpy as np
import pymc as pm

from ...models import Model
from ...utils import ModelParams


class ABC:

    @classmethod
    def calibrate(
        self,
        model: Model,
        data: np.array,
        time_step: str,
        model_params: ModelParams,
        sample: int = 100,
        epsilon: int = 3000,
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

        def simulation_func(rng, alpha, beta, size=None):

            simulate_params.alpha = alpha
            simulate_params.beta = beta

            model.simulate(params=simulate_params, modeling_duration=duration)
            return get_newly_infected_base_on_time_step()

        with pm.Model() as PMmodel:
            alpha = pm.Uniform(name="alpha", lower=0, upper=1, shape=(alpha_dim,))
            beta = pm.Uniform(name="beta", lower=0, upper=1, shape=(beta_dim,))

            sim = pm.Simulator(
                "sim",
                simulation_func,
                list(alpha) + [0] * (beta_dim - alpha_dim),
                beta,
                epsilon=epsilon,
                observed=data,
            )

            idata = pm.sample_smc(progressbar=False)

        posterior = idata.posterior.stack(samples=("draw", "chain"))

        alpha = np.array(
            [
                np.random.choice(posterior["alpha"][i], size=sample)
                for i in range(alpha_dim)
            ]
        )
        beta = np.array(
            [np.random.choice(posterior["beta"][i], size=sample) for i in range(beta_dim)]
        )

        ci_params = []

        for i in range(sample):

            ci_par = ModelParams(
                alpha=alpha[:, i],
                beta=beta[:, i],
                population_size=model_params.population_size,
                initial_infectious=model_params.initial_infectious,
            )

            ci_params.append(ci_par)

        model.set_ci_params(ci_params)

        simulate_params.alpha = [a.mean() for a in alpha]
        simulate_params.beta = [b.mean() for b in beta]

        model.set_best_params(simulate_params)
