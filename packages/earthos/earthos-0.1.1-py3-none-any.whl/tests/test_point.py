from earthos import EarthOS, normalize_timestamp
import os
from datetime import datetime

APIKEY = os.environ.get('EARTHOS_APIKEY', None)
if not APIKEY:
    raise ValueError("Please set EARTHOS_APIKEY environment variable")
eo = EarthOS(APIKEY)

def test_point():
    # Hafnarhaus, Reykjavik, Iceland:
    lat = 64.149141
    lon = -21.940747
    # Relative humidity in Reykjavik, Iceland on June 24, 2024 at 16:30 UTC:
    humidity = 84.7
    points = eo.get_point(lat, lon, alt=None, time='2024-06-24T16:30:00Z', formula='gfs.relative_humidity')
    assert(type(points) == dict)
    assert('result' in points)
    assert(type(points['spacetime']) == dict)
    assert('time' in points['spacetime'])
    assert('latitude' in points['spacetime'])
    assert('longitude' in points['spacetime'])
    assert('error' in points)
    assert(points['error']['type'] == "NoError")
    assert(abs(points['spacetime']['latitude'] - lat) < 0.0001)
    assert(abs(points['spacetime']['longitude'] - lon) < 0.0001)
    assert(points['spacetime']['time'] == 1719246600)
    assert(abs(points['result'] - humidity) < 0.1)

def test_points():
    points = {
        'Reykjavik': (64.149141, -21.940747),
        'New York': (40.7128, -74.0060),
        'Tokyo': (35.6895, 139.6917),
        'Sydney': (-33.8688, 151.2093),
        'San Francisco': (37.7749, -122.4194),
    }

    formulas = [
        'gfs.relative_humidity',
        'gfs.temperature * 9 / 5 + 32',
        'gfs.wind_speed',
        'cams.column_integrated_mass_density_of_hydrogen_cyanide'
    ]

    query = {
        'default': {
            'time': datetime.now().timestamp(),
            'altitude': 2,
        },
        'points': []
    }

    fid = 0
    for formula in formulas:
        fid += 1
        for point in points:
            query['points'].append({
                'id': f"{point}_{fid}",
                'latitude': points[point][0],
                'longitude': points[point][1],
                'formula': formula,
            })

    eo.get_points(query)


def test_timestamp_normalization():
    assert(normalize_timestamp('2024-06-24T16:30:00Z') == 1719246600)
    assert(normalize_timestamp('2024-06-24T16:30:00') == 1719246600)
    assert(normalize_timestamp('2024-06-24T16:30') == 1719246600)
    assert(normalize_timestamp('2024-06-24') == 1719187200)
    assert(normalize_timestamp(1719246600) == 1719246600)
    assert(normalize_timestamp('1719246600') == 1719246600)
    assert(normalize_timestamp('1719246600.0') == 1719246600)
    assert(normalize_timestamp(1719246600.0) == 1719246600)
    assert(normalize_timestamp(1719246600.0) == 1719246600)
    assert(normalize_timestamp(1719206400) == 1719206400)
    assert(normalize_timestamp('1719206400') == 1719206400)
    assert(normalize_timestamp('1719206400.0') == 1719206400)
    assert(normalize_timestamp(1719206400.0) == 1719206400)
    assert(normalize_timestamp(1719206400.0) == 1719206400)


