from datetime import datetime
import os
from earthos import EarthOS, EOVar, EORegion

APIKEY = os.environ.get('EARTHOS_APIKEY', None)
if not APIKEY:
    raise ValueError("Please set EARTHOS_APIKEY environment variable")
eo = EarthOS(APIKEY)

def test_region():
    data = eo.get_region(EORegion(90, -90, 180, -180), datetime.now(), "gfs.air_temperature", 1000, 500)
    assert(data.resolution() == (1000, 500))
    assert(data._data.size == 500000)   

def test_region_string():
    assert(EORegion(90, -90, 180, -180).__str__() == '90,-90,180,-180')
    assert(EORegion(64.0, -64.0, 128.0, -128.0).__str__() == '64.0,-64.0,128.0,-128.0')

def test_tile():
    data = eo.get_tile(0, 0, 0, datetime.now(), "gfs.air_temperature")
    assert(data.resolution() == (256, 256))
    assert(data._data.size == 65536)

def test_formula_tile():
    # Difference in air temperature from 24 hours ago
    airtemp_past = EOVar('gfs.air_temperature').offset(time=-(3600*24))
    airtemp_now = EOVar('gfs.air_temperature')
    airtemp_diff = airtemp_now - airtemp_past
    tile = eo.get_tile(0, 0, 0, timestamp=datetime.now(), formula=airtemp_diff)
    assert(str(airtemp_diff) == '(gfs.air_temperature - gfs.air_temperature[time: -86400])')
    assert(tile.resolution() == (256, 256))
    assert(tile._data.size == 65536)
    assert(tile._original_format == 'pfpng')
    assert(repr(tile) == '<EOImage:256x256>')

def test_save_region_pfpng():
    data = eo.get_region(EORegion(90, -90, 180, -180), datetime.now(), "gfs.air_temperature", 1000, 500)
    data.save('test.pfpng')
    assert(os.path.exists('test.pfpng'))
    os.remove('test.pfpng')

def test_save_region_png():
    data = eo.get_region(EORegion(90, -90, 180, -180), datetime.now(), "gfs.air_temperature", 1000, 500)
    cs = eo.get_colorscale('waves')
    data.save('test.png', colorscale=cs)
    assert(os.path.exists('test.png'))
    os.remove('test.png')

    data.save('test.png', colorscale='waves')
    assert(os.path.exists('test.png'))
    os.remove('test.png')

def test_region_stats():
    data = eo.get_region(EORegion(90, -90, 180, -180), datetime.now(), "gfs.air_temperature", 1000, 500)
    assert(data.min() < data.max())
    assert(data.mean() > data.min())
    assert(data.mean() < data.max())
