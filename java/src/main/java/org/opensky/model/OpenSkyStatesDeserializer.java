package org.opensky.model;

import com.fasterxml.jackson.core.*;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import com.fasterxml.jackson.databind.node.ArrayNode;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;

/**
 * Custom JSON deserializer for OpenSkyStates retrieved from the API.
 *
 * XXX Because actual state vectors arrive as array we need a custom deserializer like this.
 * If anyone comes up with something better, feel free to create a pull request!
 *
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
public class OpenSkyStatesDeserializer extends StdDeserializer<OpenSkyStates> {
	public OpenSkyStatesDeserializer() {
		super(OpenSkyStates.class);
	}

	private Collection<StateVector> deserializeStates(TreeNode statesRoot) throws JsonParseException {
		Iterator<JsonNode> states = ((ArrayNode) statesRoot).elements();
		ArrayList<StateVector> stateVectors = new ArrayList<>();

		while (states.hasNext()) {
			JsonNode vector = states.next();
			String icao24 = vector.get(0).asText();
			if (vector.get(0).isNull())
				throw new JsonParseException(
						String.format("Got 'null' icao24, vector payload: %s", vector), JsonLocation.NA
				);

			StateVector sv = new StateVector(icao24);

			sv.setCallsign(stringOrNull(vector.get(1)));
			sv.setOriginCountry(stringOrNull(vector.get(2)));
			sv.setLastPositionUpdate(doubleOrNull(vector.get(3)));
			sv.setLastContact(doubleOrNull(vector.get(4)));
			sv.setLongitude(doubleOrNull(vector.get(5)));
			sv.setLatitude(doubleOrNull(vector.get(6)));
			sv.setBaroAltitude(doubleOrNull(vector.get(7)));
			sv.setOnGround(vector.get(8).asBoolean());
			sv.setVelocity(doubleOrNull(vector.get(9)));
			sv.setHeading(doubleOrNull(vector.get(10)));
			sv.setVerticalRate(doubleOrNull(vector.get(11)));

			Iterator<JsonNode> serials = vector.get(12).elements(); // Array of serials
			while (serials.hasNext()) {
				JsonNode serial = serials.next();
				sv.addSerial(serial.asInt());
			}

			sv.setGeoAltitude(doubleOrNull(vector.get(13)));
			sv.setSquawk(stringOrNull(vector.get(14)));
			sv.setSpi(vector.get(15).asBoolean());

			int psi = vector.get(16).asInt(0);
			StateVector.PositionSource ps = psi <= StateVector.PositionSource.values().length ?
					StateVector.PositionSource.values()[psi] : StateVector.PositionSource.UNKNOWN;
			sv.setPositionSource(ps);

			stateVectors.add(sv);
		}

		return stateVectors;
	}

	private static Double doubleOrNull(JsonNode node) {
		return node.isNumber() ? node.asDouble() : null;
	}

	private static String stringOrNull(JsonNode node) {
		return node.isNull() ? null : node.asText();
	}

	@Override
	public OpenSkyStates deserialize(JsonParser jp, DeserializationContext dc) throws IOException {
		try {
			OpenSkyStates res = new OpenSkyStates();
			JsonNode node = jp.getCodec().readTree(jp);

			if (node.get("time") != null && node.get("time").isNumber())
				res.setTime(node.get("time").asInt());

			if (node.get("states") != null && node.get("states").isArray())
				res.setStates(deserializeStates(node.get("states")));

			return res;
		} catch (JsonParseException jpe) {
			throw dc.mappingException(OpenSkyStates.class);
		}
	}
}
