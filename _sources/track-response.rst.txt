This endpoint is inactive / deprecated.

The response is a JSON object with the following properties:

+----------------+-----------+------------------------------------------------------------------------+
| Property       | Type      | Description                                                            |
+================+===========+========================================================================+
| *icao24*       | string    | Unique ICAO 24-bit address of the transponder in lower case hex string |
|                |           | representation.                                                        |
+----------------+-----------+------------------------------------------------------------------------+
| *startTime*    | integer   | Time of the first waypoint in seconds since epoch (Unix time).         |
+----------------+-----------+------------------------------------------------------------------------+
| *endTime*      | integer   | Time of the last waypoint in seconds since epoch (Unix time).          |
+----------------+-----------+------------------------------------------------------------------------+
| *calllsign*    | string    | Callsign (8 characters) that holds for the whole track. Can be null.   |
+----------------+-----------+------------------------------------------------------------------------+
| *path*         | array     | Waypoints of the trajectory (description below).                       |
+----------------+-----------+------------------------------------------------------------------------+

Waypoints are represented as JSON arrays to save bandwidth. Each point contains the following
information:

+-------+-------------------+---------+------------------------------------------------------------------+
| Index | Property          | Type    | Description                                                      |
+=======+===================+=========+==================================================================+
| 0     | *time*            | integer | Time which the given waypoint is associated with in seconds since|
|       |                   |         | epoch (Unix time).                                               |
+-------+-------------------+---------+------------------------------------------------------------------+
| 1     | *latitude*        | float   | WGS-84 latitude in decimal degrees. Can be null.                 |
+-------+-------------------+---------+------------------------------------------------------------------+
| 2     | *longitude*       | float   | WGS-84 longitude in decimal degrees. Can be null.                |
+-------+-------------------+---------+------------------------------------------------------------------+
| 3     | *baro_altitude*   | float   | Barometric altitude in meters. Can be null.                      |
+-------+-------------------+---------+------------------------------------------------------------------+
| 4     | *true_track*      | float   | True track in decimal degrees clockwise from north (north=0°).   |
|       |                   |         | Can be null.                                                     |
+-------+-------------------+---------+------------------------------------------------------------------+
| 5     | *on_ground*       | boolean | Boolean value which indicates if the position was retrieved from |
|       |                   |         | a surface position report.                                       |
+-------+-------------------+---------+------------------------------------------------------------------+
