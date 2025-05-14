import matplotlib.pyplot as plt
import numpy as np


from sklearn.metrics import r2_score
from model_complex import Calibration, FactoryModel, Forecast, ModelParams


def forecast_plot(
    forecast_duration,
    epid_data,
    city,
    method,
    type,
    save_path="./",
    epsilon=3000,
    epid_data_future=None
):

    epid_data.get_wave_data(type=type)
    data = epid_data.get_data()
    dur = epid_data.get_duration()
    plot_data = epid_data.prepare_for_plot()
    model_params = ModelParams(
        alpha=[0],
        beta=[0],
        population_size=epid_data.get_rho() // 10,
        initial_infectious=[100],
    )

    if epid_data_future is not None:
        epid_data_future.get_wave_data(type=type)
        plot_future_data = epid_data_future.prepare_for_plot()
        print(plot_future_data)
        plt.plot(np.arange(len(plot_data), len(plot_data) + len(plot_future_data)),
                 plot_future_data[:, 0], '--o', color='red', alpha=0.3, label='Future data')

    model = FactoryModel.get_model(type)

    if type == "age":
        model_params.initial_infectious = [100, 100]
        label = {0: "0-14 years", 1: "15+ years"}

    else:
        label = {0: "total"}
    color = {0: "blue", 1: "orange"}

    if data.attrs["time_step"] == "week":
        func_to_get_newly_data = model.get_weekly_newly_infected_by_group
    else:
        func_to_get_newly_data = model.get_daily_newly_infected_by_group

    calibration = Calibration(model, data, model_params)

    if method == "abc":
        calibration.abc_calibration(epsilon=epsilon)
    else:
        calibration.mcmc_calibration(epsilon=epsilon)

    forecast_result = Forecast.forecast(model, data, forecast_duration)

    model.simulate(params=model.get_best_params(), modeling_duration=dur)

    result = func_to_get_newly_data()

    for i in range(len(result)):
        for_from = len(plot_data[:, i]) - 1
        r2 = round(r2_score(plot_data[:, i], result[i]), 2)
        plt.plot(forecast_result[i, :, 1], color=color[i], alpha=0.3)
        plt.plot(
            result[i],
            label=f"{label[i]}, $R^2$: {r2}",
            color=color[i],
        )
        plt.plot(plot_data[:, i], "--o", color=color[i], label='Current data')
        plt.fill_between(
            range(for_from, len(forecast_result[i, :, 0])),
            forecast_result[i, :, 0][for_from:],
            forecast_result[i, :, 2][for_from:],
            color=color[i],
            alpha=0.1,
        )
        plt.plot(
            range(for_from, len(forecast_result[i, :, 0])),
            forecast_result[i, :, 0][for_from:],
            color=color[i],
        )
        plt.plot(
            range(for_from, len(forecast_result[i, :, 0])),
            forecast_result[i, :, 2][for_from:],
            color=color[i],
        )

    # plt.xticks(data["datetime"])
    plt.ylabel("Incidence, cases")
    plt.xlabel("Week number")
    # plt.title(f"{method.upper()}, {type.capitalize()}")
    plt.legend()

    plt.savefig(save_path + f"forecast_{city}_{method}_{type}.png", dpi=600,
                bbox_inches='tight')
    plt.savefig(save_path + f"forecast_{city}_{method}_{type}.pdf",
                bbox_inches='tight')
    plt.clf()
