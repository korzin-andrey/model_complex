from .Models import TotalBRModel
from .Models import StrainBRModel
# from .Models import StrainAgeGroupBRModel
from .Models import AgeGroupBRModel
from .Interface import BRModel

class FactoryModel:
    def get_model(model_type: str):
        if model_type == 'BR-total':
            return TotalBRModel()
        elif model_type == 'BR-strain':
            return StrainBRModel()
        elif model_type == 'BR-age-group':
            return AgeGroupBRModel()
        elif model_type == 'BR-strain-age-group':
            # TODO: make class StrainAgeGroupModel
            pass
        elif model_type == 'SEIR-...':
            pass
        else:
            raise Exception(f"model \"{model_type}\" does not exist")