OpenSky Python API
==================

Our official Python implementation can be found on github in
`this repository <http://github.com/openskynetwork/opensky-api>`_.
See the README for installation instructions.


Retrieving Data
---------------

The API is encapsulated in a single class with two methods for retrieving
:ref:`state vectors <state-vectors>`.

.. module :: opensky_api
.. autoclass :: OpenSkyApi
    :members: __init__, get_states, get_my_states

Return Types
------------

.. autoclass :: OpenSkyStates

.. autoclass :: StateVector


Examples
--------

Without any authentication you should only retrieve state vectors every 10 seconds. Any higher rate is unnecessary due to the rate limitations. Example for retrieving all states without authentication::

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

It is also possible to retrieve state vectors for a certain area. For this purpose, you need to provide a bounding box. It is defined by lower and upper bounds for longitude and latitude. The following example shows how to retrieve data for a bounding box which encompasses Switzerland::

    from opensky_api import OpenSkyApi
    
    api = OpenSkyApi()
    # bbox = (min latitude, max latitude, min longitude, max longitude)
    states = api.get_states(bbox=(45.8389, 47.8229, 5.9962, 10.5226))
    for s in states.states:
        print("(%r, %r, %r, %r)" % (s.longitude, s.latitude, s.baro_altitude, s.velocity))
