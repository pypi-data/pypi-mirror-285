from datetime import datetime
from earthos import EarthOS, EOVar, EOFormula

def test_formula():
    # Just convert air temperature from Celsius to Farenheit
    airtemp_farenheit = 32 + ( EOVar('gfs.air_temperature') * 9/5 )
    assert(str(airtemp_farenheit) == '(32 + ((gfs.air_temperature * 9) / 5))')

def test_complex_formula():
    # Windchill in Farenheit
    airtemp_farenheit = 32 + ( EOVar('gfs.air_temperature') * 9/5 )
    windchill_farenheit = 35.74 + (0.6215 * airtemp_farenheit) - (35.75 * (EOVar('gfs.wind_speed') ** 0.16)) + (0.4275 * airtemp_farenheit * (EOVar('gfs.wind_speed') ** 0.16))
    assert(str(windchill_farenheit) == '(((35.74 + (0.6215 * (32 + ((gfs.air_temperature * 9) / 5)))) - (35.75 * (gfs.wind_speed ^ 0.16))) + ((0.4275 * (32 + ((gfs.air_temperature * 9) / 5))) * (gfs.wind_speed ^ 0.16)))')

def test_formula_offset():
    # Difference in air temperature from 24 hours ago
    airtemp_past = EOVar('gfs.air_temperature').offset(time=-(3600*24))
    airtemp_now = EOVar('gfs.air_temperature')
    airtemp_diff = airtemp_now - airtemp_past
    assert(str(airtemp_diff) == '(gfs.air_temperature - gfs.air_temperature[time: -86400])')

def test_formula_conversions():
    test = EOVar('gfs.air_temperature') + 5
    assert(test.to_string() == '(gfs.air_temperature + 5)')
    assert((test - 5).to_string() == '((gfs.air_temperature + 5) - 5)')
    assert((test * 5).to_string() == '((gfs.air_temperature + 5) * 5)')
    assert((test / 5).to_string() == '((gfs.air_temperature + 5) / 5)')
    assert((test ** 5).to_string() == '((gfs.air_temperature + 5) ^ 5)')
    assert((5 + test).to_string() == '(5 + (gfs.air_temperature + 5))')
    assert((5 - test).to_string() == '(5 - (gfs.air_temperature + 5))')
    assert((5 * test).to_string() == '(5 * (gfs.air_temperature + 5))')
    assert((5 / test).to_string() == '(5 / (gfs.air_temperature + 5))')
    assert((5 ** test).to_string() == '(5 ^ (gfs.air_temperature + 5))')
    assert((test + test).to_string() == '((gfs.air_temperature + 5) + (gfs.air_temperature + 5))')