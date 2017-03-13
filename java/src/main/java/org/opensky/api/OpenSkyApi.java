package org.opensky.api;


import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import org.apache.http.*;
import org.apache.http.client.ClientProtocolException;
import org.apache.http.client.HttpResponseException;
import org.apache.http.client.ResponseHandler;
import org.apache.http.client.fluent.Executor;
import org.apache.http.client.fluent.Request;
import org.apache.http.client.utils.URIBuilder;
import org.apache.http.entity.ContentType;
import org.apache.http.message.BasicNameValuePair;
import org.opensky.model.OpenSkyStates;
import org.opensky.model.OpenSkyStatesDeserializer;

import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URISyntaxException;
import java.nio.charset.Charset;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

/**
 * Main class of the OpenSky Network API. Instances retrieve data from OpenSky via HTTP
 *
 * @author Markus Fuchs, fuchs@opensky-network.org
 */
public class OpenSkyApi {
	private static final String HOST = "opensky-network.org";
	private static final String API_ROOT = "https://" + HOST + "/api";
	private static final String STATES_URI = API_ROOT + "/states/all";
	private static final String MY_STATES_URI = API_ROOT + "/states/own";
	
	private static HttpHost proxy;

	private String username;
	private String password;

	private final ObjectMapper mapper;
	private final ResponseHandler<OpenSkyStates> statesRh;

	private Executor executor;
	private final Map<Integer, Long> lastRequestTime;

	/**
	 * Create an instance of the API for anonymous access.
	 */
	public OpenSkyApi() {
		lastRequestTime = new HashMap<Integer, Long>();
		// set up JSON mapper
		mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		// handler for responses with OpenSkyStates
		statesRh = new ResponseHandler<OpenSkyStates>() {

			/**
			 * @return OpenSky states as parsed from JSON response
			 * @throws HttpResponseException if there was an HTTP error
			 * @throws ClientProtocolException if response body is empty
			 */
			public OpenSkyStates handleResponse(final HttpResponse response) throws IOException {
				StatusLine statusLine = response.getStatusLine();
				HttpEntity entity = response.getEntity();
				if (statusLine.getStatusCode() >= 300) {
					throw new HttpResponseException(
							statusLine.getStatusCode(),
							statusLine.getReasonPhrase());
				}
				if (entity == null) {
					throw new ClientProtocolException("Response contains no content");
				}
				ContentType contentType = ContentType.getOrDefault(entity);
				Charset charset = contentType.getCharset();
				return mapper.readValue(new InputStreamReader(entity.getContent(), charset), OpenSkyStates.class);
			}
		};

		executor = Executor.newInstance();
	}

	/**
	 * Create an instance of the API for authenticated access
	 * @param username an OpenSky username
	 * @param password an OpenSky password for the given username
	 */
	public OpenSkyApi(String username, String password) {
		this();
		this.username = username;
		this.password = password;
		executor = executor.auth(username, password).authPreemptive(new HttpHost(HOST, 443, "https"));
	}

	/**
	 * Prevent client from sending too many requests. Checks are applied on server-side, too.
	 * @param key identifies calling function (0 = getStates, 1 = getMyStates)
	 * @param timeDiffAuth time im ms that must be in between two consecutive calls if user is authenticated
	 * @param timeDiffNoAuth time im ms that must be in between two consecutive calls if user is not authenticated
	 * @return true if request may be issued, false otherwise
	 */
	private boolean checkRateLimit(int key, long timeDiffAuth, long timeDiffNoAuth) {
		Long t = lastRequestTime.get(key);
		long now = System.currentTimeMillis();
		lastRequestTime.put(key, now);
		return (t == null || (username != null && now - t > timeDiffAuth) ||
				(username == null && now - t > timeDiffNoAuth));
	}

	/**
	 * Get states from server and handle errors
	 * @throws HttpResponseException if there was an HTTP error
	 * @throws ClientProtocolException if response body is empty
	 */
	private OpenSkyStates getOpenSkyStates(String baseUri, ArrayList<NameValuePair> nvps) throws IOException {
		try {
			return statesRh.handleResponse(executor.execute(Request.Get(new URIBuilder(baseUri)
					.addParameters(nvps).build()).viaProxy(proxy)).returnResponse());
		} catch (URISyntaxException e) {
			// this should not happen
			e.printStackTrace();
			throw new RuntimeException("Prgramming Error. Invalid URI. Please report a bug");
		}
	}

	/**
	 * Retrieve state vectors for a given time. If time == 0 the most recent ones are taken.
	 * Optional filters might be applied for ICAO24 addresses.
	 *
	 * @param time Unix time stamp (seconds since epoch).
	 * @param icao24 retrieve only state vectors for the given ICAO24 addresses. If {@code null}, no filter will be applied on the ICAO24 address.
	 * @return {@link OpenSkyStates} if request was successful, {@code null} otherwise or if there's no new data/rate limit reached
	 * @throws HttpResponseException if there was an HTTP error
	 * @throws ClientProtocolException if response body is empty
	 */
	public OpenSkyStates getStates(int time, String[] icao24) throws IOException {
		ArrayList<NameValuePair> nvps = new ArrayList<NameValuePair>();
		if (icao24 != null) {
			for (String i : icao24) {
				nvps.add(new BasicNameValuePair("icao24", i));
			}
		}
		nvps.add(new BasicNameValuePair("time", Integer.toString(time)));
		return checkRateLimit(0, 4900, 9900) ? getOpenSkyStates(STATES_URI, nvps) : null;
	}

	/**
	 * Retrieve state vectors for your own sensors. Authentication is required for this operation.
	 * If time = 0 the most recent ones are taken. Optional filters may be applied for ICAO24 addresses and sensor
	 * serial numbers.
	 *
	 * @param time Unix time stamp (seconds since epoch).
	 * @param icao24  retrieve only state vectors for the given ICAO24 addresses. If {@code null}, no filter will be applied on the ICAO24 address.
	 * @param serials retrieve only states of vehicles as seen by the given sensors. It expects an array of sensor serial numbers which belong to the given account. If {@code null}, no filter will be applied on the sensor.
	 * @return {@link OpenSkyStates} if request was successful, {@code null} otherwise or if there's no new data/rate limit reached
	 * @throws HttpResponseException if there was an HTTP error
	 * @throws ClientProtocolException if response body is empty
	 */
	public OpenSkyStates getMyStates(int time, String[] icao24, Integer[] serials) throws IOException {
		if (this.username == null || this.password == null) {
			throw new IllegalAccessError("Anonymous access of 'myStates' not allowed");
		}

		ArrayList<NameValuePair> nvps = new ArrayList<NameValuePair>();
		if (icao24 != null) {
			for (String i : icao24) {
				nvps.add(new BasicNameValuePair("icao24", i));
			}
		}
		if (serials != null) {
			for (Integer s : serials) {
				nvps.add(new BasicNameValuePair("serials", Integer.toString(s)));
			}
		}
		nvps.add(new BasicNameValuePair("time", Integer.toString(time)));
		return checkRateLimit(1, 900, 0) ? getOpenSkyStates(MY_STATES_URI, nvps) : null;
	}

	public HttpHost getProxy() {
		return proxy;
	}

	public void setProxy(HttpHost proxy) {
		OpenSkyApi.proxy = proxy;
	}
	
	
}
