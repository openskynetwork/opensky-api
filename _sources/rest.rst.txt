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

Authentication
^^^^^^^^^^^^^^

OpenSky exclusively supports the OAuth2 *client credentials* flow. Basic authentication with username and password is no longer accepted.

To get started:

1. Log in to your OpenSky account and visit the `Account <https://opensky-network.org/my-opensky/account>`_ page.
2. Create a new API client and retrieve your ``client_id`` and ``client_secret``.
3. Exchange these for an access token, then pass it as a ``Bearer`` token on every request.

.. code-block:: bash

   export CLIENT_ID=your_client_id
   export CLIENT_SECRET=your_client_secret

   export TOKEN=$(curl -X POST "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials" \
     -d "client_id=$CLIENT_ID" \
     -d "client_secret=$CLIENT_SECRET" | jq -r .access_token)

   curl -H "Authorization: Bearer $TOKEN" https://opensky-network.org/api/states/all | jq .

Tokens expire after 30 minutes. A ``401 Unauthorized`` response means the token has expired - request a new one and retry.

Python Token Manager Example
'''''''''''''''''''''''''''''

For scripts making multiple calls, use this ``TokenManager`` class to handle token refresh automatically:

.. code-block:: python

    import requests
    from datetime import datetime, timedelta

    TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
    CLIENT_ID = "your_client_id"
    CLIENT_SECRET = "your_client_secret"

    # How many seconds before expiry to proactively refresh the token.
    TOKEN_REFRESH_MARGIN = 30


    class TokenManager:
        def __init__(self):
            self.token = None
            self.expires_at = None

        def get_token(self):
            """Return a valid access token, refreshing automatically if needed."""
            if self.token and self.expires_at and datetime.now() < self.expires_at:
                return self.token
            return self._refresh()

        def _refresh(self):
            """Fetch a new access token from the OpenSky authentication server."""
            r = requests.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                },
            )
            r.raise_for_status()

            data = r.json()
            self.token = data["access_token"]
            expires_in = data.get("expires_in", 1800)
            self.expires_at = datetime.now() + timedelta(seconds=expires_in - TOKEN_REFRESH_MARGIN)
            return self.token

        def headers(self):
            """Return request headers with a valid Bearer token."""
            return {"Authorization": f"Bearer {self.get_token()}"}


    # Create a single shared instance for your script.
    tokens = TokenManager()

    # Use it for any API call - the token is refreshed automatically.
    response = requests.get(
        "https://opensky-network.org/api/states/all",
        headers=tokens.headers(),
    )
    print(response.json())

* ``get_token()`` only fetches a new token when the current one is about to expire.
* ``headers()`` can be passed directly to any ``requests`` call.
* Create **one** ``TokenManager`` instance and reuse it for all requests in your script.

.. _limitations:

Limitations
^^^^^^^^^^^

**Anonymous users** (unauthenticated, bucketed by IP):

* Only the most recent state vectors are available - the ``time`` parameter is ignored.
* Time resolution is 10 seconds: :math:`now - (now\ \bmod\ 10)`.

**Authenticated users:**

* State vectors up to 1 hour in the past. Requests with :math:`t < now - 3600` return ``400 Bad Request``.
* Time resolution is 5 seconds: :math:`t - (t\ \bmod\ 5)`.

.. note::
    You can retrieve state vectors from your own receivers without any credit cost or time restriction. See :ref:`own-states`.

API Credits
^^^^^^^^^^^

All endpoints consume credits except ``/states/own``. Credits are tracked in **three independent buckets** - one each for ``/states/*``, ``/tracks/*``, and ``/flights/*``. Spending credits on one endpoint has no effect on the others.

**Credit quotas by tier - per endpoint (states, tracks, and flights each have their own independent quota):**

+---------------------+-----------+---------------+
| Tier                | Credits   | Refill        |
+=====================+===========+===============+
| Anonymous           | 400       | Daily         |
+---------------------+-----------+---------------+
| Standard user       | 4,000     | Daily         |
+---------------------+-----------+---------------+
| Active feeder       | 8,000     | Daily         |
| (≥30% uptime/month) |           |               |
+---------------------+-----------+---------------+
| Licensed user       | 14,400    | Hourly        |
+---------------------+-----------+---------------+

.. note::
    Active feeder status is recalculated every 2 hours. Tier upgrades take effect after ~50 requests. To confirm you are receiving the 8,000-credit allowance, check that ``X-Rate-Limit-Remaining`` exceeds 4,000 at the start of a day.

**Credit cost - ``/states/all``** (bounding box area in sq°  = latitude range × longitude range):

+---------------------+---------+
| Bounding box area   | Credits |
+=====================+=========+
| ≤ 25 sq° or         | 1       |
| serial-only query   |         |
+---------------------+---------+
| 25 – 100 sq°        | 2       |
+---------------------+---------+
| 100 – 400 sq°       | 3       |
+---------------------+---------+
| > 400 sq° or global | 4       |
+---------------------+---------+

**Credit cost - ``/flights/*`` and ``/tracks/*``** (by day partitions - calendar day boundaries crossed by the time range):

+---------------------+---------+
| Partitions          | Credits |
+=====================+=========+
| Live / < 24 h       | 4       |
+---------------------+---------+
| 1 – 2               | 30      |
+---------------------+---------+
| 3 – 10              | 60 × N  |
+---------------------+---------+
| 11 – 15             | 120 × N |
+---------------------+---------+
| 16 – 20             | 240 × N |
+---------------------+---------+
| 21 – 25             | 480 × N |
+---------------------+---------+
| > 25                | 960 × N |
+---------------------+---------+

When credits are available, ``X-Rate-Limit-Remaining`` shows your remaining balance. When exhausted, the API returns ``429 Too Many Requests`` and ``X-Rate-Limit-Retry-After-Seconds`` indicates how many seconds to wait.

Examples
^^^^^^^^^

Retrieve all states as an anonymous user:

.. code-block:: bash

    $ curl -s "https://opensky-network.org/api/states/all" | python -m json.tool


Retrieve all states as an authenticated OpenSky user:

.. code-block:: bash

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/states/all" | python -m json.tool

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

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/states/own" | python -m json.tool


Retrieve states as seen by a specific sensor with serial `123456`

.. code-block:: bash

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/states/own?serials=123456" | python -m json.tool


Retrieve states for several receivers:

.. code-block:: bash

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/states/own?serials=123456&serials=98765" | python -m json.tool




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

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/flights/all?begin=1517227200&end=1517230800" | python -m json.tool


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

The given time interval must not be larger than 2 days!

Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties:

.. include:: flight-response.rst

Examples
^^^^^^^^^

Get flights for D-AIZZ (3c675a) on Jan 29 2018:

.. code-block:: bash

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/flights/aircraft?icao24=3c675a&begin=1517184000&end=1517270400" | python -m json.tool


.. _flights-arrival:

Arrivals by Airport
--------------------------------------

Retrieve flights for a certain airport which arrived within a given time interval [begin, end].
If no flights are found for the given period, HTTP stats `404 - Not found` is returned with an
empty response body.

.. note::  Similar to flights, arrivals are updated by a batch process at night, i.e., only arrivals from the previous day or earlier are available using this endpoint.

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

The given time interval must not be larger than two days!


Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties:

.. include:: flight-response.rst

Examples
^^^^^^^^^

Get all flights arriving at Frankfurt International Airport (EDDF) from 12pm to 1pm on Jan 29 2018:

.. code-block:: bash

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/flights/arrival?airport=EDDF&begin=1517227200&end=1517230800" | python -m json.tool



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

The given time interval must cover more than two days (UTC)!

Response
^^^^^^^^

The response is a JSON array of flights where each flight is an object with the following properties

.. include:: flight-response.rst


Examples
^^^^^^^^^

Get all flights departing at Frankfurt International Airport (EDDF) from 12pm to 1pm on Jan 29 2018:

.. code-block:: bash

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/flights/departure?airport=EDDF&begin=1517227200&end=1517230800" | python -m json.tool


.. _tracks:

Track by Aircraft
------------------

.. note:: The tracks endpoint is purely **experimental**. You can use the flights endpoint for historical data: :ref:`flights-all`.

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

    $ curl -H "Authorization: Bearer $TOKEN" -s "https://opensky-network.org/api/tracks/all?icao24=3c4b26&time=0"

.. seealso::

   :ref:`trino` - For historical data spanning more than one hour, use the Trino/MinIO interface instead of the REST API.
