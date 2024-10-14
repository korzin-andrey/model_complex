import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json

type Vector = list[float]

class SimpleBRModel:
    def __init__(self, alpha: float, beta: float, initial_infectious: int,
                 rho: int, br_func_array: Vector):
        self.model_name = "SimpleBRModel"
        self.alpha = alpha # fraction of non-immune
        self.beta = beta # effective contacts intensivity
        self.initial_infectious = initial_infectious
        self.rho = rho # population size 
        self.br_func_array = br_func_array # Baroyan-Rvachev function of infectiousness

        ### PARAMETERS BELOW ARE SET AFTER SIMULATION
        self.time = None
        self.newly_infected = None
        self.susceptible = None
        self.total_infected = None


    def br_function(self, day: int):
        if day >= len(self.br_func_array):
            return 0
        return self.br_func_array[day]
        

    def simulate(self, modeling_duration=150):
        # SETTING UP INITIAL CONDITIONS
        self.time = np.linspace(1, modeling_duration, modeling_duration)
        initial_susceptible = int(self.alpha*self.rho)
        initial_infectious = self.initial_infectious
        self.total_infected = np.zeros(modeling_duration)
        self.newly_infected = np.zeros(modeling_duration)
        self.susceptible = np.zeros(modeling_duration)
        self.total_infected[0] = initial_infectious 
        self.newly_infected[0] = initial_infectious
        self.susceptible[0] = initial_susceptible

        # SIMULATION
        for day in range(modeling_duration-1):
            self.total_infected[day] = min(sum([self.newly_infected[day - tau]*self.br_function(tau) 
                                    for tau in range(len(self.br_func_array)) if (day - tau) >=0]),
                                    self.rho)
            
            self.newly_infected[day+1] = min(self.beta*self.susceptible[day]*self.total_infected[day]/self.rho,
                                             self.susceptible[day])
            self.susceptible[day+1] = self.susceptible[day] - self.newly_infected[day+1]            
        
    def plot_output(self):
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(self.newly_infected, '--o')
        # ax.plot(self.total_infected, '--o')
        # ax.plot(self.susceptible, '--o')
        # ax.hlines(self.rho, xmin=self.time[0], xmax=self.time[-1])
        ax.set_xlim([0, self.time[-1]])
        ax.legend(['Incidence', 'Prevalence', 'Susceptible'])
        ax.grid()
        plt.show()
        # fig.savefig(str(self.make_params_dict()) + '.png')

    def make_params_dict(self):
        params_dict = {}
        params_dict['alpa'] = self.alpha
        params_dict['beta'] = self.beta
        params_dict['initial_infectious'] = self.initial_infectious
        params_dict['rho'] = self.rho
        params_dict['br_func'] = self.br_func_array
        return params_dict

    def save_result(self):
        # TODO: put string of parameter dictionary in the beginning of the file
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
        file_name = r'{}_{}.csv'.format(self.model_name, current_time)
        df = pd.DataFrame(columns=['incidence', 'prevalence', 'susceptible'])
        df['incidence'] = self.newly_infected
        df['prevalence'] = self.total_infected
        df['susceptible'] = self.susceptible
        df.to_csv(file_name, index=False)


if __name__ == '__main__':
    br_model = SimpleBRModel(alpha=1, beta=0.7, initial_infectious=100, rho=5e5, 
                             br_func_array=[0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05])
    br_model.simulate(modeling_duration=80)
    br_model.plot_output()
    br_model.save_result()
