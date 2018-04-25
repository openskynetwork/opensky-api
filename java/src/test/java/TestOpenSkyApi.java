import org.junit.Test;
import org.opensky.api.OpenSkyApi;
import org.opensky.model.OpenSkyStates;
import org.opensky.model.StateVector;

import java.io.IOException;
import static org.junit.Assert.*;

/**
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
public class TestOpenSkyApi {

	/** credentials to test authenticated API calls **/
	static final String USERNAME = null;
	static final String PASSWORD = null;
	// serials which belong to the given account
	static final Integer[] SERIALS = null;

	@Test
	public void testAnonGetStates() throws IOException, InterruptedException {
		OpenSkyApi api = new OpenSkyApi();
		long t0 = System.nanoTime();
		OpenSkyStates os = api.getStates(0, null);
		long t1 = System.nanoTime();
		System.out.println("Request anonStates time = " + ((t1 - t0) / 1000000) + "ms");
		assertTrue("More than 1 state vector", os.getStates().size() > 1);
		int time = os.getTime();

		// more than two requests withing ten seconds
		os = api.getStates(0, null);
		assertNull("No new data", os);

		// wait ten seconds
		Thread.sleep(10000);

		// now we can retrieve states again
		t0 = System.nanoTime();
		os = api.getStates(0, null);
		t1 = System.nanoTime();
		System.out.println("Request anonStates time = " + ((t1 - t0) / 1000000) + "ms");
		assertNotNull(os);
		assertTrue("More than 1 state vector for second valid request", os.getStates().size() > 1);
		assertNotEquals(time, os.getTime());

		// test bounding box around Switzerland
		api = new OpenSkyApi();

		try {
			api.getStates(0, null, new OpenSkyApi.BoundingBox(145.8389, 47.8229, 5.9962, 10.5226));
			fail("Illegal coordinates should be detected");
		} catch (RuntimeException re) {
			// NOP
		}

		try {
			api.getStates(0, null, new OpenSkyApi.BoundingBox(45.8389, -147.8229, 5.9962, 10.5226));
			fail("Illegal coordinates should be detected");
		} catch (RuntimeException re) {
			// NOP
		}

		try {
			api.getStates(0, null, new OpenSkyApi.BoundingBox(45.8389, 47.8229, 255.9962, 10.5226));
			fail("Illegal coordinates should be detected");
		} catch (RuntimeException re) {
			// NOP
		}

		try {
			api.getStates(0, null, new OpenSkyApi.BoundingBox(45.8389, 47.8229, 5.9962, -180.5226));
			fail("Illegal coordinates should be detected");
		} catch (RuntimeException re) {
			// NOP
		}

		OpenSkyStates os2 = api.getStates(0, null, new OpenSkyApi.BoundingBox(45.8389, 47.8229, 5.9962, 10.5226));
		assertTrue("Much less states in Switzerland area than world-wide", os2.getStates().size() < os.getStates().size() - 200);
	}

	// can only be tested with a valid account
	@Test
	public void testAuthGetStates() throws IOException, InterruptedException {
		if (USERNAME == null || PASSWORD == null) {
			System.out.println("WARNING: testAuthGetStates needs valid credentials and did not run");
			return;
		}

		OpenSkyApi api = new OpenSkyApi(USERNAME, PASSWORD);
		OpenSkyStates os = api.getStates(0, null);
		assertTrue("More than 1 state vector", os.getStates().size() > 1);
		int time = os.getTime();

		// more than two requests withing ten seconds
		os = api.getStates(0, null);
		assertNull("No new data", os);

		// wait five seconds
		Thread.sleep(5000);

		// now we can retrieve states again
		long t0 = System.nanoTime();
		os = api.getStates(0, null);
		long t1 = System.nanoTime();
		System.out.println("Request authStates time = " + ((t1 - t0) / 1000000) + "ms");
		assertNotNull(os);
		assertTrue("More than 1 state vector for second valid request", os.getStates().size() > 1);
		assertNotEquals(time, os.getTime());
	}

	@Test
	public void testAnonGetMyStates() {
		OpenSkyApi api = new OpenSkyApi();
		try {
			api.getMyStates(0, null, null);
			fail("Anonymous access of 'myStates' expected");
		} catch (IllegalAccessError iae) {
			// like expected
			assertTrue("Mismatched exception message",
					iae.getMessage().equals("Anonymous access of 'myStates' not allowed"));
		} catch (IOException e) {
			fail("Request should not be submitted");
		}
	}

	@Test
	public void testAuthGetMyStates() throws IOException {
		/* DEBUG output:
		 System.setProperty("org.apache.commons.logging.Log","org.apache.commons.logging.impl.SimpleLog");
		 System.setProperty("org.apache.commons.logging.simplelog.showdatetime", "true");
		 System.setProperty("org.apache.commons.logging.simplelog.log.org.apache.http.wire", "DEBUG");
		 System.setProperty("org.apache.commons.logging.simplelog.log.org.apache.http.impl.conn", "DEBUG");
		 System.setProperty("org.apache.commons.logging.simplelog.log.org.apache.http.impl.client", "DEBUG");
		 System.setProperty("org.apache.commons.logging.simplelog.log.org.apache.http.client", "DEBUG");
		 System.setProperty("org.apache.commons.logging.simplelog.log.org.apache.http", "DEBUG");
		 */
		if (USERNAME == null || PASSWORD == null) {
			System.out.println("WARNING: testAuthGetMyStates needs valid credentials and did not run");
			return;
		}

		OpenSkyApi api = new OpenSkyApi(USERNAME, PASSWORD);
		OpenSkyStates os = api.getMyStates(0, null, SERIALS);
		assertTrue("More than 1 state vector", os.getStates().size() > 1);

		for (StateVector sv : os.getStates()) {
			// all states contain at least one of the user's sensors
			boolean gotOne = false;
			for (Integer ser : SERIALS) {
				gotOne = gotOne || sv.getSerials().contains(ser);
			}
			assertTrue(gotOne);
		}
	}

}
