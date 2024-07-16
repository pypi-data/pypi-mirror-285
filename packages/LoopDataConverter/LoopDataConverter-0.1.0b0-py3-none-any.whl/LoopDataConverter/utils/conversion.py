import numpy
import beartype


@beartype.beartype
def convert_dipdir_cardinals(cardinal: str):
    """
    Convert cardinal directions to degrees.

    Parameters:
    cardinal (str): The cardinal direction to convert.

    return (float): The cardinal direction in degrees.
    """
    if cardinal == "N":
        return 0.0
    elif cardinal == "NNE":
        return 22.5
    elif cardinal == "NE":
        return 45.0
    elif cardinal == "ENE":
        return 67.5
    elif cardinal == "E":
        return 90.0
    elif cardinal == "ESE":
        return 112.5
    elif cardinal == "SE":
        return 135.0
    elif cardinal == "SSE":
        return 157.5
    elif cardinal == "S":
        return 180.0
    elif cardinal == "SSW":
        return 202.5
    elif cardinal == "SW":
        return 225.0
    elif cardinal == "WSW":
        return 247.5
    elif cardinal == "W":
        return 270.0
    elif cardinal == "WNW":
        return 292.5
    elif cardinal == "NW":
        return 315.0
    elif cardinal == "NNW":
        return 337.5
    else:
        return numpy.nan


def convert_dip_terms(dip_term: str, type: str):
    """
    Convert dip terms to degrees.

    Parameters:
    dip_term (str): The dip term to convert.

    return (float): The dip term in degrees.
    """
    if type == "fault":
        if dip_term == "Vertical":
            return 90.0
        elif dip_term == "Horizontal":
            return 0.0
        elif dip_term == "Moderate":
            return 45.0
        elif dip_term == "Steep":
            return 75.0
        else:
            return numpy.nan

    elif type == "fold":
        if dip_term == "Upright":
            return 90.0
        elif dip_term == "Recumbent":
            return 0.0
        elif dip_term == "Inclined":
            return 45.0
        elif dip_term == "Reclined":
            return 75.0
        else:
            return numpy.nan


def convert_tightness_terms(tightness_term: str):
    """
    Convert tightness terms to degrees.

    Parameters:
    tightness_term (str): The tightness term to convert.

    return (float): The tightness term in degrees,
    which is the average of the interlimb angle range.
    """
    if tightness_term == "gentle":
        return 150.0
    elif tightness_term == "open":
        return 95.0
    elif tightness_term == "close":
        return 50.0
    elif tightness_term == "tight":
        return 15.0
    elif tightness_term == "isoclinal":
        return 0.0
    else:
        return numpy.nan


def convert_displacement_terms(displacement_term: str):
    """
    Convert displacement terms to meters.

    Parameters:
    displacement_term (str): The displacement term to convert.

    return (float): The displacement term in meters.
    """
    if displacement_term == "1m-100m":
        return 50.5
    elif displacement_term == "100m-1km":
        return 550.0
    elif displacement_term == "1km-5km":
        return 3000.0
    elif displacement_term == ">5km":
        return 5000.0
    else:
        return numpy.nan
