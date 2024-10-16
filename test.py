from model_complex import Calibration
import matplotlib.pyplot as plt


d = Calibration('total', 1, 1)
epid, simulation_func, data = d.calibrate('spb', './', '01-01-2019', '5-27-2019')

fig, ax = plt.subplots(1, 1, figsize=(6, 5)) 
posterior = epid.posterior.stack(samples=("draw", "chain"))
ax.plot(data, "o")
ax.plot(simulation_func(None, posterior["alpha"].mean(), posterior["beta"].mean()), 
                linewidth=3)
plt.savefig('test.png')
