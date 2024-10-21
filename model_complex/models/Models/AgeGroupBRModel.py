import numpy as np
import pymc as pm

from ..Interface import BRModel


class AgeGroupBRModel(BRModel):
    """
    Model for case of several age-group
    """

    def simulate(
        self, 
        alpha: list[float], 
        beta: list[list[float]], 
        initial_infectious: list[int], 
        rho: int, 
        modeling_duration=150
    ):
        """
        Download epidemiological excel data file from the subdirectory of epid_data.
        epid_data directory looks like 'epid_data/{city}/epid_data.xlsx'.

        :param alpha: Fraction of non-immune people
        :param beta: Effective contacts intensivity
        :param initial_infectious: Numbers of initial infected people in the simulation
        :param rho: Numbers of people in simulation
        :param modeling_duration: duration of modeling

        :return:
        """
        # assert len(alpha) == 2 
        # assert len(beta) == 2 
        # assert len(beta[0]) == 2 
        # assert len(initial_infectious) == 2

        self.newly_infected_all = []

        # SETTING UP INITIAL CONDITIONS
        for j in range(2):

            total_infected = np.zeros(modeling_duration)
            newly_infected = np.zeros(modeling_duration)
            susceptible = np.zeros(modeling_duration)

            total_infected[0] = initial_infectious[j] 
            newly_infected[0] = initial_infectious[j]

            initial_susceptible = int(alpha[j]*rho)
            susceptible[0] = initial_susceptible

            # SIMULATION
            for day in range(modeling_duration-1):
                total_infected[day] = min(
                    sum(
                        newly_infected[day - tau] * self.br_function(tau) 
                            for tau in range(len(self.br_func_array)) if (day - tau) >= 0
                    ),
                    rho
                )
                
                newly_infected[day+1] = min(
                    sum(
                        beta[2*i + j] * susceptible[day] * total_infected[day] / rho
                            for i in range(2)
                    ),
                    susceptible[day]
                )

                susceptible[day+1] = susceptible[day] - newly_infected[day+1]      

            self.newly_infected_all.append(list(newly_infected))    

    def get_newly_infected(self):
        return self.newly_infected_all

    def data_columns(self, epid_data):
        return [
            list(epid_data['strain_B_age_15+_cases'] + epid_data['strain_A(H3N2)_age_15+_cases'] + epid_data['strain_A(H1N1)pdm09_age_15+_cases']),
            list(epid_data['strain_B_age_0-14_cases'] + epid_data['strain_A(H3N2)_age_0-14_cases'] + epid_data['strain_A(H1N1)pdm09_age_0-14_cases'])
        ]

    def context_manager(self, initial_infectious, data):

        def simulation_func(rng, alpha, beta, gamma, delta, sigma, rho, size=None):
            self.simulate(
                alpha=[alpha, gamma], 
                beta=[beta, delta, sigma, rho], 
                initial_infectious=initial_infectious, 
                rho=5e5, 
                modeling_duration=len(data)
            )
            return self.get_newly_infected()
        
        with pm.Model() as model:
            alpha = pm.Uniform(name="a", lower=0, upper=1)
            beta = pm.Uniform(name="b", lower=0, upper=1)
            gamma = pm.Uniform(name="gamma", lower=0, upper=1)
            delta = pm.Uniform(name="delta", lower=0, upper=1)
            sigma = pm.Uniform(name="sigma", lower=0, upper=1)
            rho = pm.Uniform(name="rho", lower=0, upper=1)
            # alpha1 = pm.Uniform(name="a0", lower=0, upper=1)
            # beta1 = pm.Uniform(name="b1", lower=0, upper=1)
            # beta2 = pm.Uniform(name="b2", lower=0, upper=1)
            # beta3 = pm.Uniform(name="b3", lower=0, upper=1)

            sim = pm.Simulator("sim", simulation_func, alpha, beta, gamma, delta, sigma, rho,
                            epsilon=10, observed=data)
            
            idata = pm.sample_smc()
        
        return idata
