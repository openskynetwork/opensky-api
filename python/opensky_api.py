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
import requests

from datetime import datetime
from collections import defaultdict
import time

logger = logging.getLogger('opensky_api')
logger.addHandler(logging.NullHandler())


class StateVector(object):
    """ Represents the state of a vehicle at a particular time. It has the following fields:

      |  **icao24** - ICAO24 address of the transmitter in hex string representation.
      |  **callsign** - callsign of the vehicle. Can be None if no callsign has been received.
      |  **origin_country** - inferred through the ICAO24 address
      |  **time_position** - seconds since epoch of last position report. Can be None if there was no position report received by OpenSky within 15s before.
      |  **last_contact** - seconds since epoch of last received message from this transponder
      |  **longitude** - in ellipsoidal coordinates (WGS-84) and degrees. Can be None
      |  **latitude** - in ellipsoidal coordinates (WGS-84) and degrees. Can be None
      |  **geo_altitude** - geometric altitude in meters. Can be None
      |  **on_ground** - true if aircraft is on ground (sends ADS-B surface position reports).
      |  **velocity** - over ground in m/s. Can be None if information not present
      |  **heading** - in decimal degrees (0 is north). Can be None if information not present.
      |  **vertical_rate** - in m/s, incline is positive, decline negative. Can be None if information not present.
      |  **sensors** - serial numbers of sensors which received messages from the vehicle within the validity period of this state vector. Can be None if no filtering for sensor has been requested.
      |  **baro_altitude** - barometric altitude in meters. Can be None
      |  **squawk** - transponder code aka Squawk. Can be None
      |  **spi** - special purpose indicator
      |  **position_source** - origin of this state's position: 0 = ADS-B, 1 = ASTERIX, 2 = MLAT, 3 = FLARM
    """
    keys = ["icao24", "callsign", "origin_country", "time_position",
            "last_contact", "longitude", "latitude", "baro_altitude", "on_ground",
            "velocity", "heading", "vertical_rate", "sensors",
            "geo_altitude", "squawk", "spi", "position_source"]

    # We are not using namedtuple here as state vectors from the server might be extended; zip() will ignore additional
    #  entries in this case
    def __init__(self, arr):
        """ arr is the array representation of a state vector as received by the API """
        self.__dict__ = dict(zip(StateVector.keys, arr))

    def __repr__(self):
        return "StateVector(%s)" % repr(self.__dict__.values())

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class OpenSkyStates(object):
    """ Represents the state of the airspace as seen by OpenSky at a particular time. It has the following fields:

      |  **time** - in seconds since epoch (Unix time stamp). Gives the validity period of all states. All vectors represent the state of a vehicle with the interval :math:`[time - 1, time]`.
      |  **states** - a list of `StateVector` or is None if there have been no states received
    """
    def __init__(self, j):
        self.__dict__ = j
        if self.states is not None:
            self.states = [StateVector(a) for a in self.states]
        else:
            self.states = []

    def __repr__(self):
        return "<OpenSkyStates@%s>" % str(self.__dict__)

    def __str__(self):
        return pprint.pformat(self.__dict__, indent=4)


class OpenSkyApi(object):
    """
    Main class of the OpenSky Network API. Instances retrieve data from OpenSky via HTTP
    """
    def __init__(self, username=None, password=None):
        """ Create an instance of the API client. If you do not provide username and password requests will be
        anonymous which imposes some limitations.

        :param username: an OpenSky username (optional)
        :param password: an OpenSky password for the given username (optional)
        """
        if username is not None:
            self._auth = (username, password)
        else:
            self._auth = ()
        self._api_url = "https://opensky-network.org/api"
        self._last_requests = defaultdict(lambda: 0)

    def _get_json(self, url_post, callee, params=None):
        r = requests.get("{0:s}{1:s}".format(self._api_url, url_post),
                         auth=self._auth, params=params, timeout=15.00)
        if r.status_code == 200:
            self._last_requests[callee] = time.time()
            return r.json()
        else:
            logger.debug("Response not OK. Status {0:d} - {1:s}".format(r.status_code, r.reason))
        return None

    def _check_rate_limit(self, time_diff_noauth, time_diff_auth, func):
        """ impose client-side rate limit

        :param time_diff_noauth: the minimum time between two requests in seconds if not using authentication
        :param time_diff_auth: the minimum time between two requests in seconds if using authentication
        :param func: the API function to evaluate
        """
        if len(self._auth) < 2:
            return abs(time.time() - self._last_requests[func]) >= time_diff_noauth
        else:
            return abs(time.time() - self._last_requests[func]) >= time_diff_auth

    @staticmethod
    def _check_lat(lat):
        if lat < -90 or lat > 90:
            raise ValueError("Invalid latitude {:f}! Must be in [-90, 90]".format(lat))

    @staticmethod
    def _check_lon(lon):
        if lon < -180 or lon > 180:
            raise ValueError("Invalid longitude {:f}! Must be in [-180, 180]".format(lon))

    def get_states(self, time_secs=0, icao24=None, serials=None, bbox=()):
        """ Retrieve state vectors for a given time. If time = 0 the most recent ones are taken.
        Optional filters may be applied for ICAO24 addresses.

        :param time_secs: time as Unix time stamp (seconds since epoch) or datetime. The datetime must be in UTC!
        :param icao24: optionally retrieve only state vectors for the given ICAO24 address(es). The parameter can either be a single address as str or an array of str containing multiple addresses
        :param bbox: optionally retrieve state vectors within a bounding box. The bbox must be a tuple of exactly four values [min_latitude, max_latitude, min_longitude, max_latitude] each in WGS84 decimal degrees.
        :return: OpenSkyStates if request was successful, None otherwise
        """
        if not self._check_rate_limit(10, 5, self.get_states):
            logger.debug("Blocking request due to rate limit")
            return None

        t = time_secs
        if type(time_secs) == datetime:
            t = calendar.timegm(t.timetuple())

        params = {"time": int(t), "icao24": icao24}

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
            raise ValueError("Invalid bounding box! Must be [min_latitude, max_latitude, min_longitude, max_latitude]")

        states_json = self._get_json("/states/all", self.get_states,
                                     params=params)
        if states_json is not None:
            return OpenSkyStates(states_json)
        return None

    def get_my_states(self, time_secs=0, icao24=None, serials=None):
        """ Retrieve state vectors for your own sensors. Authentication is required for this operation.
        If time = 0 the most recent ones are taken. Optional filters may be applied for ICAO24 addresses and sensor
        serial numbers.

        :param time_secs: time as Unix time stamp (seconds since epoch) or datetime. The datetime must be in UTC!
        :param icao24: optionally retrieve only state vectors for the given ICAO24 address(es). The parameter can either be a single address as str or an array of str containing multiple addresses
        :param serials: optionally retrieve only states of vehicles as seen by the given sensor(s). The parameter can either be a single sensor serial number (int) or a list of serial numbers.
        :return: OpenSkyStates if request was successful, None otherwise
        """
        if len(self._auth) < 2:
            raise Exception("No username and password provided for get_my_states!")
        if not self._check_rate_limit(0, 1, self.get_my_states):
            logger.debug("Blocking request due to rate limit")
            return None
        t = time_secs
        if type(time_secs) == datetime:
            t = calendar.timegm(t.timetuple())
        states_json = self._get_json("/states/own", self.get_my_states,
                                     params={"time": int(t), "icao24": icao24,
                                                             "serials": serials})
        if states_json is not None:
            return OpenSkyStates(states_json)
        return None
