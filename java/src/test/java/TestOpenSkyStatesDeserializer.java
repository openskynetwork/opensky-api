import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.junit.Test;
import org.opensky.model.OpenSkyStates;
import org.opensky.model.OpenSkyStatesDeserializer;
import org.opensky.model.StateVector;

import java.io.IOException;
import java.util.Iterator;

import static org.junit.Assert.*;

/**
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
public class TestOpenSkyStatesDeserializer {
	static final String validJson = "{" +
			"\"time\":1002," +
			"\"states\":[" +
				"[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,null]," +
				"[\"cabeef\",null,\"USA\",null,1000,null,null,null,false,4.0,5.0,6.0,null]," +
				"[\"cabeef\",null,\"USA\",1001,null,1.0,2.0,3.0,false,null,null,null,null]," +
				"[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,[1234,6543]]," +
				"[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,[1234]]," +
				"[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,true,4.0,5.0,6.0,[]]" +
				"]}";

	static final String invalidJson = "{" +
			"\"time\":1002," +
			"\"states\":[" +
				"[null,\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,null]" +
			"]}";

	@Test(expected = JsonMappingException.class)
	public void testInvalidDeser() throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		mapper.readValue(invalidJson, OpenSkyStates.class);
	}

	@Test(expected = JsonMappingException.class)
	public void testInvalidDeser2() throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		// ObjectMapper throws Exception here
		mapper.readValue("", OpenSkyStates.class);
	}

	@Test
	public void testInvalidDeser3() throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		OpenSkyStates states = mapper.readValue("{}", OpenSkyStates.class);
		assertEquals(0, states.getTime());
		assertNull(states.getStates());

		states = mapper.readValue("null", OpenSkyStates.class);
		assertNull(states);
	}

	@Test
	public void testDeser() throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		OpenSkyStates states = mapper.readValue(validJson, OpenSkyStates.class);
		assertEquals("Correct Time", 1002, states.getTime());
		assertEquals("Number states", 6, states.getStates().size());

		// possible cases for state vectors
		Iterator<StateVector> statesIt = states.getStates().iterator();

		// "[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,null],"
		StateVector sv = statesIt.next();
		assertEquals( "cabeef", sv.getIcao24());
		assertEquals("ABCDEFG", sv.getCallsign());
		assertEquals("USA", sv.getOriginCountry());
		assertEquals(new Double(1001), sv.getLastPositionUpdate());
		assertEquals(new Double(1000), sv.getLastVelocityUpdate());
		assertEquals(new Double(1.0), sv.getLongitude());
		assertEquals(new Double(2.0), sv.getLatitude());
		assertEquals(new Double(3.0), sv.getAltitude());
		assertEquals(new Double(4.0), sv.getVelocity());
		assertEquals(new Double(5.0), sv.getHeading());
		assertEquals(new Double(6.0), sv.getVerticalRate());
		assertFalse(sv.isOnGround());
		assertNull(sv.getSerials());

		// "[\"cabeef\",null,\"USA\",null,1000,null,null,null,false,4.0,5.0,6.0,null],"
		sv = statesIt.next();
		assertEquals( "cabeef", sv.getIcao24());
		assertNull(sv.getCallsign());
		assertEquals("USA", sv.getOriginCountry());
		assertNull(sv.getLastPositionUpdate());
		assertEquals(new Double(1000), sv.getLastVelocityUpdate());
		assertNull(sv.getLongitude());
		assertNull(sv.getLatitude());
		assertNull(sv.getAltitude());
		assertEquals(new Double(4.0), sv.getVelocity());
		assertEquals(new Double(5.0), sv.getHeading());
		assertEquals(new Double(6.0), sv.getVerticalRate());
		assertFalse(sv.isOnGround());
		assertNull(sv.getSerials());

		// "[\"cabeef\",null,\"USA\",1001,null,1.0,2.0,3.0,false,null,null,null,null],"
		sv = statesIt.next();
		assertEquals( "cabeef", sv.getIcao24());
		assertNull(sv.getCallsign());
		assertEquals("USA", sv.getOriginCountry());
		assertEquals(new Double(1001), sv.getLastPositionUpdate());
		assertNull(sv.getLastVelocityUpdate());
		assertEquals(new Double(1.0), sv.getLongitude());
		assertEquals(new Double(2.0), sv.getLatitude());
		assertEquals(new Double(3.0), sv.getAltitude());
		assertNull(sv.getVelocity());
		assertNull(sv.getHeading());
		assertNull(sv.getVerticalRate());
		assertFalse(sv.isOnGround());
		assertNull(sv.getSerials());

		// "[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,[1234,6543]],"
		sv = statesIt.next();
		assertEquals( "cabeef", sv.getIcao24());
		assertEquals("ABCDEFG", sv.getCallsign());
		assertEquals("USA", sv.getOriginCountry());
		assertEquals(new Double(1001), sv.getLastPositionUpdate());
		assertEquals(new Double(1000), sv.getLastVelocityUpdate());
		assertEquals(new Double(1.0), sv.getLongitude());
		assertEquals(new Double(2.0), sv.getLatitude());
		assertEquals(new Double(3.0), sv.getAltitude());
		assertEquals(new Double(4.0), sv.getVelocity());
		assertEquals(new Double(5.0), sv.getHeading());
		assertEquals(new Double(6.0), sv.getVerticalRate());
		assertFalse(sv.isOnGround());
		assertArrayEquals(new Integer[] {1234, 6543}, sv.getSerials().toArray(new Integer[sv.getSerials().size()]));

		// "[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,false,4.0,5.0,6.0,[1234]],"
		sv = statesIt.next();
		assertEquals( "cabeef", sv.getIcao24());
		assertEquals("ABCDEFG", sv.getCallsign());
		assertEquals("USA", sv.getOriginCountry());
		assertEquals(new Double(1001), sv.getLastPositionUpdate());
		assertEquals(new Double(1000), sv.getLastVelocityUpdate());
		assertEquals(new Double(1.0), sv.getLongitude());
		assertEquals(new Double(2.0), sv.getLatitude());
		assertEquals(new Double(3.0), sv.getAltitude());
		assertEquals(new Double(4.0), sv.getVelocity());
		assertEquals(new Double(5.0), sv.getHeading());
		assertEquals(new Double(6.0), sv.getVerticalRate());
		assertFalse(sv.isOnGround());
		assertArrayEquals(new Integer[] {1234}, sv.getSerials().toArray(new Integer[sv.getSerials().size()]));


		// "[\"cabeef\",\"ABCDEFG\",\"USA\",1001,1000,1.0,2.0,3.0,true,4.0,5.0,6.0,[]],"
		sv = statesIt.next();
		assertEquals( "cabeef", sv.getIcao24());
		assertEquals("ABCDEFG", sv.getCallsign());
		assertEquals("USA", sv.getOriginCountry());
		assertEquals(new Double(1001), sv.getLastPositionUpdate());
		assertEquals(new Double(1000), sv.getLastVelocityUpdate());
		assertEquals(new Double(1.0), sv.getLongitude());
		assertEquals(new Double(2.0), sv.getLatitude());
		assertEquals(new Double(3.0), sv.getAltitude());
		assertEquals(new Double(4.0), sv.getVelocity());
		assertEquals(new Double(5.0), sv.getHeading());
		assertEquals(new Double(6.0), sv.getVerticalRate());
		assertTrue(sv.isOnGround());
		assertNull(sv.getSerials());
	}

	//@Test
	public void testDeserSpeed() throws IOException {
		ObjectMapper mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		long count = 1000000;
		long t0 = System.nanoTime();
		for (long i = 0; i < count; i++) {
			mapper.readValue(validJson, OpenSkyStates.class);
		}
		long t1 = System.nanoTime();
		System.out.println("Average time: " + ((t1 - t0) / count / 1000) + "µs");
	}
}
