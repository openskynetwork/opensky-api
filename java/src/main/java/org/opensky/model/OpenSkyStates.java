package org.opensky.model;

import com.fasterxml.jackson.databind.annotation.JsonDeserialize;

import java.util.Collection;

/**
 * Represents states of vehicles at a given time.
 *
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
@JsonDeserialize(using = OpenSkyStatesDeserializer.class)
public class OpenSkyStates {
	private int time;
	private Collection<StateVector> flightStates;

	/**
	 * @return The point in time for which states are stored
	 */
	public int getTime() {
		return time;
	}
	public void setTime(int time) {
		this.time = time;
	}

	/**
	 * @return Actual states for this point in time
	 */
	public Collection<StateVector> getStates() {
		if (flightStates == null || flightStates.isEmpty()) return null;
		return this.flightStates;
	}

	public void setStates(Collection<StateVector> states) {
		this.flightStates = states;
	}
}