OpenSky Python API
==================

Our official Python implementation can be found on github in
`this repository <http://github.com/openskynetwork/opensky-api>`_.
See the README for installation instructions.


Retrieving Data
---------------

The API is encapsulated in a single class with methods for data retrieving.

.. module :: opensky_api
.. autoclass :: OpenSkyApi
    :members: __init__, get_states, get_my_states, get_flights_from_interval, get_flights_by_aircraft, get_arrivals_by_airport, get_departures_by_airport, get_track_by_aircraft

Return Types
------------

.. autoclass :: OpenSkyStates

.. autoclass :: StateVector

.. autoclass :: FlightData

.. autoclass :: Waypoint

.. autoclass :: FlightTrack


Examples
--------

Without any authentication you should only retrieve state vectors every 10 seconds. Any higher rate is unnecessary due
to the rate limitations and strongly advised against. Example for retrieving all states without authentication::

    from opensky_api import OpenSkyApi
    
    api = OpenSkyApi()
    states = api.get_states()
    for s in states.states:
        print("(%r, %r, %r, %r)" % (s.longitude, s.latitude, s.baro_altitude, s.velocity))


Example for retrieving all state vectors currently received by your receivers (no rate limit)::

    from opensky_api import OpenSkyApi
    
    api = OpenSkyApi(USERNAME, PASSWORD)
    states = api.get_my_states()
    print(states)
    for s in states.states:
        print(s.sensors)

It is also possible to retrieve state vectors for a certain area. For this purpose, you need to provide a bounding box.
It is defined by lower and upper bounds for longitude and latitude. The following example shows how to retrieve data
for a bounding box which encompasses Switzerland::

    from opensky_api import OpenSkyApi
    
    api = OpenSkyApi()
    # bbox = (min latitude, max latitude, min longitude, max longitude)
    states = api.get_states(bbox=(45.8389, 47.8229, 5.9962, 10.5226))
    for s in states.states:
        print("(%r, %r, %r, %r)" % (s.longitude, s.latitude, s.baro_altitude, s.velocity))

You can retrieve FlightData from a specific time interval, using the `get_flights_from_interval` method. To do this,
provide the beginning and end of the time period, as a timestamps. It's important, that provided time interval must not
be greater than 2 hours. The following example shows how to retrieve the FlightData frames from 12pm to 1pm on Jan 29
2018::

    from opensky_api import OpenSkyApi
    api = OpenSkyApi()
    data = api.get_flights_from_interval(1517227200, 1517230800)
    for flight in data:
        print(flight)

The `get_flights_by_aircraft` method enables you to retrieve flights of a certain aircraft in time interval. To do this,
specify the unique ICAO 24-bit aircraft address in hex string representation, the beginning and end of the time interval
in the form of timestamps. The time interval must be smaller than 30 days. The example below shows steps to follow to
get flights for D-AIZZ (3c675a), on Jan 29 2018::

    from opensky_api import OpenSkyApi
    api = OpenSkyApi()
    data = api.get_flights_by_aircraft("3c675a", 1517184000, 1517270400)
    for flight in data:
        print(flight)

It's possible to retrieve arrivals and departures for a specific airport and time interval, using
`get_arrivals_by_airport` and `get_departures_by_airport` methods. Both methods require the ICAO identifier for the
airport, start and end of the time period. The time interval must be smaller than 7 days. The following code shows how
to retrieve the arrivals and departures at Frankfurt International Airport (EDDF) from 12pm to 1pm on Jan 29 2018::

    from opensky_api import OpenSkyApi
    api = OpenSkyApi()
    arrivals = api.get_arrivals_by_airport("EDDF", 1517227200, 1517230800)
    departures = api.get_departures_by_airport("EDDF", 1517227200, 1517230800)
    print("Arrivals:")
    for flight in arrivals:
        print(flight)
    print("Departures:")
    for flight in departures:
        print(flight)

The `get_track_by_aircraft` method enables you to retrieve trajectory of the aircraft. Trajectory is given as a list of
waypoints containing position, barometric altitude, true track and on-ground flag. In order to get the trajectory of the
certain aircraft, you need to provide unique ICAO 24-bit aircraft address in hex string representation and optionally
the timestamp between the start and end of a flight to be tracked. The default value of the timestamp, for the live
tracking is 0. It is not possible to access flight tracks from more than 30 days in the past. The example below shows
how to get the live track for aircraft with transponder address 3c4b26 (D-ABYF)::

    from opensky_api import OpenSkyApi
    api = OpenSkyApi()
    track = api.get_track_by_aircraft("3c4b26")
    print(track)

