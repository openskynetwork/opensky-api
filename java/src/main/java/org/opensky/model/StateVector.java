package org.opensky.model;

import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
import java.util.HashSet;
import java.util.Set;

/**
 * Represents the State of a vehicle as seen by the network at a particular time.
 *
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
@Getter
@Setter
public class StateVector implements Serializable {
	private static final long serialVersionUID = -8285575266619754750L;

	private Double geoAltitude;
	private Double longitude;
	private Double latitude;
	private Double velocity;
	private Double heading;
	private Double verticalRate;
	private String icao24;
	private String callsign;
	private boolean onGround;
	private Double lastContact;
	private Double lastPositionUpdate;
	private String originCountry;
	private String squawk;
	private boolean spi;
	private Double baroAltitude;
	private PositionSource positionSource;

	private Set<Integer> serials;

	public StateVector(String icao24) {
		if (icao24 == null) throw new RuntimeException("Invalid icao24. Must not be null");
		this.icao24 = icao24;
		this.serials = null;
	}


	public void addSerial(int serial) {
		if (this.serials == null) {
			this.serials = new HashSet<>();
		}
		this.serials.add(serial);
	}

	@Override
	public String toString() {
		return "StateVector{" +
				"geoAltitude=" + geoAltitude +
				", longitude=" + longitude +
				", latitude=" + latitude +
				", velocity=" + velocity +
				", heading=" + heading +
				", verticalRate=" + verticalRate +
				", icao24='" + icao24 + '\'' +
				", callsign='" + callsign + '\'' +
				", onGround=" + onGround +
				", lastContact=" + lastContact +
				", lastPositionUpdate=" + lastPositionUpdate +
				", originCountry='" + originCountry + '\'' +
				", squawk='" + squawk + '\'' +
				", spi=" + spi +
				", baroAltitude=" + baroAltitude +
				", positionSource=" + positionSource +
				", serials=" + serials +
				'}';
	}

	@Override
	public boolean equals(Object o) {
		if (this == o) return true;
		if (!(o instanceof StateVector)) return false;

		StateVector that = (StateVector) o;

		if (onGround != that.onGround) return false;
		if (spi != that.spi) return false;
		if (geoAltitude != null ? !geoAltitude.equals(that.geoAltitude) : that.geoAltitude != null) return false;
		if (longitude != null ? !longitude.equals(that.longitude) : that.longitude != null) return false;
		if (latitude != null ? !latitude.equals(that.latitude) : that.latitude != null) return false;
		if (velocity != null ? !velocity.equals(that.velocity) : that.velocity != null) return false;
		if (heading != null ? !heading.equals(that.heading) : that.heading != null) return false;
		if (verticalRate != null ? !verticalRate.equals(that.verticalRate) : that.verticalRate != null) return false;
		if (!icao24.equals(that.icao24)) return false;
		if (callsign != null ? !callsign.equals(that.callsign) : that.callsign != null) return false;
		if (lastContact != null ? !lastContact.equals(that.lastContact) : that.lastContact != null) return false;
		if (lastPositionUpdate != null ? !lastPositionUpdate.equals(that.lastPositionUpdate) : that.lastPositionUpdate != null)
			return false;
		if (originCountry != null ? !originCountry.equals(that.originCountry) : that.originCountry != null)
			return false;
		if (squawk != null ? !squawk.equals(that.squawk) : that.squawk != null) return false;
		if (baroAltitude != null ? !baroAltitude.equals(that.baroAltitude) : that.baroAltitude != null) return false;
		if (positionSource != that.positionSource) return false;
		return serials != null ? serials.equals(that.serials) : that.serials == null;
	}

	@Override
	public int hashCode() {
		int result = geoAltitude != null ? geoAltitude.hashCode() : 0;
		result = 31 * result + (longitude != null ? longitude.hashCode() : 0);
		result = 31 * result + (latitude != null ? latitude.hashCode() : 0);
		result = 31 * result + (velocity != null ? velocity.hashCode() : 0);
		result = 31 * result + (heading != null ? heading.hashCode() : 0);
		result = 31 * result + (verticalRate != null ? verticalRate.hashCode() : 0);
		result = 31 * result + icao24.hashCode();
		result = 31 * result + (callsign != null ? callsign.hashCode() : 0);
		result = 31 * result + (onGround ? 1 : 0);
		result = 31 * result + (lastContact != null ? lastContact.hashCode() : 0);
		result = 31 * result + (lastPositionUpdate != null ? lastPositionUpdate.hashCode() : 0);
		result = 31 * result + (originCountry != null ? originCountry.hashCode() : 0);
		result = 31 * result + (squawk != null ? squawk.hashCode() : 0);
		result = 31 * result + (spi ? 1 : 0);
		result = 31 * result + (baroAltitude != null ? baroAltitude.hashCode() : 0);
		result = 31 * result + (positionSource != null ? positionSource.hashCode() : 0);
		result = 31 * result + (serials != null ? serials.hashCode() : 0);
		return result;
	}

	public enum PositionSource {
		ADS_B,
		ASTERIX,
		MLAT,
		FLARM,
		UNKNOWN
	}

}
