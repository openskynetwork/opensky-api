OpenSky Java API
================

Have a look at the `Javadoc <javadoc/org/opensky/api/OpenSkyApi.html>`_ for a more detailed explanation of the data types.
The Java binding is a wrapper for OpenSky's REST API. We strongly recommend to read the :doc:`REST API documentation <rest>` first.

Usage
-----

Install it in your local repository::

    mvn clean install


and add the following dependency to your project::

    <dependency>
        <groupId>org.opensky</groupId>
        <artifactId>opensky-api</artifactId>
        <version>1.3.0</version>
    </dependency>


Examples
--------

Retrieve :ref:`state vectors <state-vectors>` in real-time for your own sensors::

    OpenSkyApi api = new OpenSkyApi(USERNAME, PASSWORD);
    // no filter on icao24 or sensor serial number
    OpenSkyStates os = api.getMyStates(0, null, null);

This will return all state vectors which as least one of your receivers contributed to. Use this to retrieven the unlimited
live view of your receiver. You may apply additional filters on the aircraft (by ICAO 24-bit address) or decide to retrieve
only states of a particular sensor owned by you::

    OpenSkyApi api = new OpenSkyApi(USERNAME, PASSWORD);
    // filter for states of particular aircraft
    OpenSkyStates os = api.getMyStates(0, new String[] { "aabbcc", "cafeca" }, null);
    // or add another filter for a sub set of your receivers
    OpenSkyStates os = api.getMyStates(0, null, new Integer[] { 12345678 });
    // or do both
    OpenSkyStates os = api.getMyStates(0, new String[] { "aabbcc", "coffee" },
                                       new Integer[] { 12345678 });


Retrieve all state vectors, i.e. the current global view of the network::

    OpenSkyApi api = new OpenSkyApi(USERNAME, PASSWORD);
    OpenSkyStates os = api.getStates(0, null);

Keep in mind that there are :ref:`rate limitiations <limitations-anon>` for the global view!

It is also possible to retrieve state vectors for a certain area. For this purpose, you need to provide a bounding box. It is defined by lower and upper bounds for longitude and latitude. The following example shows how to retrieve data for a bounding box which encompasses Switzerland::

    OpenSkyApi api = new OpenSkyApi(USERNAME, PASSWORD);
    OpenSkyStates os = api.getStates(0, null, 
        new OpenSkyApi.BoundingBox(45.8389, 47.8229, 5.9962, 10.5226));



