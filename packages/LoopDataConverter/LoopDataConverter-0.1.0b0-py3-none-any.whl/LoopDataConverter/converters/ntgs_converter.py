# internal imports
from .base_converter import BaseConverter
from ..utils import (
    convert_dipdir_terms,
    convert_dip_terms,
    convert_tightness_terms,
    convert_displacement_terms,
)

# external imports
import pandas
import numpy


class NTGSConverter(BaseConverter):
    # TODO: modify class to take fold, fault, and structure layers as arguments
    def __init__(self, data: pandas.DataFrame):
        self.raw_data = data.copy()
        self._type_label = "NTGSConverter"
        self._data = None

    def type(self):
        return self._type_label

    def convert_fold_map(self):
        # convert dip direction terms to degrees
        self.raw_data["AxialPlaneDipDir"] = self.raw_data["AxialPlaneDipDir"].apply(
            lambda x: convert_dipdir_terms(x)
        )
        # convert dip terms to degrees
        self.raw_data["AxialPlaneDip"] = self.raw_data["AxialPlaneDip"].apply(
            lambda x: convert_dip_terms(x, type="fold")
        )
        # convert tightness terms to degrees
        self.raw_data["InterlimbAngle"] = self.raw_data["InterlimbAngle"].apply(
            lambda x: convert_tightness_terms(x)
        )

    def convert_fault_map(self):
        # convert dip direction terms to degrees
        self.raw_data["DipDirection"] = self.raw_data["DipDirection"].apply(
            lambda x: convert_dipdir_terms(x)
        )
        # convert dip terms to degrees
        self.raw_data["Dip"] = self.raw_data["Dip"].apply(
            lambda x: convert_dip_terms(x, type="fault")
        )
        self.raw_data["Displacement"] = self.raw_data["Displacement"].apply(
            lambda x: convert_displacement_terms(x)
        )

    def convert_structure_map(self):
        # discard any rows that has a dip value of -99 and does not have any esimated dip value
        condition = (self.raw_data["Dip"] != -99) & (self.raw_data["DipEstimate"] != numpy.nan)
        self.raw_data = self.raw_data[condition]
        # convert dip estimate to float (average of the range)
        condition = self.raw_data["Dip"] == -99
        self.raw_data.loc[condition, "DipEstimate"] = self.raw_data.loc[
            condition, "DipEstimate"
        ].apply(lambda x: sum(map(float, x.split("-"))) / 2)
        self.raw_data[condition, "Dip"] = self.raw_data[condition, "DipEstimate"]

    def convert(self):
        self.convert_fold_map()
        self.convert_fault_map()
        self.convert_structure_map()

        self._data = self.raw_data.copy()
