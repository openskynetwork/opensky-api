+--------------------------------------------+---------+-----------------------------------------------------+
| Property                                   | Type    | Description                                         |
+============================================+=========+=====================================================+
| *icao24*                                   | string  | Unique ICAO 24-bit address of the transponder in    |
|                                            |         | hex string representation. All letters are lower    |
|                                            |         | case.                                               |
+--------------------------------------------+---------+-----------------------------------------------------+
| *firstSeen*                                | integer | Estimated time of departure for the flight as Unix  |
|                                            |         | time (seconds since epoch).                         |
+--------------------------------------------+---------+-----------------------------------------------------+
| *estDepartureAirport*                      | string  | ICAO code of the estimated departure airport. Can   |
|                                            |         | be null if the airport could not be identified.     |
+--------------------------------------------+---------+-----------------------------------------------------+
| *lastSeen*                                 | integer | Estimated time of arrival for the flight as Unix    |
|                                            |         | time (seconds since epoch)                          |
+--------------------------------------------+---------+-----------------------------------------------------+
| *estArrivalAirport*                        | string  | ICAO code of the estimated arrival airport. Can be  |
|                                            |         | null if the airport could not be identified.        |
+--------------------------------------------+---------+-----------------------------------------------------+
| *callsign*                                 | string  | Callsign of the vehicle (8 chars). Can be null if   |
|                                            |         | no callsign has been received. If the vehicle       |
|                                            |         | transmits multiple callsigns during the flight, we  |
|                                            |         | take the one seen most frequently                   |
+--------------------------------------------+---------+-----------------------------------------------------+
| *estDepartureAirportHorizDistance*         | integer | Horizontal distance of the last received airborne   |
|                                            |         | position to the estimated departure airport in      |
|                                            |         | meters                                              |
+--------------------------------------------+---------+-----------------------------------------------------+
| *estDepartureAirportVertDistance*          | integer | Vertical distance of the last received airborne     |
|                                            |         | position to the estimated departure airport in      |
|                                            |         | meters                                              |
+--------------------------------------------+---------+-----------------------------------------------------+
| *estArrivalAirportHorizDistance*           | integer | Horizontal distance of the last received airborne   |
|                                            |         | position to the estimated arrival airport in meters |
+--------------------------------------------+---------+-----------------------------------------------------+
| *estArrivalAirportVertDistance*            | integer | Vertical distance of the last received airborne     |
|                                            |         | position to the estimated arrival airport in meters |
+--------------------------------------------+---------+-----------------------------------------------------+
| *departureAirportCandidatesCount*          | integer | Number of other possible departure airports. These  |
|                                            |         | are airports in short distance to                   |
|                                            |         | *estDepartureAirport*.                              |
+--------------------------------------------+---------+-----------------------------------------------------+
| *arrivalAirportCandidatesCount*            | integer | Number of other possible departure airports. These  |
|                                            |         | are airports in short distance to                   |
|                                            |         | *estArrivalAirport*.                                |
+--------------------------------------------+---------+-----------------------------------------------------+
