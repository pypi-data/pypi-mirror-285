from ...datatypes.enums import Datatype


class NtgsConfig:
    def __init__(self):
        self.fold_config = (
            {
                "structtype_column": "FoldEvent",
                "fold_text": "FeatureCodeDesc",
                "description_column": "Description",
                "synform_text": "FoldType",
                "foldname_column": "FoldName",
                "objectid_column": "OBJECTID",
                "tightness_column": "InterlimbAngle",
                "axial_plane_dipdir_column": "AxialPlaneDipDir",
                "axial_plane_dip_column": "AxialPlaneDip",
                "interp_source_column": "InterpSource",
            },
        )

        self.fault_config = {
            "structtype_column": "FaultType",
            "fault_text": "'Normal', 'Reverse', 'Shear zone', 'Strike-slip', 'Thrust', 'Unknown'",
            "dip_null_value": "-999",
            "dipdir_flag": "num",
            "dipdir_column": "DipDirection",
            "dip_column": "Dip",
            "orientation_type": "dip direction",
            "dipestimate_column": "DipEstimate",
            "dipestimate_text": "'NORTH_EAST','NORTH',<rest of cardinals>,'NOT ACCESSED'",
            "displacement_column": "Displacement",
            "displacement_text": "'1m-100m', '100m-1km', '1km-5km', '>5km'",
            "fault_length_column": "FaultLength",
            "fault_length_text": "'Small (0-5km)', 'Medium (5-30km)', 'Large (30-100km)', 'Regional (>100km)', 'Unclassified'",
            "name_column": "FaultName",
            "objectid_column": "OBJECTID",
            "interp_source_column": "InterpSource",
        }

        self.geology_config = {
            "unitname_column": "Formation",
            "alt_unitname_column": "CODE",
            "group_column": "GroupSuite",
            "supergroup_column": "Supergroup",
            "description_column": "LithDescription",
            "minage_column": "AgeMin",
            "maxage_column": "AgeMax",
            "rocktype_column": "LithClass",
            "alt_rocktype_column": "RockCategory",
            "sill_text": "RockCategory",
            "intrusive_text": "RockCategory",
            "volcanic_text": "RockCategory",
            "objectid_column": "OBJECTID",
            "ignore_codes": ["cover"],
        }

        self.structure_config = {
            "orientation_type": "dip direction",
            "dipdir_column": "DipDirection",
            "dip_column": "Dip",
            "description_column": "FeatureCodeDesc",
            "bedding_text": "'Bedding', 'Cleavage', 'Faulting', 'Folding', 'Foliation', 'Geophysical', 'Igneous banding', 'Lineation'",
            "overturned_column": "FeatureCodeDesc",
            "overturned_text": "overturned",
            "objectid_column": "ID",
            "interp_source_column": "InterpSource",
        }

        self.config_map = {
            Datatype.GEOLOGY: self.geology_config,
            Datatype.STRUCTURE: self.structure_config,
            Datatype.FAULT: self.fault_config,
            Datatype.FOLD: self.fold_config,
        }

    def __getitem__(self, datatype):
        return self.config_map[datatype]
