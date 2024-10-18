from .Models import TotalBRModel
from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel
from .Interface import BRModel

class FactoryBRModel:
    def get_model(incidence: str) -> BRModel:
        if incidence == 'total':
            return TotalBRModel()

        elif incidence == 'strain':
            return StrainBRModel()

        elif incidence == 'age-group':
            return AgeGroupBRModel()

        elif incidence == 'strain_age-group':
            ...

        else:
            raise Exception(f"model \"{incidence}\" does not exist")