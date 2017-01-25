The response is a JSON object with the following properties

+----------------+-----------+------------------------------------------------------------------------+
| Property       | Type      | Description                                                            |
+================+===========+========================================================================+
| *time*         | integer   | The time which the state vectors in this response are associated with. |
|                |           | All vectors represent the state of a vehicle with the interval         |
|                |           | :math:`[time - 1, time]`.                                              |
+----------------+-----------+------------------------------------------------------------------------+
| *states*       | array     | The state vectors.                                                     |
+----------------+-----------+------------------------------------------------------------------------+

The *states* property is a two-dimensional array. Each row represents a :ref:`state vector <state-vectors>`
and contains the following fields:

+-------+------------------+---------+------------------------------------------------------------------+
| Index | Property         | Type    | Description                                                      |
+=======+==================+=========+==================================================================+
| 0     | *icao24*         | string  | Unique ICAO 24-bit address of the transponder in hex string      |
|       |                  |         | representation.                                                  |
+-------+------------------+---------+------------------------------------------------------------------+
| 1     | *callsign*       | string  | Callsign of the vehicle (8 chars). Can be null if no callsign    |
|       |                  |         | has been received.                                               |
+-------+------------------+---------+------------------------------------------------------------------+
| 2     | *origin_country* | string  | Country name inferred from the ICAO 24-bit address.              |
+-------+------------------+---------+------------------------------------------------------------------+
| 3     | *time_position*  | float   | Unix timestamp (seconds) for the last position update. Can be    |
|       |                  |         | null if no position report was received by OpenSky within the    |
|       |                  |         | past 15s.                                                        |
+-------+------------------+---------+------------------------------------------------------------------+
| 4     | *time_velocity*  | float   | Unix timestamp (seconds) for the last velocity update. Can be    |
|       |                  |         | null if no velocity report was received by OpenSky within the    |
|       |                  |         | past 15s.                                                        |
+-------+------------------+---------+------------------------------------------------------------------+
| 5     | *longitude*      | float   | WGS-84 longitude in decimal degrees. Can be null.                |
+-------+------------------+---------+------------------------------------------------------------------+
| 6     | *latitude*       | float   | WGS-84 latitude in decimal degrees. Can be null.                 |
+-------+------------------+---------+------------------------------------------------------------------+
| 7     | *altitude*       | float   | Barometric or geometric altitude in meters. Can be null.         |
+-------+------------------+---------+------------------------------------------------------------------+
| 8     | *on_ground*      | boolean | Boolean value which indicates if the position was retrieved from |
|       |                  |         | a surface position report.                                       |
+-------+------------------+---------+------------------------------------------------------------------+
| 9     | *velocity*       | float   | Velocity over ground in m/s. Can be null.                        |
+-------+------------------+---------+------------------------------------------------------------------+
| 10    | *heading*        | float   | Heading in decimal degrees clockwise from north (i.e. north=0°). |
|       |                  |         | Can be null.                                                     |
+-------+------------------+---------+------------------------------------------------------------------+
| 11    | *vertical_rate*  | float   | Vertical rate in m/s. A positive value indicates that the        |
|       |                  |         | airplane is climbing, a negative value indicates that it         |
|       |                  |         | descends. Can be null.                                           |
+-------+------------------+---------+------------------------------------------------------------------+
| 12    | *sensors*        | int[]   | IDs of the receivers which contributed to this state vector.     |
|       |                  |         | Is null if no filtering for sensor was used in the request.      |
+-------+------------------+---------+------------------------------------------------------------------+

