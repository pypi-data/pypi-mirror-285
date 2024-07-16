from .ntgs_converter import NTGSConverter
from ..datatypes import SurveyName
from ..file_readers import LoopGisReader
from ..input import InputData


class LoopConverter:
    """
    LoopConverter class use the LoopGisReader to look up the correct file
    reader for the input file type and then converting the data to
    Map2Loop or LoopStrucural formats using the adequate converter
    """

    def __init__(self, survey_name: SurveyName, data: InputData, layer: str = None):
        self._fileData = data
        self._layer = layer
        self._survey_name = survey_name
        self._converters = {
            SurveyName.NTGS: NTGSConverter,
            SurveyName.GA: "",
            SurveyName.GSQ: "",
            SurveyName.GSWA: "",
            SurveyName.GSSA: "",
            SurveyName.GSV: "",
            SurveyName.GSNSW: "",
            SurveyName.MRT: "",
        }

    def read_file(self):
        """
        read the file using the correct file reader
        """
        file_reader = LoopGisReader(self._fileData)
        file_reader.read(self._fileData, self._layer)
        return file_reader.data

    def get_converter(self):
        return self._converters[self._survey_name]

    def convert(self):
        data = self.read_file()
        converter = self.get_converter()
        converter(data)
        self.data = converter._data
