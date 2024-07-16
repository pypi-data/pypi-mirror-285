from .base_converter import BaseConverter
from .ntgs_converter import NTGSConverter
from ..datatypes import SurveyName

converter_map = {
    SurveyName.NTGS: NTGSConverter,
    SurveyName.GA: "",
    SurveyName.GSQ: "",
    SurveyName.GSWA: "",
    SurveyName.GSSA: "",
    SurveyName.GSV: "",
    SurveyName.MRT: "",
    SurveyName.GSNSW: "",
}
