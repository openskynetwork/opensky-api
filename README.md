# The official OpenSky Network API

This repository contains API client implementations for the OpenSky Network in
Python and Java as well as the sources for the [documentation](https://opensky-network.org/apidoc). By using the OpenSky API, you agree with our [terms of use](https://opensky-network.org/about/terms-of-use).



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
{   'earliest': 1371222960,
    'states': [   {   'altitude': 9075.42,
    'callsign': 'YZR7453',
    'heading': 124.78,
    'icao24': '78072a',
    'latitude': 51.626,
    'longitude': 6.8621,
    'on_ground': False,
    'origin_country': 'China',
    'sensors': [90003, 90002, 90006],
    'time_position': 1456583158,
    'time_velocity': 1456583158,
    'velocity': 248,
    'vertical_rate': 0},
                  {   'altitude': 4564.38,
    'callsign': 'XK103JA',
    'heading': 45,
    'icao24': '3945f8',
    'latitude': 42.9847,
    'longitude': 7.7095,
    'on_ground': False,
    'origin_country': 'France',
    'sensors': [31813],
    'time_position': 1456583158,
    'time_velocity': 1456582189,
    'velocity': 59.16,
    'vertical_rate': None},
    ...
```


## Java API

* Maven project (not yet in a public repository)
* Uses [```HTTP Components```](http://hc.apache.org/) for HTTP requests

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
    <version>1.0.0</version>
</dependency>
```

### Usage

```
OpenSkyStates states = new OpenSkyApi().getStates(0);
System.out.println("Number of states: " + states.getStates().size());
```

### Proxy configuration

To set a proxy for API request set prxy setting after OpenSkyApi initialization.

```
OpenSkyApi api = new OpenSkyApi();
api.setProxy(new HttpHost("proxy_adress",proxy_port);
```

### Using the API within Android Apps

Build and install the OpenSky API in your local repository as described above.
You can use it within your Android App by telling gradle to lookup the local repository and adding the dependencies.
As Android ships an [incompatible fork](https://hc.apache.org/httpcomponents-client-4.3.x/android-port.html) of the HttpClient library, you also need to add a dependency for HttpClient.

In build.gradle, add the following lines

    dependencies {
        /* do not delete the other entries, just add those below */
        compile 'org.opensky:opensky-api:1.0.0'
        compile 'org.apache.httpcomponents:httpclient-android:4.3.5.1'
    }

    repositories {
        mavenLocal()
        mavenCentral()
    }

Also note, that you need the [INTERNET permission](https://developer.android.com/training/basics/network-ops/connecting.html) in your manifest to use the API.

## Resources

* [API documentation](https://opensky-network.org/apidoc)
* [OpenSky Forum](https://opensky-network.org/forum)
