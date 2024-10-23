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
        initial_susceptible = int(alpha*rho)
        initial_infectious = initial_infectious
        total_infected = np.zeros(modeling_duration)
        newly_infected = np.zeros(modeling_duration)
        susceptible = np.zeros(modeling_duration)
        total_infected[0] = initial_infectious 
        newly_infected[0] = initial_infectious
        susceptible[0] = initial_susceptible

        # SIMULATION
        for day in range(modeling_duration-1):
            total_infected[day] = min(sum([newly_infected[day - tau]*self.br_function(tau) 
                                    for tau in range(len(self.br_func_array)) if (day - tau) >=0]),
                                    rho)
            
            newly_infected[day+1] = min(beta*susceptible[day]*total_infected[day]/rho,
                                             susceptible[day])
            susceptible[day+1] = susceptible[day] - newly_infected[day+1]      

        self.newly_infected = newly_infected    

    def get_newly_infected(self):
        return self.newly_infected

    def data_columns(self, epid_data):
        return epid_data['total']
    


if __name__ == '__main__':
    model = TotalBRModel()
    print(model.is_calibrated)
