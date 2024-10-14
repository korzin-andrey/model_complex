from .Models import TotalBRModel
# from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
# from .Models import AgeGroupBRModel

class FactoryBRModel:
    def __new__(self, incidence: str):
        if incidence == 'total':
            return TotalBRModel

        if incidence == 'strain':
            ...

        if incidence == 'age-group':
            ...

        if incidence == 'strain_age-group':
            ...