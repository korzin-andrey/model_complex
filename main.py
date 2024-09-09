import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

from models.BR_model import SimpleBRModel
from epid_data.data_preparation import EpidData


incidence_arr = []

beta_arr = np.linspace(start=0.6, stop=0.84, num=20)
alpha_arr = np.linspace(start=0.5, stop=1,num=20)
initial_infectious_arr = np.linspace(start=100, stop=500, num=20)

for beta in tqdm(beta_arr):
    for alpha in alpha_arr:
        for initial_infectious in initial_infectious_arr:
            br_model = SimpleBRModel(alpha=alpha, beta=beta, initial_infectious=initial_infectious, 
                                     rho=5e5, br_func_array=[0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05])
            br_model.simulate(modeling_duration=52)
            incidence_arr.append(br_model.newly_infected)

fig, ax = plt.subplots(figsize=(10,5))

for arr in incidence_arr:
    ax.plot(arr, color='royalblue', alpha=0.05)
epid_data = EpidData()
epid_data.read_epid_data()
# epid_data.plot_epid_data()
epid_data.get_waves()
y_val = epid_data.waves[7][20:]
shift = 8
x_val = np.linspace(1, len(y_val), len(y_val)) + shift
ax.plot(x_val, y_val, '--o', color='orangered', zorder=10000)
ax.grid()
ax.set_xlabel('Time, weeks')
ax.set_ylabel('Incidence, cases')
ax.set_title('Baroyan-Rvachev model, wave#7')
fig.savefig('sweep.png', bbox_inches='tight')
plt.show()