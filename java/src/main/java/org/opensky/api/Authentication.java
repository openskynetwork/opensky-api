package org.opensky.api;

import okhttp3.*;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;

/**
 * The Authentication class is responsible for handling authentication
 * requests to retrieve an access token from the OpenSky Network's authentication API.
 */
public class Authentication {

    /**
     * The API endpoint for retrieving an access token from the OpenSky Network's authentication system.
     * This URL is used to send authentication requests with client credentials to obtain access tokens.
     */
    private static final String TOKEN_API =
            "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token";

    /**
     * Retrieves an access token from the authentication API using the provided client credentials.
     *
     * @param clientId the client identifier to authenticate with the API
     * @param clientSecret the client secret associated with the client identifier
     * @return the access token as a string
     * @throws RuntimeException if the token retrieval fails or an I/O error occurs
     */
    public String accessToken(String clientId, String clientSecret) {
        // Create the OkHttpClient instance
        OkHttpClient client = new OkHttpClient();

        // Build the request body with the required parameters
        RequestBody requestBody = new FormBody.Builder()
                .add("grant_type", "client_credentials")
                .add("client_id", clientId)
                .add("client_secret", clientSecret)
                .build();

        // Create the POST request
        Request request = new Request.Builder()
                .url(TOKEN_API)
                .post(requestBody)
                .addHeader("Content-Type", "application/x-www-form-urlencoded")
                .build();

        // Execute the request
        try (Response response = client.newCall(request).execute()) {
            if (response.isSuccessful() && response.body() != null) {
                String responseBody = response.body().string();
                ObjectMapper mapper = new ObjectMapper();
                JsonNode jsonNode = mapper.readTree(responseBody);
                String accessToken = jsonNode.get("access_token").asText();
                //System.out.println("Access Token: " + accessToken);
                return accessToken;
            } else {
                throw new RuntimeException("Failed to fetch access token. Response: " + response);
            }
        } catch (IOException e) {
            throw new RuntimeException(e);
        }

    }
}
