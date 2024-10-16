class BRModel:
    """
    Interface for all BRModels
    """

    br_func_array = [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05]

    def simulate(self):
        ...

    def br_function(self, day: int) -> int:
        """
        Baroyan-Rvachev function

        :param day: Illness day

        :return: human virulence
        """

        if day >= len(self.br_func_array):
            return 0
        return self.br_func_array[day]
    
    def get_newly_infected(self):
        ...
    
    def data_columns(self):
        ...
