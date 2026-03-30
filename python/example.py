#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Example usage of the OpenSky Network API client.
#
# Retrieves all aircraft currently over Germany and prints a summary,
# then shows which of your own receivers are currently active.
#
# Author: Jannis Lübbe <luebbe@opensky-network.org>
# URL:    http://github.com/openskynetwork/opensky-api
#
import os

from opensky_api import OpenSkyApi, TokenManager

# Use credentials file if available, otherwise fall back to anonymous access.
# Anonymous access has reduced rate limits and no access to own sensor data.
_CREDENTIALS_PATH = "credentials.json"


def fmt_alt(value):
    """Format an altitude value, omitting the unit if the value is None."""
    return f"{value}m" if value is not None else "None"


def main():
    if os.path.exists(_CREDENTIALS_PATH):
        tm = TokenManager.from_json_file(_CREDENTIALS_PATH)
        print("Authenticated with credentials file.")
    else:
        tm = None
        print("No credentials file found, using anonymous access (reduced rate limits).")

    with OpenSkyApi(token_manager=tm) as api:
        # Get all aircraft currently over Germany (bounding box)
        print("\n--- Aircraft over Germany ---")
        states = api.get_states(bbox=(47.2, 55.1, 5.9, 15.1))
        if states and states.states:
            for s in states.states:
                print(
                    f"{s.icao24:8s}  {s.callsign or '?':10s}  {s.origin_country:20s}  "
                    f"baro={fmt_alt(s.baro_altitude)}  "
                    f"geo={fmt_alt(s.geo_altitude)}  "
                    f"{'on ground' if s.on_ground else 'airborne'}"
                )
        else:
            print("No states received.")

        # Show which own receivers are currently active and delivering data.
        # Requires authentication.
        if tm is not None:
            print("\n--- Own receivers ---")
            my_states = api.get_my_states()
            if my_states and my_states.states:
                active_serials = set()
                for s in my_states.states:
                    if s.sensors:
                        active_serials.update(s.sensors)
                if active_serials:
                    print(f"Active serials providing data: {sorted(active_serials)}")
                else:
                    print("No sensor information available in state vectors.")
            else:
                print("No states received from own receivers.")


if __name__ == "__main__":
    main()
