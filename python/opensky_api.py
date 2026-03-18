#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Official OpenSky Network API client implementation
#
# Original Author: Markus Fuchs <fuchs@opensky-network.org>
# Contributors:    Jannis Lübbe <luebbe@opensky-network.org> (Python)
# URL:             http://github.com/openskynetwork/opensky-api
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
import json
import logging
import pprint
import time
from collections import defaultdict
from datetime import datetime, timedelta

import requests

logger = logging.getLogger("opensky_api")
logger.addHandler(logging.NullHandler())

TOKEN_URL = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
# Refresh the token this many seconds before it actually expires to avoid
# race conditions on long-running requests.
TOKEN_REFRESH_MARGIN = 30


class TokenManager:
    """Manages OAuth2 client-credentials tokens for the OpenSky REST API.

    Tokens are fetched lazily on the first request and refreshed automatically
    when they are about to expire, so callers never have to think about token
    lifecycle.
    """

    def __init__(self, client_id: str, client_secret: str):
        self._client_id = client_id
        self._client_secret = client_secret
        self._token: str | None = None
        self._expires_at: datetime | None = None

    def get_token(self) -> str:
        """Return a valid access token, refreshing automatically if needed."""
        if (
            self._token
            and self._expires_at
            and datetime.now() < self._expires_at
        ):
            return self._token
        return self._refresh()

    def auth_headers(self) -> dict:
        """Return a dict with a valid ``Authorization: Bearer …`` header."""
        return {"Authorization": f"Bearer {self.get_token()}"}

    def _refresh(self) -> str:
        """Fetch a new access token from the OpenSky authentication server."""
        r = requests.post(
            TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self._client_id,
                "client_secret": self._client_secret,
            },
            timeout=15.0,
        )
        r.raise_for_status()

        data = r.json()
        self._token = data["access_token"]
        expires_in = data.get("expires_in", 1800)
        self._expires_at = datetime.now() + timedelta(
            seconds=expires_in - TOKEN_REFRESH_MARGIN
        )
        logger.debug("OAuth2 token refreshed, valid for %ds.", expires_in)
        return self._token

    @classmethod
    def from_json_file(cls, path: str) -> "TokenManager":
        """Create a :class:`TokenManager` from a JSON credentials file.

        The file must contain the keys ``clientId`` and ``clientSecret``
        (the format produced by the OpenSky account page).

        Example file contents::

            {"clientId": "my-client", "clientSecret": "s3cr3t"}
        """
        with open(path) as fh:
            creds = json.load(fh)
        return cls(
            client_id=creds["clientId"],
            client_secret=creds["clientSecret"],
        )


class StateVector:
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
        "icao24",           # 0
        "callsign",         # 1
        "origin_country",   # 2
        "time_position",    # 3
        "last_contact",     # 4
        "longitude",        # 5
        "latitude",         # 6
        "baro_altitude",    # 7
        "on_ground",        # 8
        "velocity",         # 9
        "true_track",       # 10
        "vertical_rate",    # 11
        "sensors",          # 12
        "geo_altitude",     # 13
        "squawk",           # 14
        "spi",              # 15
        "position_source",  # 16
        "category",         # 17
    ]

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


class OpenSkyStates:
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


class FlightData:
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
    |  **arrivalAirportCandidatesCount**: `int` - Number of other possible arrival airports.
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
        Initializes the FlightData object.

        :param list arr: array representation of a flight data as received by the API.
        """
        self.__dict__ = dict(zip(FlightData.keys, arr))

    def __repr__(self):
        return "FlightData(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class Waypoint:
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
        Initializes the Waypoint object.

        :param list arr: array representation of a single waypoint as received by the API.
        """
        self.__dict__ = dict(zip(Waypoint.keys, arr))

    def __repr__(self):
        return "Waypoint(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class FlightTrack:
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
        Initializes the FlightTrack object.

        :param list arr: array representation of the flight track received by the API.
        """
        for key, value in arr.items():
            if key == "path":
                value = [Waypoint(point) for point in value]
            self.__dict__[key] = value

    def __repr__(self):
        return "FlightTrack(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class OpenSkyApi:
    """
    Main class of the OpenSky Network API. Instances retrieve data from OpenSky via HTTP.

    Authentication uses the OAuth2 *client credentials* flow. Pass either a
    :class:`TokenManager` instance directly, or supply ``client_id`` /
    ``client_secret`` as keyword arguments. If neither is provided, requests
    are made anonymously (reduced rate limits apply).
    """

    def __init__(
        self,
        token_manager: TokenManager | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        """Create an instance of the API client.

        Provide credentials in one of three ways (in order of precedence):

        1. Pass a pre-built :class:`TokenManager` via *token_manager*.
        2. Pass *client_id* and *client_secret* directly.
        3. Pass nothing → anonymous access (rate limits apply).

        The credentials file produced by the OpenSky account page can be
        loaded conveniently with::

            tm = TokenManager.from_json_file("credentials.json")
            api = OpenSkyApi(token_manager=tm)

        :param TokenManager token_manager: a ready-to-use token manager (optional).
        :param str client_id: OAuth2 client ID (optional).
        :param str client_secret: OAuth2 client secret (optional).
        """
        if token_manager is not None:
            self._token_manager: TokenManager | None = token_manager
        elif client_id is not None and client_secret is not None:
            self._token_manager = TokenManager(client_id, client_secret)
        else:
            self._token_manager = None

        self._api_url = "https://opensky-network.org/api"
        self._last_requests = defaultdict(lambda: 0)
        self._session = requests.Session()

    def _update_session_auth(self) -> None:
        """Keep the session Authorization header up to date with the current token."""
        if self._token_manager is not None:
            self._session.headers.update(self._token_manager.auth_headers())
        else:
            self._session.headers.pop("Authorization", None)

    def _get_json(self, url_post, callee, params=None):
        """
        Sends HTTP request to the given endpoint and returns the response as a json.

        :param str url_post: endpoint to which the request will be sent.
        :param Callable callee: method that calls _get_json().
        :param dict params: request parameters.
        :rtype: dict|None
        """
        self._update_session_auth()
        r = self._session.get(
            f"{self._api_url}{url_post}",
            params=params,
            timeout=15.00,
        )
        if r.status_code == 200:
            self._last_requests[callee] = time.time()
            return r.json()
        else:
            logger.debug(
                f"Response not OK. Status {r.status_code} - {r.reason}"
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
        if self._token_manager is None:
            return abs(time.time() - self._last_requests[func]) >= time_diff_noauth
        else:
            return abs(time.time() - self._last_requests[func]) >= time_diff_auth

    @staticmethod
    def _check_lat(lat):
        if lat < -90 or lat > 90:
            raise ValueError(f"Invalid latitude {lat:f}! Must be in [-90, 90].")

    @staticmethod
    def _check_lon(lon):
        if lon < -180 or lon > 180:
            raise ValueError(
                f"Invalid longitude {lon:f}! Must be in [-180, 180]."
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
        if isinstance(time_secs, datetime):
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
        if self._token_manager is None:
            raise Exception("No credentials provided for get_my_states!")
        if not self._check_rate_limit(0, 1, self.get_my_states):
            logger.debug("Blocking request due to rate limit.")
            return None
        t = time_secs
        if isinstance(time_secs, datetime):
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
        if end - begin > 172800:
            raise ValueError("The time interval must be smaller than 2 days.")

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

        :param str airport: ICAO identifier for the airport.
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
            "/flights/arrival", self.get_arrivals_by_airport, params=params
        )

        if states_json is not None:
            return [FlightData(list(entry.values())) for entry in states_json]
        return None

    def get_departures_by_airport(self, airport, begin, end):
        """
        Retrieves flights for a certain airport which departed within a given time interval [begin, end].

        :param str airport: ICAO identifier for the airport.
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
        return None

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
        if int(time.time()) - t > 2592000 and t != 0:
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
