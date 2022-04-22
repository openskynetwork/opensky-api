# The official OpenSky Network API

This repository contains API client implementations for the OpenSky Network in
Python and Java as well as the sources for the [documentation](https://openskynetwork.github.io/opensky-api/). By using the OpenSky API, you agree with our [terms of use](https://opensky-network.org/about/terms-of-use).



## Python API

* depends on the python-requests library (http://docs.python-requests.org/)
* both compatible with Python 2 and 3 (tested with 2.7 and 3.5)

### Installation

```
sudo python setup.py install
```

or with pip (recommended)

```
pip install -e /path/to/repository/python
```

### Usage

```
from opensky_api import OpenSkyApi
api = OpenSkyApi()
s = api.get_states()
print(s)
```

will output something like this:

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

* [API documentation](https://opensky-network.org/apidoc)
* [OpenSky Forum](https://opensky-network.org/forum)
