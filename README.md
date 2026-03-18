# The OpenSky Network API

This repository contains API client implementations for the OpenSky Network in
Python and Java as well as the sources for the [documentation](https://openskynetwork.github.io/opensky-api/). By using the OpenSky API, you agree with our [terms of use](https://opensky-network.org/about/terms-of-use). We may block AWS and other hyperscalers due to generalized abuse from these IPs.

Note that the Java implementation is not actively maintained and serves mostly as an example. The Python implementation has been updated to support OAuth2 authentication as required from March 18, 2026.

For actively maintained libraries, check our [Data Tools](https://opensky-network.org/data/tools) page, which includes many third-party and community tools. 

## Python API

* Requires Python 3.10 or later
* Depends on the [requests](http://docs.python-requests.org/) library
* Authentication uses the OAuth2 client credentials flow (see [Authentication](#authentication))

### Installation

Install directly from GitHub using pip (recommended):

```
pip install "git+https://github.com/openskynetwork/opensky-api.git#subdirectory=python"
```

Or clone the repository and install locally:

```
git clone https://github.com/openskynetwork/opensky-api.git
pip install -e opensky-api/python
```

### Authentication

Since March 18, 2026, basic authentication with username and password is no longer supported.
Authentication now uses the OAuth2 client credentials flow.

1. Log in to your OpenSky account and visit the [Account](https://opensky-network.org/my-opensky/account) page.
2. Create a new API client and download the credentials file (`credentials.json`).
3. Pass the credentials to the API client as shown below.

Without credentials, requests are made anonymously with reduced rate limits.

### Usage

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

Example output:

```
{
  'states': [
    StateVector(dict_values(['c04049', '', 'Canada', 1507203246, 1507203249, -81.126, 37.774, 10980.42, False, 245.93, 186.49, 0.33, None, 10972.8, None, False, 0])),
    StateVector(dict_values(['4240eb', 'UTA716  ', 'United Kingdom', 1507202967, 1507202981, 37.4429, 55.6265, 609.6, True, 92.52, 281.87, -3.25, None, None, '4325', False, 0])),
    StateVector(dict_values(['aa8c39', 'UAL534  ', 'United States', 1507203250, 1507203250, -118.0869, 33.8656, 1760.22, False, 111.31, 343.07, -5.2, None, 1752.6, '2643', False, 0])),
    StateVector(dict_values(['7800ed', 'CES5124 ', 'China', 1507203250, 1507203250, 116.8199, 40.2763, 3459.48, False, 181.88, 84.64, 11.7, None, 3566.16, '5632', False, 0])),...
  ],
  'time': 1507203250
}
```


## Java API

* Maven project (not yet in a public repository)
* Uses [```OkHttp```](https://square.github.io/okhttp/) for HTTP requests

### Installation

For usage with Maven

```
mvn clean install
```

Add the following dependency to your project

```
<dependency>
    <groupId>org.opensky</groupId>
    <artifactId>opensky-api</artifactId>
    <version>1.3.0</version>
</dependency>
```

### Usage

```
OpenSkyStates states = new OpenSkyApi().getStates(0);
System.out.println("Number of states: " + states.getStates().size());
```

### Using the API within Android Apps

Build and install the OpenSky API in your local repository as described above.
You can use it within your Android App by telling gradle to lookup the local repository and adding the dependencies.

In build.gradle, add the following lines

    dependencies {
        /* do not delete the other entries, just add this one */
        compile 'org.opensky:opensky-api:1.3.0'
    }

    repositories {
        mavenLocal()
        mavenCentral()
    }

Also note, that you need the [INTERNET permission](https://developer.android.com/training/basics/network-ops/connecting.html) in your manifest to use the API.

### Running behind a Proxy

If you need to use a proxy server, set the `http.proxyHost` and `http.proxyPort`
flags when starting your application:

```
java -Dhttp.proxyHost=10.0.0.10 -Dhttp.proxyPort=9090 ...
```

## Resources

* [API documentation](https://openskynetwork.github.io/opensky-api/)
* [OpenSky Discord](https://discord.gg/RPh89jpVVz)
