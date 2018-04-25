package org.opensky.api;


import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.module.SimpleModule;
import okhttp3.*;
import org.opensky.model.OpenSkyStates;
import org.opensky.model.OpenSkyStatesDeserializer;

import java.io.IOException;
import java.io.InputStreamReader;
import java.net.MalformedURLException;
import java.nio.charset.Charset;
import java.util.*;

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

	private enum REQUEST_TYPE {
		GET_STATES,
		GET_MY_STATES
	}

	private final boolean authenticated;

	private final ObjectMapper mapper;

	private final OkHttpClient okHttpClient;
	private final Map<REQUEST_TYPE, Long> lastRequestTime;

	private static class BasicAuthInterceptor implements Interceptor {
		private final String credentials;

		BasicAuthInterceptor(String username, String password) {
			credentials = Credentials.basic(username, password);
		}

		@Override
		public Response intercept(Chain chain) throws IOException {
			Request req = chain.request()
					.newBuilder()
					.header("Authorization", credentials)
					.build();
			return chain.proceed(req);
		}
	}

	/**
	 * Create an instance of the API for anonymous access.
	 */
	public OpenSkyApi() {
		this(null, null);
	}

	/**
	 * Create an instance of the API for authenticated access
	 * @param username an OpenSky username
	 * @param password an OpenSky password for the given username
	 */
	public OpenSkyApi(String username, String password) {
		lastRequestTime = new HashMap<>();
		// set up JSON mapper
		mapper = new ObjectMapper();
		SimpleModule sm = new SimpleModule();
		sm.addDeserializer(OpenSkyStates.class, new OpenSkyStatesDeserializer());
		mapper.registerModule(sm);

		authenticated = username != null && password != null;

        if (authenticated) {
            okHttpClient = new OkHttpClient.Builder()
                    .addInterceptor(new BasicAuthInterceptor(username, password))
                    .build();
        } else {
            okHttpClient = new OkHttpClient();
        }
	}

	/** Make the actual HTTP Request and return the parsed response
	 * @param baseUri base uri to request
	 * @param nvps name value pairs to be sent as query parameters
	 * @return parsed states
	 * @throws IOException if there was an HTTP error
	 */
    private OpenSkyStates getResponse(String baseUri, Collection<AbstractMap.Entry<String,String>> nvps) throws IOException {
        HttpUrl parsedUrl = HttpUrl.parse(baseUri);
        if (parsedUrl == null) {
			throw new MalformedURLException("Could not parse uri " + baseUri);
		}

        HttpUrl.Builder urlBuilder = parsedUrl.newBuilder();
        for (AbstractMap.Entry<String,String> nvp : nvps) {
			urlBuilder.addQueryParameter(nvp.getKey(), nvp.getValue());
		}
        Request req = new Request.Builder()
                .url(urlBuilder.build())
                .build();

        Response response = okHttpClient.newCall(req).execute();
        if (!response.isSuccessful()) {
			throw new IOException("Could not get OpenSky Vectors, response " + response);
		}

        String contentType = response.header("Content-Type");
        Charset charset = null;
        if (contentType != null) {
            MediaType mediaType = MediaType.parse(contentType);
            if (mediaType != null) {
				charset = mediaType.charset();
			}
        }
        if (charset != null) {
            return mapper.readValue(new InputStreamReader(response.body().byteStream(), charset), OpenSkyStates.class);
        } else {
            throw new IOException("Could not read charset in response. Content-Type is " + contentType);
        }
    }

	/**
	 * Prevent client from sending too many requests. Checks are applied on server-side, too.
	 * @param type identifies calling function (GET_STATES or GET_MY_STATES)
	 * @param timeDiffAuth time im ms that must be in between two consecutive calls if user is authenticated
	 * @param timeDiffNoAuth time im ms that must be in between two consecutive calls if user is not authenticated
	 * @return true if request may be issued, false otherwise
	 */
	private boolean checkRateLimit(REQUEST_TYPE type, long timeDiffAuth, long timeDiffNoAuth) {
		Long t = lastRequestTime.get(type);
		long now = System.currentTimeMillis();
		lastRequestTime.put(type, now);
		return (t == null || (authenticated && now - t > timeDiffAuth) || (!authenticated && now - t > timeDiffNoAuth));
	}

	/**
	 * Get states from server and handle errors
	 * @throws IOException if there was an HTTP error
	 */
	private OpenSkyStates getOpenSkyStates(String baseUri, ArrayList<AbstractMap.Entry<String,String>> nvps) throws IOException {
		try {
			return getResponse(baseUri, nvps);
		} catch (MalformedURLException e) {
			// this should not happen
			e.printStackTrace();
			throw new RuntimeException("Programming Error in OpenSky API. Invalid URI. Please report a bug");
		} catch (JsonParseException | JsonMappingException e) {
			// this should not happen
			e.printStackTrace();
			throw new RuntimeException("Programming Error in OpenSky API. Could not parse JSON Data. Please report a bug");
		}
	}

	/**
	 * Represents a bounding box of WGS84 coordinates (decimal degrees) that encompasses a certain area. It is
	 * defined by a lower and upper bound for latitude and longitude.
	 */
	public static class BoundingBox {
		private double minLatitude;
		private double minLongitude;
		private double maxLatitude;
		private double maxLongitude;

		/**
		 * Create a bounding box, given the lower and upper bounds for latitude and longitude.
		 */
		public BoundingBox(double minLatitude, double maxLatitude,  double minLongitude, double maxLongitude) {
			checkLatitude(minLatitude);
			checkLatitude(maxLatitude);
			checkLongitude(minLongitude);
			checkLongitude(maxLongitude);

			this.minLatitude = minLatitude;
			this.minLongitude = minLongitude;
			this.maxLatitude = maxLatitude;
			this.maxLongitude = maxLongitude;
		}

		public double getMinLatitude() {
			return minLatitude;
		}

		public double getMinLongitude() {
			return minLongitude;
		}

		public double getMaxLatitude() {
			return maxLatitude;
		}

		public double getMaxLongitude() {
			return maxLongitude;
		}

		@Override
		public boolean equals(Object o) {
			if (this == o) return true;
			if (!(o instanceof BoundingBox)) return false;

			BoundingBox that = (BoundingBox) o;

			if (Double.compare(that.minLatitude, minLatitude) != 0) return false;
			if (Double.compare(that.minLongitude, minLongitude) != 0) return false;
			if (Double.compare(that.maxLatitude, maxLatitude) != 0) return false;
			return Double.compare(that.maxLongitude, maxLongitude) == 0;
		}

		@Override
		public int hashCode() {
			int result;
			long temp;
			temp = Double.doubleToLongBits(minLatitude);
			result = (int) (temp ^ (temp >>> 32));
			temp = Double.doubleToLongBits(minLongitude);
			result = 31 * result + (int) (temp ^ (temp >>> 32));
			temp = Double.doubleToLongBits(maxLatitude);
			result = 31 * result + (int) (temp ^ (temp >>> 32));
			temp = Double.doubleToLongBits(maxLongitude);
			result = 31 * result + (int) (temp ^ (temp >>> 32));
			return result;
		}

		private void checkLatitude(double lat) {
			if (lat < -90 || lat > 90) throw new RuntimeException(String.format("Illegal latitude %f. Must be within [-90, 90]", lat));
		}

		private void checkLongitude(double lon) {
			if (lon < -180 || lon > 180) throw new RuntimeException(String.format("Illegal longitude %f. Must be within [-90, 90]", lon));
		}
	}

	/**
	 * Retrieve state vectors for a given time. If time == 0 the most recent ones are taken.
	 * Optional filters might be applied for ICAO24 addresses.
	 *
	 * @param time Unix time stamp (seconds since epoch).
	 * @param icao24 retrieve only state vectors for the given ICAO24 addresses. If {@code null}, no filter will be applied on the ICAO24 address.
	 * @return {@link OpenSkyStates} if request was successful, {@code null} otherwise or if there's no new data/rate limit reached
	 * @throws IOException if there was an HTTP error
	 */
	public OpenSkyStates getStates(int time, String[] icao24) throws IOException {
		ArrayList<AbstractMap.Entry<String,String>> nvps = new ArrayList<>();
		if (icao24 != null) {
			for (String i : icao24) {
				nvps.add(new AbstractMap.SimpleImmutableEntry<>("icao24", i));
			}
		}
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("time", Integer.toString(time)));
		return checkRateLimit(REQUEST_TYPE.GET_STATES, 4900, 9900) ? getOpenSkyStates(STATES_URI, nvps) : null;
	}

	/**
	 * Retrieve state vectors for a given time. If time == 0 the most recent ones are taken.
	 * Optional filters might be applied for ICAO24 addresses.
	 * Furthermore, data can be retrieved for a certain area by using a bounding box.
	 *
	 * @param time Unix time stamp (seconds since epoch).
	 * @param icao24 retrieve only state vectors for the given ICAO24 addresses. If {@code null}, no filter will be applied on the ICAO24 address.
	 * @param bbox bounding box to retrieve data for a certain area. If {@code null}, no filter will be applied on the position.
	 * @return {@link OpenSkyStates} if request was successful, {@code null} otherwise or if there's no new data/rate limit reached
	 * @throws IOException if there was an HTTP error
	 */
	public OpenSkyStates getStates(int time, String[] icao24, BoundingBox bbox) throws IOException {
		if (bbox == null) return getStates(time, icao24);

		ArrayList<AbstractMap.Entry<String,String>> nvps = new ArrayList<>();
		if (icao24 != null) {
			for (String i : icao24) {
				nvps.add(new AbstractMap.SimpleImmutableEntry<>("icao24", i));
			}
		}
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("time", Integer.toString(time)));
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("lamin", Double.toString(bbox.getMinLatitude())));
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("lamax", Double.toString(bbox.getMaxLatitude())));
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("lomin", Double.toString(bbox.getMinLongitude())));
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("lomax", Double.toString(bbox.getMaxLongitude())));
		return checkRateLimit(REQUEST_TYPE.GET_STATES, 4900, 9900) ? getOpenSkyStates(STATES_URI, nvps) : null;
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
	 * @throws IOException if there was an HTTP error
	 */
	public OpenSkyStates getMyStates(int time, String[] icao24, Integer[] serials) throws IOException {
		if (!authenticated) {
			throw new IllegalAccessError("Anonymous access of 'myStates' not allowed");
		}

        ArrayList<AbstractMap.Entry<String,String>> nvps = new ArrayList<>();
		if (icao24 != null) {
			for (String i : icao24) {
				nvps.add(new AbstractMap.SimpleImmutableEntry<>("icao24", i));
			}
		}
		if (serials != null) {
			for (Integer s : serials) {
				nvps.add(new AbstractMap.SimpleImmutableEntry<>("serials", Integer.toString(s)));
			}
		}
		nvps.add(new AbstractMap.SimpleImmutableEntry<>("time", Integer.toString(time)));
		return checkRateLimit(REQUEST_TYPE.GET_MY_STATES, 900, 0) ? getOpenSkyStates(MY_STATES_URI, nvps) : null;
	}
}
