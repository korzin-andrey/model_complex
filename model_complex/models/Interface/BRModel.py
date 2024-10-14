class BRModel:
    """
    Interface for all models
    """
    Br_func_array = [0.1, 0.1, 1, 0.9, 0.55, 0.3, 0.15, 0.05]

    def __init__(self):
        ### PARAMETERS BELOW ARE SET AFTER SIMULATION
        self.time = None
        self.newly_infected = None
        self.susceptible = None
        self.total_infected = None

    def simulate(self):
        ...

    def br_function(self, day: int):
        if day >= len(self.Br_func_array):
            return 0
        return self.Br_func_array[day]