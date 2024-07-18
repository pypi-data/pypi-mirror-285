# Ecosophy EarthOS API Python bindings

These are open API bindings for Ecosophy's EarthOS API. You must have an EarthOS account
in order to use the bindings.

## Prerequisites

Before you can use these API bindings, ensure you have:
 * Python 3.9 or later.
 * An active EarthOS account with API access.

## Installation

Try:
```python
pip install earthos
```

Or, if you have cloned this from a git repository, you can also:
```python
python setup.py install
```
(Note that this method is deprecated, but it will work for now.)

## Getting started

First, log in to [EarthOS](https://earthos.ai/) and generate an API key in your organization 
settings dialog. 

Then, in Python:

```python
from earthos import EarthOS
APIKEY = 'your api key here'
eo = EarthOS(APIKEY)
```

With this in place, you can start fetching and working with the data, for example:

```python
myformula = EOVar('gfs.relative_humidity')/100.0
data = eo.get_region(north=90.0, south=-90.0, east=180.0, west=-180.0, formula=myformula)
data.show()
```

# Examples and testing

You can use `pytest` to run tests to see if your setup is accurate. Beware that these tests will count against your API credits. See code in the `tests` and `examples` directories for further examples.

# API Reference

Refer to the [Ecosophy EarthOS API documentation](https://docs.ecosophy.is) for full API documentation.

# License

This library is copyright © Ecosophy ehf 2024. It is released under the terms of the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0).

Use of the EarthOS API is subject to end user license conditions, which can be seen at https://earthos.ai/api-license

# Contact

For support or any questions, please contact us at info@ecosophy.is or through your EarthOS account.
