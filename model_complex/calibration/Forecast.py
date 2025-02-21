from datetime import timedelta

import numpy as np
import pandas as pd

from ..models import Model


class Forecast:

    @classmethod
    def forecast(
        self,
        model: Model,
        data: pd.DataFrame,
        duration: timedelta,
    ):

        ci_params = model.get_ci_params()
        calibration_duration = len(data)
        group_cnt = len(ci_params[0].initial_infectious)

        if data.attrs["time_step"] == "week":
            calibration_duration *= 7
            get_newly_infected_base_on_time_step = (
                model.get_weekly_newly_infected_by_group
            )
            # округляем вверх кол-во недель, чтобы не выравнивать numpy матрицу
            duration = calibration_duration + (duration.days + 6) // 7 * 7
            min_mean_max_points_cnt = duration // 7
        else:
            get_newly_infected_base_on_time_step = model.get_daily_newly_infected_by_group
            duration = calibration_duration + duration.days
            min_mean_max_points_cnt = duration

        min_mean_max = np.array(
            [
                [[float("inf"), 0, float("-inf")] for _ in range(min_mean_max_points_cnt)]
                for j in range(group_cnt)
            ]
        )

        for params in ci_params:

            model.simulate(params=params, modeling_duration=duration)

            new_result = get_newly_infected_base_on_time_step()

            for i in range(group_cnt):
                min_mean_max[i, :, 0] = np.minimum(min_mean_max[i, :, 0], new_result[i])
                min_mean_max[i, :, 2] = np.maximum(min_mean_max[i, :, 2], new_result[i])

        model.simulate(params=model.get_best_params(), modeling_duration=duration)

        new_result = get_newly_infected_base_on_time_step()

        for i in range(group_cnt):
            min_mean_max[i, :, 1] = new_result[i]

        return min_mean_max
