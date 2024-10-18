import numpy as np

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

        assert len(alpha) == 2 & len(beta) == 2 & len(beta[0]) == 2 & len(initial_infectious) == 2

        self.newly_infected_all = []

        # SETTING UP INITIAL CONDITIONS
        for j in range(2):

            total_infected = np.zeros(modeling_duration)
            newly_infected = np.zeros(modeling_duration)
            susceptible = np.zeros(modeling_duration)

            initial_infectious = initial_infectious[j]
            total_infected[0] = initial_infectious 
            newly_infected[0] = initial_infectious

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
                        beta[i][j] * susceptible[day] * total_infected[day] / rho
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
