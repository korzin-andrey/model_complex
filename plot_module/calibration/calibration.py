import matplotlib.pyplot as plt
from sklearn.metrics import r2_score

from model_complex import Calibration, FactoryModel, ModelParams

# from ..epid_results import prevalence_plot, recovered_plot


def calibration_plot(
    epid_data,
    city,
    method,
    type,
    save_path="./",
    epsilon=3000,
    is_prevalence_plot=False,
    is_recovered_plot=False,
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

    if method.lower() == "annealing":
        calibration.annealing_calibration()
    elif method.lower() == "abc":
        calibration.abc_calibration(epsilon=epsilon)
    elif method.lower() == "mcmc":
        calibration.mcmc_calibration(epsilon=epsilon)
    else:
        calibration.optuna_calibration()

    # if is_prevalence_plot:
    #     prevalence_plot(
    #         st_time,
    #         end_time,
    #         city,
    #         method,
    #         type,
    #         save_path,
    #         model,
    #         data.attrs["time_step"],
    #     )

    # if is_recovered_plot:
    #     recovered_plot(
    #         st_time,
    #         end_time,
    #         city,
    #         method,
    #         type,
    #         save_path,
    #         model,
    #         data.attrs["time_step"],
    #     )

    for ci_par in model.get_ci_params():
        model.simulate(params=ci_par, modeling_duration=dur)

        res = func_to_get_newly_data()

        for i in range(len(res)):
            plt.plot(res[i], lw=0.3, alpha=0.5, color=color[i])

    model.simulate(params=model.get_best_params(), modeling_duration=dur)

    res = func_to_get_newly_data()

    for i in range(len(res)):
        plt.plot(
            res[i],
            label=f"{label[i]}, $R^2$: {round(r2_score(plot_data[:, i], res[i]), 2)}",
            color=color[i],
        )
        plt.plot(plot_data[:, i], "--o", color=color[i])

    # plt.title(f"{method.capitalize()}, {type.capitalize()}")
    plt.legend()
    plt.xlabel('Week number')
    plt.ylabel('Incidence, cases')

    plt.savefig(save_path + f"_{city}_{method}_{type}_{epid_data.begin_year}-{epid_data.end_year}.png",
                dpi=600, bbox_inches="tight")
    plt.savefig(save_path + f"_{city}_{method}_{type}_{epid_data.begin_year}-{epid_data.end_year}.pdf",
                bbox_inches="tight")
    plt.clf()
