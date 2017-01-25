.. rest-api_:

OpenSky REST API
================

The root URL of our REST API is::

    https://opensky-network.org/api

There are several functions available to retrieve :ref:`state vectors <state-vectors>` for the whole network, a particular sensor, or a particular aircraft. Note that the functions to retrieve state vectors of sensors other than your own are rate limited (see :ref:`limitations`).

.. _all-states:

All State Vectors
-----------------

The following API call can be used to retrieve any state vector of the OpenSky. Please note that rate limits apply for this call (see :ref:`limitations`). For API calls without rate limitation, see :ref:`own-states`.

.. include:: rest-states-all-request.rst

Example query: :code:`https://opensky-network.org/api/states/all?time=1458564121&icao24=3c6444`

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
* Anonymous users can only retrieve data with a time resultion of 10 seconds. That means, the API will return state vectors for time :math:`now - (now\ mod\ 10)`.

Limitations for OpenSky users
"""""""""""""""""""""""""""""

An OpenSky user is anybody who uses a valid OpenSky account (see below) to access the API. The rate limitations for OpenSky users are:

* OpenSky users can retrieve data of up to 1 hour in the past. If the `time` parameter has a value :math:`t<now-3600` the API will return `400 Bad Request`.
* OpenSky users can retrieve data with a time resultion of 5 seconds. That means, if the *time* parameter was set to :math:`t`, the API will return state vectors for time :math:`t - (t\ mod\ 5)`.

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


