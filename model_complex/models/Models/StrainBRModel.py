import numpy as np

from ..Interface import BRModel


class StrainBRModel(BRModel):
    """
    Model for case of several strains
    """

    br_func_array = [
        [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05],
        [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05],
        [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05],
    ]

    def br_function(self, day: int, strain: int) -> int:
        """
        Baroyan-Rvachev function

        :param day: Illness day

        :return: human virulence
        """

        if day >= len(self.br_func_array[strain]):
            return 0
        return self.br_func_array[strain][day]

    def f(h, m, a):
        """
        Function determining the proportion of persons with a history of infection h

        :param h: protected against this strain
        :param m: current strain
        :param a: Proportion of susceptible persons among those infected

        :return: people's susceptibility for current strain
        """
        return a if m == h else 1

    def simulate(
        self,
        alpha: list[float],
        beta: list[float],
        initial_infectious: list[int],
        rho: int,
        modeling_duration=150,
    ):
        """
        Download epidemiological excel data file from the subdirectory of epid_data.
        epid_data directory looks like 'epid_data/{city}/epid_data.xlsx'.

        :param alpha: Fraction of non-immune people for each strain
        :param beta: Effective contacts intensivity
        :param initial_infectious: Numbers of initial infected people in the simulation
        :param rho: Numbers of people in simulation
        :param modeling_duration: duration of modeling

        :return:
        """

        assert len(alpha) == 3 & len(beta) == 3 & len(initial_infectious) == 3

        # self.newly_infected_all = []

        # # должны ли быть фиксированными или же получать из конфига их или из gui
        # delta = 6.528
        # mu = 0.3

        # total_infected = np.zeros((3, modeling_duration))
        # newly_infected = np.zeros((3, modeling_duration))
        # susceptible = np.zeros((3, modeling_duration))

        # for m in range(3):
        #     newly_infected[m][0] = initial_infectious[m]
        #     total_infected[m][0] = initial_infectious[m]

        # for h in range(3):
        #     susceptible[h][0] = alpha[h] * ((1-mu) * rho - sum(newly_infected[:,0]))

        # # SETTING UP INITIAL CONDITIONS
        # for m in range(3):

        #     # SIMULATION
        #     for day in range(modeling_duration-1):
        #         total_infected[day] = min(
        #             sum(
        #                 newly_infected[day - tau] * self.br_function(tau)
        #                     for tau in range(len(self.br_func_array)) if (day - tau) >= 0
        #             ),
        #             rho
        #         )

        #         newly_infected[day+1] = min(
        #             sum(
        #                 beta[i][j] * susceptible[day] * total_infected[day] / rho
        #                     for i in range(2)
        #             ),
        #             susceptible[day]
        #         )

        #         susceptible[day+1] = susceptible[day] - newly_infected[day+1]

        #     self.newly_infected_all.append(newly_infected)

    def get_newly_infected(self):
        return self.newly_infected_all

    def data_columns(self, epid_data):
        return epid_data["total"]
