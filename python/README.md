# OpenSky Network Python API

Official Python client for the [OpenSky Network REST API](https://openskynetwork.github.io/opensky-api/).
By using the OpenSky API, you agree with the [terms of use](https://opensky-network.org/about/terms-of-use).

## Requirements

* Python 3.10 or later
* [requests](http://docs.python-requests.org/) library

## Installation

Install directly from GitHub using pip (recommended):

```
pip install "git+https://github.com/openskynetwork/opensky-api.git#subdirectory=python"
```

Or clone the repository and install locally:

```
git clone https://github.com/openskynetwork/opensky-api.git
pip install -e opensky-api/python
```

## Authentication

Since March 18, 2026, basic authentication with username and password is no longer supported.
Authentication now uses the OAuth2 client credentials flow.

1. Log in to your OpenSky account and visit the [Account](https://opensky-network.org/my-opensky/account) page.
2. Create a new API client and download the credentials file (`credentials.json`).
3. Pass the credentials to the API client as shown below.

Without credentials, requests are made anonymously with reduced rate limits.

## Usage

Anonymous access (reduced rate limits):

```python
from opensky_api import OpenSkyApi

api = OpenSkyApi()
s = api.get_states()
print(s)
```

Authenticated access using a credentials file:

```python
from opensky_api import OpenSkyApi, TokenManager

api = OpenSkyApi(token_manager=TokenManager.from_json_file("credentials.json"))
s = api.get_states()
print(s)
```

The token is refreshed automatically before it expires, so no manual token management is required.

The client also supports use as a context manager:

```python
with OpenSkyApi(token_manager=TokenManager.from_json_file("credentials.json")) as api:
    states = api.get_states(bbox=(47.2, 55.1, 5.9, 15.1))
```

### Example output

```
{
  'states': [
    StateVector(dict_values(['c04049', '', 'Canada', 1507203246, 1507203249, -81.126, 37.774, 10980.42, False, 245.93, 186.49, 0.33, None, 10972.8, None, False, 0])),
    StateVector(dict_values(['4240eb', 'UTA716  ', 'United Kingdom', 1507202967, 1507202981, 37.4429, 55.6265, 609.6, True, 92.52, 281.87, -3.25, None, None, '4325', False, 0])),
    ...
  ],
  'time': 1507203250
}
```

## Resources

* [Full API documentation](https://openskynetwork.github.io/opensky-api/)
* [OpenSky Discord](https://discord.gg/RPh89jpVVz)
* [Data Tools](https://opensky-network.org/data/tools) – third-party and community libraries
