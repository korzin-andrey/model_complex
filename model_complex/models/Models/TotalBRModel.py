import numpy as np

from ..Interface import BRModel


class TotalBRModel(BRModel):
    """
    Model for total case
    """

    def simulate(
        self, 
        alpha: float, 
        beta: float, 
        initial_infectious: int, 
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

        # SETTING UP INITIAL CONDITIONS
        self.total_infected = np.zeros(modeling_duration)
        self.newly_infected = np.zeros(modeling_duration)
        self.susceptible = np.zeros(modeling_duration)
        self.total_infected[0] = initial_infectious 
        self.newly_infected[0] = initial_infectious
        initial_susceptible = int(alpha*initial_infectious)
        self.susceptible[0] = initial_susceptible

        # SIMULATION
        for day in range(modeling_duration-1):
            self.total_infected[day] = min(
                sum([
                        self.newly_infected[day - tau] * self.br_function(tau) 
                        for tau in range(len(self.br_func_array))     if (day - tau) >= 0
                ]),
                initial_infectious
            )
            
            self.newly_infected[day+1] = min(
                beta * self.susceptible[day] * self.total_infected[day] / initial_infectious,
                self.susceptible[day]
            )

            self.susceptible[day+1] = self.susceptible[day] - self.newly_infected[day+1]        

    def get_newly_infected(self):
        return self.newly_infected

    def data_columns(self, epid_data):
        return epid_data['total']
