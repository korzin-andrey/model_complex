from .Models import TotalBRModel
from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel
from .Interface import BRModel

class FactoryModel:
    def total() -> BRModel:
        return TotalBRModel()

    def age() -> BRModel:
        return AgeGroupBRModel()