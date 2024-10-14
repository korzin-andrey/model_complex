import numpy as np

from ..Interface import BRModel


class TotalBRModel(BRModel):
    """
    Model for total case
    """
    def __init__(self, alpha: float, beta: float, initial_infectious: int, rho: int):
        self.alpha = alpha      # fraction of non-immune
        self.beta = beta        # effective contacts intensivity
        self.initial_infectious = initial_infectious
        self.rho = rho          # population size 

    def simulate(self, modeling_duration=150):
        # SETTING UP INITIAL CONDITIONS
        self.total_infected = np.zeros(modeling_duration)
        self.newly_infected = np.zeros(modeling_duration)
        self.susceptible = np.zeros(modeling_duration)
        self.total_infected[0] = self.initial_infectious 
        self.newly_infected[0] = self.initial_infectious
        initial_susceptible = int(self.alpha*self.rho)
        self.susceptible[0] = initial_susceptible

        # SIMULATION
        for day in range(modeling_duration-1):
            self.total_infected[day] = min(
                sum([
                        self.newly_infected[day - tau] * self.br_function(tau) 
                        for tau in range(len(self.Br_func_array))     if (day - tau) >= 0
                ]),
                self.rho
            )
            
            self.newly_infected[day+1] = min(
                self.beta * self.susceptible[day] * self.total_infected[day] / self.rho,
                self.susceptible[day]
            )

            self.susceptible[day+1] = self.susceptible[day] - self.newly_infected[day+1]        

    def get_newly_infected(self):
        return self.newly_infected

    def data_columns():
        return ['Все']