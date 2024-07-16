import pytest
import geopandas
import pandas
import shapely
from LoopDataConverter.file_readers import GeoDataFileReader
import os
import tempfile


# build structures file
structures = [
    {
        'x': 2775.287768202244933,
        'y': 4330.15,
        'strike2': 45.00,
        'dip_2': 45.70,
        'id': 147.00,
        'sf': 's0',
    },
    {
        'x': 3529.794754080061011,
        'y': 3091.192011237949828,
        'strike2': 288.50,
        'dip_2': 41.70,
        'id': 204.00,
        'sf': 's0',
    },
    {
        'x': 7928.315269200518742,
        'y': 7234.561058065713951,
        'strike2': 48.80,
        'dip_2': 41.10,
        'id': 229.00,
        'sf': 's0',
    },
    {
        'x': 8003.966104268994968,
        'y': 7421.634268009857806,
        'strike2': 48.80,
        'dip_2': 41.10,
        'id': 235.00,
        'sf': 's0',
    },
    {
        'x': 6881.165236574942355,
        'y': 1213.128646564158771,
        'strike2': 299.10,
        'dip_2': 44.70,
        'id': 252.00,
        'sf': 's0',
    },
    {
        'x': 3674.015651128655009,
        'y': 5266.677487068354822,
        'strike2': 41.20,
        'dip_2': 40.10,
        'id': 347.00,
        'sf': 's0',
    },
    {
        'x': 3970.895076049027921,
        'y': 2944.223069901633608,
        'strike2': 273.00,
        'dip_2': 46.00,
        'id': 408.00,
        'sf': 's0',
    },
]

for row in structures:
    row['geometry'] = shapely.Point(row['x'], row['y'])
    del row['x'], row['y']

shp_structures = geopandas.GeoDataFrame(structures, crs='epsg:7854')
# csv_structures = pandas.DataFrame(structures)
f_path = tempfile.mkdtemp()
shp_structures.to_file(os.path.join(f_path, "structures.shp"))
shp_structures.to_file(os.path.join(f_path, "structures.geojson"), driver="GeoJSON")


# csv_structures.to_csv(os.path.join(f_path, "structures.csv"))
# Fixtures for sample file sources
@pytest.fixture
def shp_file_source():
    # Assuming a sample .shp file exists for testing
    return os.path.join(f_path, "structures.shp")


@pytest.fixture
def geojson_file_source():
    # Assuming a sample .geojson file exists for testing
    return os.path.join(f_path, "structures.geojson")


# @pytest.fixture
# def gpkg_file_source():
#     # Assuming a sample .gpkg file exists for testing, with a layer name
#     return "sample_data/sample.gpkg", "layer1"


@pytest.fixture
def invalid_file_source():
    return "sample_data/invalid.txt"


# Test Initialization
def test_initialization():
    reader = GeoDataFileReader()
    assert reader.file_reader_label == "GeoDataFileReader"


# Test Check Source Type
def test_check_source_type_valid(shp_file_source, geojson_file_source):
    reader = GeoDataFileReader()
    # Assuming these calls do not raise an exception
    reader.check_source_type(shp_file_source)
    reader.check_source_type(geojson_file_source)
    # reader.check_source_type(gpkg_file_source[0])


def test_check_source_type_invalid(invalid_file_source):
    reader = GeoDataFileReader()
    with pytest.raises(AssertionError):
        reader.check_source_type(invalid_file_source)


# Test Get File
@pytest.mark.parametrize("file_source", ["shp_file_source", "geojson_file_source"])
def test_get_file(file_source, request):
    reader = GeoDataFileReader()
    file_source = request.getfixturevalue(file_source)
    if isinstance(file_source, tuple):
        file, layer = file_source
        df = reader.get_file(file, layer)
    else:
        df = reader.get_file(file_source)
    assert isinstance(df, geopandas.GeoDataFrame)


def test_get_file_unsupported(invalid_file_source):
    reader = GeoDataFileReader()
    with pytest.raises(ValueError):
        reader.get_file(invalid_file_source)


# Test Read Method
def test_read_method_shp(shp_file_source):
    reader = GeoDataFileReader()
    reader.read(shp_file_source)
    assert isinstance(reader.data, geopandas.GeoDataFrame)


def test_read_method_geojson(geojson_file_source):
    reader = GeoDataFileReader()
    reader.read(geojson_file_source)
    assert isinstance(reader.data, geopandas.GeoDataFrame)


# Test Save Method
def test_save_method(geojson_file_source):
    reader = GeoDataFileReader()
    reader.read(geojson_file_source)
    with tempfile.TemporaryDirectory() as tmpdirname:
        save_path = os.path.join(tmpdirname, "output.geojson")
        reader.save(save_path, "geojson")
        assert os.path.exists(save_path)


def test_save_method_unsupported(geojson_file_source):
    reader = GeoDataFileReader()
    reader.read(geojson_file_source)
    with pytest.raises(ValueError):
        reader.save("output.unsupported")
