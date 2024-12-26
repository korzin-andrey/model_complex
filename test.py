from model_complex.compartmental_models import Calibration, EpidData, FactoryModel
import matplotlib.pyplot as plt

use_regime = 'total'
data = EpidData(city='samara', path='./', 
                start_time='01-07-2015', end_time='20-06-2016', 
                regime='total')
init_infected = [100]
model =  FactoryModel.get_model('BR-total')

d = Calibration(init_infected, model, data)
idata, data, simulation_func = d.abc_calibration()

