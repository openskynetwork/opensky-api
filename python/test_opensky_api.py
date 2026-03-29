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
import os
import time
from datetime import datetime
from unittest import TestCase, skipIf

from opensky_api import FlightData, FlightTrack, OpenSkyApi, StateVector, TokenManager, Waypoint

# Authenticated tests run automatically when credentials.json is present.
_CREDENTIALS_PATH = "credentials.json"
_has_credentials = os.path.exists(_CREDENTIALS_PATH)


def _make_api():
    if _has_credentials:
        return OpenSkyApi(token_manager=TokenManager.from_json_file(_CREDENTIALS_PATH))
    return OpenSkyApi()


def _get_active_serials(api):
    """Fetch own states without a serial filter and return the list of sensor
    serials that are currently delivering data. Used to build a dynamic serial
    list for the filtered test so no hardcoded serials are needed."""
    my_states = api.get_my_states()
    if not my_states or not my_states.states:
        return []
    serials = set()
    for s in my_states.states:
        if s.sensors:
            serials.update(s.sensors)
    return sorted(serials)


class TestOpenSkyApi(TestCase):
    def setUp(self):
        self.api = _make_api()
        self.addCleanup(self.api.close)

    def test_get_states(self):
        r = self.api.get_states()
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    def test_get_states_rate_limit(self):
        r = self.api.get_states()
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")
        r = self.api.get_states()
        self.assertIsNone(r, "Rate limit produces 'None' result")

    def test_get_states_time(self):
        now = int(time.time())
        r = self.api.get_states(time_secs=now)
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    def test_get_states_datetime(self):
        r = self.api.get_states(time_secs=datetime.now())
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    def test_get_states_bbox(self):
        r = self.api.get_states(bbox=(45.8389, 47.8229, 5.9962, 10.5226))
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    def test_get_states_bbox_err(self):
        with self.assertRaisesRegex(ValueError, "Invalid bounding box!.*"):
            self.api.get_states(bbox=(0, 0))

    def test_get_states_bbox_err_lat(self):
        with self.assertRaisesRegex(ValueError, "Invalid latitude 95.8389.*"):
            self.api.get_states(bbox=(95.8389, 47.8229, 5.9962, 10.5226))
        with self.assertRaisesRegex(ValueError, "Invalid latitude -147.8229.*"):
            self.api.get_states(bbox=(45.8389, -147.8229, 5.9962, 10.5226))

    def test_get_states_bbox_err_lon(self):
        with self.assertRaisesRegex(ValueError, "Invalid longitude -255.9962.*"):
            self.api.get_states(bbox=(45.8389, 47.8229, -255.9962, 10.5226))
        with self.assertRaisesRegex(ValueError, "Invalid longitude 210.5226.*"):
            self.api.get_states(bbox=(45.8389, 47.8229, 5.9962, 210.5226))

    def test_state_vector_parsing(self):
        s = StateVector(
            [
                "cabeef",   # 0  icao24
                "ABCDEFG",  # 1  callsign
                "USA",      # 2  origin_country
                1001,       # 3  time_position
                1000,       # 4  last_contact
                1.0,        # 5  longitude
                2.0,        # 6  latitude
                3.0,        # 7  baro_altitude
                False,      # 8  on_ground
                4.0,        # 9  velocity
                5.0,        # 10 true_track
                6.0,        # 11 vertical_rate
                None,       # 12 sensors
                6743.7,     # 13 geo_altitude
                "6714",     # 14 squawk
                False,      # 15 spi
                0,          # 16 position_source
                0,          # 17 category
            ]
        )
        self.assertEqual("cabeef", s.icao24)
        self.assertEqual("ABCDEFG", s.callsign)
        self.assertEqual("USA", s.origin_country)
        self.assertEqual(1001, s.time_position)
        self.assertEqual(1000, s.last_contact)
        self.assertEqual(1.0, s.longitude)
        self.assertEqual(2.0, s.latitude)
        self.assertEqual(3.0, s.baro_altitude)
        self.assertFalse(s.on_ground)
        self.assertEqual(4.0, s.velocity)
        self.assertEqual(5.0, s.true_track)
        self.assertEqual(6.0, s.vertical_rate)
        self.assertIsNone(s.sensors)
        self.assertEqual(6743.7, s.geo_altitude)
        self.assertEqual("6714", s.squawk)
        self.assertFalse(s.spi)
        self.assertEqual(0, s.position_source)
        self.assertEqual(0, s.category)

    def test_flight_data_parsing(self):
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
        values = [
            "4951d0",
            1517230550,
            "EDDF",
            1517240237,
            "LPCS",
            "TAP583  ",
            3808,
            80,
            14016,
            708,
            2,
            3,
        ]
        f = FlightData(values)
        for key, exp_val in zip(keys, values):
            self.assertEqual(exp_val, getattr(f, key))

    def test_waypoint_parsing(self):
        keys = [
            "time",
            "latitude",
            "longitude",
            "baro_altitude",
            "true_track",
            "on_ground",
        ]
        values = [1675450754, 39.0912, -94.5794, 304.0, 91.0, False]
        w = Waypoint(values)
        for key, exp_val in zip(keys, values):
            self.assertEqual(exp_val, getattr(w, key))

    def test_flight_track_parsing(self):
        entry = {
            "icao24": "a01391",
            "callsign": "N104AA  ",
            "startTime": 1675450754,
            "endTime": 1675451752,
            "path": [
                [1675450754, 39.0912, -94.5794, 304.0, 91.0,  False],
                [1675450768, 39.0916, -94.5717, 304.0, 65.0,  False],
                [1675450776, 39.0936, -94.5687, 304.0, 33.0,  False],
                [1675450776, 39.0936, -94.5687, 304.0, 8.0,   False],
                [1675451134, 39.1073, -94.613,  304.0, 296.0, False],
                [1675451134, 39.1073, -94.613,  304.0, 292.0, False],
                [1675451752, 39.1056, -94.6143, 304.0, 287.0, False],
            ],
        }

        f = FlightTrack(entry)
        self.assertEqual(entry["icao24"], f.icao24)
        self.assertEqual(entry["callsign"], f.callsign)
        self.assertEqual(entry["startTime"], f.startTime)
        self.assertEqual(entry["endTime"], f.endTime)
        self.assertEqual(len(entry["path"]), len(f.path))
        for waypoint, raw in zip(f.path, entry["path"]):
            self.assertIsInstance(waypoint, Waypoint)
            self.assertEqual(raw[0], waypoint.time)
            self.assertEqual(raw[1], waypoint.latitude)
            self.assertEqual(raw[2], waypoint.longitude)
            self.assertEqual(raw[3], waypoint.baro_altitude)
            self.assertEqual(raw[4], waypoint.true_track)
            self.assertEqual(raw[5], waypoint.on_ground)

    def test_get_my_states_no_auth(self):
        a = OpenSkyApi()
        with self.assertRaisesRegex(
            Exception, "No credentials provided for get_my_states!"
        ):
            a.get_my_states()

    @skipIf(not _has_credentials, "Missing credentials file")
    def test_get_my_states(self):
        r = self.api.get_my_states()
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    @skipIf(not _has_credentials, "Missing credentials file")
    def test_get_my_states_time(self):
        r = self.api.get_my_states(time_secs=int(time.time()) - 10)
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    @skipIf(not _has_credentials, "Missing credentials file")
    def test_get_my_states_datetime(self):
        r = self.api.get_my_states(time_secs=datetime.now())
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    @skipIf(not _has_credentials, "Missing credentials file")
    def test_get_my_states_serials(self):
        # Discover active serials dynamically from an unfiltered request rather
        # than relying on a hardcoded list. The test is skipped gracefully if
        # none of the own receivers happen to be delivering data right now.
        serials = _get_active_serials(self.api)
        if not serials:
            self.skipTest("No active serials found - own receivers may be offline")
        # The discovery call above already consumed one get_my_states request.
        # Wait out the 1-second authenticated rate limit before the next call.
        time.sleep(1)
        r = self.api.get_my_states(serials=serials)
        self.assertIsNotNone(r, "Request with active serials should succeed")
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")

    @skipIf(not _has_credentials, "Missing credentials file")
    def test_get_my_states_rate_limit(self):
        r = self.api.get_my_states()
        self.assertGreater(len(r.states), 0, "Retrieve at least one State Vector")
        r = self.api.get_my_states()
        self.assertIsNone(r, "Rate limit produces 'None' result")

    def test_get_flights_from_interval(self):
        r = self.api.get_flights_from_interval(1517227200, 1517230800)
        self.assertGreater(len(r), 0, "Retrieve at least one State Vector")

    def test_get_flights_from_interval_reversed_timestamps(self):
        with self.assertRaisesRegex(
            Exception, "The end parameter must be greater than begin"
        ):
            self.api.get_flights_from_interval(1517230800, 1517227200)

    def test_get_flights_from_interval_too_long_time_interval(self):
        with self.assertRaisesRegex(
            Exception, "The time interval must be smaller than 2 hours"
        ):
            self.api.get_flights_from_interval(1517227200, 1517234401)

    def test_get_flights_by_aircraft(self):
        r = self.api.get_flights_by_aircraft("3c675a", 1517184000, 1517270400)
        self.assertGreater(len(r), 0, "Retrieve at least one State Vector")

    def test_get_flights_by_aircraft_reversed_timestamps(self):
        with self.assertRaisesRegex(
            Exception, "The end parameter must be greater than begin"
        ):
            self.api.get_flights_by_aircraft("3c675a", 1517270400, 1517184000)

    def test_get_flights_by_aircraft_too_long_time_interval(self):
        with self.assertRaisesRegex(
            Exception, "The time interval must be smaller than 2 days"
        ):
            self.api.get_flights_by_aircraft("3c675a", 1517184000, 1517184000 + 172801)

    def test_get_arrivals_by_airport(self):
        r = self.api.get_arrivals_by_airport("EDDF", 1517227200, 1517230800)
        self.assertGreater(len(r), 0, "Retrieve at least one State Vector")

    def test_get_arrivals_by_airport_reversed_timestamps(self):
        with self.assertRaisesRegex(
            Exception, "The end parameter must be greater than begin"
        ):
            self.api.get_arrivals_by_airport("EDDF", 1517230800, 1517227200)

    def test_get_arrivals_by_airport_too_long_time_interval(self):
        with self.assertRaisesRegex(
            Exception, "The time interval must not span more than 1 UTC calendar day"
        ):
            self.api.get_arrivals_by_airport("EDDF", 1517184000, 1517184000 + 2 * 86400)

    def test_get_departures_by_airport(self):
        r = self.api.get_departures_by_airport("EDDF", 1517227200, 1517230800)
        self.assertGreater(len(r), 0, "Retrieve at least one State Vector")

    def test_get_departures_by_airport_reversed_timestamps(self):
        with self.assertRaisesRegex(
            Exception, "The end parameter must be greater than begin"
        ):
            self.api.get_departures_by_airport("EDDF", 1517230800, 1517227200)

    def test_get_departures_by_airport_too_long_time_interval(self):
        with self.assertRaisesRegex(
            Exception, "The time interval must not span more than 1 UTC calendar day"
        ):
            self.api.get_departures_by_airport("EDDF", 1517184000, 1517184000 + 2 * 86400)
