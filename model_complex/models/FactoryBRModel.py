from .Models import TotalBRModel
from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel
from .Interface import BRModel

class FactoryBRModel:

    def total() -> BRModel:
        return TotalBRModel()

    def age_group() -> BRModel:
        return AgeGroupBRModel()
