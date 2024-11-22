class BRModel:
    """
    Interface for all BRModels
    """

    br_func_array = [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05]

    def __init__(self):
        self.alpha_len = 0
        self.beta_len = 0

    def simulate(
        self,
        alpha: list[float],
        beta: list[float],
        initial_infectious: list[int],
        rho: int,
        modeling_duration: int,
    ):
        pass

    def br_function(self, day: int) -> int:
        """
        Baroyan-Rvachev function

        :param day: Illness day

        :return: human virulence
        """

        if day >= len(self.br_func_array):
            return 0
        return self.br_func_array[day]

    def params(self):
        """
        TODO
        """
        return (self.alpha_len, self.beta_len)

    def _chunk(self, lst, size):
        return [lst[i : i + size] for i in range(0, len(lst), size)]

    def get_result(self):
        size = len(self.newly_infected) // self.alpha_len

        return self._chunk(self.newly_infected, size)
