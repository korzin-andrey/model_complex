from model_complex import Calibration
from model_complex import FactoryBRModel

BRModel = FactoryBRModel.get_model('total')
print(BRModel.is_calibrated)

# class Person:
#     def __init__(self):
#         self.id = 0


# class Student(Person):
#     pass


# class Factory:
#     def __init__(self):
#         self.model = Student()

#     def get_class(self):
#         return self.model

# a = Factory().get_class()
# print(a.id)
