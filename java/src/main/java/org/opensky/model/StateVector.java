package org.opensky.model;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;

/**
 * Represents the State of a vehicle as seen by the network at a particular time.
 *
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
public class StateVector implements Serializable {
	private static final long serialVersionUID = -8285575266619754750L;

	private Double altitude;
	private Double longitude;
	private Double latitude;
	private Double velocity;
	private Double heading;
	private Double verticalRate;
	private String icao24;
	private String callsign;
	private boolean onGround;
	private Double lastVelocityUpdate;
	private Double lastPositionUpdate;
	private String originCountry;

	private Set<Integer> serials;

	public StateVector(String icao24) {
		this.icao24 = icao24;
		this.serials = null;
	}

	/**
	 * @return altitude in meters. Can be {@code null}.
	 */
	public Double getAltitude() {
		return altitude;
	}

	public void setAltitude(Double altitude) {
		this.altitude = altitude;
	}

	/**
	 * @return longitude in ellipsoidal coordinates (WGS-84) and degrees. Can be {@code null}
	 */
	public Double getLongitude() {
		return longitude;
	}

	public void setLongitude(Double longitude) {
		this.longitude = longitude;
	}

	/**
	 * @return latitude in ellipsoidal coordinates (WGS-84) and degrees. Can be {@code null}
	 */
	public Double getLatitude() {
		return latitude;
	}

	public void setLatitude(Double latitude) {
		this.latitude = latitude;
	}

	/**
	 * @return over ground in m/s. Can be {@code null} if information not present
	 */
	public Double getVelocity() {
		return velocity;
	}

	public void setVelocity(Double velocity) {
		this.velocity = velocity;
	}

	/**
	 * @return in decimal degrees (0 is north). Can be {@code null} if information not present
	 */
	public Double getHeading() {
		return heading;
	}

	public void setHeading(Double heading) {
		this.heading = heading;
	}

	/**
	 * @return in m/s, incline is positive, decline negative. Can be {@code null} if information not present.
	 */
	public Double getVerticalRate() {
		return verticalRate;
	}

	public void setVerticalRate(Double verticalRate) {
		this.verticalRate = verticalRate;
	}

	/**
	 * @return ICAO24 address of the transmitter in hex string representation.
	 */
	public String getIcao24() {
		return icao24;
	}

	public void setIcao24(String icao24) {
		this.icao24 = icao24;
	}

	/**
	 * @return callsign of the vehicle. Can be {@code null} if no callsign has been received.
	 */
	public String getCallsign() { return callsign;	}

	public void setCallsign(String callsign) {
		this.callsign = callsign;
	}

	/**
	 * @return true if aircraft is on ground (sends ADS-B surface position reports).
	 */
	public boolean isOnGround() {
		return onGround;
	}

	public void setOnGround(boolean onGround) {
		this.onGround = onGround;
	}

	/**
	 * @return  seconds since epoch of last velocity report. Can be {@code null} if there was no velocity report received by OpenSky within 15s before.
	 */
	public Double getLastVelocityUpdate() {
		return lastVelocityUpdate;
	}

	public void setLastVelocityUpdate(Double lastVelocityUpdate) {
		this.lastVelocityUpdate = lastVelocityUpdate;
	}

	/**
	 * @return seconds since epoch of last position report. Can be {@code null} if there was no position report received by OpenSky within 15s before.
	 */
	public Double getLastPositionUpdate() {
		return lastPositionUpdate;
	}

	public void setLastPositionUpdate(Double lastPositionUpdate) {
		this.lastPositionUpdate = lastPositionUpdate;
	}

	public void addSerial(int serial) {
		if (this.serials == null) {
			this.serials = new HashSet<>();
		}
		this.serials.add(serial);
	}

	/**
	 * @return serial numbers of sensors which received messages from the vehicle within the validity period of this state vector. {@code null} if information is not present, i.e., there was no filter for a sensor in the request
	 */
	public Set<Integer> getSerials() {
		return this.serials;
	}

	/**
	 * @return the country inferred through the ICAO24 address
	 */
	public String getOriginCountry() {
		return originCountry;
	}

	public void setOriginCountry(String originCountry) {
		this.originCountry = originCountry;
	}
}
