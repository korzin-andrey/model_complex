import scipy
import numpy as np
import pandas as pd
from models.BR_model import SimpleBRModel
import matplotlib.pyplot as plt

def generate_synthetic_data(size=20):
    model = SimpleBRModel(1, 0.52, 1, 5e6, [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05])
    model.simulate()
    data = model.newly_infected
    peak = max(model.newly_infected)
    for day in range(len(model.newly_infected)):
        data[day]+=np.random.normal(0, data)

def func(alpha, beta):
    pass
     



if __name__ == '__main__':
    plt.plot(generate_synthetic_data(), '--o')
    plt.show()