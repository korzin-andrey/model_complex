from dataclasses import dataclass
import numpy as np


@dataclass
class ModelParams:
    population_size: int
    initial_infectious: list[float]
    alpha: list[float]
    beta: list[float]
