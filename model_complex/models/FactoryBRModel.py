from .Interface import BRModel

# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel, StrainBRModel, TotalBRModel


class FactoryBRModel:
    @classmethod
    def total(self) -> BRModel:
        return TotalBRModel()

    @classmethod
    def age_group(self) -> BRModel:
        return AgeGroupBRModel()
