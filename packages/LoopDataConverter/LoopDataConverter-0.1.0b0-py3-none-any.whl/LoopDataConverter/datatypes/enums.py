from enum import IntEnum


class Datatype(IntEnum):
    GEOLOGY = 0
    STRUCTURE = 1
    FAULT = 2
    FOLD = 3
    DTM = 4
    FAULT_ORIENTATION = 5


class SurveyName(IntEnum):

    GA = 0
    NTGS = 1
    GSQ = 2
    GSWA = 3
    GSSA = 4
    GSV = 5
    MRT = 6
    GSNSW = 7


class Filetype(IntEnum):

    CSV = 0
    GEOJSON = 1
    SHP = 2
    GPKG = 3
    ZIP = 4
