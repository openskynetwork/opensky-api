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
