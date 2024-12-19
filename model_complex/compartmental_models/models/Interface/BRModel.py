class BRModel:
    """
    Interface for all BRModels
    """

    def __init__(self):
        self.is_calibrated: bool = False

    br_func_array = [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05]

    def __init__(self):
        self.alpha_len = (0,)
        self.beta_len = (0,)

        self.groups = []
        self.pattern = []

    def simulate(
        self,
        alpha: list[float],
        beta: list[float],
        initial_infectious: list[int],
        population_size: int,
        modeling_duration: int
    ):
        pass

    def get_newly_infected(self):
        pass

    def params(self):
        """
        TODO
        """
        return (self.alpha_len, self.beta_len)

    def br_function(self, day: int) -> int:
        """
        Baroyan-Rvachev function

        :param day: Illness day

        :return: human virulence
        """

        if day >= len(self.br_func_array):
            return 0
        return self.br_func_array[day]

    def get_params_if_calibrated(self):
        pass
