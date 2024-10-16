from .Models import TotalBRModel
# from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
# from .Models import AgeGroupBRModel
from .Interface import BRModel

class FactoryBRModel:
    def get_model(incidence: str) -> BRModel:
        if incidence == 'total':
            return TotalBRModel()

        if incidence == 'strain':
            ...

        if incidence == 'age-group':
            ...

        if incidence == 'strain_age-group':
            ...