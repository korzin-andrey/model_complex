from .Models import TotalBRModel
from .Models import StrainBRModel
from .Models import PairwiseModel
from .Models import SIRNetworkModel
from .Models import SEIRNetworkModel
# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel
from .Interface import BRModel


class FactoryModel:
    def total() -> BRModel:
        return TotalBRModel()

    def age() -> BRModel:
        return AgeGroupBRModel()

    # Arguments for models using networks passed for
    # creation of graph once during initialization.
    def pairwise(population_size: int, m_vertices: int) -> PairwiseModel:
        return PairwiseModel(population_size, m_vertices)

    def sir_network(population_size: int, m_vertices: int) -> SIRNetworkModel:
        return SIRNetworkModel(population_size, m_vertices)

    def seir_network(population_size: int, m_vertices: int) -> SEIRNetworkModel:
        return SEIRNetworkModel(population_size, m_vertices)
