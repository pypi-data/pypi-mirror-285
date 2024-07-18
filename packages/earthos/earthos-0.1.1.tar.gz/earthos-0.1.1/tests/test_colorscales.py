from datetime import datetime
from copy import deepcopy
import os
from earthos import EarthOS, EOVar, EORegion, EOColorScale, COLOR_SCALES

APIKEY = os.environ.get('EARTHOS_APIKEY', None)
if not APIKEY:
    raise ValueError("Please set EARTHOS_APIKEY environment variable")
eo = EarthOS(APIKEY)

def test_colorscale_with_minmax():
    airtemp = EOVar('gfs.air_temperature')
    tile = eo.get_tile(0, 0, 0, timestamp=datetime(2024, 5, 10, 12, 0), formula=airtemp)
    template = COLOR_SCALES['waves']
    cs = EOColorScale(colors=template.colors, offsets=template.offsets, data=tile)
    assert(cs.min == -56.61235809326172) # Lowest air temperature on Earth at this time
    assert(cs.max == 44.931297302246094) # Highest air temperature on Earth at this time
    assert(tile.resolution() == (256, 256))
    assert(tile._data.size == 65536)

def test_colorscale_from_json():
    cs = EOColorScale.from_json({
        'colors': [(0, 0, 255, 255), (255, 0, 0, 255)],
        'offsets': [0, 1],
        'min': 30,
        'max': 500
    })
    assert(cs.min == 30)
    assert(cs.max == 500)
    assert(cs.colors == [(0, 0, 255, 255), (255, 0, 0, 255)])
    assert(cs.offsets == [0, 1])


def test_colorscale_add_color():
    cs = deepcopy(COLOR_SCALES['black-white'])
    cs.add_color((255, 0, 0, 255), 0.5)     # Black, Red, White
    assert(cs.offsets == [0, 0.5, 1])
    assert(cs.colors == [(0, 0, 0, 255), (255, 0, 0, 255), (255, 255, 255, 255)])

    cs.add_color((0, 255, 0, 255), 1.0)     # Black, Red, White, Blue
    assert(cs.offsets == [0, 0.5, 1, 1])    # A bit weird to have two colors in one point, but it's technically possible
    assert(cs.colors == [(0, 0, 0, 255), (255, 0, 0, 255), (255, 255, 255, 255), (0, 255, 0, 255)])


def test_colorscale_to_json():
    cs = COLOR_SCALES['black-white']
    js = cs.to_json()
    assert(js == {
        'colors': [(0, 0, 0, 255), (255, 255, 255, 255)],
        'offsets': [0, 1],
        'min': 0,
        'max': 1
    })


def test_colorscale_interpolate():
    cs = COLOR_SCALES['black-white']
    assert(cs._interpolate((0, 0, 0, 255), (255, 255, 255, 255), 0.5) == (127, 127, 127, 255))
    assert(cs._interpolate((0, 0, 0, 255), (255, 255, 255, 255), 0.0) == (0, 0, 0, 255))
    assert(cs._interpolate((0, 0, 0, 255), (255, 255, 255, 255), 1.0) == (255, 255, 255, 255))
    assert(cs._interpolate((0, 0, 0, 255), (255, 255, 255, 255), 0.25) == (63, 63, 63, 255))
    assert(cs._interpolate((0, 0, 0, 255), (255, 255, 255, 255), 0.75) == (191, 191, 191, 255))


def test_colorscale_getvalue_two_colors():
    cs = deepcopy(COLOR_SCALES['black-white'])
    val = cs.get_color(0.5)
    assert(val == (127, 127, 127, 255))
    cs.min = -100
    cs.max = 100
    val = cs.get_color(0, rescale=True)
    assert(val == (127, 127, 127, 255))

def test_colorscale_getvalue_many_colors():
    cs = deepcopy(COLOR_SCALES['waves'])
    assert(cs.get_color(0.00) == (0, 0, 255, 255))
    assert(cs.get_color(0.25) == (0, 255, 255, 255))
    assert(cs.get_color(0.50) == (255, 255, 255, 255))
    assert(cs.get_color(0.75) == (255, 0, 255, 255))
    assert(cs.get_color(1.00) == (0, 0, 255, 255))
    
    cs.min = -100
    cs.max = 100
    assert(cs.get_color(0, rescale=True) == (255, 255, 255, 255))
    assert(cs.get_color(50, rescale=True) == (255, 0, 255, 255))

