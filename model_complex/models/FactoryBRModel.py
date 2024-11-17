from .Models import TotalBRModel
from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel
from .Interface import BRModel

class FactoryBRModel:
    @classmethod
    def total(self) -> BRModel:
        return TotalBRModel()

    @classmethod
    def age_group(self) -> BRModel:
        return AgeGroupBRModel()
