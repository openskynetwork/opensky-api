.. rest-api_:

OpenSky REST API
================

The root URL of our REST API is::

    https://opensky-network.org/api

There are several functions available to retrieve :ref:`state vectors <state-vectors>`, flights and tracks for the whole network, a particular sensor, or a particular aircraft. Note that the functions to retrieve state vectors of sensors other than your own are rate limited (see :ref:`limitations`).

.. _all-states:

All State Vectors
-----------------

The following API call can be used to retrieve any state vector of the OpenSky. Please note that rate limits apply for this call (see :ref:`limitations`). For API calls without rate limitation, see :ref:`own-states`.

.. include:: rest-states-all-request.rst

Example query with time and aircraft: :code:`https://opensky-network.org/api/states/all?time=1458564121&icao24=3c6444`


Example query with bounding box covering Switzerland: :code:`https://opensky-network.org/api/states/all?lamin=45.8389&lomin=5.9962&lamax=47.8229&lomax=10.5226`

Response
^^^^^^^^^
.. include:: states-response.rst

.. _limitations:

Limitations
^^^^^^^^^^^

Limitiations for anonymous (unauthenticated) users
""""""""""""""""""""""""""""""""""""""""""""""""""

Anonymous are those users who access the API without using credentials. The limitations for anonymous users are:

* Anonymous users can only get the most recent state vectors, i.e. the `time` parameter will be ignored.
* Anonymous users can only retrieve data with a time resolution of 10 seconds. That means, the API will return state vectors for time :math:`now - (now\ mod\ 10)`.

Limitations for OpenSky users
"""""""""""""""""""""""""""""

An OpenSky user is anybody who uses a valid OpenSky account (see below) to access the API. The rate limitations for OpenSky users are:

* OpenSky users can retrieve data of up to 1 hour in the past. If the `time` parameter has a value :math:`t<now-3600` the API will return `400 Bad Request`.
* OpenSky users can retrieve data with a time resolution of 5 seconds. That means, if the *time* parameter was set to :math:`t`, the API will return state vectors for time :math:`t - (t\ mod\ 5)`.

.. note:: You can retrieve all state vectors received by your receivers without any restrictions. See :ref:`own-states`.

Examples
^^^^^^^^^

Retrieve all states as an anonymous user:

.. code-block:: bash

    $ curl -s "https://opensky-network.org/api/states/all" | python -m json.tool


Retrieve all states as an authenticated OpenSky user:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/states/all" | python -m json.tool

Retrieve states of two particular airplanes:

.. code-block:: bash

    $ curl -s "https://opensky-network.org/api/states/all?icao24=3c6444&icao24=3e1bf9" | python -m json.tool

----

.. _own-states:

Own State Vectors
-----------------

The following API call can be used to retrieve state vectors for your own sensors without rate limitations.
Note that authentication is required for this operation, otherwise you will get a `403 - Forbidden`.

Operation
^^^^^^^^^

:code:`GET /states/own`

Request
^^^^^^^

Pass one of the following (optional) properties as request parameters to the `GET` request.

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *time*         | integer   | The time in seconds since epoch (Unix          |
|                |           | timestamp to retrieve states for. Current time |
|                |           | will be used if omitted.                       |
+----------------+-----------+------------------------------------------------+
| *icao24*       | string    | One or more ICAO24 transponder addresses       |
|                |           | represented by a hex string (e.g. `abc9f3`).   |
|                |           | To filter multiple ICAO24 append the property  |
|                |           | once for each address. If omitted, the state   |
|                |           | vectors of all aircraft are returned.          |
+----------------+-----------+------------------------------------------------+
| *serials*      | integer   | Retrieve only states of a subset of your       |
|                |           | receivers. You can pass this argument several  |
|                |           | time to filter state of more than one of your  |
|                |           | receivers. In this case, the API returns all   |
|                |           | states of aircraft that are visible to at      |
|                |           | least one of the given receivers.              |
+----------------+-----------+------------------------------------------------+


Response
^^^^^^^^

.. include:: states-response.rst

Examples
^^^^^^^^^

Retrieve states for all sensors that belong to you:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/states/own" | python -m json.tool


Retrieve states as seen by a specific sensor with serial `123456`

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/states/own?serials=123456" | python -m json.tool


Retrieve states for several receivers:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/states/own?serials=123456&serials=98765" | python -m json.tool




.. _flights-all:

Flights in Time Interval
----------------------------

This API call retrieves flights for a certain time interval [begin, end]. If no flights
are found for the given time period, HTTP status `404 - Not found` is returned with an empty
response body.

Operation
^^^^^^^^^

:code:`GET /flights/all`

Request
^^^^^^^

These are the required request parameters:

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *begin*        | integer   | Start of time interval to retrieve flights for |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+
| *end*          | integer   | End of time interval to retrieve flights for   |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+

The given time interval must not be larger than two hours!

Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties:

.. include:: flight-response.rst

Examples
^^^^^^^^^

Get flights from 12pm to 1pm on Jan 29 2018:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/flights/all?begin=1517227200&end=1517230800" | python -m json.tool


.. _flights-aircraft:

Flights by Aircraft
--------------------------------------

This API call retrieves flights for a particular aircraft within a certain time interval.
Resulting flights departed and arrived within [begin, end].
If no flights are found for the given period, HTTP stats `404 - Not found` is returned with an
empty response body. 

.. note::  Flights are updated by a batch process at night, i.e., only flights from the previous day or earlier are available using this endpoint.

Operation
^^^^^^^^^

:code:`GET /flights/aircraft`

Request
^^^^^^^

These are the required request parameters:

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *icao24*       | string    | Unique ICAO 24-bit address of the transponder  |
|                |           | in hex string representation. All letters need |
|                |           | to be lower case                               |
+----------------+-----------+------------------------------------------------+
| *begin*        | integer   | Start of time interval to retrieve flights for |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+
| *end*          | integer   | End of time interval to retrieve flights for   |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+

The given time interval must not be larger than 30 days!

Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties:

.. include:: flight-response.rst

Examples
^^^^^^^^^

Get flights for D-AIZZ (3c675a) on Jan 29 2018:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/flights/aircraft?icao24=3c675a&begin=1517184000&end=1517270400" | python -m json.tool


.. _flights-arrival:

Arrivals by Airport
--------------------------------------

Retrieve flights for a certain airport which arrived within a given time interval [begin, end].
If no flights are found for the given period, HTTP stats `404 - Not found` is returned with an
empty response body.

Operation
^^^^^^^^^

:code:`GET /flights/arrival`

Request
^^^^^^^

These are the required request parameters:

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *airport*      | string    | ICAO identier for the airport                  |
+----------------+-----------+------------------------------------------------+
| *begin*        | integer   | Start of time interval to retrieve flights for |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+
| *end*          | integer   | End of time interval to retrieve flights for   |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+

The given time interval must not be larger than seven days!


Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties:

.. include:: flight-response.rst

Examples
^^^^^^^^^

Get all flights arriving at Frankfurt International Airport (EDDF) from 12pm to 1pm on Jan 29 2018:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/flights/arrival?airport=EDDF&begin=1517227200&end=1517230800" | python -m json.tool



.. _flights-departure:

Departures by Airport
--------------------------------------

Retrieve flights for a certain airport which departed within a given time interval [begin, end].
If no flights are found for the given period, HTTP stats `404 - Not found` is returned with an
empty response body.

Operation
^^^^^^^^^

:code:`GET /flights/departure`

Request
^^^^^^^

These are the required request parameters:

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *airport*      | string    | ICAO identier for the airport (usually upper   |
|                |           | case)                                          |
+----------------+-----------+------------------------------------------------+
| *begin*        | integer   | Start of time interval to retrieve flights for |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+
| *end*          | integer   | End of time interval to retrieve flights for   |
|                |           | as Unix time (seconds since epoch)             |
+----------------+-----------+------------------------------------------------+

The given time interval must not be larger than seven days!

Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties

.. include:: flight-response.rst


Examples
^^^^^^^^^

Get all flights departing at Frankfurt International Airport (EDDF) from 12pm to 1pm on Jan 29 2018:

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/flights/departure?airport=EDDF&begin=1517227200&end=1517230800" | python -m json.tool


.. _tracks:

Track by Aircraft
------------------

.. note:: The tracks endpoint is currently **not functional**. You can use the flights endpoint for historical data: :ref:`flights-all`.

Retrieve the trajectory for a certain aircraft at a given time.  The trajectory
is a list of waypoints containing position, barometric altitude, true track and
an on-ground flag.

In contrast to state vectors, trajectories do not contain all information we
have about the flight, but rather show the aircraft's general movement
pattern.  For this reason, waypoints are selected among available state
vectors given the following set of rules:

- The first point is set immediately after the the aircraft's expected
  departure, or after the network received the first poisition when the
  aircraft entered its reception range.

- The last point is set right before the aircraft's expected arrival, or the
  aircraft left the networks reception range.

- There is a waypoint at least every 15 minutes when the aircraft is in-flight.

- A waypoint is added if the aircraft changes its track more than 2.5°.

- A waypoint is added if the aircraft changes altitude by more than 100m (~330ft).

- A waypoint is added if the on-ground state changes.

Tracks are strongly related to :ref:`flights <flights-all>`. Internally, we compute flights
and tracks within the same processing step. As such, it may be benificial to
retrieve a list of flights with the API methods from above, and use these results
with the given time stamps to retrieve detailed track information.


Operation
^^^^^^^^^

:code:`GET /tracks`

Request
^^^^^^^

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *icao24*       | string    | Unique ICAO 24-bit address of the transponder  |
|                |           | in hex string representation. All letters need |
|                |           | to be lower case                               |
+----------------+-----------+------------------------------------------------+
| *time*         | integer   | Unix time in seconds since epoch. It can be    |
|                |           | any time betwee start and end of a known       |
|                |           | flight. If time = 0, get the live track if     |
|                |           | there is any flight ongoing for the given      |
|                |           | aircraft.                                      |
+----------------+-----------+------------------------------------------------+


Response
^^^^^^^^

.. include:: track-response.rst


Limitations
^^^^^^^^^^^

It is not possible to access flight tracks from more than 30 days in the past.


Examples
^^^^^^^^^

Get the live track for aircraft with transponder address `3c4b26` (D-ABYF)

.. code-block:: bash

    $ curl -s "https://USERNAME:PASSWORD@opensky-network.org/api/tracks/all?icao24=3c4b26&time=0"

