Operation
^^^^^^^^^

:code:`GET /states/all`

Request
^^^^^^^

You can (optionally) request state vectors for particular airplanes or times using the following request parameters:

+----------------+-----------+------------------------------------------------+
| Property       | Type      | Description                                    |
+================+===========+================================================+
| *time*         | integer   | The time in seconds since epoch (Unix time     |
|                |           | stamp to retrieve states for. Current time     |
|                |           | will be used if omitted.                       |
+----------------+-----------+------------------------------------------------+
| *icao24*       | string    | One or more ICAO24 transponder addresses       |
|                |           | represented by a hex string (e.g. `abc9f3`).   |
|                |           | To filter multiple ICAO24 append the property  |
|                |           | once for each address. If omitted, the state   |
|                |           | vectors of all aircraft are returned.          |
+----------------+-----------+------------------------------------------------+

In addition to that, it is possible to query a certain area defined by a bounding box of WGS84 coordinates.
For this purpose, add all of the following parameters:

+----------------+-----------+---------------------------------------------------+
| Property       | Type      | Description                                       |
+================+===========+===================================================+
| *lamin*        | float     | lower bound for the latitude in decimal degrees   |
+----------------+-----------+---------------------------------------------------+
| *lomin*        | float     | lower bound for the longitude in decimal degrees  |
+----------------+-----------+---------------------------------------------------+
| *lamax*        | float     | upper bound for the latitude in decimal degrees   |
+----------------+-----------+---------------------------------------------------+
| *lomax*        | float     | upper bound for the longitude in decimal degrees  |
+----------------+-----------+---------------------------------------------------+
