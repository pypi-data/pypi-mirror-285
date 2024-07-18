from earthos import EarthOS, EOColorScale, COLOR_SCALES, EOVar
import os

APIKEY = os.environ.get('EARTHOS_APIKEY', None)
if not APIKEY:
    raise ValueError("Please set EARTHOS_APIKEY environment variable")
eo = EarthOS(APIKEY)

def test_variable_list():
    variables = eo.get_variables()
    assert(type(variables) == dict)

def test_variable():
    var = eo.get_variable('gfs.relative_humidity')
    assert(type(var) == EOVar)
    assert(var._namespace == 'gfs')
    assert(var._name == 'relative_humidity')
    assert(type(var._info) == dict)
    assert(var._info["source_type"] == "SPATIOTEMPORAL")

def test_variable_split():
    var = eo.get_variable_namespaced('gfs', 'relative_humidity')
    assert(type(var) == EOVar)
    assert(var._namespace == 'gfs')
    assert(var._name == 'relative_humidity')
    assert(type(var._info) == dict)
    assert(var._info["source_type"] == "SPATIOTEMPORAL")
    