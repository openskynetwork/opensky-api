#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Official OpenSky Network API client implementation
#
# Author: Markus Fuchs <fuchs@opensky-network.org>
# URL:    http://github.com/openskynetwork/opensky-api
#
# Dependencies: requests (http://docs.python-requests.org/)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import calendar
import logging
import pprint
import time
from collections import defaultdict
from datetime import datetime

import requests

logger = logging.getLogger("opensky_api")
logger.addHandler(logging.NullHandler())


class StateVector(object):
    """Represents the state of a vehicle at a particular time. It has the following fields:

    |  **icao24**: `str` - ICAO24 address of the transmitter in hex string representation.
    |  **callsign**: `str` - callsign of the vehicle. Can be None if no callsign has been received.
    |  **origin_country**: `str` - inferred through the ICAO24 address.
    |  **time_position**: `int` - seconds since epoch of last position report. Can be None if there was no position
      report received by OpenSky within 15s before.
    |  **last_contact**: `int` - seconds since epoch of last received message from this transponder.
    |  **longitude**: `float` - in ellipsoidal coordinates (WGS-84) and degrees. Can be None.
    |  **latitude**: `float` - in ellipsoidal coordinates (WGS-84) and degrees. Can be None.
    |  **geo_altitude**: `float` - geometric altitude in meters. Can be None.
    |  **on_ground**: `bool` - true if aircraft is on ground (sends ADS-B surface position reports).
    |  **velocity**: `float` - over ground in m/s. Can be None if information not present.
    |  **true_track**: `float` - in decimal degrees (0 is north). Can be None if information not present.
    |  **vertical_rate**: `float` - in m/s, incline is positive, decline negative. Can be None if information not
      present.
    |  **sensors**: `list` [`int`] - serial numbers of sensors which received messages from the vehicle within
      the validity period of this state vector. Can be None if no filtering for sensor has been requested.
    |  **baro_altitude**: `float` - barometric altitude in meters. Can be None.
    |  **squawk**: `str` - transponder code aka Squawk. Can be None.
    |  **spi**: `bool` - special purpose indicator.
    |  **position_source**: `int` - origin of this state's position: 0 = ADS-B, 1 = ASTERIX, 2 = MLAT, 3 = FLARM
    |  **category**: `int` - aircraft category: 0 = No information at all, 1 = No ADS-B Emitter Category Information,
      2 = Light (< 15500 lbs), 3 = Small (15500 to 75000 lbs), 4 = Large (75000 to 300000 lbs),
      5 = High Vortex Large (aircraft such as B-757), 6 = Heavy (> 300000 lbs),
      7 = High Performance (> 5g acceleration and 400 kts), 8 = Rotorcraft, 9 = Glider / sailplane,
      10 = Lighter-than-air, 11 = Parachutist / Skydiver, 12 = Ultralight / hang-glider / paraglider,
      13 = Reserved, 14 = Unmanned Aerial Vehicle, 15 = Space / Trans-atmospheric vehicle,
      16 = Surface Vehicle – Emergency Vehicle, 17 = Surface Vehicle – Service Vehicle,
      18 = Point Obstacle (includes tethered balloons), 19 = Cluster Obstacle, 20 = Line Obstacle.
    """

    keys = [
        "icao24",
        "callsign",
        "origin_country",
        "time_position",
        "last_contact",
        "longitude",
        "latitude",
        "baro_altitude",
        "on_ground",
        "velocity",
        "true_track",
        "vertical_rate",
        "sensors",
        "geo_altitude",
        "squawk",
        "spi",
        "position_source",
        "category",
    ]

    # We are not using namedtuple here as state vectors from the server might be extended; zip() will ignore additional
    #  entries in this case
    def __init__(self, arr):
        """
        Initializes the StateVector object.

        :param list arr: the array representation of a state vector as received by the API.
        """
        self.__dict__ = dict(zip(StateVector.keys, arr))

    def __repr__(self):
        return "StateVector(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class OpenSkyStates(object):
    """Represents the state of the airspace as seen by OpenSky at a particular time. It has the following fields:

    |  **time**: `int` - in seconds since epoch (Unix time stamp). Gives the validity period of all states.
      All vectors represent the state of a vehicle with the interval :math:`[time - 1, time]`.
    |  **states**: `list` [`StateVector`] - a list of `StateVector` or is None if there have been no states received.
    """

    def __init__(self, states_dict):
        """
        Initializes the OpenSkyStates object.

        :param dict states_dict: the dictionary that represents the state of the airspace as seen by OpenSky
            at a particular time.
        """
        self.__dict__ = states_dict
        if self.states is not None:
            self.states = [StateVector(a) for a in self.states]
        else:
            self.states = []

    def __repr__(self):
        return "<OpenSkyStates@%s>" % str(self.__dict__)

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class FlightData(object):
    """
    Class that represents data of certain flight. It has the following fields:

    |  **icao24**: `str` - Unique ICAO 24-bit address of the transponder in hex string representation.
        All letters are lower case.
    |  **firstSeen**: `int` - Estimated time of departure for the flight as Unix time (seconds since epoch).
    |  **estDepartureAirport**: `str` - ICAO code of the estimated departure airport.
        Can be null if the airport could not be identified.
    |  **lastSeen**: `int` - Estimated time of arrival for the flight as Unix time (seconds since epoch).
    |  **estArrivalAirport**: `str` - ICAO code of the estimated arrival airport.
        Can be null if the airport could not be identified.
    |  **callsign**: `str` - Callsign of the vehicle (8 chars). Can be null if no callsign has been received.
        If the vehicle transmits multiple callsigns during the flight, we take the one seen most frequently.
    |  **estDepartureAirportHorizDistance**: `int` - Horizontal distance of the last received airborne position to the
        estimated departure airport in meters.
    |  **estDepartureAirportVertDistance**: `int` - Vertical distance of the last received airborne position to the
        estimated departure airport in meters.
    |  **estArrivalAirportHorizDistance**: `int` - Horizontal distance of the last received airborne position to the
        estimated arrival airport in meters.
    |  **estArrivalAirportVertDistance**: `int` - Vertical distance of the last received airborne position to the
        estimated arrival airport in meters.
    |  **departureAirportCandidatesCount**: `int` - Number of other possible departure airports.
        These are airports in short distance to estDepartureAirport.
    |  **arrivalAirportCandidatesCount**: `int` - Number of other possible departure airports.
    These are airports in short distance to estArrivalAirport.
    """

    keys = [
        "icao24",
        "firstSeen",
        "estDepartureAirport",
        "lastSeen",
        "estArrivalAirport",
        "callsign",
        "estDepartureAirportHorizDistance",
        "estDepartureAirportVertDistance",
        "estArrivalAirportHorizDistance",
        "estArrivalAirportVertDistance",
        "departureAirportCandidatesCount",
        "arrivalAirportCandidatesCount",
    ]

    def __init__(self, arr):
        """
        Function that initializes the FlightData object.

        :param list arr: array representation of a flight data as received by the API.
        """
        self.__dict__ = dict(zip(FlightData.keys, arr))

    def __repr__(self):
        return "FlightData(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class Waypoint(object):
    """
    Class that represents the single waypoint that is a basic part of flight trajectory:

    |  **time**: `int` - Time which the given waypoint is associated with in seconds since epoch (Unix time).
    |  **latitude**: `float` - WGS-84 latitude in decimal degrees. Can be null.
    |  **longitude**: `float` - WGS-84 longitude in decimal degrees. Can be null.
    |  **baro_altitude**: `float` - Barometric altitude in meters. Can be null.
    |  **true_track**: `float` - True track in decimal degrees clockwise from north (north=0°). Can be null.
    |  **on_ground**: `bool` - Boolean value which indicates if the position was retrieved from a surface
        position report.
    """

    keys = [
        "time",
        "latitude",
        "longitude",
        "baro_altitude",
        "true_track",
        "on_ground",
    ]

    def __init__(self, arr):
        """
        Function that initializes the Waypoint object.

        :param list arr: array representation of a single waypoint as received by the API.
        """
        self.__dict__ = dict(zip(Waypoint.keys, arr))

    def __repr__(self):
        return "Waypoint(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class FlightTrack(object):
    """
    Class that represents the trajectory for a certain aircraft at a given time.:

    |  **icao24**: `str` - Unique ICAO 24-bit address of the transponder in lower case hex string representation.
    |  **startTime**: `int` - Time of the first waypoint in seconds since epoch (Unix time).
    |  **endTime**: `int` - Time of the last waypoint in seconds since epoch (Unix time).
    |  **calllsign**: `str` - Callsign (8 characters) that holds for the whole track. Can be null.
    |  **path**: `list` [`Waypoint`] - waypoints of the trajectory.
    """

    def __init__(self, arr):
        """
        Function that initializes the FlightTrack object.

        :param list arr: array representation of the flight track received by the API.
        """
        for key, value in arr.items():
            if key == "path":
                v = [Waypoint(point) for point in value]
            self.__dict__[key] = value

    def __repr__(self):
        return "FlightTrack(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class OpenSkyApi(object):
    """
    Main class of the OpenSky Network API. Instances retrieve data from OpenSky via HTTP.
    """

    def __init__(self, username=None, password=None):
        """Create an instance of the API client. If you do not provide username and password requests will be
        anonymous which imposes some limitations.

        :param str username: an OpenSky username (optional).
        :param str password: an OpenSky password for the given username (optional).
        """
        if username is not None:
            self._auth = (username, password)
        else:
            self._auth = ()
        self._api_url = "https://opensky-network.org/api"
        self._last_requests = defaultdict(lambda: 0)

    def _get_json(self, url_post, callee, params=None):
        """
        Sends HTTP request to the given endpoint and returns the response as a json.

        :param str url_post: endpoint to which the request will be sent.
        :param Callable callee: method that calls _get_json().
        :param dict params: request parameters.
        :rtype: dict|None
        """
        r = requests.get(
            "{0:s}{1:s}".format(self._api_url, url_post),
            auth=self._auth,
            params=params,
            timeout=15.00,
        )
        if r.status_code == 200:
            self._last_requests[callee] = time.time()
            return r.json()
        else:
            logger.debug(
                "Response not OK. Status {0:d} - {1:s}".format(r.status_code, r.reason)
            )
        return None

    def _check_rate_limit(self, time_diff_noauth, time_diff_auth, func):
        """
        Impose client-side rate limit.

        :param int time_diff_noauth: the minimum time between two requests in seconds if not using authentication.
        :param int time_diff_auth: the minimum time between two requests in seconds if using authentication.
        :param callable func: the API function to evaluate.
        :rtype: bool
        """
        if len(self._auth) < 2:
            return abs(time.time() - self._last_requests[func]) >= time_diff_noauth
        else:
            return abs(time.time() - self._last_requests[func]) >= time_diff_auth

    @staticmethod
    def _check_lat(lat):
        if lat < -90 or lat > 90:
            raise ValueError("Invalid latitude {:f}! Must be in [-90, 90].".format(lat))

    @staticmethod
    def _check_lon(lon):
        if lon < -180 or lon > 180:
            raise ValueError(
                "Invalid longitude {:f}! Must be in [-180, 180].".format(lon)
            )

    def get_states(self, time_secs=0, icao24=None, bbox=()):
        """
        Retrieve state vectors for a given time. If time = 0 the most recent ones are taken.
        Optional filters may be applied for ICAO24 addresses.

        :param int time_secs: time as Unix time stamp (seconds since epoch) or datetime. The datetime must be in UTC!
        :param str icao24: optionally retrieve only state vectors for the given ICAO24 address(es).
            The parameter can either be a single address as str or an array of str containing multiple addresses.
        :param tuple bbox: optionally retrieve state vectors within a bounding box.
            The bbox must be a tuple of exactly four values [min_latitude, max_latitude, min_longitude, max_longitude]
            each in WGS84 decimal degrees.
        :return: OpenSkyStates if request was successful, None otherwise.
        :rtype: OpenSkyStates | None
        """
        if not self._check_rate_limit(10, 5, self.get_states):
            logger.debug("Blocking request due to rate limit.")
            return None

        t = time_secs
        if type(time_secs) == datetime:
            t = calendar.timegm(t.timetuple())

        params = {"time": int(t), "icao24": icao24, "extended": True}

        if len(bbox) == 4:
            OpenSkyApi._check_lat(bbox[0])
            OpenSkyApi._check_lat(bbox[1])
            OpenSkyApi._check_lon(bbox[2])
            OpenSkyApi._check_lon(bbox[3])

            params["lamin"] = bbox[0]
            params["lamax"] = bbox[1]
            params["lomin"] = bbox[2]
            params["lomax"] = bbox[3]
        elif len(bbox) > 0:
            raise ValueError(
                "Invalid bounding box! Must be [min_latitude, max_latitude, min_longitude, max_longitude]."
            )

        states_json = self._get_json("/states/all", self.get_states, params=params)
        if states_json is not None:
            return OpenSkyStates(states_json)
        return None

    def get_my_states(self, time_secs=0, icao24=None, serials=None):
        """
        Retrieve state vectors for your own sensors. Authentication is required for this operation.
        If time = 0 the most recent ones are taken. Optional filters may be applied for ICAO24 addresses and sensor
        serial numbers.

        :param int time_secs: time as Unix time stamp (seconds since epoch) or datetime. The datetime must be in UTC!
        :param str icao24: optionally retrieve only state vectors for the given ICAO24 address(es).
            The parameter can either be a single address as str or an array of str containing multiple addresses.
        :param int serials: optionally retrieve only states of vehicles as seen by the given sensor(s).
            The parameter can either be a single sensor serial number (int) or a list of serial numbers.
        :return: OpenSkyStates if request was successful, None otherwise.
        :rtype: OpenSkyStates | None
        """
        if len(self._auth) < 2:
            raise Exception("No username and password provided for get_my_states!")
        if not self._check_rate_limit(0, 1, self.get_my_states):
            logger.debug("Blocking request due to rate limit.")
            return None
        t = time_secs
        if type(time_secs) == datetime:
            t = calendar.timegm(t.timetuple())

        params = {
            "time": int(t),
            "icao24": icao24,
            "serials": serials,
            "extended": True,
        }
        states_json = self._get_json("/states/own", self.get_my_states, params=params)
        if states_json is not None:
            return OpenSkyStates(states_json)
        return None

    def get_flights_from_interval(self, begin, end):
        """
        Retrieves data of flights for certain time interval [begin, end].

        :param int begin: Start of time interval to retrieve flights for as Unix time (seconds since epoch).
        :param int end: End of time interval to retrieve flights for as Unix time (seconds since epoch).
        :return: list of FlightData objects if request was successful, None otherwise.
        :rtype: FlightData | None
        """
        if begin >= end:
            raise ValueError("The end parameter must be greater than begin.")
        if end - begin > 7200:
            raise ValueError("The time interval must be smaller than 2 hours.")

        params = {"begin": begin, "end": end}
        states_json = self._get_json(
            "/flights/all", self.get_flights_from_interval, params=params
        )

        if states_json is not None:
            return [FlightData(list(entry.values())) for entry in states_json]
        return None

    def get_flights_by_aircraft(self, icao24, begin, end):
        """
        Retrieves data of flights for certain aircraft and time interval.

        :param str icao24: Unique ICAO 24-bit address of the transponder in hex string representation.
            All letters need to be lower case.
        :param int begin: Start of time interval to retrieve flights for as Unix time (seconds since epoch).
        :param int end: End of time interval to retrieve flights for as Unix time (seconds since epoch).
        :return: list of FlightData objects if request was successful, None otherwise.
        :rtype: FlightData | None
        """

        if begin >= end:
            raise ValueError("The end parameter must be greater than begin.")
        if end - begin > 2592 * 1e3:
            raise ValueError("The time interval must be smaller than 30 days.")

        params = {"icao24": icao24, "begin": begin, "end": end}
        states_json = self._get_json(
            "/flights/aircraft", self.get_flights_by_aircraft, params=params
        )

        if states_json is not None:
            return [FlightData(list(entry.values())) for entry in states_json]
        return None

    def get_arrivals_by_airport(self, airport, begin, end):
        """
        Retrieves flights for a certain airport which arrived within a given time interval [begin, end].

        :param str airport: ICAO identier for the airport.
        :param int begin: Start of time interval to retrieve flights for as Unix time (seconds since epoch).
        :param int end: End of time interval to retrieve flights for as Unix time (seconds since epoch).
        :return: list of FlightData objects if request was successful, None otherwise..
        :rtype: FlightData | None
        """
        if begin >= end:
            raise ValueError("The end parameter must be greater than begin.")
        if end - begin > 604800:
            raise ValueError("The time interval must be smaller than 7 days.")

        params = {"airport": airport, "begin": begin, "end": end}
        states_json = self._get_json(
            "/flights/arrival", self.get_arrivals_by_airport, params=params
        )

        if states_json is not None:
            return [FlightData(list(entry.values())) for entry in states_json]
        return None

    def get_departures_by_airport(self, airport, begin, end):
        """
        Retrieves flights for a certain airport which arrived within a given time interval [begin, end].

        :param str airport: ICAO identier for the airport.
        :param int begin: Start of time interval to retrieve flights for as Unix time (seconds since epoch).
        :param int end: End of time interval to retrieve flights for as Unix time (seconds since epoch).
        :return: list of FlightData objects if request was successful, None otherwise.
        :rtype: FlightData | None
        """
        if begin >= end:
            raise ValueError("The end parameter must be greater than begin.")
        if end - begin > 604800:
            raise ValueError("The time interval must be smaller than 7 days.")

        params = {"airport": airport, "begin": begin, "end": end}
        states_json = self._get_json(
            "/flights/departure", self.get_departures_by_airport, params=params
        )

        if states_json is not None:
            return [FlightData(list(entry.values())) for entry in states_json]
        return []

    def get_track_by_aircraft(self, icao24, t=0):
        """
        Retrieve the trajectory for a certain aircraft at a given time.
        **The tracks endpoint is purely experimental.**

        :param str icao24: Unique ICAO 24-bit address of the transponder in hex string representation.
            All letters need to be lower case.
        :param int t: Unix time in seconds since epoch. It can be any time between start and end of a known flight.
            If time = 0, get the live track if there is any flight ongoing for the given aircraft.
        :return: FlightTrack object if request was successful, None otherwise.
        :rtype: FlightTrack | None
        """
        if int(time.time()) - t > 2592 * 1e3 and t != 0:
            raise ValueError(
                "It is not possible to access flight tracks from more than 30 days in the past."
            )

        params = {"icao24": icao24, "time": t}
        states_json = self._get_json(
            "/tracks/all", self.get_track_by_aircraft, params=params
        )

        if states_json is not None:
            return FlightTrack(states_json)
        return None
