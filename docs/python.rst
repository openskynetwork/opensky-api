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
    for s in states:
        print("(%f, %f, %f, %f) % (s.longitude, s.latitude, s.altitude, s.velocity))


Example for retrieving all state vectors currently received by your receivers (no rate limit)::

    from opensky_api import OpenSkyApi
    
    api = OpenSkyApi(USERNAME, PASSWORD)
    states = api.get_my_states()
    print(states)
    for s in states:
        print(s.sensors)

