from abc import ABC, abstractmethod


class BaseConverter(ABC):

    def __init__(self):
        self._type_label = "BaseTypeConverter"

    def type(self):
        return self._type_label

    @abstractmethod
    def convert_fold_map(self):
        pass

    @abstractmethod
    def convert_fault_map(self):
        pass

    @abstractmethod
    def convert_structure_map(self):
        pass

    @abstractmethod
    def convert(self):
        pass
