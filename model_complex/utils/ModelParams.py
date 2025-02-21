from dataclasses import dataclass


@dataclass
class ModelParams:
    """
    Contain model parameters

    :param alpha: Fraction of non-immune people
    :param beta: Effective contacts intensivity
    :param population_size: Numbers of people in simulation
    :param initial_infectious: Numbers of initial infected people in the simulation
    """

    alpha: list[float]
    beta: list[float]
    population_size: int
    initial_infectious: list[float]
