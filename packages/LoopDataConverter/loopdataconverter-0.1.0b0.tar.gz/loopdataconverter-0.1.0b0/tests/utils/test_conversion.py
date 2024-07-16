import pytest
from LoopDataConverter.utils import conversion


@pytest.mark.parametrize(
    "cardinal,expected",
    [
        ("N", 0.0),
        ("NE", 45.0),
        ("E", 90.0),
        ("SE", 135.0),
        ("S", 180.0),
        ("SW", 225.0),
        ("W", 270.0),
        ("NW", 315.0),
    ],
)
def test_convert_dipdir_cardinals(cardinal, expected):
    assert conversion.convert_dipdir_cardinals(cardinal) == expected


@pytest.mark.parametrize(
    "dip_term,type,expected",
    [
        ("Vertical", "fault", 90.0),
        ("Horizontal", "fault", 0.0),
        ("Moderate", "fault", 45.0),
        ("Steep", "fault", 75.0),
        ("Upright", "fold", 90.0),
        ("Recumbent", "fold", 0.0),
        ("Inclined", "fold", 45.0),
        ("Reclined", "fold", 75.0),
    ],
)
def test_convert_dip_terms(dip_term, type, expected):
    assert conversion.convert_dip_terms(dip_term, type) == expected


@pytest.mark.parametrize(
    "tightness_term,expected",
    [("gentle", 150.0), ("open", 95.0), ("close", 50.0), ("tight", 15.0), ("isoclinal", 0.0)],
)
def test_convert_tightness_terms(tightness_term, expected):
    assert conversion.convert_tightness_terms(tightness_term) == expected


@pytest.mark.parametrize(
    "displacement_term,expected",
    [("1m-100m", 50.5), ("100m-1km", 550.0), ("1km-5km", 3000.0), (">5km", 5000.0)],
)
def test_convert_displacement_terms(displacement_term, expected):
    assert conversion.convert_displacement_terms(displacement_term) == expected
