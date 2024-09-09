import datetime
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.integrate import odeint


class SEIRModel:
    def __init__(self, beta: float, epsilon: float, gamma: float, 
                 delta: float, initial_susceptible_fraction: float, 
                 initial_exposed_fraction: float, 
                 initial_infectious_fraction: float,
                 rho: int):
        self.model_name = "SEIRModel"
        self.beta = beta 
        self.epsilon = epsilon
        self.gamma = gamma
        self.delta = delta
        self.rho = rho # population size

        self.initial_susceptible_fraction = initial_susceptible_fraction
        self.initial_exposed_fraction = initial_exposed_fraction
        self.initial_infectious_fraction = initial_infectious_fraction
        self.initial_recovered_fraction = 1 - self.initial_susceptible_fraction - \
        self.initial_exposed_fraction - self.initial_infectious_fraction

        ### PARAMETERS BELOW ARE SET AFTER SIMULATION
        self.time = None
        self.newly_infected = None
        self.susceptible = None
        self.exposed = None
        self.infected = None
        self.recovered = None
        

    def deriv(self, y, time):
        S, E, I, R = y
        dSdt = -self.beta * S * I + self.epsilon*R
        dEdt = self.beta*S*I - self.gamma*E
        dIdt = self.gamma*E - self.delta*I
        dRdt = self.delta*I - self.epsilon*R
        return dSdt, dEdt, dIdt, dRdt
    
    def simulate(self, modeling_duration=100):
        initial_values = self.initial_susceptible_fraction, self.initial_exposed_fraction, self.initial_infectious_fraction, self.initial_recovered_fraction
        self.time = np.linspace(1, modeling_duration, modeling_duration)
        ret = odeint(self.deriv, initial_values, self.time)
        self.susceptible, self.exposed, self.infected, self.recovered = ret.T

    def plot_output(self):
        fig, ax = plt.subplots(figsize=(10,5))
        ax.plot(self.infected, '--o')
        ax.set_xlim([0, self.time[-1]])
        ax.legend(['Prevalence'])
        ax.grid()
        plt.show()
        # fig.savefig(str(self.make_params_dict()) + '.png')

if __name__ == '__main__':
    # TODO: check model, strange plots
    seir_model = SEIRModel(0.5, 0.3, 0.2, 0.1, 0.8, 0, 0.05, 10000)
    seir_model.simulate()
    seir_model.plot_output()