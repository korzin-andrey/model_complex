from .Models import AgeGroupBRModel, TotalBRModel


class FactoryModel:

    @classmethod
    def get_model(self, type):
        match type:
            case "total":
                return TotalBRModel()
            case "age":
                return AgeGroupBRModel()

        raise Exception("Модель не существует")

    # Arguments for models using networks passed for
    # creation of graph once during initialization.
    # @classmethod
    # def pairwise(population_size: int, m_vertices: int) -> PairwiseModel:
    #     return PairwiseModel(population_size, m_vertices)
    # @classmethod
    # def sir_network(population_size: int, m_vertices: int) -> SIRNetworkModel:
    #     return SIRNetworkModel(population_size, m_vertices)
    # @classmethod
    # def seir_network(population_size: int, m_vertices: int) -> SEIRNetworkModel:
    #     return SEIRNetworkModel(population_size, m_vertices)
