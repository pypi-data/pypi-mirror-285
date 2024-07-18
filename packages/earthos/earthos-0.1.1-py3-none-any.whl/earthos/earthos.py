import math
import requests
import os
from datetime import datetime
from typing import List, Tuple, Union
from copy import deepcopy

from .eoformula import EOFormula, EOVar, EOOffset
from .eoimage import EOData, EOColorScale, COLOR_SCALES
from .eoregion import EORegion

EARTHOS_ENGINE_HOST = os.environ.get('EARTHOS_ENGINE_HOST', 'https://engine.earthos.ai')
EARTHOS_APIKEY = os.environ.get('EARTHOS_APIKEY', None)


def num2deg(xtile, ytile, zoom):
    """
    Convert Slippy Map tile coordinates to latitude and longitude.
    """
    n = 1 << zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return lat_deg, lon_deg


def tile_to_region(x, y, z):
    # Convert Slippy Map tile coordinates to region coordinates.
    # The region coordinates are the bounding box of the tile.
    # The bounding box is in the format (north, south, east, west).
    # The tile coordinates are in the format (x, y, z).
    north, west = num2deg(x, y, z)
    south, east = num2deg(x + 1, y + 1, z)

    return EORegion(north, south, east, west)


def normalize_timestamp(timestamp) -> float:
    """
    Normalize a timestamp to a Unix timestamp.
    """
    if isinstance(timestamp, str):
        try:
            return int(timestamp)
        except ValueError:
            pass
    
        try:
            return int(float(timestamp))
        except ValueError:
            pass 

        return int(datetime.fromisoformat(timestamp).timestamp())
    
    if isinstance(timestamp, datetime):
        return int(timestamp.timestamp())

    if isinstance(timestamp, int):
        return timestamp
    
    if isinstance(timestamp, float):
        return int(timestamp)
    
    raise ValueError("Invalid timestamp format.")


class EarthOSAPIError(Exception):
    """
    Exception raised when an API request fails.
    """
    def __init__(self, message, response: requests.Response = None):
        self.message = message
        self.response = response

    def __str__(self):
        if self.response is None:
            return self.message
        return f"{self.message} ({self.response.status_code}): {self.response.text}"


class EarthOS:
    """
    EarthOS API client.
    This class provides methods to interact with the EarthOS API. It exposes a variety of methods of
    querying the EarthOS API, such as getting data for a single point, a region, or a tile.

    You are expected to provide an API key and a host URL when creating an instance of this class.
    If you do not provide an API key, the class will attempt to read it from the EARTHOS_APIKEY environment variable.
    If you do not provide a host URL, the class will attempt to read it from the EARTHOS_ENGINE_HOST environment variable.

    To obtain an API key, sign up at https://earthos.ai

    For more information on the EarthOS API, see the documentation at https://docs.ecosophy.is
    """

    def __init__(self, api_key : str = None, host : str = None):
        api_key = api_key or EARTHOS_APIKEY
        host = host or EARTHOS_ENGINE_HOST

        if not api_key: # pragma: no cover
            raise ValueError("API key is required. Provide it as a parameter or set the EARTHOS_APIKEY environment variable.")
        if not host: # pragma: no cover
            raise ValueError("EARTHOS_ENGINE_HOST environment variable is required.")
        self.api_key = api_key
        self.host = host
        self._varcache = None

    def _get(self, path, params: Union[dict, List[Tuple[str, str]], bytes] = None, **kwargs):
        """HTTP GET request to the EarthOS API."""
        url = f'{self.host}/{path}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        response = requests.get(url, headers=headers, params={} if params is None else params, **kwargs)
        if response.status_code != 200:
            self._show_error(response)
            return None

        return response
    
    def _post(self, path, data, **kwargs):
        """HTTP POST request to the EarthOS API."""
        url = f'{self.host}/{path}'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        response = requests.post(url, headers=headers, json=data, **kwargs)
        if response.status_code != 200:
            self._show_error(response)
            return None

        return response

    def get_engine_version(self):
        """Get the version of the EarthOS Engine."""
        return self._get('version/').json()
    
    def get_variables(self):
        """Get a list of all variables available in the EarthOS Engine."""
        if not self._varcache:
            self._varcache = {}
            sets = self._get('variables/').json()
            for _set in sets:
                for var in _set['variables']:
                    self._varcache[f"{var['namespace']}.{var['name']}"] = var

        return self._varcache
    
    def get_variable_namespaced(self, namespace, name):
        """Get information about a specific variable based on namespace and name."""
        vars = self.get_variables()
        return EOVar(f'{namespace}.{name}', info=vars.get(f'{namespace}.{name}', None))
    
    def get_variable(self, name):
        """Get information about a specific variable based on a single concatinated name."""
        vars = self.get_variables()
        return EOVar(name, info=vars.get(name, None))

    def get_point(self, lat, lon, alt, time, formula):
        """
        Get data for a single point in time and space.
        """
        if isinstance(formula, EOFormula):
            formula = str(formula)

        format = 'json'

        params = {
            'time': normalize_timestamp(time),
            'formula': formula,
            'format': format,
            'latitude': lat,
            'longitude': lon,
            'altitude': alt,
        }

        response = self._get('point/', params)
        return response.json()

    def get_points(self, query):
        """
        Perform a complex points query. The query payload is a dictionary
        that can contain a variety of parameters to filter and aggregate data.
        See https://docs.ecosophy.is/#evaluate-multiple-points for details.
        """
        response = self._post('points/', query)
        return response.json()

    def get_tile(self, x, y, z, timestamp, formula):
        """
        Get data for a single Slippy-style map tile at a specific time.
        """
        if isinstance(formula, EOFormula):
            formula = str(formula)

        format = 'pfpng'

        params = {
            'timestamp': normalize_timestamp(timestamp),
            'formula': formula,
            'format': format,
        }
        region = tile_to_region(x, y, z)

        response = self._get(f'map/{x}/{y}/{z}/', params)
        
        return EOData.from_pfpng(response.content, region)

    def get_region(self, region: EORegion, timestamp, formula, width: int = 2000, height: int = 1000):
        """
        Get data for a region at a specific time.
        """
        assert isinstance(region, EORegion), "Region must be an instance of EORegion."
        assert isinstance(timestamp, (str, int, float, datetime)), "Timestamp must be a string, integer, float, or datetime object."
        assert isinstance(formula, (str, EOFormula)), "Formula must be a string or EOFormula object."

        if isinstance(formula, EOFormula):
            formula = str(formula)

        format = 'pfpng'

        params = {
            'timestamp': normalize_timestamp(timestamp),
            'formula': formula,
            'format': format,
            'width': width,
            'height': height,
        }
        params.update(region.to_dict())

        response = self._get(f'map/', params)
        
        return EOData.from_pfpng(response.content, region)

    def get_colorscale(self, name):
        return deepcopy(COLOR_SCALES[name])

    def _show_error(self, response):
        """Show an error message based on the response from the API."""

        if response.status_code == 204:
            raise EarthOSAPIError("No data available for this region and time.", response)
        elif response.status_code == 400:
            raise EarthOSAPIError("Bad request", response)
        elif response.status_code == 500:
            raise EarthOSAPIError("Internal server error.", response)
        elif response.status_code == 401:
            raise EarthOSAPIError("Unauthorized. Is your API key correct?", response)
        elif response.status_code == 403:
            raise EarthOSAPIError("Forbidden. Are you allowed to access this resource?", response)
        elif response.status_code == 404:
            raise EarthOSAPIError("Not found.", response)
        else:
            raise EarthOSAPIError(f"Unknown error.", response)
