from dataclasses import dataclass
from ..datatypes import Datatype


@dataclass
class InputData:
    """Class to store input data for the loop data converter

    Attributes:
    geology: Datatype.GEOLOGY = None
    structure: Datatype.STRUCTURE = None
    fault: Datatype.FAULT = None
    fold: Datatype.FOLD = None

    """

    geology: Datatype.GEOLOGY = None
    structure: Datatype.STRUCTURE = None
    fault: Datatype.FAULT = None
    fold: Datatype.FOLD = None

    def __getitem__(self, datatype: Datatype):
        """Method to get the the file directory of a datatype

        Parameters:
            datatype (Datatype): The datatype to get the file directory of

        Returns:
            The file directory of the datatype
        """

        return self.__dict__[datatype]


@dataclass
class OutputData(InputData):

    def __getitem__(self, datatype: Datatype):
        return super().__getitem__(datatype)
